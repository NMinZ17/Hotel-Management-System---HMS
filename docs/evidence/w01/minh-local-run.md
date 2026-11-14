# Kiểm tra chạy trực tiếp trên máy Minh

Ngày: 14/11/2026. Phạm vi: sửa lỗi `503 DATABASE_UNAVAILABLE` trên API người dùng đang chạy ở `127.0.0.1:8000`.

- Nguyên nhân kiểm tra được: `backend/.env` chưa tồn tại; cluster PostgreSQL riêng của workspace đã dừng sau lượt kiểm thử trước.
- Đã khởi động cluster riêng tại `tmp/hms-w01-pgdata`, chỉ lắng nghe `127.0.0.1:55441`.
- Đã tạo database phát triển mới `hms_dev`, nạp schema/seed nguyên bản của Trang vào database rỗng: 28 bảng, 4 phòng.
- Đã tạo `backend/.env` local, không đưa vào gói mã nguồn.
- Đã để tiến trình Uvicorn đang chạy với `--reload` nạp lại ứng dụng sau khi cấu hình được tạo.

Kết quả gọi HTTP thật tới chính API cổng 8000 sau khi sửa:

```json
{"health": 200, "rooms_status": 200, "room_numbers": ["101", "102", "201", "202"]}
```

PostgreSQL được giữ chạy cho việc thử trong trình duyệt. Chưa xác nhận ghép React thật hoặc Trang chạy lại trên máy khác; đây là kiểm tra backend/API local.
