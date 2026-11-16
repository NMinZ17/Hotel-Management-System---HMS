from decimal import Decimal

from pydantic import BaseModel


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
