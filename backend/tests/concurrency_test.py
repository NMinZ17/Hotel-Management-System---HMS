# hai khách (id 1 và 2) cùng đặt phòng 101 từ 20 đến 22/12/2026.
from __future__ import annotations

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

engine = create_engine(
    URL.create(
        "postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    ),
    pool_size=5,
)

ROOM_ID = 101
CHECK_IN, CHECK_OUT = "2026-12-20", "2026-12-22"
GUEST_IDS = [1, 2]
P = {"room_id": ROOM_ID, "ci": CHECK_IN, "co": CHECK_OUT}

LOCK_SQL = "SELECT room_id FROM room WHERE room_id = :room_id AND is_active FOR UPDATE"
OVERLAP_SQL = """
    SELECT COUNT(*) FROM reservation_room
    WHERE room_id = :room_id
      AND is_cancelled IS NOT TRUE
      AND check_in_date < :co AND check_out_date > :ci
"""


def reset() -> None:
    """Don sach du lieu demo cua phong 101 (khong dung vao seed)."""
    with engine.begin() as c:
        ids = [r[0] for r in c.execute(
            text("SELECT reservation_id FROM reservation_room WHERE room_id = :r"),
            {"r": ROOM_ID})]
        # booking_events tham chieu reservation nen phai xoa truoc
        c.execute(text("DELETE FROM booking_events "
                       "WHERE room_id = :r AND dataset = 'demo'"), {"r": ROOM_ID})
        # reservation_room, reservation_guest xoa theo ON DELETE CASCADE
        c.execute(text("DELETE FROM reservation "
                       "WHERE reservation_id = ANY(CAST(:ids AS BIGINT[]))"),
                  {"ids": ids})


def book(guest_id: int, barrier: threading.Barrier, use_lock: bool):
    barrier.wait(timeout=5)
    with engine.begin() as c:
        if use_lock:
            if c.execute(text(LOCK_SQL), P).first() is None:
                return guest_id, "NO_ROOM"
        if c.execute(text(OVERLAP_SQL), P).scalar_one() > 0:
            return guest_id, "REJECTED"
        time.sleep(1)  # keo dai khoang giua kiem tra va INSERT de race lo ro

        res_id = c.execute(text("""
            INSERT INTO reservation (booked_by_guest_id, status, created_at)
            VALUES (:g, 'CONFIRMED', CURRENT_TIMESTAMP)
            RETURNING reservation_id"""), {"g": guest_id}).scalar_one()
        rr_id = c.execute(text("""
            INSERT INTO reservation_room
                (reservation_id, room_id, check_in_date, check_out_date,
                 adults, children, nightly_price, is_cancelled)
            VALUES (:res, :room_id, :ci, :co, 2, 0, 800000, FALSE)
            RETURNING reservation_room_id"""),
                          {"res": res_id, **P}).scalar_one()
        c.execute(text("""
            INSERT INTO reservation_guest (reservation_id, guest_id, is_primary)
            VALUES (:res, :g, TRUE)"""), {"res": res_id, "g": guest_id})
        c.execute(text("""
            INSERT INTO booking_events
                (reservation_id, reservation_room_id, guest_id, room_id,
                 event_type, source, dataset)
            VALUES (:res, :rr, :g, :room_id, 'CREATED', 'test', 'demo')"""),
                  {"res": res_id, "rr": rr_id, "g": guest_id, "room_id": ROOM_ID})
        return guest_id, "BOOKED"


def run(use_lock: bool) -> int:
    reset()
    barrier = threading.Barrier(len(GUEST_IDS))
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(book, g, barrier, use_lock) for g in GUEST_IDS]
        results = [f.result() for f in futures]
    with engine.connect() as c:
        active = c.execute(text("""
            SELECT COUNT(*) FROM reservation_room
            WHERE room_id = :room_id AND is_cancelled IS NOT TRUE
              AND check_in_date < :co AND check_out_date > :ci"""), P).scalar_one()
        events = c.execute(text("""
            SELECT COUNT(*) FROM booking_events
            WHERE room_id = :r AND dataset = 'demo'"""), {"r": ROOM_ID}).scalar_one()
    print(f"use_lock={use_lock}: {results} -> dat phong ACTIVE: {active}, "
          f"su kien ghi nhan: {events}")
    return active


if __name__ == "__main__":
    unsafe = run(use_lock=False)
    print("  (khong khoa) loi double booking tai hien duoc:", unsafe == 2)
    safe = run(use_lock=True)
    assert safe == 1, f"Co khoa nhung van co {safe} dat phong"
    print("PASS: chi mot dat phong thanh cong cho phong 101.")
    # Khong reset o cuoi de con du lieu chay truy van xac nhan; chay lai se tu reset.