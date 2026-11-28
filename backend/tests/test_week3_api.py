"""Week 3: multi-room atomic booking, check-in, folio, invoice, payment and check-out.

Run from backend/:
    python -m unittest tests.test_week3_api -v

Set HMS_TEST_DATABASE_URL to a disposable PostgreSQL database to run integration
cases. If Trang's migration files (V001__init_hms_schema.sql and
V002__hardening_constraints.sql) are available via HMS_TEST_MIGRATIONS_DIR or
database/migrations/, the suite runs directly against them; otherwise it uses
database/schema.sql hardened with V001/V002 constraints.
"""

import os
import threading
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app.config import Settings
from app.main import create_app
from app.schemas import PaymentRequest, ReservationRequest
from app.security import hash_password
from app.services.booking import compute_discount_amount, quantize_money

TEST_DATABASE_URL = os.environ.get("HMS_TEST_DATABASE_URL", "")
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "database" / "schema.sql"
MIGRATIONS_DIR = Path(
    os.environ.get("HMS_TEST_MIGRATIONS_DIR", str(REPO_ROOT / "database" / "migrations"))
)
SECRET = "test-week3-secret-" + "y" * 32
UNAVAILABLE = "postgresql://u_secret:p_secret_do_not_log@127.0.0.1:1/hms_priv?connect_timeout=1"

# Fallback constraints mirroring V001 + V002 when database/migrations/ is not yet merged.
FALLBACK_HARDENING = """
ALTER TABLE guest ALTER COLUMN full_name SET NOT NULL, ALTER COLUMN phone SET NOT NULL;
ALTER TABLE stay ALTER COLUMN checked_in_by SET NOT NULL;
ALTER TABLE stay ADD CONSTRAINT uq_stay_res UNIQUE (reservation_id);
ALTER TABLE stay ADD CONSTRAINT ck_stay_cons CHECK (
    (status = 'CHECKED_OUT' AND actual_check_out IS NOT NULL AND checked_out_by IS NOT NULL)
    OR (status = 'IN_HOUSE' AND actual_check_out IS NULL)
);
ALTER TABLE stay_room ADD CONSTRAINT ck_sr_int CHECK (
    assigned_to IS NULL OR assigned_to > assigned_from
);
ALTER TABLE folio ADD CONSTRAINT uq_folio_stay UNIQUE (stay_id);
ALTER TABLE folio_item ADD CONSTRAINT ck_fi_price CHECK (
    (entry_type IN ('CHARGE', 'TAX') AND unit_price >= 0)
    OR (entry_type = 'DISCOUNT' AND unit_price <= 0)
    OR (entry_type = 'ADJUSTMENT')
);
CREATE UNIQUE INDEX uq_fi_source ON folio_item(folio_id, source_key) WHERE source_key IS NOT NULL;
ALTER TABLE invoice ADD CONSTRAINT uq_inv_num UNIQUE (invoice_number);
ALTER TABLE payment ALTER COLUMN recorded_by SET NOT NULL;
CREATE UNIQUE INDEX uq_pay_ref ON payment(transaction_ref) WHERE transaction_ref IS NOT NULL;
ALTER TABLE housekeeping_task ALTER COLUMN scheduled_at SET NOT NULL;
"""

