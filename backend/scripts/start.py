"""Check PostgreSQL and run the HMS API in the current terminal."""

import argparse
import ipaddress
import os
from pathlib import Path
import shutil
import subprocess
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]


class StartupError(Exception):
    """A configuration problem safe to display without connection details."""


def port_number(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("Port phải là số từ 1 đến 65535.") from None
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port phải là số từ 1 đến 65535.")
    return port


def local_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else BACKEND_DIR / path


def is_loopback(host):
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def start_local_postgres(connection_options):
    data_value = os.environ.get("HMS_PG_DATA_DIR", "").strip()
    if not data_value:
        return

    data_dir = local_path(data_value)
    if not (data_dir / "PG_VERSION").is_file():
        raise StartupError(
            "HMS_PG_DATA_DIR phải trỏ tới cụm PostgreSQL đã có PG_VERSION. "
            "Script không tự khởi tạo cơ sở dữ liệu."
        )

    host = connection_options.get("host", "")
    hostaddr = connection_options.get("hostaddr") or os.environ.get("PGHOSTADDR", "")
    if not is_loopback(host) or (hostaddr and not is_loopback(hostaddr)):
        raise StartupError(
            "Tự khởi động PostgreSQL chỉ hỗ trợ DATABASE_URL dùng host loopback. "
            "Với máy chủ khác, bỏ HMS_PG_DATA_DIR và khởi động PostgreSQL riêng."
        )
    try:
        database_port = port_number(
            connection_options.get("port") or os.environ.get("PGPORT") or "5432"
        )
    except argparse.ArgumentTypeError:
        raise StartupError("Port PostgreSQL phải là một số từ 1 đến 65535.") from None

    binary_name = "pg_ctl.exe" if os.name == "nt" else "pg_ctl"
    bin_value = os.environ.get("HMS_PG_BIN", "").strip()
    if bin_value:
        candidate = local_path(bin_value) / binary_name
        pg_ctl = str(candidate) if candidate.is_file() else None
    else:
        pg_ctl = shutil.which(binary_name)
    if not pg_ctl:
        raise StartupError(
            "Không tìm thấy pg_ctl. Đặt HMS_PG_BIN tới thư mục bin của PostgreSQL "
            "hoặc thêm thư mục đó vào PATH."
        )

    child_options = {
        "capture_output": True,
        "text": True,
        "errors": "replace",
        "creationflags": subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    }
    try:
        status = subprocess.run(
            [pg_ctl, "-D", str(data_dir), "status"],
            timeout=10,
            **child_options,
        )
        if status.returncode == 0:
            print("[OK] Cụm PostgreSQL cục bộ đang chạy.", flush=True)
            return
        if status.returncode != 3:
            raise StartupError(
                "Không kiểm tra được trạng thái cụm PostgreSQL. "
                "Kiểm tra HMS_PG_BIN và HMS_PG_DATA_DIR."
            )

        result = subprocess.run(
            [
                pg_ctl, "-D", str(data_dir),
                "-l", str(data_dir.parent / "hms-postgres.log"),
                "-o", f"-h 127.0.0.1 -p {database_port}",
                "-t", "30", "-w", "start",
            ],
            timeout=35,
            **child_options,
        )
        if result.returncode != 0:
            raise StartupError(
                "Không khởi động được PostgreSQL. "
                "Kiểm tra cổng kết nối và file hms-postgres.log cạnh thư mục dữ liệu."
            )
        print("[OK] Đã khởi động cụm PostgreSQL cục bộ.", flush=True)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise StartupError(
            f"Không chạy được pg_ctl ({type(exc).__name__}). "
            "Kiểm tra PostgreSQL và cấu hình khởi động cục bộ."
        ) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Kiểm tra DB rồi thoát.")
    parser.add_argument("--port", type=port_number, default=8000, help="Cổng API (8000).")
    args = parser.parse_args()
    os.chdir(BACKEND_DIR)

    try:
        from dotenv import load_dotenv
        import psycopg
        from psycopg.conninfo import conninfo_to_dict
    except ImportError:
        print(
            "Thiếu thư viện. Từ backend/, chạy: "
            ".venv/Scripts/python.exe -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    if not (BACKEND_DIR / ".env").is_file():
        print(
            "Chưa có backend/.env. Sao chép .env.example thành .env "
            "và cấu hình DATABASE_URL.",
            file=sys.stderr,
        )
        return 1

    load_dotenv(BACKEND_DIR / ".env", override=False)
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        print("Chưa cấu hình DATABASE_URL trong backend/.env.", file=sys.stderr)
        return 1

    try:
        start_local_postgres(conninfo_to_dict(database_url))
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            connection.read_only = True
            connection.execute("SELECT 1").fetchone()
            tables = connection.execute(
                "SELECT to_regclass('room'), to_regclass('room_type')"
            ).fetchone()
            if not all(tables):
                raise StartupError(
                    "Đã kết nối PostgreSQL nhưng thiếu bảng room hoặc room_type. "
                    "Dựng schema theo docs/backend-week1.md trước khi chạy API."
                )
    except StartupError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except psycopg.Error as exc:
        print(
            f"Không kết nối hoặc đọc được PostgreSQL ({type(exc).__name__}). "
            "Kiểm tra DATABASE_URL, dịch vụ PostgreSQL và quyền truy cập.",
            file=sys.stderr,
        )
        return 1

    print("[OK] Kết nối PostgreSQL; đã tìm thấy room và room_type.", flush=True)
    if args.check:
        return 0

    print(f"API: http://127.0.0.1:{args.port} — nhấn Ctrl+C để dừng.", flush=True)
    try:
        return subprocess.call(
            [
                sys.executable, "-m", "uvicorn", "app.main:app", "--reload",
                "--host", "127.0.0.1", "--port", str(args.port),
            ]
        )
    except KeyboardInterrupt:
        print("\nĐã dừng API.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
