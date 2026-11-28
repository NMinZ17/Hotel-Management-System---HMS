"""Availability search, booking and cancellation.

All write paths run inside one transaction supplied by the caller
(`get_tx`). A transaction-level advisory lock serialises writers so the ids
allocated with `next_id` (the schema has no sequences) cannot collide, and
candidate rooms are additionally locked with `FOR UPDATE`.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.deps import CurrentUser
from app.errors import conflict, forbidden, invalid, not_found

ID_LOCK = 7_420_001
MAX_NIGHTS = 30
HOTEL_TZ = timezone(timedelta(hours=7))  # Asia/Ho_Chi_Minh, no DST

_ID_TABLES = {
    ("app_user", "user_id"),
    ("guest", "guest_id"),
    ("reservation", "reservation_id"),
    ("reservation_room", "reservation_room_id"),
    ("audit_event", "event_id"),
}


def today() -> date:
    return datetime.now(HOTEL_TZ).date()


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


# A room is busy when a live reservation line overlaps [check_in, check_out).
_BUSY = """
    EXISTS (
        SELECT 1
        FROM reservation_room rr
        JOIN reservation res ON res.reservation_id = rr.reservation_id
        WHERE rr.room_id = r.room_id
          AND rr.is_cancelled IS NOT TRUE
          AND res.status IS DISTINCT FROM 'CANCELLED'
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


def _audit(connection, user_id, reservation_id, action, details):
    from psycopg.types.json import Jsonb

    connection.execute(
        "INSERT INTO audit_event (event_id, actor_user_id, reservation_id, action, details, occurred_at) "
        "VALUES (%s, %s, %s, %s, %s, now())",
        (
            next_id(connection, "audit_event", "event_id"),
            user_id,
            reservation_id,
            action,
            Jsonb(details),
        ),
    )


def create_reservation(connection, user: CurrentUser, body) -> dict:
    """Book one physical room of the requested type; the server picks the room."""
    nights = validate_stay(body.check_in, body.check_out)
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    room_type = connection.execute(
        "SELECT room_type_id, name, max_guests, base_price FROM room_type "
        "WHERE room_type_id = %s AND is_active IS TRUE",
        (body.room_type_id,),
    ).fetchone()
    if room_type is None:
        raise not_found("ROOM_TYPE_NOT_FOUND", "Không tìm thấy loại phòng.")
    validate_guests(body.adults, body.children, room_type["max_guests"])
    if room_type["base_price"] is None:
        raise conflict("PRICE_NOT_SET", "Loại phòng chưa có giá, chưa thể đặt.")

    # Lock every candidate, then re-read the calendar so a room taken by a
    # concurrent booking is skipped instead of being reported as "sold out".
    connection.execute(
        "SELECT room_id FROM room WHERE room_type_id = %s AND is_active IS TRUE "
        "ORDER BY room_number, room_id FOR UPDATE",
        (body.room_type_id,),
    ).fetchall()
    room = connection.execute(
        f"""
        SELECT r.room_id, r.room_number FROM room r
        WHERE r.room_type_id = %(room_type_id)s AND r.is_active IS TRUE
          AND NOT {_BUSY}
        ORDER BY r.room_number, r.room_id LIMIT 1
        """,
        {
            "room_type_id": body.room_type_id,
            "check_in": body.check_in,
            "check_out": body.check_out,
        },
    ).fetchone()
    if room is None:
        raise conflict(
            "NO_ROOM_AVAILABLE", "Không còn phòng trống thuộc loại này trong khoảng ngày đã chọn."
        )

    reservation_id = next_id(connection, "reservation", "reservation_id")
    line_id = next_id(connection, "reservation_room", "reservation_room_id")
    nightly_price: Decimal = room_type["base_price"]
    connection.execute(
        "INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, note) "
        "VALUES (%s, %s, 'CONFIRMED', now(), %s)",
        (reservation_id, user.guest_id, body.note),
    )
    connection.execute(
        "INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, "
        "check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)",
        (
            line_id,
            reservation_id,
            room["room_id"],
            body.check_in,
            body.check_out,
            body.adults,
            body.children,
            nightly_price,
        ),
    )
    connection.execute(
        "INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES (%s, %s, TRUE)",
        (reservation_id, user.guest_id),
    )
    _audit(
        connection,
        user.user_id,
        reservation_id,
        "RESERVATION_CREATED",
        {
            "room_id": room["room_id"],
            "room_type_id": body.room_type_id,
            "check_in": body.check_in.isoformat(),
            "check_out": body.check_out.isoformat(),
            "nights": nights,
            "nightly_price": str(nightly_price),
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
        price = row["nightly_price"] or Decimal("0")
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
                "line_total": price * nights,
                "is_cancelled": bool(row["is_cancelled"]),
            }
        )
    result = []
    for head in heads:
        rooms = lines.get(head["reservation_id"], [])
        result.append(
            {
                **head,
                "rooms": rooms,
                "total_price": sum(
                    (line["line_total"] for line in rooms if not line["is_cancelled"]),
                    Decimal("0"),
                ),
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
    _audit(connection, user.user_id, reservation_id, "RESERVATION_CANCELLED", {})
    return fetch_reservations(connection, [reservation_id])[0]
