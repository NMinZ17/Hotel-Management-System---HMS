# Chạy backend tuần 1

Backend dùng FastAPI và PostgreSQL. [Hợp đồng API](api-contract.md) mô tả response; [báo cáo kiểm thử](testing/backend-week1.md) ghi kết quả kiểm tra.

## Thiết lập lần đầu

Cài Python 3.14 và PostgreSQL, bảo đảm có lệnh `psql` và PostgreSQL đang chạy. Phiên bản đã kiểm tra: Python 3.14.8, PostgreSQL 18.6. Các lệnh bên dưới bắt đầu tại gốc repository, nơi có `backend/` và `database/`.

### Cài môi trường Python

PowerShell:

```powershell
py -3.14 -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-lock.txt
if (-not (Test-Path -LiteralPath 'backend/.env')) {
    Copy-Item -LiteralPath 'backend/.env.example' -Destination 'backend/.env'
}
notepad backend/.env
```

Linux:

```bash
python3.14 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements-lock.txt
cp -n backend/.env.example backend/.env
```

`requirements-lock.txt` chứa toàn bộ thư viện của môi trường đã kiểm tra. `requirements.txt` dành cho runtime; `requirements-dev.txt` thêm gói kiểm thử.

### Tạo database và nạp dữ liệu

Chạy một lần trên database phát triển mới. Ví dụ PostgreSQL dùng tài khoản `postgres`, cổng `5432`:

```powershell
createdb -h 127.0.0.1 -p 5432 -U postgres hms_dev
psql -h 127.0.0.1 -p 5432 -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/schema.sql
psql -h 127.0.0.1 -p 5432 -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/seed.sql
```

Các lệnh PostgreSQL trên cũng dùng được trên Linux. Nhập mật khẩu khi công cụ hỏi. Nếu database đã có schema/dữ liệu, bỏ qua bước tạo và nạp lại. Nguồn SQL của Trang được ghi tại [database/README.md](../database/README.md).

### Cấu hình backend/.env

Sửa thông tin kết nối theo PostgreSQL của máy mình:

```dotenv
DATABASE_URL=postgresql://postgres:replace-me@127.0.0.1:5432/hms_dev
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Thay `replace-me` bằng mật khẩu thật; mã hóa ký tự đặc biệt trong tên tài khoản/mật khẩu theo URL. `.env` không được commit.

Trên máy Minh hiện tại, database `hms_dev` đã có 28 bảng/4 phòng mẫu và dùng cổng **55441**. Đây là cấu hình local của máy Minh; các máy khác điền cổng của mình.

Nếu dùng một PostgreSQL cluster local cần khởi động bằng runner, có thể thêm:

| Biến tùy chọn | Giá trị |
| --- | --- |
| `HMS_PG_DATA_DIR` | Thư mục dữ liệu của cluster PostgreSQL đã khởi tạo |
| `HMS_PG_BIN` | Thư mục chứa `pg_ctl` và công cụ PostgreSQL |

Đường dẫn tương đối được tính từ `backend/`. Có thể bỏ `HMS_PG_BIN` nếu `pg_ctl` đã có trong PATH; bỏ `HMS_PG_DATA_DIR` khi PostgreSQL đã chạy dưới dạng dịch vụ. Runner chỉ khởi động cluster local đã có, không tự tạo cluster hoặc nạp SQL.

## Chạy mỗi lần

Dừng API cũ bằng **Ctrl+C** nếu terminal trước vẫn chạy. Từ gốc repository, mở PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backend\scripts\start.ps1
```

Runner dùng Python của `backend/.venv`, nạp `.env`, kiểm tra database và khởi động API. Giữ terminal mở. API ở `http://127.0.0.1:8000`; Swagger UI ở [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Thêm `-Check` vào lệnh để chỉ kiểm tra database rồi thoát; dùng `-Port 8001` nếu cần đổi cổng API.

Trên Linux, khởi động PostgreSQL theo cấu hình máy rồi chạy từ gốc repository:

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Sau khi sửa `.env`, dừng và chạy lại API. Biến môi trường trong terminal được ưu tiên hơn file `.env`; nếu cấu hình không khớp, kiểm tra biến `DATABASE_URL`/`CORS_ORIGINS` cũ trong terminal.

## Kiểm tra API

Mở terminal thứ hai:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
Invoke-RestMethod 'http://127.0.0.1:8000/api/rooms' | ConvertTo-Json -Depth 5
Invoke-RestMethod 'http://127.0.0.1:8000/api/rooms?room_type_id=2&limit=2&offset=0' | ConvertTo-Json -Depth 5
```

Trên Linux dùng `curl` với các URL tương ứng. Health trả `200` và trạng thái tiến trình. Rooms trả mảng dữ liệu PostgreSQL, có `room_type` và giá dạng chuỗi. Với seed hiện tại, danh sách có 4 phòng; loại phòng 2 là Deluxe.

Frontend dùng `VITE_API_BASE_URL=http://127.0.0.1:8000/api` và gọi `/rooms`; restart Vite sau khi đổi biến môi trường. Origin Vite cần có trong `CORS_ORIGINS`.

## Chạy kiểm thử

Từ thư mục `backend`, đặt `HMS_TEST_DATABASE_URL` trỏ database thử có quyền tạo schema, rồi chạy:

```powershell
$env:HMS_TEST_DATABASE_URL = 'postgresql://postgres:replace-me@127.0.0.1:5432/hms_dev'
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Remove-Item Env:HMS_TEST_DATABASE_URL
```

Linux:

```bash
export HMS_TEST_DATABASE_URL='postgresql://postgres:replace-me@127.0.0.1:5432/hms_dev'
.venv/bin/python -m unittest discover -s tests -v
unset HMS_TEST_DATABASE_URL
```

Đổi thông tin kết nối theo máy, gồm cổng 55441 nếu dùng database local hiện tại của Minh. Mỗi ca tích hợp tạo/dọn schema riêng. Không đặt biến này thì các ca PostgreSQL bị skip. Kết quả và log nằm ở [báo cáo kiểm thử](testing/backend-week1.md).

## Xử lý lỗi

| Hiện tượng | Cách xử lý |
| --- | --- |
| Health 200, rooms 503 | Kiểm tra PostgreSQL đã chạy, cổng/database đúng, có `backend/.env` và đã nạp schema/seed |
| Đã sửa .env nhưng kết nối vẫn sai | Dừng/chạy lại API; kiểm tra biến môi trường cũ trong terminal |
| Rooms trả `[]` | Kiểm tra bộ lọc, offset và cờ hoạt động của phòng/loại phòng |
| Trình duyệt báo CORS | Thêm đúng origin gồm hostname và cổng vào `CORS_ORIGINS`, restart API |
| Frontend gọi sai API | Kiểm tra `VITE_API_BASE_URL`, tiền tố `/api`, restart Vite và dừng mock backend |
| Cổng 8000 đã dùng | Ctrl+C trong terminal API cũ trước khi chạy runner |
| Không tìm thấy module app | Chạy bằng runner hoặc chuyển vào `backend` và dùng Python của `.venv` |
