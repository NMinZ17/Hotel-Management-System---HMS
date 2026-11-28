from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.db import get_db, get_tx
from app.deps import CurrentUser, current_user, require_guest
from app.schemas import AvailabilityItem, ReservationOut, ReservationRequest
from app.services import booking

router = APIRouter(prefix="/api", tags=["reservations"])


@router.get(
    "/availability",
    response_model=list[AvailabilityItem],
    summary="Tìm loại phòng còn trống theo ngày và số khách",
)
def availability(
    request: Request,
    check_in: date,
    check_out: date,
    guests: Annotated[int, Query(ge=1, le=40)] = 1,
    room_type_id: Annotated[int | None, Query(gt=0, le=9223372036854775807)] = None,
):
    booking.validate_stay(check_in, check_out)  # reject bad dates before opening a DB connection
    with get_db(request) as connection:
        return booking.search_availability(connection, check_in, check_out, guests, room_type_id)


@router.post(
    "/reservations",
    response_model=ReservationOut,
    status_code=201,
    summary="Đặt một phòng theo loại phòng; server chọn phòng vật lý",
)
def create_reservation(
    body: ReservationRequest, request: Request, user: CurrentUser = Depends(require_guest)
):
    with get_tx(request) as connection:
        return booking.create_reservation(connection, user, body)


@router.get(
    "/reservations/mine",
    response_model=list[ReservationOut],
    summary="Đơn đặt phòng của tôi",
)
def my_reservations(request: Request, user: CurrentUser = Depends(require_guest)):
    with get_db(request) as connection:
        return booking.list_my_reservations(connection, user)


@router.get(
    "/reservations/{reservation_id}",
    response_model=ReservationOut,
    summary="Chi tiết một đơn (chủ đơn hoặc nhân viên)",
)
def reservation_detail(
    reservation_id: int,
    request: Request,
    user: CurrentUser = Depends(current_user),
):
    with get_db(request) as connection:
        return booking.get_reservation(connection, reservation_id, user)


@router.post(
    "/reservations/{reservation_id}/cancel",
    response_model=ReservationOut,
    summary="Hủy đơn của mình; hủy lặp trả lại trạng thái đã hủy",
)
def cancel_reservation(
    reservation_id: int, request: Request, user: CurrentUser = Depends(current_user)
):
    with get_tx(request) as connection:
        return booking.cancel_reservation(connection, reservation_id, user)
