# Hợp đồng tích hợp HMS

Backend tuần 1 cung cấp hai endpoint đọc bên dưới. Hướng dẫn chạy ở [backend-week1.md](backend-week1.md), kết quả kiểm tra ở [báo cáo kiểm thử](testing/backend-week1.md).

## Tuần 1: endpoint đọc dữ liệu

Base URL khi phát triển: `http://127.0.0.1:8000`. Các route đã bao gồm tiền tố `/api`.

`GET /` chuyển hướng `307` đến `/docs` để mở Swagger UI.

### GET /api/health

Trả `200 OK` khi tiến trình API xử lý được request:

```json
{"status":"ok","service":"hms-api"}
```

Endpoint này không truy vấn PostgreSQL. Health trả 200 chưa chứng minh kết nối database hoạt động; cần gọi thêm `/api/rooms`.

### GET /api/rooms

Đọc PostgreSQL, chỉ lấy phòng đang hoạt động thuộc loại phòng đang hoạt động. Đây là danh mục phòng tuần 1, chưa phải tìm phòng trống theo ngày và chưa xác nhận phòng có thể đặt. Sắp xếp theo `room_number`, rồi `room_id`.

| Query parameter | Kiểu và giới hạn | Mặc định |
| --- | --- | --- |
| `room_type_id` | Số nguyên từ 1 đến 9223372036854775807; tùy chọn | Không lọc loại phòng |
| `limit` | Số nguyên từ 1 đến 200 | 100 |
| `offset` | Số nguyên từ 0 đến 9223372036854775807 | 0 |

Ví dụ request: `GET /api/rooms?room_type_id=1&limit=20&offset=0`.

Response `200 OK` là **mảng JSON**, không có envelope `data` hoặc `items`. Nếu không có bản ghi phù hợp, trả `[]`. Một phần tử trích từ [response chạy thật với seed Trang](evidence/w01/minh-rooms-response.json):

```json
[
  {
    "room_id": 101,
    "room_number": "101",
    "room_type_id": 1,
    "floor": 1,
    "housekeeping_status": "CLEAN",
    "maintenance_status": "OK",
    "room_type": {
      "room_type_id": 1,
      "name": "Standard",
      "max_guests": 2,
      "base_price": "800000.00"
    }
  }
]
```

`base_price` khi có giá trị là chuỗi thập phân, giữ độ chính xác của PostgreSQL `NUMERIC`. Schema hiện tại cho phép `NULL` ở `room_number`, `floor`, hai trạng thái phòng và `room_type.name`, `max_guests`, `base_price`; API giữ `null` tương ứng, không tự tạo dữ liệu thay thế. `room_id`, `room_type_id` và đối tượng `room_type` luôn có trong mỗi phần tử trả về. Phòng không có loại phòng phù hợp hoặc không có cờ hoạt động `true` bị loại khỏi danh sách.

Frontend định dạng giá để hiển thị; số tiền nghiệp vụ vẫn do backend xác nhận. Giữ nguyên trạng thái từ DB; seed Trang được kiểm tra hiện dùng `maintenance_status="OK"`. Cần nhóm chốt từ vựng trạng thái trước khi mở rộng nghiệp vụ, không tự đổi tên trong frontend. Vệ sinh và bảo trì là hai nhóm trạng thái độc lập.

### Lỗi tuần 1

| HTTP status | Trường hợp | Response |
| --- | --- | --- |
| 422 | Query sai kiểu hoặc ngoài giới hạn, được kiểm tra trước khi mở kết nối DB | Validation chuẩn FastAPI, `detail` là danh sách lỗi |
| 503 | Thiếu cấu hình DB, lỗi kết nối hoặc truy vấn DB | Body cố định bên dưới |

```json
{
  "detail": {
    "code": "DATABASE_UNAVAILABLE",
    "message": "Không thể đọc dữ liệu phòng. Kiểm tra cấu hình và kết nối PostgreSQL."
  }
}
```

Không trả chuỗi kết nối, mật khẩu hoặc lỗi nội bộ PostgreSQL trong response. Không thay lỗi DB bằng mảng mock hoặc mảng rỗng.

### Cấu hình ghép frontend

- Frontend dùng `VITE_API_BASE_URL=http://127.0.0.1:8000/api` nếu client ghép thêm `/rooms`. Thống nhất tên biến giữa cấu hình và mã client, không ghép `/api` hai lần.
- Backend đọc `DATABASE_URL` và `CORS_ORIGINS` từ `backend/.env`. CORS mặc định cho phép `http://localhost:5173` và `http://127.0.0.1:5173`; origin bổ sung ngăn cách bằng dấu phẩy.
- Frontend phân biệt đang tải, lỗi và mảng rỗng. Khi API trả 503 hoặc lỗi mạng, hiển thị lỗi thay vì dữ liệu mock.
- Kiểm tra tích hợp bằng cách thay dữ liệu DB phát triển, gọi lại API rồi tải lại UI; lưu response/SQL/ảnh tương ứng.

