# Evidence – Ngày 3: Xây dựng component dùng chung

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người thực hiện:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Nhánh:** `Thanh-Thư`  
**Ngày ghi nhận:** 17/11/2026

## 1. Mục tiêu

Xây dựng các component React dùng chung dựa trên cấu trúc frontend đã được khởi tạo và quy ước giao diện đã thống nhất.

Không chạy `create-vite` lần thứ hai để tránh ghi đè hoặc tạo trùng cấu trúc frontend của nhóm.

## 2. Điều kiện trước khi thực hiện

- Nhánh khởi tạo frontend của Linh đã được merge.
- Tiếp tục phát triển trên cấu trúc frontend hiện có.
- Áp dụng quy ước trong `docs/ui-conventions.md`.

## 3. Component đã triển khai

| Component | Vai trò |
|---|---|
| Header | Header dùng chung cho Customer, Staff và Admin thông qua props |
| FilterBar | Hiển thị các trường lọc và thao tác reset |
| DataTable | Hiển thị dữ liệu dạng bảng |
| FormField | Chuẩn hóa label, input và thông báo lỗi |
| StatusBadge | Hiển thị trạng thái bằng màu sắc tương ứng |
| Notification | Hiển thị thông báo sau thao tác |

## 4. Nguyên tắc triển khai

- Tái sử dụng component thay vì viết lại giao diện cho từng trang.
- Truyền cấu hình và dữ liệu thông qua props.
- Tách CSS theo component.
- Giữ giao diện thống nhất với `docs/ui-conventions.md`.
- Không khởi tạo lại dự án Vite.

## 5. Kết quả

Các component dùng chung đã được tạo trong:

```text
frontend/src/components/common/
```

Các component đã có:

- `Header.jsx`
- `FilterBar.jsx`
- `DataTable.jsx`
- `FormField.jsx`
- `StatusBadge.jsx`
- `Notification.jsx`

Các file CSS tương ứng cũng được tổ chức trong thư mục component dùng chung.

## 6. Kiểm tra

Frontend đã được kiểm tra bằng lệnh build:

```powershell
npm --prefix frontend run build
```

**Kết quả:** Build thành công.

## 7. Minh chứng và giới hạn

- Mã nguồn component trong `frontend/src/components/common/`.
- Quy ước giao diện trong `docs/ui-conventions.md`.
- Kết quả build frontend.
- Không đính kèm ảnh trong file này; ảnh theo yêu cầu Issue sẽ được bổ sung trong PR.

## 8. Kết luận

Đã triển khai các component dùng chung trên cấu trúc frontend hiện có, không khởi tạo Vite lần thứ hai.

**Trạng thái:** Đã triển khai – frontend build thành công.