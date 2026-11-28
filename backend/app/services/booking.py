"""Availability search, booking (single & multi-room) and cancellation.

All write paths run inside one transaction supplied by the caller
(`get_tx`). A transaction-level advisory lock serialises writers so the ids
allocated with `next_id` (compatible with both schema.sql and V001 IDENTITY)
cannot collide, and candidate rooms are locked in deterministic `room_id`
order with `FOR UPDATE` to prevent deadlocks on multi-room bookings.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from app.deps import CurrentUser
from app.errors import conflict, forbidden, invalid, not_found

ID_LOCK = 7_420_001
MAX_NIGHTS = 30
HOTEL_TZ = timezone(timedelta(hours=7))  # Asia/Ho_Chi_Minh, no DST
MONEY_Q = Decimal("0.01")

_ID_TABLES = {
    ("app_user", "user_id"),
    ("guest", "guest_id"),
    ("reservation", "reservation_id"),
    ("reservation_room", "reservation_room_id"),
    ("stay", "stay_id"),
    ("stay_room", "stay_room_id"),
    ("folio", "folio_id"),
    ("folio_item", "folio_item_id"),
    ("invoice", "invoice_id"),
    ("payment", "payment_id"),
    ("housekeeping_task", "task_id"),
    ("audit_event", "event_id"),
}


def today() -> date:
    return datetime.now(HOTEL_TZ).date()


def quantize_money(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY_Q, rounding=ROUND_HALF_UP)


def next_id(connection, table: str, column: str) -> int:
    # Identifiers come from a fixed allow-list, never from user input.
    if (table, column) not in _ID_TABLES:
        raise ValueError("unsupported id column")
    row = connection.execute(f"SELECT COALESCE(MAX({column}), 0) + 1 AS id FROM {table}").fetchone()
    return row["id"]


def validate_stay(check_in: date, check_out: date, today_value: date | None = None) -> int:
    """Return the number of nights; the range is [check_in, check_out)."""
    if check_out <= check_in:
        raise invalid("INVALID_DATES", "Ngày trả phòng phải sau ngày nhận phòng.")
    if check_in < (today_value or today()):
        raise invalid("INVALID_DATES", "Ngày nhận phòng không được ở quá khứ.")
    nights = (check_out - check_in).days
    if nights > MAX_NIGHTS:
        raise invalid("INVALID_DATES", f"Chỉ được đặt tối đa {MAX_NIGHTS} đêm cho một đơn.")
    return nights


def validate_guests(adults: int, children: int, max_guests: int | None) -> None:
    if adults < 1 or children < 0:
        raise invalid("INVALID_GUESTS", "Cần ít nhất 1 người lớn.")
    if max_guests is not None and adults + children > max_guests:
        raise invalid(
            "INVALID_GUESTS", f"Loại phòng này chứa tối đa {max_guests} khách."
        )


def compute_discount_amount(discount_type: str, value: Decimal, base_amount: Decimal) -> Decimal:
    """Calculate a non-negative discount capped at `base_amount`."""
    if base_amount <= 0:
        return Decimal("0.00")
    if discount_type == "PERCENT":
        amount = quantize_money(base_amount * value / Decimal("100"))
    elif discount_type == "FIXED":
        amount = quantize_money(value)
    else:
        raise invalid("INVALID_DISCOUNT", "Loại mã giảm giá không hợp lệ.")
    return min(max(amount, Decimal("0.00")), quantize_money(base_amount))


# A room is busy when a live reservation line overlaps [check_in, check_out).
_BUSY = """
    EXISTS (
        SELECT 1
        FROM reservation_room rr
        JOIN reservation res ON res.reservation_id = rr.reservation_id
        WHERE rr.room_id = r.room_id
          AND rr.is_cancelled IS NOT TRUE
          AND res.status IS DISTINCT FROM 'CANCELLED'
          AND res.status IS DISTINCT FROM 'NO_SHOW'
          AND rr.check_in_date < %(check_out)s
          AND rr.check_out_date > %(check_in)s
    )
"""

AVAILABILITY_SQL = f"""
    SELECT rt.room_type_id, rt.name, rt.max_guests, rt.base_price,
           COUNT(r.room_id) AS available_rooms
    FROM room_type rt
    JOIN room r ON r.room_type_id = rt.room_type_id AND r.is_active IS TRUE
    WHERE rt.is_active IS TRUE
      AND (%(room_type_id)s::bigint IS NULL OR rt.room_type_id = %(room_type_id)s)
      AND (rt.max_guests IS NULL OR rt.max_guests >= %(guests)s)
      AND NOT {_BUSY}
    GROUP BY rt.room_type_id, rt.name, rt.max_guests, rt.base_price
    ORDER BY rt.room_type_id