Hướng dẫn chạy và request kiểm tra: [backend tuần 1](backend-week1.md).

## Tuần 2: xác thực, tìm phòng và đặt / hủy

Cần `AUTH_SECRET` trong `backend/.env` (xem `.env.example`). Lỗi nghiệp vụ luôn có dạng `{"detail": {"code": "...", "message": "..."}}`. Mọi route ghi dữ liệu chạy trong một transaction; lỗi DB trả `503 DATABASE_UNAVAILABLE`, không bao giờ trả 2xx.

Token: gửi header `Authorization: Bearer <access_token>`. Vai trò theo seed: `ADMIN`, `RECEPTION` (nhân viên), `GUEST`. Mật khẩu băm scrypt; tài khoản seed dùng `demo_hash` không đăng nhập được cho tới khi đặt lại mật khẩu thật.

| Endpoint | Quyền | Kết quả |
| --- | --- | --- |
| `POST /api/auth/register` `{email, password≥8, full_name, phone}` | Công khai | 201 `UserOut`; 409 `EMAIL_TAKEN`; 422 thiếu/sai trường (kể cả thiếu `phone`) |
| `POST /api/auth/login` `{email, password}` | Công khai | 200 `{access_token, token_type, expires_in, user}`; 401 sai thông tin; 503 `AUTH_NOT_CONFIGURED` |
| `GET /api/auth/me` | Đã đăng nhập | 200 `UserOut`; 401 |
| `GET /api/availability?check_in&check_out&guests=1&room_type_id?` | Công khai | 200 mảng `{room_type, available_rooms, nights, nightly_price, total_price}`; 422 `INVALID_DATES` |
| `POST /api/reservations` (1 phòng: `{room_type_id, check_in, check_out, adults, children=0, ...}` hoặc nhiều phòng: `{rooms: [...], companion_guest_ids?, discount_code?, note?}`) | GUEST | 201 `ReservationOut`; 404 `ROOM_TYPE_NOT_FOUND`/`GUEST_NOT_FOUND`/`DISCOUNT_NOT_FOUND`; 409 `NO_ROOM_AVAILABLE`; 422 `INVALID_DATES`/`INVALID_GUESTS`/`INVALID_DISCOUNT`; 403 tài khoản nhân viên |
| `GET /api/reservations/mine` | GUEST | 200 mảng `ReservationOut` |
| `GET /api/reservations/{id}` | Chủ đơn hoặc nhân viên | 200; 404 `RESERVATION_NOT_FOUND` (kể cả đơn của người khác) |
| `POST /api/reservations/{id}/cancel` | Chủ đơn hoặc nhân viên | 200 `ReservationOut`; hủy lặp trả lại đơn đã hủy, không đổi `cancelled_at`; 409 nếu đã check-in |

Quy tắc: khoảng ngày `[check_in, check_out)`, không ở quá khứ (giờ UTC+7), tối đa 30 đêm; `adults ≥ 1` và `adults + children ≤ max_guests`. Server khóa phòng ứng viên theo thứ tự `room_id` tăng dần (tránh deadlock khi đặt nhiều phòng) và chọn phòng vật lý còn trống nguyên tử — thiếu bất kỳ dòng phòng nào sẽ rollback toàn bộ đơn (`409`). Giá đêm được chụp vào `reservation_room.nightly_price`; `line_total = nightly_price × nights`, `subtotal` cộng các dòng chưa hủy, `total_price = subtotal − discount_amount`. Hủy cập nhật `reservation.status = CANCELLED`, `cancelled_at` và `reservation_room.is_cancelled`, giữ nguyên lịch sử và ghi `audit_event`. Tiền là chuỗi thập phân.

## Tuần 3: check-in, folio, hóa đơn, thanh toán và check-out

Các thao tác nghiệp vụ ghi nhận yêu cầu tài khoản nhân viên (`ADMIN` hoặc `RECEPTION`) có bản ghi `employee` đang hoạt động (`employee_id` được trả thêm trong `UserOut`); khách chỉ được đọc `stay`, `folio`, `invoice` thuộc đơn của chính mình (đơn người khác trả `404`).

