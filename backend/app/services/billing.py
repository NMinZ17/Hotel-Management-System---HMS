"""Folio totals, invoice issuance and payment recording.

Money arithmetic matches Trang's financial fixture (database/seeds/06_financial_fixture.sql)
and V002 constraints:
  - CHARGE/TAX folio_items have unit_price >= 0.
  - DISCOUNT folio_items have unit_price <= 0 (quantity = 1, source_key = DISC:<res>:<disc>).
  - subtotal = sum of CHARGE (+ positive ADJUSTMENT).
  - discount_total = positive magnitude of DISCOUNT (+ negative ADJUSTMENT), capped at subtotal.
  - net = subtotal - discount_total.
  - tax_amount = explicit TAX rows if present, otherwise 8% VAT on net (ROUND_HALF_UP).
  - gross_total = net + tax_amount.
  - Payments are always aggregated independently from folio_item to prevent fan-out.
"""

from decimal import Decimal

from app.deps import CurrentUser
from app.errors import conflict, not_found
from app.services.booking import (
    ID_LOCK,
    audit,
    compute_discount_amount,
    next_id,
    quantize_money,
)

VAT_RATE = Decimal("0.08")


def sync_discount_item(connection, folio_id: int, reservation_id: int) -> None:
    """Keep the reservation's DISCOUNT folio_item aligned with current CHARGE subtotal."""
    disc = connection.execute(
        """
        SELECT rd.discount_id, d.code, d.discount_type, d.value
        FROM reservation_discount rd
        JOIN discount d ON d.discount_id = rd.discount_id
        WHERE rd.reservation_id = %s
        """,
        (reservation_id,),
    ).fetchone()
    if disc is None:
        return

    row = connection.execute(
        """
        SELECT COALESCE(SUM(quantity * unit_price), 0) AS charge_subtotal
        FROM folio_item
        WHERE folio_id = %s
          AND (entry_type = 'CHARGE' OR (entry_type = 'ADJUSTMENT' AND unit_price > 0))
        """,
        (folio_id,),
    ).fetchone()
    charge_subtotal = quantize_money(Decimal(row["charge_subtotal"]))
    discount_amount = compute_discount_amount(
        disc["discount_type"], Decimal(disc["value"]), charge_subtotal
    )

    connection.execute(
        "UPDATE reservation_discount SET discount_amount = %s WHERE reservation_id = %s",
        (discount_amount, reservation_id),
    )

    source_key = f"DISC:{reservation_id}:{disc['discount_id']}"
    unit_price = -discount_amount  # V002 ck_folio_item_unit_price: DISCOUNT <= 0
    existing = connection.execute(
        "SELECT folio_item_id FROM folio_item WHERE folio_id = %s AND source_key = %s",
        (folio_id, source_key),
    ).fetchone()
    if existing is not None:
        connection.execute(
            "UPDATE folio_item SET quantity = 1.00, unit_price = %s WHERE folio_item_id = %s",
            (unit_price, existing["folio_item_id"]),
        )
    else:
        desc = (
            f"Ma giam {disc['code']} (-{disc['value']}% tren tong CHARGE)"
            if disc["discount_type"] == "PERCENT"
            else f"Ma giam {disc['code']} (-{discount_amount})"
        )
        connection.execute(
            "INSERT INTO folio_item "
            "(folio_item_id, folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at) "
            "VALUES (%s, %s, 'DISCOUNT', %s, 1.00, %s, %s, now())",
            (
                next_id(connection, "folio_item", "folio_item_id"),
                folio_id,
                desc[:200],
                unit_price,
                source_key,
            ),
        )