"""


def search_availability(connection, check_in, check_out, guests, room_type_id):
    nights = validate_stay(check_in, check_out)
    rows = connection.execute(
        AVAILABILITY_SQL,
        {
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "room_type_id": room_type_id,
        },
    ).fetchall()
    items = []
    for row in rows:
        price = row["base_price"]
        items.append(
            {
                "room_type": {
                    "room_type_id": row["room_type_id"],
                    "name": row["name"],
                    "max_guests": row["max_guests"],
                    "base_price": price,
                },
                "available_rooms": row["available_rooms"],
                "nights": nights,
                "nightly_price": price,
                "total_price": price * nights if price is not None else None,
            }
        )
    return items


def audit(connection, user_id, reservation_id, action, details, service_order_id=None):
    from psycopg.types.json import Jsonb

    connection.execute(
        "INSERT INTO audit_event "
        "(event_id, actor_user_id, reservation_id, service_order_id, action, details, occurred_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, now())",
        (
            next_id(connection, "audit_event", "event_id"),
            user_id,
            reservation_id,
            service_order_id,
            action,
            Jsonb(details),
        ),
    )


def _dates_overlap(a_in: date, a_out: date, b_in: date, b_out: date) -> bool:
    return a_in < b_out and a_out > b_in


def create_reservation(connection, user: CurrentUser, body) -> dict:
    """Atomically book one or more physical rooms; server locks in room_id order."""
    requested_rooms = body.normalized_rooms()
    nights_list = [validate_stay(item.check_in, item.check_out) for item in requested_rooms]

    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))

    # 1. Load & validate all requested room types up front.
    distinct_type_ids = sorted({item.room_type_id for item in requested_rooms})
    type_rows = connection.execute(
        "SELECT room_type_id, name, max_guests, base_price FROM room_type "
        "WHERE room_type_id = ANY(%s) AND is_active IS TRUE",
        (distinct_type_ids,),
    ).fetchall()
    room_types = {row["room_type_id"]: row for row in type_rows}

    for item in requested_rooms:
        room_type = room_types.get(item.room_type_id)
        if room_type is None:
            raise not_found("ROOM_TYPE_NOT_FOUND", "Không tìm thấy loại phòng.")
        validate_guests(item.adults, item.children, room_type["max_guests"])
        if room_type["base_price"] is None:
            raise conflict("PRICE_NOT_SET", "Loại phòng chưa có giá, chưa thể đặt.")

    # 2. Validate companion guests (if any).
    companion_ids = sorted({gid for gid in body.companion_guest_ids if gid != user.guest_id})
    if companion_ids:
        found_guests = connection.execute(
            "SELECT guest_id FROM guest WHERE guest_id = ANY(%s)", (companion_ids,)
        ).fetchall()
        if len(found_guests) != len(companion_ids):
            raise not_found("GUEST_NOT_FOUND", "Không tìm thấy khách đi cùng.")

    # 3. Validate discount code (if any) against the earliest check-in date.
    discount_row = None
    cleaned_code = body.discount_code.strip() if body.discount_code else ""
    if cleaned_code:
        discount_row = connection.execute(
            "SELECT discount_id, code, discount_type, value, valid_from, valid_to, is_active "
            "FROM discount WHERE UPPER(code) = UPPER(%s) LIMIT 1",
            (cleaned_code,),
        ).fetchone()
        if discount_row is None:
            raise not_found("DISCOUNT_NOT_FOUND", "Không tìm thấy mã giảm giá.")
        earliest_in = min(item.check_in for item in requested_rooms)
        if discount_row["is_active"] is not True or not (
            discount_row["valid_from"] <= earliest_in <= discount_row["valid_to"]
        ):
            raise invalid("INVALID_DISCOUNT", "Mã giảm giá đã hết hạn hoặc không còn hiệu lực.")

    # 4. Lock every candidate physical room across all requested types in
    #    ascending room_id order so concurrent multi-room bookings never deadlock.
    connection.execute(
        "SELECT room_id FROM room "
        "WHERE room_type_id = ANY(%s) AND is_active IS TRUE "
        "ORDER BY room_id FOR UPDATE",
        (distinct_type_ids,),
    ).fetchall()

    # 5. Assign distinct available physical rooms for every line atomically.
    #    If any line lacks a room, raise 409 before writing anything.
    assigned: list[tuple[dict, object, int, Decimal]] = []
    chosen_ranges: list[tuple[int, date, date]] = []

    for item, nights in zip(requested_rooms, nights_list):
        candidates = connection.execute(
            f"""
            SELECT r.room_id, r.room_number FROM room r
            WHERE r.room_type_id = %(room_type_id)s AND r.is_active IS TRUE
              AND NOT {_BUSY}
            ORDER BY r.room_number, r.room_id
            """,
            {
                "room_type_id": item.room_type_id,
                "check_in": item.check_in,
                "check_out": item.check_out,
            },
        ).fetchall()
        picked = None
        for candidate in candidates:
            rid = candidate["room_id"]
            if not any(
                cid == rid and _dates_overlap(c_in, c_out, item.check_in, item.check_out)
                for cid, c_in, c_out in chosen_ranges
            ):
                picked = candidate
                break
        if picked is None:
            raise conflict(
                "NO_ROOM_AVAILABLE",
                "Không còn đủ phòng trống thuộc loại đã chọn trong khoảng ngày này.",
            )
        chosen_ranges.append((picked["room_id"], item.check_in, item.check_out))
        nightly_price: Decimal = room_types[item.room_type_id]["base_price"]
        assigned.append((picked, item, nights, nightly_price))

    # 6. Persist reservation head, lines, guests, optional discount and audit.
    reservation_id = next_id(connection, "reservation", "reservation_id")
    connection.execute(
        "INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, note) "
        "VALUES (%s, %s, 'CONFIRMED', now(), %s)",
        (reservation_id, user.guest_id, body.note),
    )

    subtotal = Decimal("0.00")
    audit_rooms = []
    for picked, item, nights, nightly_price in assigned:
        line_id = next_id(connection, "reservation_room", "reservation_room_id")
        connection.execute(
            "INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, "
            "check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)",
            (
                line_id,
                reservation_id,
                picked["room_id"],
                item.check_in,
                item.check_out,
                item.adults,
                item.children,
                nightly_price,
            ),
        )
        subtotal += quantize_money(nightly_price * nights)
        audit_rooms.append(
            {
                "room_id": picked["room_id"],
                "room_type_id": item.room_type_id,
                "check_in": item.check_in.isoformat(),
                "check_out": item.check_out.isoformat(),
                "nights": nights,
                "nightly_price": str(nightly_price),
            }
        )

    connection.execute(
        "INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES (%s, %s, TRUE)",
        (reservation_id, user.guest_id),
    )
    for gid in companion_ids:
        connection.execute(
            "INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) "
            "VALUES (%s, %s, FALSE)",
            (reservation_id, gid),
        )

    discount_amount = Decimal("0.00")
    if discount_row is not None:
        discount_amount = compute_discount_amount(
            discount_row["discount_type"], discount_row["value"], subtotal
        )
        connection.execute(
            "INSERT INTO reservation_discount (reservation_id, discount_id, discount_amount) "
            "VALUES (%s, %s, %s)",
            (reservation_id, discount_row["discount_id"], discount_amount),
        )

    audit(
        connection,
        user.user_id,
        reservation_id,
        "RESERVATION_CREATED",
        {
            "rooms": audit_rooms,
            "room_id": audit_rooms[0]["room_id"],
            "discount_code": discount_row["code"] if discount_row else None,
            "discount_amount": str(discount_amount),
        },
    )
    return fetch_reservations(connection, [reservation_id])[0]


LINES_SQL = """
    SELECT rr.reservation_id, rr.reservation_room_id, rr.room_id, r.room_number,
           rt.room_type_id, rt.name, rt.max_guests, rt.base_price,
           rr.check_in_date, rr.check_out_date, rr.adults, rr.children,
           rr.nightly_price, rr.is_cancelled
    FROM reservation_room rr
    JOIN room r ON r.room_id = rr.room_id
    JOIN room_type rt ON rt.room_type_id = r.room_type_id
    WHERE rr.reservation_id = ANY(%s)
    ORDER BY rr.reservation_id, rr.reservation_room_id