| Endpoint | Quyền | Kết quả |
| --- | --- | --- |
| `POST /api/reservations/{id}/check-in` | Nhân viên | 200 `StayOut` (gồm `folio_id`, danh sách `rooms`); lặp trên đơn đang `IN_HOUSE` trả lại lượt ở cũ; 409 `ROOM_NOT_CLEAN` / `ROOM_MAINTENANCE_BLOCKED` / `ROOM_OCCUPIED` / `RESERVATION_NOT_CHECKINABLE` / `ALREADY_CHECKED_OUT` |
| `GET /api/stays/{id}` | Nhân viên hoặc chủ đơn | 200 `StayOut`; 404 `STAY_NOT_FOUND` |
| `GET /api/folios/{id}` | Nhân viên hoặc chủ đơn | 200 `FolioOut` (danh sách `items`, `subtotal`, `discount_total`, `tax_amount`, `gross_total`, `paid_total`, `balance_due`, `invoice`); 404 `FOLIO_NOT_FOUND` |
| `POST /api/folios/{id}/invoices` | Nhân viên | 200 `InvoiceOut` (mã `INV-YYYYMM-NNNN`, gọi lặp trả lại hóa đơn hiện hành, tự cập nhật khi folio `OPEN` có thêm phí mới); 404 `FOLIO_NOT_FOUND`; 409 `FOLIO_VOID` / `INVOICE_OVERPAID` |
| `GET /api/invoices/{id}` | Nhân viên hoặc chủ đơn | 200 `InvoiceOut` kèm `payments`; 404 `INVOICE_NOT_FOUND` |
| `POST /api/invoices/{id}/payments` `{amount>0, method: "CASH"\|"TRANSFER", transaction_ref?}` | Nhân viên | 200 `{payment, invoice, idempotent_replay}`; lặp cùng `transaction_ref` + `invoice_id` + `amount` + `method` trả lại giao dịch cũ (`idempotent_replay=true`); 409 `OVERPAYMENT` / `INVOICE_ALREADY_PAID` / `DUPLICATE_TRANSACTION_REF` / `INVOICE_VOID` |
| `POST /api/stays/{id}/check-out` | Nhân viên | 200 `StayOut` (gồm `housekeeping_task_ids`); đóng `folio` (`CLOSED`), cập nhật `stay` & `reservation` (`CHECKED_OUT`), chuyển phòng `housekeeping_status=DIRTY` (giữ nguyên `maintenance_status`), tạo `housekeeping_task` `PENDING`; gọi lặp trả lại lượt ở đã chốt; 409 `PAYMENT_REQUIRED` / `INVOICE_STALE` / `OPEN_SERVICE_ORDERS` |

Công thức tài chính (khớp `database/seeds/06_financial_fixture.sql` và ràng buộc `V002`):
- Tiền phòng khi check-in ghi `folio_item` (`entry_type='CHARGE'`, `quantity=nights`, `unit_price=nightly_price`, `source_key='ROOM:<reservation_room_id>:<check_in_date>'`).
- Mã giảm giá của đơn ghi `folio_item` (`entry_type='DISCOUNT'`, `quantity=1`, `unit_price=-discount_amount <= 0`, `source_key='DISC:<reservation_id>:<discount_id>'`), tính lại theo tổng `CHARGE` (`PERCENT` hoặc `FIXED`, không vượt `subtotal`).
- `net = subtotal - discount_total`; `tax_amount = 8% × net` (làm tròn `ROUND_HALF_UP` đến 2 chữ số thập phân, hoặc lấy tổng các dòng `TAX` tường minh nếu có); `gross_total = net + tax_amount`; `balance_due = gross_total - paid_total`.
- Kiểm tra phòng trước check-in: `housekeeping_status IN ('CLEAN', 'INSPECTED')` và `maintenance_status = 'OK'` (chặn `DIRTY`, `OUT_OF_SERVICE`, `MINOR_ISSUE`, `OUT_OF_ORDER`, `BLOCKED`).

## Endpoint dự kiến cho các tuần sau

Các route dưới đây vẫn là kế hoạch.

| Endpoint dự kiến | Mục đích | Tuần |
| --- | --- | --- |
| POST /api/service-orders và thao tác nhận/hoàn thành | Dịch vụ và ghi phí | 4 |
| /api/housekeeping-tasks, /api/maintenance-tickets | Vận hành có kiểm tra phân công | 4 |
| /api/reports/... | Sáu báo cáo cho admin | 5 |

Đặt phòng theo loại và khoảng ngày: khách chọn loại phòng, server chọn và giữ phòng vật lý trong transaction. Giá được chụp tại lúc đặt. Khoảng ngày [check_in, check_out) cho phép nhận ngày khách trước trả. Check-in kiểm tra CLEAN và không BLOCKED; không coi phòng trống là phòng sạch.

Chốt trong tuần 2: payload/response cho đặt một phòng, nâng cấp nhiều phòng/khách, một mã giảm giá; cơ chế đăng nhập; lỗi không tìm thấy/xung đột/ngày sai; công thức tiền và quyền đối tượng. Đây là việc phải làm, chưa được mô tả là đã có.

Lỗi nghiệp vụ dự kiến: 404 không tìm thấy, 409 xung đột, 422 đầu vào sai; xác thực dùng 401/403 phù hợp. Chuẩn hóa body lỗi và test cùng UI. Dữ liệu tiền do backend tính chính xác; UI chỉ hiển thị giá trị đã xác nhận.