SEED = """
INSERT INTO hotel (hotel_id, name, address, phone, timezone)
VALUES (1, 'HMS Test Hotel', '1 Demo St', '0240000000', 'Asia/Ho_Chi_Minh');

INSERT INTO room_type (room_type_id, name, max_guests, base_price, is_active) VALUES
(1, 'Standard', 2,  800000.00, TRUE),
(2, 'Deluxe',   3, 1200000.00, TRUE),
(3, 'Suite',    4, 2500000.00, TRUE);

INSERT INTO room (room_id, room_type_id, room_number, floor, housekeeping_status, maintenance_status, is_active) VALUES
(101, 1, '101', 1, 'CLEAN', 'OK', TRUE),
(102, 1, '102', 1, 'CLEAN', 'OK', TRUE),
(201, 2, '201', 2, 'CLEAN', 'OK', TRUE),
(202, 3, '202', 2, 'CLEAN', 'OK', TRUE);

INSERT INTO role (role_id, code, name) VALUES
(1, 'ADMIN',     'Quan tri'),
(2, 'RECEPTION', 'Le tan'),
(3, 'GUEST',     'Khach');

INSERT INTO app_user (user_id, email, password_hash, is_active, created_at) VALUES
(1, 'admin@hms.example',  '__ADMIN_HASH__', TRUE, now()),
(2, 'letan@hms.example',  '__STAFF_HASH__', TRUE, now());

INSERT INTO user_role (user_id, role_id) VALUES (1, 1), (2, 2);

INSERT INTO employee (employee_id, user_id, full_name, job_title, is_active) VALUES
(1, 1, 'Nguyen Van Quan', 'Manager', TRUE),
(2, 2, 'Tran Thi Le',     'Receptionist', TRUE);

INSERT INTO guest (guest_id, user_id, full_name, phone, email) VALUES
(2, NULL, 'Nguyen Minh Anh', '0900000002', 'anh@example.com');

INSERT INTO discount (discount_id, code, discount_type, value, valid_from, valid_to, is_active) VALUES
(1, 'WELCOME10',   'PERCENT',     10.00, '2026-01-01', '2028-12-31', TRUE),
(2, 'FIXED500K',   'FIXED',   500000.00, '2026-01-01', '2028-12-31', TRUE),
(3, 'EXPIRED2025', 'PERCENT',     15.00, '2025-01-01', '2025-12-31', FALSE);

INSERT INTO service (service_id, name, category, unit_price, is_active) VALUES
(1, 'Giat ui', 'LAUNDRY',   50000.00, TRUE),
(2, 'An sang', 'FOOD',     120000.00, TRUE),
(3, 'Minibar', 'BEVERAGE',  80000.00, TRUE);
"""


def future(days: int) -> date:
    return date.today() + timedelta(days=days)


def _strip_tx_wrappers(script: str) -> str:
    lines = []
    for line in script.splitlines():
        stripped = line.strip().upper()
        if stripped in ("BEGIN;", "COMMIT;", "CREATE EXTENSION IF NOT EXISTS BTREE_GIST;"):
            continue
        lines.append(line)
    return "\n".join(lines)


class PureWeek3Tests(unittest.TestCase):
    def test_discount_and_money_rounding(self):
        self.assertEqual(
            compute_discount_amount("PERCENT", Decimal("10"), Decimal("6340000.00")),
            Decimal("634000.00"),
        )
        self.assertEqual(
            compute_discount_amount("FIXED", Decimal("500000"), Decimal("300000.00")),
            Decimal("300000.00"),
        )
        self.assertEqual(quantize_money(Decimal("5706000.00") * Decimal("0.08")), Decimal("456480.00"))

    def test_reservation_request_shape_validation(self):
        single = ReservationRequest(
            room_type_id=1, check_in=future(2), check_out=future(4), adults=2
        )
        self.assertEqual(len(single.normalized_rooms()), 1)

        multi = ReservationRequest(
            rooms=[
                {"room_type_id": 1, "check_in": future(2), "check_out": future(5), "adults": 2},
                {"room_type_id": 2, "check_in": future(2), "check_out": future(5), "adults": 2, "children": 1},
            ],
            discount_code="WELCOME10",
            companion_guest_ids=[2],
        )
        self.assertEqual(len(multi.normalized_rooms()), 2)

        with self.assertRaises(Exception):
            ReservationRequest(
                room_type_id=1,
                check_in=future(2),
                check_out=future(4),
                adults=2,
                rooms=[{"room_type_id": 1, "check_in": future(2), "check_out": future(4), "adults": 2}],
            )
        with self.assertRaises(Exception):
            ReservationRequest(rooms=[])

    def test_payment_request_validation(self):
        p = PaymentRequest(amount=Decimal("100000.00"), method="TRANSFER", transaction_ref="  TRF-1  ")
        self.assertEqual(p.transaction_ref, "TRF-1")
        with self.assertRaises(Exception):
            PaymentRequest(amount=Decimal("0"), method="CASH")
        with self.assertRaises(Exception):
            PaymentRequest(amount=Decimal("100"), method="CRYPTO")


