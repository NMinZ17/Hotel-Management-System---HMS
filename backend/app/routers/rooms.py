from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.db import get_db
from app.schemas import Room

router = APIRouter(prefix="/api", tags=["rooms"])

ROOMS_SQL = """
    SELECT r.room_id, r.room_number, r.room_type_id, r.floor,
           r.housekeeping_status, r.maintenance_status,
           rt.name, rt.max_guests, rt.base_price
    FROM room AS r
    JOIN room_type AS rt ON rt.room_type_id = r.room_type_id
    WHERE r.is_active = %(is_active)s
      AND rt.is_active = %(is_active)s
      AND (%(room_type_id)s::bigint IS NULL
           OR r.room_type_id = %(room_type_id)s)
    ORDER BY r.room_number, r.room_id
    LIMIT %(limit)s OFFSET %(offset)s
"""


@router.get(
    "/rooms",
    response_model=list[Room],
    summary="Danh sách phòng từ PostgreSQL",
    responses={503: {"description": "Chưa cấu hình hoặc không đọc được PostgreSQL"}},
)
def list_rooms(
    request: Request,
    room_type_id: Annotated[
        int | None, Query(gt=0, le=9223372036854775807)
    ] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0, le=9223372036854775807)] = 0,
) -> list[Room]:
    with get_db(request) as connection:
        rows = connection.execute(
            ROOMS_SQL,
            {
                "is_active": True,
                "room_type_id": room_type_id,
                "limit": limit,
                "offset": offset,
            },
        ).fetchall()
    return [
        Room(
            room_id=row["room_id"],
            room_number=row["room_number"],
            room_type_id=row["room_type_id"],
            floor=row["floor"],
            housekeeping_status=row["housekeeping_status"],
            maintenance_status=row["maintenance_status"],
            room_type={
                "room_type_id": row["room_type_id"],
                "name": row["name"],
                "max_guests": row["max_guests"],
                "base_price": row["base_price"],
            },
        )
        for row in rows
    ]
