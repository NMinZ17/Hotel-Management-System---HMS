from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints, model_validator


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


# guest.phone and guest.full_name are NOT NULL in Trang's migration V001, so the
# API requires them and rejects blanks with 422 before any database work.
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Phone = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=8,
        max_length=30,
        pattern=r"^\+?[0-9][0-9 .()-]*[0-9]$",
    ),
]


class RegisterRequest(BaseModel):
    email: Email
    password: str = Field(min_length=8, max_length=128)
    full_name: FullName
    phone: Phone


class LoginRequest(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    user_id: int
    email: str
    roles: list[str]
    guest_id: int | None
    employee_id: int | None = None
    full_name: str | None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


# ---- Week 2 & 3: availability and reservations (single + multi-room) ----


class AvailabilityItem(BaseModel):
    room_type: RoomType
    available_rooms: int
    nights: int
    nightly_price: Decimal | None
    total_price: Decimal | None


class ReservationRoomRequest(BaseModel):
    room_type_id: int = Field(gt=0, le=9223372036854775807)
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)


class ReservationRequest(BaseModel):
    """Accepts either the Week 2 single-room payload or Week 3 multi-room `rooms`."""

    room_type_id: int | None = Field(default=None, gt=0, le=9223372036854775807)
    check_in: date | None = None
    check_out: date | None = None
    adults: int | None = Field(default=None, ge=1, le=20)
    children: int = Field(default=0, ge=0, le=20)
    rooms: list[ReservationRoomRequest] | None = Field(default=None, min_length=1, max_length=20)
    companion_guest_ids: list[int] = Field(default_factory=list, max_length=20)
    discount_code: str | None = Field(default=None, max_length=30)
    note: str | None = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def _validate_shape(self) -> "ReservationRequest":
        single_fields = (self.room_type_id, self.check_in, self.check_out, self.adults)
        if self.rooms is not None:
            if any(v is not None for v in single_fields):
                raise ValueError("Không truyền đồng thời `rooms` và các trường đặt 1 phòng.")
        else:
            if any(v is None for v in single_fields):
                raise ValueError(
                    "Cần truyền `rooms` hoặc đủ `room_type_id`, `check_in`, `check_out`, `adults`."
                )
        for gid in self.companion_guest_ids:
            if gid <= 0 or gid > 9223372036854775807:
                raise ValueError("Mã khách đi cùng không hợp lệ.")
        return self

    def normalized_rooms(self) -> list[ReservationRoomRequest]:
        if self.rooms is not None:
            return self.rooms
        return [
            ReservationRoomRequest(
                room_type_id=self.room_type_id,
                check_in=self.check_in,
                check_out=self.check_out,
                adults=self.adults,
                children=self.children,
            )
        ]


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
    subtotal: Decimal = Decimal("0.00")
    discount_code: str | None = None
    discount_amount: Decimal = Decimal("0.00")
    total_price: Decimal


# ---- Week 3: stays, folios, invoices and payments -----------------------


class StayRoomOut(BaseModel):
    stay_room_id: int
    reservation_room_id: int | None
    room_id: int
    room_number: str | None
    housekeeping_status: str | None
    maintenance_status: str | None
    assigned_from: datetime
    assigned_to: datetime | None


class StayOut(BaseModel):
    stay_id: int
    reservation_id: int
    checked_in_by: int | None
    checked_out_by: int | None
    actual_check_in: datetime
    actual_check_out: datetime | None
    status: str
    folio_id: int | None
    rooms: list[StayRoomOut]
    housekeeping_task_ids: list[int] = Field(default_factory=list)


class FolioItemOut(BaseModel):
    folio_item_id: int
    entry_type: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    source_key: str | None
    occurred_at: datetime | None


class PaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    method: Literal["CASH", "TRANSFER"]
    transaction_ref: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def _clean_ref(self) -> "PaymentRequest":
        if self.transaction_ref is not None:
            cleaned = self.transaction_ref.strip()
            self.transaction_ref = cleaned or None
        return self


class PaymentOut(BaseModel):
    payment_id: int
    invoice_id: int
    recorded_by: int | None
    amount: Decimal
    method: str
    transaction_ref: str | None
    paid_at: datetime | None


class InvoiceOut(BaseModel):
    invoice_id: int
    folio_id: int
    invoice_number: str
    subtotal: Decimal
    discount_total: Decimal
    tax_amount: Decimal
    gross_total: Decimal
    paid_total: Decimal
    balance_due: Decimal
    issued_at: datetime | None
    status: str
    payments: list[PaymentOut]


class FolioOut(BaseModel):
    folio_id: int
    stay_id: int
    reservation_id: int
    status: str
    opened_at: datetime | None
    closed_at: datetime | None
    items: list[FolioItemOut]
    subtotal: Decimal
    discount_total: Decimal
    tax_amount: Decimal
    gross_total: Decimal
    paid_total: Decimal
    balance_due: Decimal
    invoice: InvoiceOut | None


class PaymentResultOut(BaseModel):
    payment: PaymentOut
    invoice: InvoiceOut
    idempotent_replay: bool = False
