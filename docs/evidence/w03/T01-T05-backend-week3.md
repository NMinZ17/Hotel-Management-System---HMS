# Minh chứng kiểm thử Backend Tuần 3 (T01–T05, đa phòng & vòng đời tài chính)

```text
Mã test / Issue: HMS-W3-MINH / Issue #10 (kèm T01, T02, T03, T04, T05, đa phòng & tài chính)
Ngày chạy: 28/11/2026
Người chạy và người kiểm tra: Nguyễn Nhật Minh (tự kiểm tra; chờ maitrang1112 review)
Commit / nhánh: Minh-Nhật (chưa push, chờ review trước khi đẩy lên remote)
Python, PostgreSQL, OS và môi trường: Python 3.14.8 (.venv), PostgreSQL 18.6 (Windows 11, 127.0.0.1:55441/hms_dev)
Dữ liệu/fixture và bước chuẩn bị:
  - Migration thật của Trang: database/migrations/V001__init_hms_schema.sql + V002__hardening_constraints.sql (từ origin/trang/checkpoint_1), chạy trong schema ngẫu nhiên riêng biệt rồi xóa sạch sau mỗi ca.
  - Chạy thêm xác nhận fallback trên database/schema.sql (13/13 OK).
Request hoặc lệnh:
  .\.venv\Scripts\python.exe -W ignore -m unittest tests.test_week1_api tests.test_week2_api tests.test_week3_api -v
Kết quả kỳ vọng: 48/48 test đạt, khớp bảng tính tay 06_financial_fixture.sql, rollback sạch khi lỗi transaction, không sinh trùng khi gọi lặp.
Kết quả thực tế: Ran 48 tests in 50.332s — OK (xem log đầy đủ tại minh-backend-tests.txt).
SQL xác nhận trạng thái cuối: Kiểm tra trực tiếp trong từng ca test (COUNT(*) trên reservation, reservation_room, stay, stay_room, folio, folio_item, invoice, payment, housekeeping_task, audit_event và trạng thái room).
Kết luận: Đạt (phần backend; phần ghép giao diện đặt/check-in/out với frontend thực hiện cùng Linh).
PR/ảnh/log và lỗi còn mở: docs/evidence/w03/minh-backend-tests.txt
```

## Ánh xạ các ca T01–T05 và tiêu chí Tuần 3

| Mã / Tiêu chí | Ca kiểm thử đã chạy thật | Kết quả |
| --- | --- | --- |
| **T01** (2+ kết nối tranh phòng cuối cùng ngày) | `test_concurrent_bookings_never_overbook` (6 luồng tranh 1 phòng Deluxe: đúng 1 mã `201`, 5 mã `409`, DB đúng 1 dòng); `test_concurrent_multi_room_bookings_no_deadlock_no_overbook` (4 luồng đặt nhiều phòng ngược thứ tự `[1,2]` vs `[2,1]`: đúng 1 mã `201`, 3 mã `409`, không deadlock) | **Đạt** |
| **T02** (Ngày liền kề `[check_in, check_out)`) | `test_sequential_double_booking_is_rejected` (đặt tiếp `[co, co+2)` được chấp nhận `201`) | **Đạt** |
| **T03** (Ngày sai bị từ chối, không ghi DB) | `test_invalid_input_is_rejected_without_writes` (`co <= ci`, ngày quá khứ, vượt quá `max_guests`: trả `422`, `COUNT(reservation) = 0`) | **Đạt** |
| **T04** (Lỗi giữa transaction rollback sạch) | `test_failed_transaction_does_not_report_success_or_write` (đặt phòng), `test_checkin_failure_rolls_back_all_tables` (lỗi trigger ở `audit_event`: `stay`/`stay_room`/`folio`/`folio_item` = 0, `reservation` vẫn `CONFIRMED`), `test_checkout_failure_rolls_back_stay_folio_and_room` (lỗi trigger ở `housekeeping_task`: `stay` vẫn `IN_HOUSE`, `folio` vẫn `OPEN`, phòng vẫn `CLEAN`) | **Đạt** |
| **T05** (Hủy lặp không sai trạng thái, đặt lại được) | `test_cancel_updates_head_and_lines_and_is_idempotent` (`cancelled_at` giữ nguyên, chỉ 1 audit, phòng đặt lại được) | **Đạt** |
| **Khớp fixture tài chính `06_financial_fixture.sql`** | `test_full_lifecycle_matches_financial_fixture_and_idempotency`: 2 phòng (Standard 101 + Deluxe 201, 3 đêm) + 2 dịch vụ (`100.000` + `240.000`) + mã `WELCOME10` (10%) → `subtotal = 6.340.000,00`, `discount_total = 634.000,00`, `tax_amount (8%) = 456.480,00`, `gross_total = 6.162.480,00`; trả 2 đợt (`3.000.000` CASH + `3.162.480` TRANSFER) → check-out đóng folio, phòng thành `DIRTY` (giữ `maintenance_status = OK`), tạo 2 `housekeeping_task` `PENDING` | **Đạt** |
| **Thao tác lặp & kiểm soát quá trả** | Check-in lặp, xuất hóa đơn lặp, thanh toán lặp cùng `transaction_ref`, check-out lặp đều không tạo bản ghi trùng; trả vượt `balance_due` trả `409 OVERPAYMENT`; còn `service_order` `IN_PROGRESS` trả `409 OPEN_SERVICE_ORDERS` | **Đạt** |
| **Đơn nhiều phòng nguyên tử** | `test_multi_room_booking_is_atomic_when_one_room_unavailable`: thiếu 1 phòng trong đơn 3 phòng trả `409 NO_ROOM_AVAILABLE`, 0 dòng ghi vào DB | **Đạt** |
| **Quyền API & vệ sinh log** | `test_rbac_guest_cannot_operate_and_cannot_read_other_guest_folio`, `test_logs_never_leak_database_url_or_password` | **Đạt** |
