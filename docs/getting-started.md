# Bắt đầu với HMS

## Chuẩn bị công cụ

Cài Git, Python 3.14 và PostgreSQL. Backend được kiểm tra với Python 3.14.8 và PostgreSQL 18.6. Người làm frontend cần thêm Node.js/npm theo cấu hình ứng dụng của Linh.

```powershell
git --version
py -3.14 --version
psql --version
```

Nếu terminal không nhận lệnh, kiểm tra cài đặt và PATH trước khi tiếp tục. Clone repository theo [quy trình GitHub](github-workflow.md), rồi mở terminal tại thư mục có `README.md`, `backend/`, `database/` và `docs/`.

## Chạy backend và database

Làm một lần theo [thiết lập backend](backend-week1.md#thiết-lập-lần-đầu): tạo `.venv`, cài dependency, tạo database từ `database/schema.sql` và `database/seed.sql`, điền `backend/.env`.

Mỗi lần dùng dự án, từ gốc repository chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backend\scripts\start.ps1
```

Giữ terminal mở và kiểm tra ở terminal thứ hai:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod 'http://127.0.0.1:8000/api/rooms' | ConvertTo-Json -Depth 5
```

Health trả trạng thái tiến trình; rooms trả dữ liệu PostgreSQL. Xem API và thử query tại [Swagger UI](http://127.0.0.1:8000/docs). Hướng dẫn xử lý lỗi 503 nằm trong [runbook backend](backend-week1.md#xử-lý-lỗi).

## Phối hợp tuần 1

- Trang quản lý schema/seed; nguồn SQL được ghi trong [database/README.md](../database/README.md).
- Minh quản lý backend; cấu trúc response và CORS ở [hợp đồng API](api-contract.md).
- Linh và Thư dùng chung một frontend. Trỏ API client tới `http://127.0.0.1:8000/api`, kiểm tra danh sách phòng và các trạng thái tải/lỗi/rỗng.

Hướng dẫn công việc từng người nằm trong [README](../README.md). Kết quả kiểm tra và phần cần phối hợp tiếp ở [báo cáo backend tuần 1](testing/backend-week1.md).