def calculate_folio_totals(connection, folio_id: int) -> dict:
    """Compute exact Decimal items and totals for a folio."""
    rows = connection.execute(
        """
        SELECT folio_item_id, entry_type, description, quantity, unit_price,
               source_key, occurred_at
        FROM folio_item
        WHERE folio_id = %s
        ORDER BY folio_item_id
        """,
        (folio_id,),
    ).fetchall()

    items = []
    subtotal = Decimal("0.00")
    discount_total = Decimal("0.00")
    explicit_tax = Decimal("0.00")
    has_explicit_tax = False

    for row in rows:
        qty = Decimal(row["quantity"])
        unit_price = Decimal(row["unit_price"])
        line_total = quantize_money(qty * unit_price)
        entry_type = row["entry_type"]
        if entry_type == "CHARGE":
            subtotal += line_total
        elif entry_type == "DISCOUNT":
            discount_total += abs(line_total)
        elif entry_type == "TAX":
            has_explicit_tax = True
            explicit_tax += line_total
        elif entry_type == "ADJUSTMENT":
            if line_total >= 0:
                subtotal += line_total
            else:
                discount_total += abs(line_total)
        items.append(
            {
                "folio_item_id": row["folio_item_id"],
                "entry_type": entry_type,
                "description": row["description"],
                "quantity": qty,
                "unit_price": unit_price,
                "line_total": line_total,
                "source_key": row["source_key"],
                "occurred_at": row["occurred_at"],
            }
        )

    subtotal = quantize_money(subtotal)
    discount_total = min(quantize_money(discount_total), subtotal)
    net_amount = max(Decimal("0.00"), subtotal - discount_total)
    tax_amount = (
        quantize_money(explicit_tax)
        if has_explicit_tax
        else quantize_money(net_amount * VAT_RATE)
    )
    gross_total = quantize_money(net_amount + tax_amount)
    return {
        "items": items,
        "subtotal": subtotal,
        "discount_total": discount_total,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
    }


def _fetch_payments(connection, invoice_id: int) -> list[dict]:
    return connection.execute(
        """
        SELECT payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at
        FROM payment
        WHERE invoice_id = %s
        ORDER BY payment_id
        """,
        (invoice_id,),
    ).fetchall()


def build_invoice_out(connection, invoice_row: dict) -> dict:
    payments = _fetch_payments(connection, invoice_row["invoice_id"])
    subtotal = quantize_money(Decimal(invoice_row["subtotal"]))
    discount_total = quantize_money(Decimal(invoice_row["discount_total"]))
    tax_amount = quantize_money(Decimal(invoice_row["tax_amount"]))
    gross_total = quantize_money(subtotal - discount_total + tax_amount)
    paid_total = quantize_money(
        sum((Decimal(p["amount"]) for p in payments), Decimal("0.00"))
    )
    balance_due = max(Decimal("0.00"), quantize_money(gross_total - paid_total))
    return {
        "invoice_id": invoice_row["invoice_id"],
        "folio_id": invoice_row["folio_id"],
        "invoice_number": invoice_row["invoice_number"],
        "subtotal": subtotal,
        "discount_total": discount_total,
        "tax_amount": tax_amount,
        "gross_total": gross_total,
        "paid_total": paid_total,
        "balance_due": balance_due,
        "issued_at": invoice_row["issued_at"],
        "status": invoice_row["status"],
        "payments": payments,
    }


def _load_folio_header(connection, folio_id: int, lock: bool = False) -> dict | None:
    return connection.execute(
        """
        SELECT f.folio_id, f.stay_id, f.status, f.opened_at, f.closed_at,
               s.reservation_id, res.booked_by_guest_id
        FROM folio f
        JOIN stay s ON s.stay_id = f.stay_id
        JOIN reservation res ON res.reservation_id = s.reservation_id
        WHERE f.folio_id = %s
        """
        + (" FOR UPDATE OF f" if lock else ""),
        (folio_id,),
    ).fetchone()


def get_folio(connection, folio_id: int, user: CurrentUser) -> dict:
    header = _load_folio_header(connection, folio_id)
    if header is None or (not user.is_staff and header["booked_by_guest_id"] != user.guest_id):
        raise not_found("FOLIO_NOT_FOUND", "Không tìm thấy folio.")

    totals = calculate_folio_totals(connection, folio_id)
    inv_row = connection.execute(
        """
        SELECT invoice_id, folio_id, invoice_number, subtotal, discount_total,
               tax_amount, issued_at, status
        FROM invoice
        WHERE folio_id = %s AND status <> 'VOID'
        ORDER BY invoice_id DESC
        LIMIT 1
        """,
        (folio_id,),
    ).fetchone()
    invoice = build_invoice_out(connection, inv_row) if inv_row else None
    paid_total = invoice["paid_total"] if invoice else Decimal("0.00")
    balance_due = max(Decimal("0.00"), quantize_money(totals["gross_total"] - paid_total))
    return {
        "folio_id": header["folio_id"],
        "stay_id": header["stay_id"],
        "reservation_id": header["reservation_id"],
        "status": header["status"],
        "opened_at": header["opened_at"],
        "closed_at": header["closed_at"],
        "items": totals["items"],
        "subtotal": totals["subtotal"],
        "discount_total": totals["discount_total"],
        "tax_amount": totals["tax_amount"],
        "gross_total": totals["gross_total"],
        "paid_total": paid_total,
        "balance_due": balance_due,
        "invoice": invoice,
    }


