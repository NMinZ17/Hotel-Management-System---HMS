# mock_backend.py  (chạy: pip install fastapi uvicorn && uvicorn mock_backend:app --reload --port 8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginIn(BaseModel):
    email: str
    password: str

# Tài khoản giả lập – KHÔNG phải bảo mật thật
USERS = {
    "admin@hms.example":  {"password": "admin123", "role": "ADMIN",     "user_id": 1},
    "letan@hms.example":  {"password": "letan123", "role": "RECEPTION", "user_id": 2},
    "khach1@hms.example": {"password": "khach123", "role": "GUEST",     "user_id": 3},
}

@app.post("/api/auth/login")
def login(payload: LoginIn):
    u = USERS.get(payload.email)
    if not u or u["password"] != payload.password:
        raise HTTPException(401, "Sai email hoặc mật khẩu")
    return {
        "access_token": f"mock-token-{u['user_id']}",
        "token_type": "bearer",
        "user": {"user_id": u["user_id"], "email": payload.email, "role": u["role"]},
    }

# Mock luôn GET /api/rooms để RoomsPage hiển thị được
@app.get("/api/rooms")
def rooms():
    return [
        {"room_id": 101, "room_number": "101", "floor": 1,
         "housekeeping_status": "CLEAN", "maintenance_status": "OK",
         "room_type": {"name": "Standard", "base_price": 800000}},
        {"room_id": 102, "room_number": "102", "floor": 1,
         "housekeeping_status": "CLEAN", "maintenance_status": "OK",
         "room_type": {"name": "Standard", "base_price": 800000}},
        {"room_id": 201, "room_number": "201", "floor": 2,
         "housekeeping_status": "CLEAN", "maintenance_status": "OK",
         "room_type": {"name": "Deluxe", "base_price": 1200000}},
        {"room_id": 202, "room_number": "202", "floor": 2,
         "housekeeping_status": "CLEAN", "maintenance_status": "OK",
         "room_type": {"name": "Suite", "base_price": 2500000}},
    ]