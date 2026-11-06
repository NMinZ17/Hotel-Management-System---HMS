# Bắt đầu từ máy chưa có dự án

Thực hiện theo thứ tự dưới đây. Repository ban đầu chỉ chứa tài liệu tổ chức công việc; backend/frontend/database sẽ được thành viên tạo trong Issue tuần 1. Các lệnh chạy ứng dụng chỉ dùng sau khi file tương ứng đã có.

**Cả bốn thành viên**

1. Cài Git, Node.js/npm, Python và PostgreSQL theo hệ điều hành; dùng phiên bản nhóm kiểm tra và ghi lại trong PR tuần 1.
2. Kiểm tra `git --version`, `node --version`, `npm --version`, `python --version`, `psql --version`. Nếu máy không nhận một lệnh, kiểm tra cài đặt/PATH trước khi viết code.
3. Clone repo theo [quy trình GitHub](github-workflow.md). Không mỗi người tạo một repo hoặc một ứng dụng frontend riêng.
4. Linh khởi tạo Vite frontend; Trang tạo schema/seed; Minh tạo FastAPI; Thư làm component và bộ request sau khi khung liên quan đã merge.
5. Để cả bốn máy chạy: Trang ghi cách dựng DB, Minh ghi lệnh backend, Linh ghi lệnh frontend; Thư thử theo hướng dẫn trên máy khác.

**Minh: backend tuần đầu (PowerShell tại thư mục repo)**

```powershell
New-Item -ItemType Directory -Force backend
Set-Location backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]" "psycopg[binary]"
```

Sau khi tạo `backend/app/main.py` có biến `app = FastAPI()`, chạy từ thư mục backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Tạo health endpoint trước, sau đó kết nối DB và rooms. Ghi dependencies/phiên bản đã kiểm tra trong requirements; người clone sau cài bằng requirements của nhóm. Các lệnh trên là hướng dẫn cài ban đầu, chưa được thực thi thay nhóm. [Python venv](https://docs.python.org/3/library/venv.html), [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/), [Psycopg installation](https://www.psycopg.org/psycopg3/docs/basic/install.html).

**Linh: tạo duy nhất một frontend**

```powershell
npm create vite@latest frontend -- --template react
Set-Location frontend
npm install
npm run dev
```

Kiểm tra Node đáp ứng yêu cầu của phiên bản Vite đang cài (tài liệu hiện nêu 20.19+ hoặc 22.12+, template có thể đòi cao hơn). Commit package.json và package-lock.json. Thư pull nhánh main sau khi PR khởi tạo được merge, rồi chạy `npm ci` trong frontend; không tạo Vite lần hai. [Vite](https://vite.dev/guide/), [React xây ứng dụng từ đầu](https://react.dev/learn/build-a-react-app-from-scratch).

**Trang: dữ liệu tuần đầu**

Tạo DB phát triển tên `hms_dev` bằng công cụ đã cài, ghi lệnh hoặc bước cài đặt. Sau khi các file SQL được tạo theo Issue, có thể chạy:

```powershell
psql -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/migrations/001_rooms.sql
psql -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/seeds/001_rooms.sql
```

Chạy tại gốc repo, nhập mật khẩu khi công cụ hỏi. Tài khoản ở ví dụ cần thay bằng tài khoản của môi trường nhóm. Script dựng từ DB rỗng; nếu chạy lại lỗi, đọc hướng dẫn migration thay vì xóa dữ liệu có giá trị. Seed chỉ dùng dữ liệu giả.

**Thư: kiểm tra luồng**

Sau khi Minh tạo endpoint và backend chạy, kiểm tra GET `/api/health` và `/api/rooms` bằng trình duyệt/Invoke-RestMethod/Postman. Ghi HTTP status, response, commit và bước tái hiện khi lỗi. Khi frontend đã merge, dùng mẫu bảng/form chung và test trạng thái lỗi khi tắt API. Kiểm tra nguồn cấp ba VM từ tuần 1.

**Điều kiện xong tuần đầu**

- Cả bốn máy clone và chạy được theo README cập nhật.
- Trang seed phòng; Minh trả dữ liệu đó; Linh hiển thị; Thư chứng minh luồng và trạng thái lỗi.
- Có PR được reviewer khác tác giả chấp nhận; không có bí mật hoặc dữ liệu cá nhân trong commit.