def get_invoice(connection, invoice_id: int, user: CurrentUser) -> dict:
    row = connection.execute(
        """
        SELECT i.invoice_id, i.folio_id, i.invoice_number, i.subtotal, i.discount_total,
               i.tax_amount, i.issued_at, i.status, res.booked_by_guest_id
        FROM invoice i
        JOIN folio f ON f.folio_id = i.folio_id
        JOIN stay s ON s.stay_id = f.stay_id
        JOIN reservation res ON res.reservation_id = s.reservation_id
        WHERE i.invoice_id = %s
        """,
        (invoice_id,),
    ).fetchone()
    if row is None or (not user.is_staff and row["booked_by_guest_id"] != user.guest_id):
        raise not_found("INVOICE_NOT_FOUND", "Không tìm thấy hóa đơn.")
    return build_invoice_out(connection, row)


def issue_invoice(connection, folio_id: int, user: CurrentUser) -> dict:
    """Create or return the active invoice for a folio (idempotent)."""
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    header = _load_folio_header(connection, folio_id, lock=True)
    if header is None:
        raise not_found("FOLIO_NOT_FOUND", "Không tìm thấy folio.")
    if header["status"] == "VOID":
        raise conflict("FOLIO_VOID", "Folio đã bị hủy, không thể xuất hóa đơn.")

    if header["status"] == "OPEN":
        sync_discount_item(connection, folio_id, header["reservation_id"])

    totals = calculate_folio_totals(connection, folio_id)
    existing = connection.execute(
        """
        SELECT invoice_id, folio_id, invoice_number, subtotal, discount_total,
               tax_amount, issued_at, status
        FROM invoice
        WHERE folio_id = %s AND status <> 'VOID'
        ORDER BY invoice_id DESC
        LIMIT 1
        FOR UPDATE
        """,
        (folio_id,),
    ).fetchone()

    if existing is not None:
        same_totals = (
            quantize_money(Decimal(existing["subtotal"])) == totals["subtotal"]
            and quantize_money(Decimal(existing["discount_total"])) == totals["discount_total"]
            and quantize_money(Decimal(existing["tax_amount"])) == totals["tax_amount"]
        )
        if same_totals or header["status"] == "CLOSED":
            return build_invoice_out(connection, existing)

        paid_row = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) AS paid FROM payment WHERE invoice_id = %s",
            (existing["invoice_id"],),
        ).fetchone()
        paid_total = quantize_money(Decimal(paid_row["paid"]))
        if totals["gross_total"] < paid_total:
            raise conflict(
                "INVOICE_OVERPAID",
                "Tổng hóa đơn mới nhỏ hơn số tiền đã thu, cần xử lý điều chỉnh thủ công.",
            )
        new_status = (
            "PAID"
            if paid_total == totals["gross_total"]
            else ("PARTIAL" if paid_total > 0 else "ISSUED")
        )
        updated = connection.execute(
            """
            UPDATE invoice
            SET subtotal = %s, discount_total = %s, tax_amount = %s, status = %s
            WHERE invoice_id = %s
            RETURNING invoice_id, folio_id, invoice_number, subtotal, discount_total,
                      tax_amount, issued_at, status
            """,
            (
                totals["subtotal"],
                totals["discount_total"],
                totals["tax_amount"],
                new_status,
                existing["invoice_id"],
            ),
        ).fetchone()
        audit(
            connection,
            user.user_id,
            header["reservation_id"],
            "INVOICE_UPDATED",
            {
                "invoice_id": updated["invoice_id"],
                "invoice_number": updated["invoice_number"],
                "gross_total": str(totals["gross_total"]),
            },
        )
        return build_invoice_out(connection, updated)

    invoice_id = next_id(connection, "invoice", "invoice_id")
    ym = connection.execute("SELECT to_char(now(), 'YYYYMM') AS ym").fetchone()["ym"]
    invoice_number = f"INV-{ym}-{invoice_id:04d}"
    status_val = "PAID" if totals["gross_total"] == Decimal("0.00") else "ISSUED"
    created = connection.execute(
        """
        INSERT INTO invoice
            (invoice_id, folio_id, invoice_number, subtotal, discount_total, tax_amount, issued_at, status)
        VALUES (%s, %s, %s, %s, %s, %s, now(), %s)
        RETURNING invoice_id, folio_id, invoice_number, subtotal, discount_total,
                  tax_amount, issued_at, status
        """,
        (
            invoice_id,
            folio_id,
            invoice_number,
            totals["subtotal"],
            totals["discount_total"],
            totals["tax_amount"],
            status_val,
        ),
    ).fetchone()
    audit(
        connection,
        user.user_id,
        header["reservation_id"],
        "INVOICE_ISSUED",
        {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "gross_total": str(totals["gross_total"]),
        },
    )
    return build_invoice_out(connection, created)