class Week3ApiWithoutDatabaseTests(unittest.TestCase):
    def client(self):
        return TestClient(create_app(Settings(database_url=UNAVAILABLE, auth_secret=SECRET)))

    def test_week3_routes_require_authentication(self):
        with self.client() as client:
            for method, path, payload in (
                ("POST", "/api/reservations/1/check-in", None),
                ("GET", "/api/stays/1", None),
                ("POST", "/api/stays/1/check-out", None),
                ("GET", "/api/folios/1", None),
                ("POST", "/api/folios/1/invoices", None),
                ("GET", "/api/invoices/1", None),
                ("POST", "/api/invoices/1/payments", {"amount": "100.00", "method": "CASH"}),
            ):
                with self.subTest(method=method, path=path):
                    r = client.request(method, path, json=payload)
                    self.assertEqual(r.status_code, 401)

    def test_logs_never_leak_database_url_or_password(self):
        with self.client() as client, self.assertLogs("app.db", level="WARNING") as logs:
            r = client.post(
                "/api/auth/login",
                json={"email": "a@b.co", "password": "MyTopSecretPassword999"},
            )
        self.assertEqual(r.status_code, 503)
        combined = "\n".join(logs.output) + "\n" + r.text
        for secret in (
            UNAVAILABLE,
            "u_secret",
            "p_secret_do_not_log",
            "hms_priv",
            "MyTopSecretPassword999",
        ):
            self.assertNotIn(secret, combined)


