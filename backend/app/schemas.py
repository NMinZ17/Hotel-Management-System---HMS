from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class RoomType(BaseModel):
    room_type_id: int
    name: str | None
    max_guests: int | None
    base_price: Decimal | None


class Room(BaseModel):
    room_id: int
    room_number: str | None
    room_type_id: int
    floor: int | None
    housekeeping_status: str | None
    maintenance_status: str | None
    room_type: RoomType


# ---- Week 2: auth -------------------------------------------------------

Email = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    ),
]


class RegisterRequest(BaseModel):
    email: Email
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=30)


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    user_id: int
    email: str
    roles: list[str]
    guest_id: int | None
    full_name: str | None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ---- Week 2: availability and reservations ---------------------------------


class AvailabilityItem(BaseModel):
    room_type: RoomType
    available_rooms: int
    nights: int
    nightly_price: Decimal | None
    total_price: Decimal | None


class ReservationRequest(BaseModel):
    room_type_id: int = Field(gt=0, le=9223372036854775807)
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)
    note: str | None = Field(default=None, max_length=200)


class ReservationRoomOut(BaseModel):
    reservation_room_id: int
    room_id: int
    room_number: str | None
    room_type: RoomType
    check_in_date: date
    check_out_date: date
    nights: int
    adults: int
    children: int
    nightly_price: Decimal
    line_total: Decimal
    is_cancelled: bool


class ReservationOut(BaseModel):
    reservation_id: int
    status: str
    created_at: datetime | None
    cancelled_at: datetime | None
    note: str | None
    rooms: list[ReservationRoomOut]
    total_price: Decimal
