"""Check-in and check-out workflows, fully transactional and idempotent."""

from decimal import Decimal

from app.deps import CurrentUser
from app.errors import conflict, not_found
from app.services import billing
from app.services.booking import ID_LOCK, audit, next_id, quantize_money

CLEAN_STATUSES = frozenset({"CLEAN", "INSPECTED"})


def _fetch_stay_out(connection, stay_id: int, housekeeping_task_ids: list[int] | None = None) -> dict:
    stay = connection.execute(
        """
        SELECT s.stay_id, s.reservation_id, s.checked_in_by, s.checked_out_by,
               s.actual_check_in, s.actual_check_out, s.status,
               f.folio_id
        FROM stay s
        LEFT JOIN folio f ON f.stay_id = s.stay_id
        WHERE s.stay_id = %s
        """,
        (stay_id,),
    ).fetchone()
    rooms = connection.execute(
        """
        SELECT sr.stay_room_id, sr.reservation_room_id, sr.room_id, r.room_number,
               r.housekeeping_status, r.maintenance_status,
               sr.assigned_from, sr.assigned_to
        FROM stay_room sr
        JOIN room r ON r.room_id = sr.room_id
        WHERE sr.stay_id = %s
        ORDER BY sr.stay_room_id
        """,
        (stay_id,),
    ).fetchall()
    return {
        **stay,
        "rooms": rooms,
        "housekeeping_task_ids": housekeeping_task_ids or [],
    }


def get_stay(connection, stay_id: int, user: CurrentUser) -> dict:
    row = connection.execute(
        """
        SELECT s.stay_id, res.booked_by_guest_id
        FROM stay s
        JOIN reservation res ON res.reservation_id = s.reservation_id
        WHERE s.stay_id = %s
        """,
        (stay_id,),
    ).fetchone()
    if row is None or (not user.is_staff and row["booked_by_guest_id"] != user.guest_id):
        raise not_found("STAY_NOT_FOUND", "Không tìm thấy lượt lưu trú.")
    return _fetch_stay_out(connection, stay_id)


