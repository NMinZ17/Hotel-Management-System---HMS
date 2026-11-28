"""Week 2: auth, availability, booking and cancellation.

Run from backend/:
    python -m unittest discover -s tests -v

Set HMS_TEST_DATABASE_URL to a disposable PostgreSQL database to enable the
integration cases. Each case builds database/schema.sql in its own random
schema and drops it afterwards; existing tables are never touched.
"""

import os
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app.config import Settings
from app.main import create_app
from app.security import create_token, decode_token, hash_password, verify_password
from app.services.booking import validate_guests, validate_stay

TEST_DATABASE_URL = os.environ.get("HMS_TEST_DATABASE_URL", "")
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "database" / "schema.sql"
SECRET = "test-secret-" + "x" * 32
UNAVAILABLE = "postgresql://u:p@127.0.0.1:1/db?connect_timeout=1"

SEED = """
INSERT INTO room_type VALUES (1,'Standard',2,800000.00,TRUE),(2,'Deluxe',3,1200000.00,TRUE),
                             (3,'Archived',4,1.00,FALSE);
INSERT INTO room VALUES (101,1,'101',1,'CLEAN','OK',TRUE),(102,1,'102',1,'CLEAN','OK',TRUE),
                        (201,2,'201',2,'CLEAN','OK',TRUE),(301,3,'301',3,'CLEAN','OK',TRUE);
INSERT INTO role VALUES (1,'ADMIN','Quan tri'),(2,'RECEPTION','Le tan'),(3,'GUEST','Khach');
INSERT INTO app_user VALUES (1,'admin@hms.example','demo_hash',TRUE,now()),
                            (2,'letan@hms.example','demo_hash',TRUE,now());
INSERT INTO user_role VALUES (1,1),(2,2);
"""


def future(days):
    return date.today() + timedelta(days=days)


class PureTests(unittest.TestCase):
    def test_password_hash_roundtrip(self):
        stored = hash_password("correct horse")
        self.assertNotIn("correct horse", stored)
        self.assertTrue(verify_password("correct horse", stored))
        self.assertFalse(verify_password("wrong", stored))
        self.assertNotEqual(stored, hash_password("correct horse"))

    def test_placeholder_hash_never_verifies(self):
        for stored in ("demo_hash", "", None, "scrypt$x$y$z$a$b"):
            self.assertFalse(verify_password("demo_hash", stored))

    def test_token_rules(self):
        token = create_token(7, SECRET, 60, now=1000)
        self.assertEqual(decode_token(token, SECRET, now=1030), 7)
        self.assertIsNone(decode_token(token, SECRET, now=1061))
        self.assertIsNone(decode_token(token, "other-secret", now=1030))
        head, payload, sig = token.split(".")
        self.assertIsNone(decode_token(f"{head}.{payload}x.{sig}", SECRET, now=1030))
        self.assertIsNone(decode_token("garbage", SECRET))

    def test_date_validation(self):
        today = date(2026, 12, 1)
        self.assertEqual(validate_stay(date(2026, 12, 2), date(2026, 12, 4), today), 2)
        for ci, co in (
            (date(2026, 12, 2), date(2026, 12, 2)),
            (date(2026, 12, 3), date(2026, 12, 2)),
            (date(2026, 11, 30), date(2026, 12, 2)),
            (date(2026, 12, 2), date(2027, 2, 1)),
        ):
            with self.subTest(ci=ci, co=co):
                with self.assertRaises(Exception) as ctx:
                    validate_stay(ci, co, today)
                self.assertEqual(ctx.exception.status_code, 422)

    def test_guest_validation(self):
        validate_guests(2, 0, 2)
        validate_guests(5, 5, None)
        for adults, children in ((0, 1), (2, 1)):
            with self.assertRaises(Exception):
                validate_guests(adults, children, 2)


