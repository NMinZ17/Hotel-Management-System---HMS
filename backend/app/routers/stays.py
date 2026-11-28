from fastapi import APIRouter, Depends, Request

from app.db import get_db, get_tx
from app.deps import CurrentUser, current_user, require_staff
from app.schemas import FolioOut, InvoiceOut, PaymentRequest, PaymentResultOut, StayOut
from app.services import billing, stays

router = APIRouter(prefix="/api", tags=["stays-billing"])


@router.post(
    "/reservations/{reservation_id}/check-in",
    response_model=StayOut,
    summary="Check-in đơn đặt phòng (tạo stay, stay_room, folio và tiền phòng)",
)
def check_in_reservation(
    reservation_id: int,
    request: Request,
    user: CurrentUser = Depends(require_staff),
):
    with get_tx(request) as connection:
        return stays.check_in(connection, reservation_id, user)


@router.get(
    "/stays/{stay_id}",
    response_model=StayOut,
    summary="Xem chi tiết lượt lưu trú (nhân viên hoặc khách chủ đơn)",
)
def stay_detail(
    stay_id: int,
    request: Request,
    user: CurrentUser = Depends(current_user),
):
    with get_db(request) as connection:
        return stays.get_stay(connection, stay_id, user)


@router.post(
    "/stays/{stay_id}/check-out",
    response_model=StayOut,
    summary="Check-out lượt lưu trú (chốt folio, chuyển phòng DIRTY, tạo task dọn)",
)
def check_out_stay(
    stay_id: int,
    request: Request,
    user: CurrentUser = Depends(require_staff),
):
    with get_tx(request) as connection:
        return stays.check_out(connection, stay_id, user)


@router.get(
    "/folios/{folio_id}",
    response_model=FolioOut,
    summary="Xem folio và bảng tính tiền chi tiết",
)
def folio_detail(
    folio_id: int,
    request: Request,
    user: CurrentUser = Depends(current_user),
):
    with get_db(request) as connection:
        return billing.get_folio(connection, folio_id, user)


@router.post(
    "/folios/{folio_id}/invoices",
    response_model=InvoiceOut,
    summary="Xuất (hoặc cập nhật) hóa đơn từ folio",
)
def issue_folio_invoice(
    folio_id: int,
    request: Request,
    user: CurrentUser = Depends(require_staff),
):
    with get_tx(request) as connection:
        return billing.issue_invoice(connection, folio_id, user)


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceOut,
    summary="Xem hóa đơn và lịch sử thanh toán",
)
def invoice_detail(
    invoice_id: int,
    request: Request,
    user: CurrentUser = Depends(current_user),
):
    with get_db(request) as connection:
        return billing.get_invoice(connection, invoice_id, user)


@router.post(
    "/invoices/{invoice_id}/payments",
    response_model=PaymentResultOut,
    summary="Ghi nhận thanh toán tiền mặt hoặc chuyển khoản",
)
def pay_invoice(
    invoice_id: int,
    body: PaymentRequest,
    request: Request,
    user: CurrentUser = Depends(require_staff),
):
    with get_tx(request) as connection:
        return billing.record_payment(connection, invoice_id, user, body)
