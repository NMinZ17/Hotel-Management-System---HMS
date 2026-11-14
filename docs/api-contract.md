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

## Endpoint dự kiến cho tuần sau

Các route dưới đây vẫn là kế hoạch, chưa được triển khai trong bản backend tuần 1.

| Endpoint dự kiến | Mục đích | Tuần |
| --- | --- | --- |
| POST /api/auth/register, POST /api/auth/login | Tài khoản khách và đăng nhập | 2 |
| GET /api/availability | Tìm phòng theo loại/ngày/số khách | 2 |
| POST /api/reservations, GET /api/reservations/mine | Đặt và xem đơn của mình | 2 |
| POST /api/reservations/{id}/cancel | Hủy có kiểm tra quyền | 2 |
| POST /api/reservations/{id}/check-in | Tạo lượt ở và folio | 3 |
| GET /api/folios/{id}, POST /api/stays/{id}/check-out | Xem phí và chốt lưu trú | 3 |
| POST /api/service-orders và thao tác nhận/hoàn thành | Dịch vụ và ghi phí | 4 |
| /api/housekeeping-tasks, /api/maintenance-tickets | Vận hành có kiểm tra phân công | 4 |
| /api/reports/... | Sáu báo cáo cho admin | 5 |

Đặt phòng theo loại và khoảng ngày: khách chọn loại phòng, server chọn và giữ phòng vật lý trong transaction. Giá được chụp tại lúc đặt. Khoảng ngày [check_in, check_out) cho phép nhận ngày khách trước trả. Check-in kiểm tra CLEAN và không BLOCKED; không coi phòng trống là phòng sạch.

Chốt trong tuần 2: payload/response cho đặt một phòng, nâng cấp nhiều phòng/khách, một mã giảm giá; cơ chế đăng nhập; lỗi không tìm thấy/xung đột/ngày sai; công thức tiền và quyền đối tượng. Đây là việc phải làm, chưa được mô tả là đã có.

Lỗi nghiệp vụ dự kiến: 404 không tìm thấy, 409 xung đột, 422 đầu vào sai; xác thực dùng 401/403 phù hợp. Chuẩn hóa body lỗi và test cùng UI. Dữ liệu tiền do backend tính chính xác; UI chỉ hiển thị giá trị đã xác nhận.

