# Frontend - Hotel Management System (HMS)

Giao diện người dùng cho hệ thống quản lý khách sạn (React + Vite).

## 1. Cấu trúc thư mục chính
- `src/lib/api.js`: Cấu hình Axios client và các hàm gọi API (`/api/auth/login`, `/api/rooms`).
- `src/pages/LoginPage.jsx`: Màn hình đăng nhập hệ thống.
- `src/pages/RoomsPage.jsx`: Màn hình hiển thị danh sách phòng (có xử lý Loading, Empty, Error).
- `mock_backend.py`: File backend chạy thử, không thay thế backend thật
## 2. Hướng dẫn cài đặt và khởi chạy

### Bước 1: Chạy Mock Backend (cổng 8000)
Từ thư mục gốc của dự án (nơi chứa file `mock_backend.py`), chạy lệnh:
```bash
pip install fastapi uvicorn
uvicorn mock_backend:app --reload --port 8000
```
- Tài khoản đăng nhập mẫu: letan@hms.example / letan123

### Bước 2: Chạy Frontend
```bash
cd frontend
npm install
npm run build
npm run dev
```