"""

DISCOUNTS_SQL = """
    SELECT rd.reservation_id, d.code, rd.discount_amount
    FROM reservation_discount rd
    JOIN discount d ON d.discount_id = rd.discount_id
    WHERE rd.reservation_id = ANY(%s)
"""


def fetch_reservations(connection, reservation_ids: list[int]) -> list[dict]:
    if not reservation_ids:
        return []
    heads = connection.execute(
        "SELECT reservation_id, status, created_at, cancelled_at, note FROM reservation "
        "WHERE reservation_id = ANY(%s) ORDER BY created_at DESC NULLS LAST, reservation_id DESC",
        (reservation_ids,),
    ).fetchall()
    lines: dict[int, list[dict]] = {}
    for row in connection.execute(LINES_SQL, (reservation_ids,)).fetchall():
        nights = (row["check_out_date"] - row["check_in_date"]).days
        price = row["nightly_price"] or Decimal("0.00")
        lines.setdefault(row["reservation_id"], []).append(
            {
                "reservation_room_id": row["reservation_room_id"],
                "room_id": row["room_id"],
                "room_number": row["room_number"],
                "room_type": {
                    "room_type_id": row["room_type_id"],
                    "name": row["name"],
                    "max_guests": row["max_guests"],
                    "base_price": row["base_price"],
                },
                "check_in_date": row["check_in_date"],
                "check_out_date": row["check_out_date"],
                "nights": nights,
                "adults": row["adults"],
                "children": row["children"],
                "nightly_price": price,
                "line_total": quantize_money(price * nights),
                "is_cancelled": bool(row["is_cancelled"]),
            }
        )
    discounts = {
        row["reservation_id"]: row
        for row in connection.execute(DISCOUNTS_SQL, (reservation_ids,)).fetchall()
    }
    result = []
    for head in heads:
        rid = head["reservation_id"]
        rooms = lines.get(rid, [])
        subtotal = sum(
            (line["line_total"] for line in rooms if not line["is_cancelled"]),
            Decimal("0.00"),
        )
        disc = discounts.get(rid)
        if disc and head["status"] != "CANCELLED" and subtotal > 0:
            discount_code = disc["code"]
            discount_amount = min(quantize_money(disc["discount_amount"]), subtotal)
        else:
            discount_code = disc["code"] if disc else None
            discount_amount = Decimal("0.00")
        result.append(
            {
                **head,
                "rooms": rooms,
                "subtotal": subtotal,
                "discount_code": discount_code,
                "discount_amount": discount_amount,
                "total_price": max(Decimal("0.00"), subtotal - discount_amount),
            }
        )
    return result


def list_my_reservations(connection, user: CurrentUser) -> list[dict]:
    ids = [
        row["reservation_id"]
        for row in connection.execute(
            "SELECT reservation_id FROM reservation WHERE booked_by_guest_id = %s",
            (user.guest_id,),
        ).fetchall()
    ]
    return fetch_reservations(connection, ids)


def _owned_head(connection, reservation_id: int, user: CurrentUser, lock: bool = False):
    head = connection.execute(
        "SELECT reservation_id, booked_by_guest_id, status FROM reservation "
        "WHERE reservation_id = %s" + (" FOR UPDATE" if lock else ""),
        (reservation_id,),
    ).fetchone()
    # Other guests' reservations look identical to missing ones.
    if head is None or (not user.is_staff and head["booked_by_guest_id"] != user.guest_id):
        raise not_found("RESERVATION_NOT_FOUND", "Không tìm thấy đơn đặt phòng.")
    return head


def get_reservation(connection, reservation_id: int, user: CurrentUser) -> dict:
    _owned_head(connection, reservation_id, user)
    return fetch_reservations(connection, [reservation_id])[0]


def cancel_reservation(connection, reservation_id: int, user: CurrentUser) -> dict:
    """Idempotent: cancelling twice leaves the first cancellation untouched."""
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    head = _owned_head(connection, reservation_id, user, lock=True)
    if not user.is_staff and head["booked_by_guest_id"] != user.guest_id:
        raise forbidden()
    if head["status"] == "CANCELLED":
        return fetch_reservations(connection, [reservation_id])[0]
    if head["status"] != "CONFIRMED":
        raise conflict("RESERVATION_NOT_CANCELLABLE", "Đơn này không còn ở trạng thái có thể hủy.")
    stay = connection.execute(
        "SELECT 1 FROM stay WHERE reservation_id = %s", (reservation_id,)
    ).fetchone()
    if stay:
        raise conflict("RESERVATION_NOT_CANCELLABLE", "Đơn đã check-in nên không thể hủy.")
    connection.execute(
        "UPDATE reservation SET status = 'CANCELLED', cancelled_at = now() "
        "WHERE reservation_id = %s",
        (reservation_id,),
    )
    connection.execute(
        "UPDATE reservation_room SET is_cancelled = TRUE WHERE reservation_id = %s",
        (reservation_id,),
    )
    audit(connection, user.user_id, reservation_id, "RESERVATION_CANCELLED", {})
    return fetch_reservations(connection, [reservation_id])[0]
