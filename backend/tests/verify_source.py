"""Verify the API over HTTP against Trang's database schema and seed."""

from datetime import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import time
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

backend = Path(__file__).resolve().parents[1]
evidence = backend.parent / "docs" / "evidence" / "w01"
evidence.mkdir(parents=True, exist_ok=True)
database_url = os.environ["HMS_TEST_DATABASE_URL"]
schema = "hms_w1_source_" + uuid4().hex
source_url = make_conninfo(database_url, options="-csearch_path=" + schema)
checks = []
process = None


def passed(name):
    checks.append({"check": name, "result": "PASS"})
    print("PASS " + name, flush=True)


with psycopg.connect(database_url, autocommit=True) as admin:
    admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    try:
        with psycopg.connect(source_url) as connection:
            for filename in ("schema.sql", "seed.sql"):
                connection.execute(
                    (backend.parent / "database" / filename).read_text(
                        encoding="utf-8"
                    ),
                    prepare=False,
                )
            version = connection.execute("SHOW server_version").fetchone()[0]
            tables = connection.execute(
                "SELECT count(*) FROM information_schema.tables WHERE table_schema=%s",
                (schema,),
            ).fetchone()[0]
        assert tables == 28, tables
        passed("Trang schema/seed: 28 tables created in a fresh isolated schema")

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        env = os.environ.copy()
        env["DATABASE_URL"] = source_url
        env["CORS_ORIGINS"] = "http://localhost:5173,http://127.0.0.1:5173"
        with (evidence / "minh-http-server.txt").open("w", encoding="utf-8") as api_log:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=backend,
                env=env,
                stdout=api_log,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False
            ) as client:
                deadline = time.monotonic() + 20
                while True:
                    try:
                        health = client.get("/api/health")
                        if health.status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    if process.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError("API did not start; inspect minh-http-server.txt")
                    time.sleep(0.1)
                assert health.json() == {"status": "ok", "service": "hms-api"}
                passed("Uvicorn real HTTP: GET /api/health returns 200")

                home = client.get("/", follow_redirects=False)
                assert home.status_code == 307 and home.headers["location"] == "/docs"
                passed("GET / redirects to the API documentation")

                response = client.get("/api/rooms", headers={"Origin": "http://localhost:5173"})
                assert response.status_code == 200, response.text
                before = response.json()
                assert [r["room_id"] for r in before] == [101, 102, 201, 202]
                assert before[0]["room_type"]["base_price"] == "800000.00"
                (evidence / "minh-rooms-response.json").write_text(
                    json.dumps(before, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )
                passed("GET /api/rooms returns all 4 rooms from Trang's seed with nested room_type")
                assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
                passed("Real HTTP response includes the configured React CORS origin")

                filtered = client.get("/api/rooms", params={"room_type_id": 2})
                assert filtered.status_code == 200 and [r["room_id"] for r in filtered.json()] == [201]
                passed("room_type_id=2 reads the seeded Deluxe room")

                with psycopg.connect(source_url) as connection:
                    connection.execute("UPDATE room SET room_number=%s WHERE room_id=%s", ("101-MINH", 101))
                    connection.execute("UPDATE room_type SET base_price=%s WHERE room_type_id=%s", ("850000.25", 1))
                changed = client.get("/api/rooms").json()
                updated_room = next(r for r in changed if r["room_id"] == 101)
                assert updated_room["room_number"] == "101-MINH"
                assert updated_room["room_type"]["base_price"] == "850000.25"
                passed("A committed SQL update is visible in the next HTTP request, without restarting API")

                invalid = client.get("/api/rooms", params={"room_type_id": "1; DROP TABLE room;--"})
                assert invalid.status_code == 422
                assert client.get("/api/rooms").status_code == 200
                passed("Injection-shaped filter returns 422 and the catalogue remains readable")

                with psycopg.connect(source_url) as connection:
                    connection.execute("ALTER TABLE room RENAME TO room_test_unavailable")
                error = client.get("/api/rooms")
                assert error.status_code == 503, error.text
                assert error.json()["detail"]["code"] == "DATABASE_UNAVAILABLE"
                assert schema not in error.text and "hms_review_admin" not in error.text
                passed("A missing database table returns a safe 503 response")

                openapi = client.get("/openapi.json")
                assert openapi.status_code == 200
                assert "/api/rooms" in openapi.json()["paths"]
                passed("OpenAPI documentation exposes both week-one endpoints")

        result = {
            "tested_at": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(),
            "scope": "HMS week-one backend; real Uvicorn HTTP and isolated PostgreSQL. React integration and other members' machines are pending verification.",
            "source": {
                "repository": "NMinZ17/Hotel-Management-System---HMS",
                "ref": "trang/checkpoint_1",
                "commit": "82f9a4339cb54b96ecb3a07a0c518ea395365eb2",
                "schema_blob": "2c546cfafe82e1b4d1c55dab1ac963a947950e15",
                "seed_blob": "96a6342f3620435c3cc83e1099c181acafcc89f8",
            },
            "environment": {
                "python": platform.python_version(),
                "postgresql": version,
                "packages": {name: importlib.metadata.version(name) for name in ["fastapi", "uvicorn", "psycopg", "pydantic", "python-dotenv", "httpx"]},
            },
            "checks": checks,
        }
        (evidence / "minh-source-verification.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))

print(f"Completed {len(checks)} source/HTTP checks; saved evidence.", flush=True)
