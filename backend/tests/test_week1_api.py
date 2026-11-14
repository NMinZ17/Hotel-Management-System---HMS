"""Week 1 API contract and PostgreSQL integration checks.

Run from backend/:
    python -m unittest discover -s tests -v

Set HMS_TEST_DATABASE_URL to a disposable PostgreSQL database to enable
integration cases. Each case creates and removes only its own random schema;
it does not create, reset, or drop the supplied database or existing tables.
"""

import os
from pathlib import Path
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

from app.config import Settings
from app.main import create_app


ALLOWED_ORIGIN = "http://localhost:5173"
CORS_ORIGINS = (ALLOWED_ORIGIN, "http://127.0.0.1:5173")
TEST_DATABASE_URL = os.environ.get("HMS_TEST_DATABASE_URL", "")
FIXTURE_PATH = Path(__file__).with_name("fixture.sql")

# A closed local port makes the failure case independent of PostgreSQL setup.
# Deliberate marker values let the test detect leaked connection details.
UNAVAILABLE_DATABASE_URL = (
    "postgresql://hms_test_user:hms_secret_do_not_echo@127.0.0.1:1/"
    "hms_private_database?connect_timeout=1"
)


def make_client(database_url):
    return TestClient(
        create_app(
            Settings(database_url=database_url, cors_origins=CORS_ORIGINS)
        )
    )


class ApiWithoutDatabaseTests(unittest.TestCase):
    def test_invalid_filters_are_rejected_before_database_connection(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            for query in ("limit=0", "offset=-1", "room_type_id=abc"):
                with self.subTest(query=query):
                    response = client.get("/api/rooms?" + query)
                    self.assertEqual(response.status_code, 422)

    def test_home_redirects_to_api_documentation(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            response = client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/docs")

    def test_health_does_not_require_a_database_connection(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "hms-api"})

    def test_database_failure_returns_safe_503(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            response = client.get("/api/rooms")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "DATABASE_UNAVAILABLE")
        for secret in (
            UNAVAILABLE_DATABASE_URL,
            "hms_test_user",
            "hms_secret_do_not_echo",
            "hms_private_database",
            "connection refused",
        ):
            with self.subTest(secret_kind=secret.split(":")[0]):
                self.assertNotIn(secret, response.text.lower())

    def test_cors_allows_configured_origins(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            for origin in CORS_ORIGINS:
                with self.subTest(origin=origin):
                    response = client.options(
                        "/api/health",
                        headers={
                            "Origin": origin,
                            "Access-Control-Request-Method": "GET",
                        },
                    )
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(
                        response.headers.get("access-control-allow-origin"), origin
                    )

    def test_cors_rejects_unconfigured_origin(self):
        with make_client(UNAVAILABLE_DATABASE_URL) as client:
            response = client.options(
                "/api/health",
                headers={
                    "Origin": "https://untrusted.example",
                    "Access-Control-Request-Method": "GET",
                },
            )
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access-control-allow-origin", response.headers)

@unittest.skipUnless(
    TEST_DATABASE_URL,
    "Set HMS_TEST_DATABASE_URL to run isolated PostgreSQL integration cases.",
)
class PostgreSqlRoomsTests(unittest.TestCase):
    def setUp(self):
        # Schema names are generated internally and quoted as identifiers.
        self.schema = "hms_w1_test_" + uuid4().hex
        self.admin_connection = psycopg.connect(
            TEST_DATABASE_URL, autocommit=True
        )
        self.addCleanup(self.admin_connection.close)
        with self.admin_connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
        self.addCleanup(self._drop_test_schema)
        self.database_url = make_conninfo(
            TEST_DATABASE_URL, options="-csearch_path=" + self.schema
        )
        with psycopg.connect(self.database_url) as connection:
            connection.execute(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.client = make_client(self.database_url)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def _drop_test_schema(self):
        with self.admin_connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(self.schema))
            )

    def get_rooms(self, **parameters):
        response = self.client.get("/api/rooms", params=parameters)
        self.assertEqual(response.status_code, 200, response.text)
        rooms = response.json()
        self.assertIsInstance(rooms, list)
        return rooms

    def test_room_contract_filters_inactive_rows_and_orders_stably(self):
        rooms = self.get_rooms()
        self.assertEqual([room["room_id"] for room in rooms], [101, 105, 102, 201])
        self.assertEqual(
            rooms[0],
            {
                "room_id": 101,
                "room_number": "101",
                "room_type_id": 1,
                "floor": 1,
                "housekeeping_status": "CLEAN",
                "maintenance_status": "OK",
                "room_type": {
                    "room_type_id": 1,
                    "name": "Standard",
                    "max_guests": 2,
                    "base_price": "800000.00",
                },
            },
        )
        self.assertEqual(rooms[-1]["room_type"]["base_price"], "1200000.50")
        self.assertEqual(rooms[-1]["maintenance_status"], "BLOCKED")

    def test_committed_database_changes_appear_in_following_request(self):
        before = self.get_rooms(room_type_id=2)
        self.assertEqual(before[0]["room_number"], "201")
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                "UPDATE room SET room_number = %s WHERE room_id = %s",
                ("209", 201),
            )
            connection.execute(
                "UPDATE room_type SET base_price = %s WHERE room_type_id = %s",
                ("1234567.89", 2),
            )
        # The connection context has committed before the second HTTP request.
        after = self.get_rooms(room_type_id=2)
        self.assertEqual(after[0]["room_number"], "209")
        self.assertEqual(after[0]["room_type"]["base_price"], "1234567.89")

    def test_room_type_filter_and_pagination(self):
        cases = (
            ({"room_type_id": 2}, [201]),
            ({"limit": 2, "offset": 1}, [105, 102]),
            ({"room_type_id": 1, "limit": 1, "offset": 1}, [105]),
            ({"room_type_id": 999}, []),
            ({"room_type_id": 3}, []),
            ({"offset": 100}, []),
            ({"limit": 200}, [101, 105, 102, 201]),
            ({"room_type_id": 9223372036854775807}, []),
        )
        for parameters, expected_ids in cases:
            with self.subTest(parameters=parameters):
                rooms = self.get_rooms(**parameters)
                self.assertEqual([room["room_id"] for room in rooms], expected_ids)

    def test_empty_database_returns_empty_array(self):
        with psycopg.connect(self.database_url) as connection:
            connection.execute("DELETE FROM room")
            connection.execute("DELETE FROM room_type")
        self.assertEqual(self.get_rooms(), [])

    def test_invalid_filters_and_injection_are_rejected(self):
        invalid_parameters = (
            {"room_type_id": "0"},
            {"room_type_id": "-1"},
            {"room_type_id": "9223372036854775808"},
            {"room_type_id": "1.5"},
            {"room_type_id": "1 OR 1=1"},
            {"room_type_id": "1; DROP TABLE room; --"},
            {"limit": "0"},
            {"limit": "201"},
            {"limit": "abc"},
            {"offset": "-1"},
            {"offset": "9223372036854775808"},
            {"offset": "0; SELECT 1"},
        )
        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters):
                response = self.client.get("/api/rooms", params=parameters)
                self.assertEqual(response.status_code, 422)
        # Rejected payloads must not alter the catalogue or drop its tables.
        self.assertEqual(
            [room["room_id"] for room in self.get_rooms()], [101, 105, 102, 201]
        )


if __name__ == "__main__":
    unittest.main()
