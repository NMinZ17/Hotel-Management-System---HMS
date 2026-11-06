# Hợp đồng tích hợp ban đầu

Trạng thái: đề xuất cho tuần 1, chưa phải API đã triển khai. Minh và Trang chốt tên trường theo ERD, Linh/Thư xác nhận response trước khi code; mọi thay đổi cập nhật tài liệu và Issue liên quan.

| Endpoint dự kiến | Mục đích | Tuần |
| --- | --- | --- |
| GET /api/health | Kiểm tra API hoạt động | 1 |
| GET /api/rooms | Danh sách phòng cho bài ghép ba tầng | 1 |
| POST /api/auth/register, POST /api/auth/login | Tài khoản khách và đăng nhập | 2 |
| GET /api/availability | Tìm phòng theo loại/ngày/số khách | 2 |
| POST /api/reservations, GET /api/reservations/mine | Đặt và xem đơn của mình | 2 |
| POST /api/reservations/{id}/cancel | Hủy có kiểm tra quyền | 2 |
| POST /api/reservations/{id}/check-in | Tạo lượt ở và folio | 3 |
| GET /api/folios/{id}, POST /api/stays/{id}/check-out | Xem phí và chốt lưu trú | 3 |
| POST /api/service-orders và thao tác nhận/hoàn thành | Dịch vụ và ghi phí | 4 |
| /api/housekeeping-tasks, /api/maintenance-tickets | Vận hành có kiểm tra phân công | 4 |
| /api/reports/... | Sáu báo cáo cho admin | 5 |

GET rooms tuần 1 cần trả các trường room_id, room_number, room_type_id, housekeeping_status, maintenance_status; giới hạn dữ liệu công khai phù hợp. Minh chốt response là mảng hay envelope và đưa ví dụ thật vào đây trước khi Linh nối API.

Đặt phòng theo loại và khoảng ngày: khách chọn loại phòng, server chọn và giữ phòng vật lý trong transaction. Giá được chụp tại lúc đặt. Khoảng ngày [check_in, check_out) cho phép nhận ngày khách trước trả. Check-in kiểm tra CLEAN và không BLOCKED; không coi phòng trống là phòng sạch.

Chốt trong tuần 2: payload/response cho đặt một phòng, nâng cấp nhiều phòng/khách, một mã giảm giá; cơ chế đăng nhập; lỗi không tìm thấy/xung đột/ngày sai; công thức tiền và quyền đối tượng. Đây là việc phải làm, chưa được mô tả là đã có.

Lỗi nghiệp vụ dự kiến: 404 không tìm thấy, 409 xung đột, 422 đầu vào sai; xác thực dùng 401/403 phù hợp. Chuẩn hóa body lỗi và test cùng UI. Dữ liệu tiền do backend tính chính xác; UI chỉ hiển thị giá trị đã xác nhận.