class ApiWithoutDatabaseTests(unittest.TestCase):
    def client(self, secret=SECRET):
        return TestClient(
            create_app(Settings(database_url=UNAVAILABLE, auth_secret=secret))
        )

    def test_protected_routes_require_a_token(self):
        with self.client() as client:
            self.assertEqual(client.get("/api/reservations/mine").status_code, 401)
            self.assertEqual(client.post("/api/reservations/1/cancel").status_code, 401)
            self.assertEqual(client.get("/api/auth/me").status_code, 401)
            bad = {"Authorization": "Bearer nonsense"}
            self.assertEqual(client.get("/api/auth/me", headers=bad).status_code, 401)

    def test_validation_happens_before_database(self):
        with self.client() as client:
            self.assertEqual(
                client.post(
                    "/api/auth/register",
                    json={"email": "bad", "password": "short", "full_name": ""},
                ).status_code,
                422,
            )
            response = client.get(
                "/api/availability",
                params={"check_in": str(future(5)), "check_out": str(future(5))},
            )
            self.assertEqual(response.status_code, 422)
            self.assertEqual(response.json()["detail"]["code"], "INVALID_DATES")

    def test_register_requires_phone_with_422_not_503(self):
        base = {"email": "a@b.co", "password": "longenough", "full_name": "A"}
        for phone in (None, "", "   ", "abc", "1234", "0900-abc-123", "1" * 31):
            body = dict(base) if phone is None else {**base, "phone": phone}
            with self.subTest(phone=phone), self.client() as client:
                response = client.post("/api/auth/register", json=body)
                self.assertEqual(response.status_code, 422, response.text)
                self.assertIn("phone", response.text)
        with self.client() as client:
            blank_name = client.post(
                "/api/auth/register", json={**base, "full_name": "   ", "phone": "0900000001"}
            )
        self.assertEqual(blank_name.status_code, 422)

    def test_login_without_secret_is_a_clear_503(self):
        with self.client(secret="") as client:
            response = client.post(
                "/api/auth/login", json={"email": "a@b.co", "password": "x"}
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "AUTH_NOT_CONFIGURED")

    def test_db_failure_on_login_is_safe_503(self):
        with self.client() as client:
            response = client.post(
                "/api/auth/login", json={"email": "a@b.co", "password": "x"}
            )
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("127.0.0.1", response.text)

    def test_register_db_failure_is_not_success(self):
        with self.client() as client:
            response = client.post(
                "/api/auth/register",
                json={
                    "email": "a@b.co",
                    "password": "longenough",
                    "full_name": "A",
                    "phone": "0900000001",
                },
            )
        self.assertEqual(response.status_code, 503)


