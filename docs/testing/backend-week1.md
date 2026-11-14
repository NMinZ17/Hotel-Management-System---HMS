# Kiểm thử backend tuần 1

Ngày kiểm tra: 14/11/2026. Công việc: [Issue #2 — Minh](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/2).

Môi trường: Windows, Python 3.14.8, PostgreSQL 18.6. Phiên bản thư viện ở [requirements-lock.txt](../../backend/requirements-lock.txt).

| Kiểm tra | Kết quả | Minh chứng |
| --- | --- | --- |
| API và tích hợp PostgreSQL | 11/11 đạt, không bỏ qua ca nào | [Log kiểm thử](../evidence/w01/minh-backend-tests.txt) |
| SQL của Trang và API qua HTTP Uvicorn | 10/10 đạt | [Kết quả HTTP/SQL](../evidence/w01/minh-source-verification.json) |
| Khởi động bằng `start.ps1 -Check` | Kết nối DB và tìm thấy `room`, `room_type` | [Hướng dẫn chạy](../backend-week1.md) |
| API trên máy Minh | Health và rooms trả 200, có 4 phòng | [Kiểm tra trên máy](../evidence/w01/minh-local-run.md) |

Bộ kiểm thử xác nhận dữ liệu thật thay đổi sau khi SQL được commit; lọc loại phòng và phân trang; giá thập phân; trạng thái hoạt động; danh sách rỗng; CORS; lỗi DB 503; tham số sai trả 422 trước khi mở kết nối. Đường dẫn `/` chuyển tới Swagger UI.

SQL được kiểm tra trên schema biệt lập, tự dọn sau khi chạy. Nguồn schema/seed và commit của Trang ở [database/README.md](../../database/README.md). [Response mẫu](../evidence/w01/minh-rooms-response.json) chứa 4 phòng:

| Phòng | Loại phòng | room_type_id |
| --- | --- | --- |
| 101 | Standard | 1 |
| 102 | Standard | 1 |
| 201 | Deluxe | 2 |
| 202 | Suite | 3 |

## Chạy lại kiểm thử

Từ `backend/`, đặt `HMS_TEST_DATABASE_URL` theo database thử rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tests/verify_source.py
```

Không đặt `HMS_TEST_DATABASE_URL` thì các ca tích hợp PostgreSQL bị bỏ qua.

## Phối hợp nghiệm thu

| Công việc | Trạng thái |
| --- | --- |
| Backend đọc PostgreSQL, cấu hình và hướng dẫn chạy | Đã kiểm tra |
| React hiển thị dữ liệu mới sau khi thay đổi DB | Cần Linh/Thư kiểm tra |
| Trang dựng lại backend theo hướng dẫn | Chưa có xác nhận |
| PR được review và merge | Chưa hoàn tất |
