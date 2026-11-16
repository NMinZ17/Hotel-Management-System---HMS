# Frontend – Hotel Management System (HMS)

Frontend được xây dựng bằng React và Vite. Tài liệu hướng dẫn cài đặt, khởi chạy và kiểm tra giao diện cùng các component dùng chung trong Week 1.

## 1. Yêu cầu

- Node.js và npm.
- Backend HMS tương thích đang chạy.
- Git để lấy mã nguồn dự án.

## 2. Cài đặt

Từ thư mục gốc dự án:

```powershell
cd frontend
npm install
```

## 3. Cấu hình API

Tạo file `.env` từ file mẫu:

```powershell
Copy-Item .env.example .env
```

Mở `.env` và cấu hình địa chỉ Backend theo môi trường đang sử dụng.

## 4. Khởi chạy Frontend

```powershell
npm run dev
```

Mở địa chỉ Local được Vite hiển thị trên terminal.

## 5. Kiểm tra giao diện và API

- Kiểm tra layout và quy ước UI tại `docs/ui-conventions.md`.
- Kiểm tra các component dùng chung trong `src/components/common/`: bảng, form, bộ lọc, thông báo và trạng thái.
- Kiểm tra danh sách phòng và các trạng thái Loading, Empty, Error.
- Kiểm tra request `GET /api/health` và `GET /api/rooms` theo hướng dẫn tại `docs/testing/requests.md`.

## 6. Kiểm tra build

```powershell
npm run build
```

Build thành công khi không có lỗi và thư mục `dist` được tạo.

**Lưu ý:** Frontend cần Backend tương thích để kiểm tra dữ liệu thực tế. Mock data chỉ phục vụ giao diện, không thay thế Backend thật. Việc chạy thành công trên máy cá nhân không đồng nghĩa với việc đã triển khai lên VM.