def record_payment(connection, invoice_id: int, user: CurrentUser, body) -> dict:
    """Record CASH/TRANSFER payment; guards overpayment and replays same transaction_ref."""
    connection.execute("SELECT pg_advisory_xact_lock(%s)", (ID_LOCK,))
    inv = connection.execute(
        """
        SELECT i.invoice_id, i.folio_id, i.invoice_number, i.subtotal, i.discount_total,
               i.tax_amount, i.issued_at, i.status, f.status AS folio_status,
               s.reservation_id
        FROM invoice i
        JOIN folio f ON f.folio_id = i.folio_id
        JOIN stay s ON s.stay_id = f.stay_id
        WHERE i.invoice_id = %s
        FOR UPDATE OF i
        """,
        (invoice_id,),
    ).fetchone()
    if inv is None:
        raise not_found("INVOICE_NOT_FOUND", "Không tìm thấy hóa đơn.")
    if inv["status"] == "VOID" or inv["folio_status"] == "VOID":
        raise conflict("INVOICE_VOID", "Hóa đơn đã bị hủy, không thể ghi nhận thanh toán.")

    amount = quantize_money(Decimal(body.amount))

    # Idempotency check on transaction_ref (also backed by uq_payment_transaction_ref in V001).
    if body.transaction_ref is not None:
        existing_payment = connection.execute(
            """
            SELECT payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at
            FROM payment
            WHERE transaction_ref = %s
            """,
            (body.transaction_ref,),
        ).fetchone()
        if existing_payment is not None:
            if (
                existing_payment["invoice_id"] == invoice_id
                and quantize_money(Decimal(existing_payment["amount"])) == amount
                and existing_payment["method"] == body.method
            ):
                return {
                    "payment": existing_payment,
                    "invoice": build_invoice_out(connection, inv),
                    "idempotent_replay": True,
                }
            raise conflict(
                "DUPLICATE_TRANSACTION_REF",
                "Mã tham chiếu giao dịch đã được sử dụng cho khoản thanh toán khác.",
            )

    gross_total = quantize_money(
        Decimal(inv["subtotal"]) - Decimal(inv["discount_total"]) + Decimal(inv["tax_amount"])
    )
    paid_row = connection.execute(
        "SELECT COALESCE(SUM(amount), 0) AS paid FROM payment WHERE invoice_id = %s",
        (invoice_id,),
    ).fetchone()
    paid_total = quantize_money(Decimal(paid_row["paid"]))
    balance_due = quantize_money(gross_total - paid_total)

    if balance_due <= Decimal("0.00"):
        raise conflict("INVOICE_ALREADY_PAID", "Hóa đơn đã được thanh toán đủ.")
    if amount > balance_due:
        raise conflict(
            "OVERPAYMENT",
            f"Số tiền thanh toán ({amount}) vượt quá số tiền còn phải trả ({balance_due}).",
        )

    payment_id = next_id(connection, "payment", "payment_id")
    payment_row = connection.execute(
        """
        INSERT INTO payment
            (payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at)
        VALUES (%s, %s, %s, %s, %s, %s, now())
        RETURNING payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at
        """,
        (
            payment_id,
            invoice_id,
            user.employee_id,
            amount,
            body.method,
            body.transaction_ref,
        ),
    ).fetchone()

    new_paid = quantize_money(paid_total + amount)
    new_status = "PAID" if new_paid == gross_total else "PARTIAL"
    updated_inv = connection.execute(
        """
        UPDATE invoice SET status = %s WHERE invoice_id = %s
        RETURNING invoice_id, folio_id, invoice_number, subtotal, discount_total,
                  tax_amount, issued_at, status
        """,
        (new_status, invoice_id),
    ).fetchone()

    audit(
        connection,
        user.user_id,
        inv["reservation_id"],
        "PAYMENT_RECORDED",
        {
            "payment_id": payment_id,
            "invoice_id": invoice_id,
            "amount": str(amount),
            "method": body.method,
            "transaction_ref": body.transaction_ref,
            "invoice_status": new_status,
        },
    )
    return {
        "payment": payment_row,
        "invoice": build_invoice_out(connection, updated_inv),
        "idempotent_replay": False,
    }
