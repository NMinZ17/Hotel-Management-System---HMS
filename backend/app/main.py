from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

# Khởi tạo ứng dụng FastAPI (thay cho file kết nối DB thực tế của bạn)
from app.database import engine 

app = FastAPI(
    title="HMS Hotel API",
    version="0.4.0",
    description="API dat phong hoan chinh voi Row Locking va Transaction"
)

# Schema dữ liệu gửi lên từ Client
class BookingRequest(BaseModel):
    user_id: int
    room_id: int

@app.post("/api/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingRequest):
    # 1. Khóa dòng phòng trong bảng room
    lock_room_sql = """
        SELECT r.room_id, rt.max_guests 
        FROM room r
        JOIN room_type rt ON r.room_type_id = rt.room_type_id
        WHERE r.room_id = :room_id 
        FOR UPDATE
    """
    
    # 2. Đếm số đợt đặt phòng đang active của phòng này
    count_booking_sql = """
        SELECT COUNT(*) 
        FROM reservation_room 
        WHERE room_id = :room_id AND is_cancelled = FALSE
    """
    
    # 3. Thêm đơn đặt phòng mới
    insert_reservation_sql = """
        INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at) 
        VALUES (:reservation_id, :user_id, 'CONFIRMED', CURRENT_TIMESTAMP)
    """
    
    insert_reservation_room_sql = """
        INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, is_cancelled) 
        VALUES (:res_room_id, :reservation_id, :room_id, FALSE)
    """
    
    # 4. Ghi log lịch sử thao tác
    insert_event_sql = """
        INSERT INTO audit_event (event_id, actor_user_id, action, occurred_at) 
        VALUES (:event_id, :user_id, 'BOOKING_CREATED', CURRENT_TIMESTAMP)
    """

    try:
        with engine.begin() as connection:
            # 2.1. Khóa tài nguyên phòng (Row Lock)
            room = connection.execute(
                text(lock_room_sql), {"room_id": payload.room_id}
            ).mappings().first()
            
            if not room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Khong tim thay phong"
                )

            # 2.2. Đếm số suất đã đặt
            booked_count = connection.execute(
                text(count_booking_sql), {"room_id": payload.room_id}
            ).scalar_one()

            # 2.3. Kiểm tra sức chứa
            if int(booked_count) >= int(room["max_guests"]):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Phong da duoc dat het cho"
                )

            # Tạo ID ngẫu nhiên hoặc dùng Sequence/Identity
            import time
            res_id = int(time.time() * 1000)
            res_room_id = res_id + 1
            event_id = res_id + 2

            # 2.4. Thực thi các lệnh INSERT trong cùng 1 Transaction
            connection.execute(
                text(insert_reservation_sql), 
                {"reservation_id": res_id, "user_id": payload.user_id}
            )
            connection.execute(
                text(insert_reservation_room_sql), 
                {"res_room_id": res_room_id, "reservation_id": res_id, "room_id": payload.room_id}
            )
            connection.execute(
                text(insert_event_sql), 
                {"event_id": event_id, "user_id": payload.user_id}
            )

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Xung dot du lieu giao dich"
        ) from exc

    return {"message": "Dat phong thanh cong", "room_id": payload.room_id}