@unittest.skipUnless(TEST_DATABASE_URL, "Set HMS_TEST_DATABASE_URL for PostgreSQL cases.")
class PostgreSqlWeek3Tests(unittest.TestCase):
    def setUp(self):
        self.schema = "hms_w3_test_" + uuid4().hex
        admin = psycopg.connect(TEST_DATABASE_URL, autocommit=True)
        self.addCleanup(admin.close)
        admin.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.addCleanup(
            lambda: admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )
        )
        self.url = make_conninfo(
            TEST_DATABASE_URL, options=f"-csearch_path={self.schema},public"
        )
        v001 = MIGRATIONS_DIR / "V001__init_hms_schema.sql"
        v002 = MIGRATIONS_DIR / "V002__hardening_constraints.sql"
        seed_sql = SEED.replace("__ADMIN_HASH__", hash_password("adminpass1")).replace(
            "__STAFF_HASH__", hash_password("staffpass1")
        )
        with psycopg.connect(self.url) as connection:
            if v001.is_file():
                connection.execute(_strip_tx_wrappers(v001.read_text(encoding="utf-8-sig")))
                if v002.is_file():
                    connection.execute(_strip_tx_wrappers(v002.read_text(encoding="utf-8-sig")))
            else:
                connection.execute(SCHEMA_PATH.read_text(encoding="utf-8-sig"))
                connection.execute(FALLBACK_HARDENING)
            connection.execute(seed_sql)

        self.client = TestClient(create_app(Settings(database_url=self.url, auth_secret=SECRET)))
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

        self.staff_headers = self._login("letan@hms.example", "staffpass1")

    def _login(self, email: str, password: str) -> dict[str, str]:
        r = self.client.post("/api/auth/login", json={"email": email, "password": password})
        self.assertEqual(r.status_code, 200, r.text)
        return {"Authorization": "Bearer " + r.json()["access_token"]}

    def register_guest(self, email="guest1@example.com") -> dict[str, str]:
        r = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Pham Thu Ha",
                "phone": "0900000001",
            },
        )
        self.assertEqual(r.status_code, 201, r.text)
        return self._login(email, "password123")

    def scalar(self, query: str, *params):
        with psycopg.connect(self.url) as connection:
            return connection.execute(query, params).fetchone()[0]

    # ---- Full lifecycle matching Trang's 06_financial_fixture.sql ----------
    def test_full_lifecycle_matches_financial_fixture_and_idempotency(self):
        guest = self.register_guest()

        # 1. Multi-room booking: Standard 101 + Deluxe 201 for 3 nights + companion + WELCOME10
        book = self.client.post(
            "/api/reservations",
            headers=guest,
            json={
                "rooms": [
                    {"room_type_id": 1, "check_in": str(future(5)), "check_out": str(future(8)), "adults": 2, "children": 0},
                    {"room_type_id": 2, "check_in": str(future(5)), "check_out": str(future(8)), "adults": 2, "children": 1},
                ],
                "companion_guest_ids": [2],
                "discount_code": "WELCOME10",
                "note": "Multi-room financial fixture flow",
            },
        )
        self.assertEqual(book.status_code, 201, book.text)
        res = book.json()
        rid = res["reservation_id"]
        self.assertEqual(len(res["rooms"]), 2)
        self.assertEqual(res["subtotal"], "6000000.00")
        self.assertEqual(res["discount_code"], "WELCOME10")
        self.assertEqual(res["discount_amount"], "600000.00")
        self.assertEqual(res["total_price"], "5400000.00")
        self.assertEqual(
            self.scalar("SELECT count(*) FROM reservation_guest WHERE reservation_id = %s", rid), 2
        )

        # 2. Check-in by staff (and verify repeat check-in is idempotent)
        ci1 = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers)
        self.assertEqual(ci1.status_code, 200, ci1.text)
        stay = ci1.json()
        stay_id = stay["stay_id"]
        folio_id = stay["folio_id"]
        self.assertEqual(stay["status"], "IN_HOUSE")
        self.assertEqual(stay["checked_in_by"], 2)
        self.assertEqual(len(stay["rooms"]), 2)
        self.assertEqual(
            self.scalar("SELECT status FROM reservation WHERE reservation_id = %s", rid),
            "CHECKED_IN",
        )

        ci2 = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers)
        self.assertEqual(ci2.status_code, 200, ci2.text)
        self.assertEqual(ci2.json()["stay_id"], stay_id)
        self.assertEqual(self.scalar("SELECT count(*) FROM stay WHERE reservation_id = %s", rid), 1)
        self.assertEqual(self.scalar("SELECT count(*) FROM folio WHERE stay_id = %s", stay_id), 1)
        self.assertEqual(
            self.scalar("SELECT count(*) FROM audit_event WHERE action = 'STAY_CHECKED_IN'"), 1
        )

        # 3. Add the 2 completed service charges from Trang's 06_financial_fixture:
        #    Laundry 2 * 50,000 = 100,000; Minibar 3 * 80,000 = 240,000.
        with psycopg.connect(self.url) as conn:
            conn.execute(
                """
                INSERT INTO folio_item
                    (folio_item_id, folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at)
                VALUES
                    (100, %s, 'CHARGE', 'Giat do (2 mon)', 2.00, 50000.00, 'SOI:100', now()),
                    (101, %s, 'CHARGE', 'Minibar (3 chai)', 3.00, 80000.00, 'SOI:101', now())
                """,
                (folio_id, folio_id),
            )

        # 4. Issue invoice -> must match Trang's hand-calculated fixture totals to the cent!
        inv_r1 = self.client.post(f"/api/folios/{folio_id}/invoices", headers=self.staff_headers)
        self.assertEqual(inv_r1.status_code, 200, inv_r1.text)
        inv = inv_r1.json()
        inv_id = inv["invoice_id"]
        self.assertEqual(inv["subtotal"], "6340000.00")
        self.assertEqual(inv["discount_total"], "634000.00")
        self.assertEqual(inv["tax_amount"], "456480.00")
        self.assertEqual(inv["gross_total"], "6162480.00")
        self.assertEqual(inv["balance_due"], "6162480.00")
        self.assertEqual(inv["status"], "ISSUED")

        # Repeat issue_invoice is idempotent
        inv_r2 = self.client.post(f"/api/folios/{folio_id}/invoices", headers=self.staff_headers)
        self.assertEqual(inv_r2.status_code, 200)
        self.assertEqual(inv_r2.json()["invoice_id"], inv_id)
        self.assertEqual(self.scalar("SELECT count(*) FROM invoice WHERE folio_id = %s", folio_id), 1)

        # Verify folio endpoint reflects exact same totals
        folio = self.client.get(f"/api/folios/{folio_id}", headers=guest).json()
        self.assertEqual(folio["gross_total"], "6162480.00")
        self.assertEqual(folio["discount_total"], "634000.00")

        # 5. Record 2 payments: 3,000,000 CASH (PARTIAL), then 3,162,480 TRANSFER (PAID)
        p1 = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={"amount": "3000000.00", "method": "CASH"},
        )
        self.assertEqual(p1.status_code, 200, p1.text)
        self.assertEqual(p1.json()["invoice"]["status"], "PARTIAL")
        self.assertEqual(p1.json()["invoice"]["balance_due"], "3162480.00")
        self.assertFalse(p1.json()["idempotent_replay"])

        # Overpayment rejected
        over = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={"amount": "3162480.01", "method": "TRANSFER", "transaction_ref": "TRF-OVER"},
        )
        self.assertEqual(over.status_code, 409)
        self.assertEqual(over.json()["detail"]["code"], "OVERPAYMENT")

        # Check-out while only partially paid is rejected
        early_co = self.client.post(f"/api/stays/{stay_id}/check-out", headers=self.staff_headers)
        self.assertEqual(early_co.status_code, 409)
        self.assertEqual(early_co.json()["detail"]["code"], "PAYMENT_REQUIRED")

        # Pay remaining balance with transaction_ref
        p2 = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={
                "amount": "3162480.00",
                "method": "TRANSFER",
                "transaction_ref": "TRF-20261208-0001",
            },
        )
        self.assertEqual(p2.status_code, 200, p2.text)
        self.assertEqual(p2.json()["invoice"]["status"], "PAID")
        self.assertEqual(p2.json()["invoice"]["paid_total"], "6162480.00")
        self.assertEqual(p2.json()["invoice"]["balance_due"], "0.00")

        # Repeat exact same payment request with same transaction_ref -> idempotent replay
        p2_dup = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={
                "amount": "3162480.00",
                "method": "TRANSFER",
                "transaction_ref": "TRF-20261208-0001",
            },
        )
        self.assertEqual(p2_dup.status_code, 200, p2_dup.text)
        self.assertTrue(p2_dup.json()["idempotent_replay"])
        self.assertEqual(self.scalar("SELECT count(*) FROM payment WHERE invoice_id = %s", inv_id), 2)

        # Reusing same transaction_ref with different amount -> 409
        p2_bad = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={
                "amount": "100.00",
                "method": "TRANSFER",
                "transaction_ref": "TRF-20261208-0001",
            },
        )
        self.assertEqual(p2_bad.status_code, 409)
        self.assertEqual(p2_bad.json()["detail"]["code"], "DUPLICATE_TRANSACTION_REF")

        # Paying again on PAID invoice without matching ref -> 409
        p3 = self.client.post(
            f"/api/invoices/{inv_id}/payments",
            headers=self.staff_headers,
            json={"amount": "1000.00", "method": "CASH"},
        )
        self.assertEqual(p3.status_code, 409)
        self.assertEqual(p3.json()["detail"]["code"], "INVOICE_ALREADY_PAID")

        # 6. Check-out -> closes folio/stay/reservation, marks rooms DIRTY, creates 2 PENDING tasks
        co1 = self.client.post(f"/api/stays/{stay_id}/check-out", headers=self.staff_headers)
        self.assertEqual(co1.status_code, 200, co1.text)
        co_body = co1.json()
        self.assertEqual(co_body["status"], "CHECKED_OUT")
        self.assertEqual(co_body["checked_out_by"], 2)
        self.assertIsNotNone(co_body["actual_check_out"])
        self.assertEqual(len(co_body["housekeeping_task_ids"]), 2)
        self.assertEqual(self.scalar("SELECT status FROM folio WHERE folio_id = %s", folio_id), "CLOSED")
        self.assertEqual(self.scalar("SELECT status FROM reservation WHERE reservation_id = %s", rid), "CHECKED_OUT")
        self.assertEqual(self.scalar("SELECT housekeeping_status FROM room WHERE room_id = 101"), "DIRTY")
        self.assertEqual(self.scalar("SELECT maintenance_status FROM room WHERE room_id = 101"), "OK")
        self.assertEqual(self.scalar("SELECT housekeeping_status FROM room WHERE room_id = 201"), "DIRTY")
        self.assertEqual(self.scalar("SELECT count(*) FROM housekeeping_task WHERE status = 'PENDING'"), 2)

        # Repeat check-out is idempotent (no extra housekeeping tasks or audit events)
        co2 = self.client.post(f"/api/stays/{stay_id}/check-out", headers=self.staff_headers)
        self.assertEqual(co2.status_code, 200)
        self.assertEqual(co2.json()["actual_check_out"], co_body["actual_check_out"])
        self.assertEqual(self.scalar("SELECT count(*) FROM housekeeping_task"), 2)
        self.assertEqual(
            self.scalar("SELECT count(*) FROM audit_event WHERE action = 'STAY_CHECKED_OUT'"), 1
        )

    # ---- Room readiness & service-order guards -----------------------------
    def test_checkin_rejects_dirty_and_maintenance_blocked_rooms(self):
        guest = self.register_guest("g_guard@example.com")
        rid = self.client.post(
            "/api/reservations",
            headers=guest,
            json={"room_type_id": 1, "check_in": str(future(2)), "check_out": str(future(4)), "adults": 2},
        ).json()["reservation_id"]
        room_id = self.scalar("SELECT room_id FROM reservation_room WHERE reservation_id = %s", rid)

        # Dirty room blocked
        with psycopg.connect(self.url) as conn:
            conn.execute("UPDATE room SET housekeeping_status = 'DIRTY' WHERE room_id = %s", (room_id,))
        r_dirty = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers)
        self.assertEqual(r_dirty.status_code, 409)
        self.assertEqual(r_dirty.json()["detail"]["code"], "ROOM_NOT_CLEAN")
        self.assertEqual(self.scalar("SELECT count(*) FROM stay"), 0)

        # Maintenance OUT_OF_ORDER blocked even when CLEAN
        with psycopg.connect(self.url) as conn:
            conn.execute(
                "UPDATE room SET housekeeping_status = 'CLEAN', maintenance_status = 'OUT_OF_ORDER' "
                "WHERE room_id = %s",
                (room_id,),
            )
        r_maint = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers)
        self.assertEqual(r_maint.status_code, 409)
        self.assertEqual(r_maint.json()["detail"]["code"], "ROOM_MAINTENANCE_BLOCKED")
        self.assertEqual(self.scalar("SELECT count(*) FROM stay"), 0)

    def test_checkout_blocked_when_service_order_still_in_progress(self):
        guest = self.register_guest("g_svc@example.com")
        rid = self.client.post(
            "/api/reservations",
            headers=guest,
            json={"room_type_id": 1, "check_in": str(future(2)), "check_out": str(future(4)), "adults": 2},
        ).json()["reservation_id"]
        stay = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers).json()
        stay_id = stay["stay_id"]
        folio_id = stay["folio_id"]
        stay_room_id = stay["rooms"][0]["stay_room_id"]

        inv = self.client.post(f"/api/folios/{folio_id}/invoices", headers=self.staff_headers).json()
        self.client.post(
            f"/api/invoices/{inv['invoice_id']}/payments",
            headers=self.staff_headers,
            json={"amount": inv["gross_total"], "method": "CASH"},
        )

        with psycopg.connect(self.url) as conn:
            conn.execute(
                "INSERT INTO service_order (service_order_id, stay_room_id, status, ordered_at) "
                "VALUES (1, %s, 'IN_PROGRESS', now())",
                (stay_room_id,),
            )

        blocked = self.client.post(f"/api/stays/{stay_id}/check-out", headers=self.staff_headers)
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.json()["detail"]["code"], "OPEN_SERVICE_ORDERS")
        self.assertEqual(self.scalar("SELECT status FROM stay WHERE stay_id = %s", stay_id), "IN_HOUSE")
        self.assertEqual(self.scalar("SELECT status FROM folio WHERE folio_id = %s", folio_id), "OPEN")

        # Complete service order -> check-out now succeeds
        with psycopg.connect(self.url) as conn:
            conn.execute("UPDATE service_order SET status = 'COMPLETED', completed_at = now() WHERE service_order_id = 1")
        ok = self.client.post(f"/api/stays/{stay_id}/check-out", headers=self.staff_headers)
        self.assertEqual(ok.status_code, 200, ok.text)

    # ---- Atomic rollback tests ---------------------------------------------
    def _attach_fail_trigger(self, table: str) -> None:
        with psycopg.connect(self.url) as conn:
            conn.execute(
                f"""
                CREATE OR REPLACE FUNCTION {self.schema}.fail_insert() RETURNS trigger AS $$
                BEGIN
                    RAISE EXCEPTION 'simulated mid-transaction failure';
                END;
                $$ LANGUAGE plpgsql;
                CREATE TRIGGER trg_fail_insert
                BEFORE INSERT ON {self.schema}.{table}
                FOR EACH ROW EXECUTE FUNCTION {self.schema}.fail_insert();
                """
            )

    def test_checkin_failure_rolls_back_all_tables(self):
        guest = self.register_guest("g_rb1@example.com")
        rid = self.client.post(
            "/api/reservations",
            headers=guest,
            json={"room_type_id": 1, "check_in": str(future(2)), "check_out": str(future(4)), "adults": 2},
        ).json()["reservation_id"]
        self._attach_fail_trigger("audit_event")
        r = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(self.scalar("SELECT count(*) FROM stay"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM stay_room"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM folio"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM folio_item"), 0)
        self.assertEqual(self.scalar("SELECT status FROM reservation WHERE reservation_id = %s", rid), "CONFIRMED")

    def test_checkout_failure_rolls_back_stay_folio_and_room(self):
        guest = self.register_guest("g_rb2@example.com")
        rid = self.client.post(
            "/api/reservations",
            headers=guest,
            json={"room_type_id": 1, "check_in": str(future(2)), "check_out": str(future(4)), "adults": 2},
        ).json()["reservation_id"]
        stay = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers).json()
        inv = self.client.post(f"/api/folios/{stay['folio_id']}/invoices", headers=self.staff_headers).json()
        self.client.post(
            f"/api/invoices/{inv['invoice_id']}/payments",
            headers=self.staff_headers,
            json={"amount": inv["gross_total"], "method": "CASH"},
        )
        self._attach_fail_trigger("housekeeping_task")
        r = self.client.post(f"/api/stays/{stay['stay_id']}/check-out", headers=self.staff_headers)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(self.scalar("SELECT status FROM stay WHERE stay_id = %s", stay["stay_id"]), "IN_HOUSE")
        self.assertEqual(self.scalar("SELECT status FROM folio WHERE folio_id = %s", stay["folio_id"]), "OPEN")
        self.assertEqual(
            self.scalar("SELECT housekeeping_status FROM room WHERE room_id = %s", stay["rooms"][0]["room_id"]),
            "CLEAN",
        )

    # ---- Multi-room atomicity & concurrency --------------------------------
    def test_multi_room_booking_is_atomic_when_one_room_unavailable(self):
        guest = self.register_guest("g_atomic@example.com")
        # Deluxe only has 1 room (201); asking for 2 Deluxe rooms must fail atomically with 0 rows written.
        r = self.client.post(
            "/api/reservations",
            headers=guest,
            json={
                "rooms": [
                    {"room_type_id": 1, "check_in": str(future(3)), "check_out": str(future(5)), "adults": 2},
                    {"room_type_id": 2, "check_in": str(future(3)), "check_out": str(future(5)), "adults": 2},
                    {"room_type_id": 2, "check_in": str(future(3)), "check_out": str(future(5)), "adults": 2},
                ],
                "discount_code": "WELCOME10",
            },
        )
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["detail"]["code"], "NO_ROOM_AVAILABLE")
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_room"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_discount"), 0)

    def test_concurrent_multi_room_bookings_no_deadlock_no_overbook(self):
        guests = [self.register_guest(f"cm{i}@example.com") for i in range(4)]
        results = []

        def worker(headers, order):
            r = self.client.post(
                "/api/reservations",
                headers=headers,
                json={
                    "rooms": [
                        {"room_type_id": rt, "check_in": str(future(10)), "check_out": str(future(12)), "adults": 2}
                        for rt in order
                    ]
                },
            )
            results.append(r.status_code)

        # Alternate room_type order [1, 2] vs [2, 1] to verify ordered room_id locking avoids deadlocks.
        threads = [
            threading.Thread(target=worker, args=(h, [1, 2] if i % 2 == 0 else [2, 1]))
            for i, h in enumerate(guests)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Deluxe has only 1 room -> exactly 1 multi-room booking may win, 3 get 409.
        self.assertEqual(sorted(results), [201, 409, 409, 409], results)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation"), 1)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_room"), 2)

    # ---- RBAC / object ownership -------------------------------------------
    def test_rbac_guest_cannot_operate_and_cannot_read_other_guest_folio(self):
        owner = self.register_guest("owner@example.com")
        other = self.register_guest("other@example.com")
        rid = self.client.post(
            "/api/reservations",
            headers=owner,
            json={"room_type_id": 1, "check_in": str(future(2)), "check_out": str(future(4)), "adults": 2},
        ).json()["reservation_id"]

        # Guest forbidden from staff operations
        self.assertEqual(self.client.post(f"/api/reservations/{rid}/check-in", headers=owner).status_code, 403)

        stay = self.client.post(f"/api/reservations/{rid}/check-in", headers=self.staff_headers).json()
        stay_id, folio_id = stay["stay_id"], stay["folio_id"]

        self.assertEqual(self.client.post(f"/api/folios/{folio_id}/invoices", headers=owner).status_code, 403)
        inv = self.client.post(f"/api/folios/{folio_id}/invoices", headers=self.staff_headers).json()
        inv_id = inv["invoice_id"]
        self.assertEqual(
            self.client.post(
                f"/api/invoices/{inv_id}/payments",
                headers=owner,
                json={"amount": "1000.00", "method": "CASH"},
            ).status_code,
            403,
        )
        self.assertEqual(self.client.post(f"/api/stays/{stay_id}/check-out", headers=owner).status_code, 403)

        # Owner can read own stay/folio/invoice; other guest gets 404
        for path in (f"/api/stays/{stay_id}", f"/api/folios/{folio_id}", f"/api/invoices/{inv_id}"):
            self.assertEqual(self.client.get(path, headers=owner).status_code, 200, path)
            self.assertEqual(self.client.get(path, headers=self.staff_headers).status_code, 200, path)
            self.assertEqual(self.client.get(path, headers=other).status_code, 404, path)


if __name__ == "__main__":
    unittest.main()