def check_in(connection, reservation_id: int, user: CurrentUser) -> dict:
    """Validate reservation & rooms (CLEAN + maintenance OK), then create stay/stay_room/folio/charges."""
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    res = connection.execute(
        "SELECT reservation_id, booked_by_guest_id, status FROM reservation "
        "WHERE reservation_id = %s FOR UPDATE",
        (reservation_id,),
    ).fetchone()
    if res is None:
        raise not_found("RESERVATION_NOT_FOUND", "Không tìm thấy đơn đặt phòng.")

    existing_stay = connection.execute(
        "SELECT stay_id, status FROM stay WHERE reservation_id = %s FOR UPDATE",
        (reservation_id,),
    ).fetchone()
    if existing_stay is not None:
        if existing_stay["status"] == "IN_HOUSE":
            return _fetch_stay_out(connection, existing_stay["stay_id"])
        raise conflict("ALREADY_CHECKED_OUT", "Đơn đặt phòng này đã check-out.")

    if res["status"] != "CONFIRMED":
        raise conflict(
            "RESERVATION_NOT_CHECKINABLE",
            "Chỉ có thể check-in đơn ở trạng thái CONFIRMED.",
        )

    lines = connection.execute(
        """
        SELECT rr.reservation_room_id, rr.room_id, rr.check_in_date, rr.check_out_date,
               rr.nightly_price, r.room_number, rt.name AS room_type_name
        FROM reservation_room rr
        JOIN room r ON r.room_id = rr.room_id
        JOIN room_type rt ON rt.room_type_id = r.room_type_id
        WHERE rr.reservation_id = %s AND rr.is_cancelled IS NOT TRUE
        ORDER BY rr.room_id, rr.reservation_room_id
        """,
        (reservation_id,),
    ).fetchall()
    if not lines:
        raise conflict("NO_ACTIVE_ROOMS", "Đơn đặt phòng không còn phòng nào đang hoạt động.")

    # Lock all rooms in deterministic room_id order.
    room_ids = sorted({line["room_id"] for line in lines})
    locked_rooms = connection.execute(
        """
        SELECT room_id, room_number, housekeeping_status, maintenance_status, is_active
        FROM room
        WHERE room_id = ANY(%s)
        ORDER BY room_id
        FOR UPDATE
        """,
        (room_ids,),
    ).fetchall()
    room_map = {r["room_id"]: r for r in locked_rooms}

    for rid in room_ids:
        room = room_map.get(rid)
        if room is None or room["is_active"] is not True:
            raise conflict("ROOM_INACTIVE", "Phòng không còn hoạt động, không thể check-in.")
        if room["housekeeping_status"] not in CLEAN_STATUSES:
            raise conflict(
                "ROOM_NOT_CLEAN",
                f"Phòng {room['room_number']} chưa sạch ({room['housekeeping_status']}), không thể check-in.",
            )
        # V001 uses OK / MINOR_ISSUE / OUT_OF_ORDER; legacy docs mention BLOCKED.
        if room["maintenance_status"] != "OK":
            raise conflict(
                "ROOM_MAINTENANCE_BLOCKED",
                f"Phòng {room['room_number']} đang bảo trì ({room['maintenance_status']}), không thể check-in.",
            )
        occupied = connection.execute(
            "SELECT 1 FROM stay_room WHERE room_id = %s AND assigned_to IS NULL LIMIT 1",
            (rid,),
        ).fetchone()
        if occupied is not None:
            raise conflict(
                "ROOM_OCCUPIED",
                f"Phòng {room['room_number']} đang có khách lưu trú, chưa check-out.",
            )

    stay_id = next_id(connection, "stay", "stay_id")
    connection.execute(
        """
        INSERT INTO stay (stay_id, reservation_id, checked_in_by, actual_check_in, status)
        VALUES (%s, %s, %s, now(), 'IN_HOUSE')
        """,
        (stay_id, reservation_id, user.employee_id),
    )

    folio_id = next_id(connection, "folio", "folio_id")
    connection.execute(
        "INSERT INTO folio (folio_id, stay_id, status, opened_at) VALUES (%s, %s, 'OPEN', now())",
        (folio_id, stay_id),
    )

    room_numbers = []
    for line in lines:
        stay_room_id = next_id(connection, "stay_room", "stay_room_id")
        connection.execute(
            """
            INSERT INTO stay_room (stay_room_id, stay_id, reservation_room_id, room_id, assigned_from)
            VALUES (%s, %s, %s, %s, now())
            """,
            (stay_room_id, stay_id, line["reservation_room_id"], line["room_id"]),
        )
        nights = (line["check_out_date"] - line["check_in_date"]).days
        nightly_price = quantize_money(Decimal(line["nightly_price"]))
        source_key = f"ROOM:{line['reservation_room_id']}:{line['check_in_date'].isoformat()}"
        desc = (
            f"Tien phong {line['room_type_name']} {line['room_number']} "
            f"({nights} dem: {line['check_in_date'].isoformat()} -> {line['check_out_date'].isoformat()})"
        )
        connection.execute(
            """
            INSERT INTO folio_item
                (folio_item_id, folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at)
            VALUES (%s, %s, 'CHARGE', %s, %s, %s, %s, now())
            """,
            (
                next_id(connection, "folio_item", "folio_item_id"),
                folio_id,
                desc[:200],
                Decimal(nights),
                nightly_price,
                source_key,
            ),
        )
        room_numbers.append(line["room_number"])

    billing.sync_discount_item(connection, folio_id, reservation_id)

    connection.execute(
        "UPDATE reservation SET status = 'CHECKED_IN' WHERE reservation_id = %s",
        (reservation_id,),
    )
    audit(
        connection,
        user.user_id,
        reservation_id,
        "STAY_CHECKED_IN",
        {"stay_id": stay_id, "folio_id": folio_id, "rooms": room_numbers},
    )
    return _fetch_stay_out(connection, stay_id)