@unittest.skipUnless(TEST_DATABASE_URL, "Set HMS_TEST_DATABASE_URL for PostgreSQL cases.")
class PostgreSqlBookingTests(unittest.TestCase):
    def setUp(self):
        self.schema = "hms_w2_test_" + uuid4().hex
        admin = psycopg.connect(TEST_DATABASE_URL, autocommit=True)
        self.addCleanup(admin.close)
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema)))
        self.addCleanup(
            lambda: admin.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )
        )
        self.url = make_conninfo(TEST_DATABASE_URL, options="-csearch_path=" + self.schema)
        with psycopg.connect(self.url) as connection:
            connection.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
            # Mirror the NOT NULL columns of Trang's migration V001 that registration writes.
            connection.execute(
                "ALTER TABLE guest ALTER COLUMN phone SET NOT NULL, "
                "ALTER COLUMN full_name SET NOT NULL"
            )
            connection.execute(SEED)
        self.client = TestClient(create_app(Settings(database_url=self.url, auth_secret=SECRET)))
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    # helpers
    def register_and_login(self, email="guest@example.com"):
        r = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "password123",
                "full_name": "Khach Test",
                "phone": "0900 000 001",
            },
        )
        self.assertEqual(r.status_code, 201, r.text)
        r = self.client.post("/api/auth/login", json={"email": email, "password": "password123"})
        self.assertEqual(r.status_code, 200, r.text)
        return {"Authorization": "Bearer " + r.json()["access_token"]}

    def book(self, headers, ci=5, co=7, room_type_id=1, adults=2, children=0):
        return self.client.post(
            "/api/reservations",
            headers=headers,
            json={
                "room_type_id": room_type_id,
                "check_in": str(future(ci)),
                "check_out": str(future(co)),
                "adults": adults,
                "children": children,
            },
        )

    def scalar(self, query, *params):
        with psycopg.connect(self.url) as connection:
            return connection.execute(query, params).fetchone()[0]

    # auth
    def test_register_login_me_and_hash_stored(self):
        headers = self.register_and_login()
        me = self.client.get("/api/auth/me", headers=headers).json()
        self.assertEqual(me["roles"], ["GUEST"])
        self.assertIsNotNone(me["guest_id"])
        stored = self.scalar("SELECT password_hash FROM app_user WHERE email = 'guest@example.com'")
        self.assertTrue(stored.startswith("scrypt$"))
        self.assertNotIn("password123", stored)

    def test_register_without_phone_is_422_and_writes_nothing(self):
        body = {"email": "nophone@example.com", "password": "password123", "full_name": "Khach"}
        missing = self.client.post("/api/auth/register", json=body)
        self.assertEqual(missing.status_code, 422, missing.text)
        self.assertEqual(self.scalar("SELECT count(*) FROM app_user WHERE email = %s", body["email"]), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM guest"), 0)
        ok = self.client.post("/api/auth/register", json={**body, "phone": " +84 900 000 001 "})
        self.assertEqual(ok.status_code, 201, ok.text)
        self.assertEqual(self.scalar("SELECT phone FROM guest"), "+84 900 000 001")

    def test_duplicate_email_and_bad_credentials(self):
        self.register_and_login()
        dup = self.client.post(
            "/api/auth/register",
            json={
                "email": "GUEST@example.com",
                "password": "password123",
                "full_name": "X",
                "phone": "0900000002",
            },
        )
        self.assertEqual(dup.status_code, 409)
        self.assertEqual(dup.json()["detail"]["code"], "EMAIL_TAKEN")
        for creds in (
            {"email": "guest@example.com", "password": "wrong-password"},
            {"email": "nobody@example.com", "password": "password123"},
            {"email": "admin@hms.example", "password": "demo_hash"},
        ):
            r = self.client.post("/api/auth/login", json=creds)
            self.assertEqual(r.status_code, 401, creds)
            self.assertNotIn("password", r.text.lower().replace("mật khẩu", ""))

    # availability
    def test_availability_counts_and_filters(self):
        params = {"check_in": str(future(5)), "check_out": str(future(7)), "guests": 2}
        items = self.client.get("/api/availability", params=params).json()
        by_type = {i["room_type"]["room_type_id"]: i for i in items}
        self.assertEqual(sorted(by_type), [1, 2])  # archived type hidden
        self.assertEqual(by_type[1]["available_rooms"], 2)
        self.assertEqual(by_type[1]["total_price"], "1600000.00")
        self.assertEqual(by_type[1]["nights"], 2)
        params["guests"] = 3
        types = [i["room_type"]["room_type_id"] for i in self.client.get("/api/availability", params=params).json()]
        self.assertEqual(types, [2])

    # booking
    def test_booking_creates_all_rows_and_snapshots_price(self):
        headers = self.register_and_login()
        r = self.book(headers)
        self.assertEqual(r.status_code, 201, r.text)
        body = r.json()
        self.assertEqual(body["status"], "CONFIRMED")
        self.assertEqual(body["total_price"], "1600000.00")
        self.assertEqual(body["rooms"][0]["room_number"], "101")
        rid = body["reservation_id"]
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_guest WHERE reservation_id=%s", rid), 1)
        self.assertEqual(self.scalar("SELECT count(*) FROM audit_event WHERE reservation_id=%s AND action='RESERVATION_CREATED'", rid), 1)
        with psycopg.connect(self.url) as c:  # later price change must not alter the booking
            c.execute("UPDATE room_type SET base_price = 999 WHERE room_type_id = 1")
        mine = self.client.get("/api/reservations/mine", headers=headers).json()
        self.assertEqual(mine[0]["total_price"], "1600000.00")

    def test_sequential_double_booking_is_rejected(self):
        headers = self.register_and_login()
        self.assertEqual(self.book(headers).status_code, 201)
        self.assertEqual(self.book(headers).status_code, 201)  # second Standard room
        third = self.book(headers)
        self.assertEqual(third.status_code, 409)
        self.assertEqual(third.json()["detail"]["code"], "NO_ROOM_AVAILABLE")
        # Adjacent range [co, ...) is allowed: check-out day equals next check-in.
        self.assertEqual(self.book(headers, ci=7, co=9).status_code, 201)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation"), 3)

    def test_invalid_input_is_rejected_without_writes(self):
        headers = self.register_and_login()
        cases = (
            (dict(ci=7, co=5), 422),
            (dict(ci=5, co=5), 422),
            (dict(ci=-2, co=3), 422),
            (dict(adults=3), 422),
            (dict(adults=2, children=1), 422),
            (dict(room_type_id=99), 404),
            (dict(room_type_id=3), 404),
        )
        for kwargs, status in cases:
            with self.subTest(kwargs=kwargs):
                self.assertEqual(self.book(headers, **kwargs).status_code, status)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation"), 0)

    def test_staff_account_cannot_book_and_anonymous_cannot(self):
        self.assertEqual(self.client.post("/api/reservations", json={}).status_code, 401)
        with psycopg.connect(self.url) as c:
            c.execute("UPDATE app_user SET password_hash=%s WHERE user_id=2", (hash_password("staffpass1"),))
        r = self.client.post("/api/auth/login", json={"email": "letan@hms.example", "password": "staffpass1"})
        staff = {"Authorization": "Bearer " + r.json()["access_token"]}
        self.assertEqual(self.book(staff).status_code, 403)

    def test_failed_transaction_does_not_report_success_or_write(self):
        headers = self.register_and_login()
        with psycopg.connect(self.url) as c:
            c.execute("DROP TABLE audit_event CASCADE")  # forces failure at the last step
        r = self.book(headers)
        self.assertEqual(r.status_code, 503)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation"), 0)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_room"), 0)

    # ownership and cancellation
    def test_only_owner_reads_and_cancels(self):
        owner = self.register_and_login("a@example.com")
        other = self.register_and_login("b@example.com")
        rid = self.book(owner).json()["reservation_id"]
        self.assertEqual(self.client.get(f"/api/reservations/{rid}", headers=owner).status_code, 200)
        self.assertEqual(self.client.get(f"/api/reservations/{rid}", headers=other).status_code, 404)
        self.assertEqual(self.client.post(f"/api/reservations/{rid}/cancel", headers=other).status_code, 404)
        self.assertEqual(self.client.get("/api/reservations/mine", headers=other).json(), [])
        self.assertEqual(self.scalar("SELECT status FROM reservation WHERE reservation_id=%s", rid), "CONFIRMED")

    def test_cancel_updates_head_and_lines_and_is_idempotent(self):
        headers = self.register_and_login()
        first = self.book(headers).json()
        rid = first["reservation_id"]
        r1 = self.client.post(f"/api/reservations/{rid}/cancel", headers=headers)
        self.assertEqual(r1.status_code, 200, r1.text)
        self.assertEqual(r1.json()["status"], "CANCELLED")
        self.assertTrue(r1.json()["rooms"][0]["is_cancelled"])
        stamp = self.scalar("SELECT cancelled_at FROM reservation WHERE reservation_id=%s", rid)
        r2 = self.client.post(f"/api/reservations/{rid}/cancel", headers=headers)
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(self.scalar("SELECT cancelled_at FROM reservation WHERE reservation_id=%s", rid), stamp)
        self.assertEqual(self.scalar("SELECT count(*) FROM audit_event WHERE action='RESERVATION_CANCELLED'"), 1)
        # history kept, and the room is bookable again
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_room WHERE reservation_id=%s", rid), 1)
        self.assertEqual(self.book(headers).status_code, 201)
        self.assertEqual(self.book(headers).status_code, 201)

    def test_checked_in_reservation_cannot_be_cancelled(self):
        headers = self.register_and_login()
        rid = self.book(headers).json()["reservation_id"]
        with psycopg.connect(self.url) as c:
            c.execute("INSERT INTO stay (stay_id, reservation_id, status) VALUES (1, %s, 'IN_HOUSE')", (rid,))
        r = self.client.post(f"/api/reservations/{rid}/cancel", headers=headers)
        self.assertEqual(r.status_code, 409)

    def test_concurrent_bookings_never_overbook(self):
        headers = [self.register_and_login(f"u{i}@example.com") for i in range(6)]
        results = []

        def run(h):
            results.append(self.book(h, room_type_id=2).status_code)

        # Deluxe has exactly one room: exactly one request may win.
        threads = [threading.Thread(target=run, args=(h,)) for h in headers]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sorted(results), [201] + [409] * 5, results)
        self.assertEqual(self.scalar("SELECT count(*) FROM reservation_room WHERE room_id=201"), 1)


if __name__ == "__main__":
    unittest.main()