def check_out(connection, stay_id: int, user: CurrentUser) -> dict:
    """Close stay/folio, mark rooms DIRTY and create housekeeping tasks (idempotent)."""
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    stay = connection.execute(
        "SELECT stay_id, reservation_id, actual_check_in, status FROM stay "
        "WHERE stay_id = %s FOR UPDATE",
        (stay_id,),
    ).fetchone()
    if stay is None:
        raise not_found("STAY_NOT_FOUND", "Không tìm thấy lượt lưu trú.")

    if stay["status"] == "CHECKED_OUT":
        return _fetch_stay_out(connection, stay_id)

    folio = connection.execute(
        "SELECT folio_id, status, opened_at FROM folio WHERE stay_id = %s FOR UPDATE",
        (stay_id,),
    ).fetchone()
    if folio is None:
        raise conflict("FOLIO_MISSING", "Không tìm thấy folio cho lượt lưu trú này.")

    # 1. No pending / in-progress service orders allowed at check-out.
    open_services = connection.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM service_order so
        JOIN stay_room sr ON sr.stay_room_id = so.stay_room_id
        WHERE sr.stay_id = %s
          AND so.status IN ('PENDING', 'IN_PROGRESS')
        """,
        (stay_id,),
    ).fetchone()["cnt"]
    if open_services > 0:
        raise conflict(
            "OPEN_SERVICE_ORDERS",
            "Còn đơn dịch vụ chưa hoàn thành hoặc chưa hủy, không thể check-out.",
        )

    # 2. Verify active invoice exists, matches current folio totals, and is fully PAID.
    if folio["status"] == "OPEN":
        billing.sync_discount_item(connection, folio["folio_id"], stay["reservation_id"])
    totals = billing.calculate_folio_totals(connection, folio["folio_id"])

    inv = connection.execute(
        """
        SELECT invoice_id, folio_id, invoice_number, subtotal, discount_total,
               tax_amount, issued_at, status
        FROM invoice
        WHERE folio_id = %s AND status <> 'VOID'
        ORDER BY invoice_id DESC
        LIMIT 1
        FOR UPDATE
        """,
        (folio["folio_id"],),
    ).fetchone()
    if inv is None:
        raise conflict("PAYMENT_REQUIRED", "Cần xuất hóa đơn và thanh toán đủ trước khi check-out.")

    same_totals = (
        quantize_money(Decimal(inv["subtotal"])) == totals["subtotal"]
        and quantize_money(Decimal(inv["discount_total"])) == totals["discount_total"]
        and quantize_money(Decimal(inv["tax_amount"])) == totals["tax_amount"]
    )
    if not same_totals:
        raise conflict(
            "INVOICE_STALE",
            "Folio có thay đổi mới sau khi xuất hóa đơn; cần cập nhật hóa đơn và thanh toán đủ.",
        )

    inv_out = billing.build_invoice_out(connection, inv)
    if inv_out["balance_due"] > Decimal("0.00") or inv_out["status"] != "PAID":
        raise conflict(
            "PAYMENT_REQUIRED",
            f"Còn thiếu {inv_out['balance_due']} chưa thanh toán, không thể check-out.",
        )

    # 3. Close folio, stay, stay_room, reservation; mark rooms DIRTY (keep maintenance_status);
    #    create PENDING housekeeping_task for each room.
    #    Use GREATEST(..., + 1ms) on assigned_to to guarantee V001 ck_stay_room_interval (>).
    connection.execute(
        """
        UPDATE folio
        SET status = 'CLOSED', closed_at = GREATEST(clock_timestamp(), opened_at)
        WHERE folio_id = %s
        """,
        (folio["folio_id"],),
    )
    connection.execute(
        """
        UPDATE stay
        SET status = 'CHECKED_OUT',
            checked_out_by = %s,
            actual_check_out = GREATEST(clock_timestamp(), actual_check_in)
        WHERE stay_id = %s
        """,
        (user.employee_id, stay_id),
    )
    connection.execute(
        """
        UPDATE stay_room
        SET assigned_to = GREATEST(clock_timestamp(), assigned_from + interval '1 millisecond')
        WHERE stay_id = %s AND assigned_to IS NULL
        """,
        (stay_id,),
    )
    connection.execute(
        "UPDATE reservation SET status = 'CHECKED_OUT' WHERE reservation_id = %s",
        (stay["reservation_id"],),
    )

    stay_rooms = connection.execute(
        "SELECT DISTINCT room_id FROM stay_room WHERE stay_id = %s ORDER BY room_id",
        (stay_id,),
    ).fetchall()
    room_ids = [r["room_id"] for r in stay_rooms]

    task_ids = []
    if room_ids:
        connection.execute(
            "SELECT room_id FROM room WHERE room_id = ANY(%s) ORDER BY room_id FOR UPDATE",
            (room_ids,),
        ).fetchall()
        # Only update housekeeping_status; maintenance_status stays independent.
        connection.execute(
            "UPDATE room SET housekeeping_status = 'DIRTY' WHERE room_id = ANY(%s)",
            (room_ids,),
        )
        for rid in room_ids:
            task_id = next_id(connection, "housekeeping_task", "task_id")
            connection.execute(
                """
                INSERT INTO housekeeping_task
                    (task_id, room_id, assigned_to, scheduled_at, completed_at, status)
                VALUES (%s, %s, NULL, clock_timestamp(), NULL, 'PENDING')
                """,
                (task_id, rid),
            )
            task_ids.append(task_id)

    audit(
        connection,
        user.user_id,
        stay["reservation_id"],
        "STAY_CHECKED_OUT",
        {
            "stay_id": stay_id,
            "invoice_number": inv_out["invoice_number"],
            "gross": str(inv_out["gross_total"]),
            "housekeeping_task_ids": task_ids,
        },
    )
    return _fetch_stay_out(connection, stay_id, housekeeping_task_ids=task_ids)
