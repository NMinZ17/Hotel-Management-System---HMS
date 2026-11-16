# Evidence – Ngày 2: React và thống nhất UI

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người thực hiện:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Nhánh:** `Thanh-Thư`  
**Ngày ghi nhận:** 17/11/2026

## 1. Mục tiêu

- Làm quen với React thông qua việc tìm hiểu layout quản trị.
- Thống nhất quy ước giao diện với Linh trước khi xây dựng component dùng chung.
- Ghi nhận màu sắc, form, bảng dữ liệu và thông báo để các thành viên sử dụng thống nhất.

## 2. Nội dung thực hiện

### 2.1. Tìm hiểu React

Tìm hiểu cấu trúc component và cách tổ chức giao diện React thông qua layout quản trị hiện có.

Các nội dung áp dụng:

- Component và JSX.
- Props để truyền dữ liệu và cấu hình.
- Tách component dùng chung khỏi từng trang.
- Tổ chức CSS riêng cho component.

### 2.2. Thống nhất quy ước giao diện với Linh

Các quy ước được ghi nhận trong `docs/ui-conventions.md`:

| Thành phần | Quy ước |
|---|---|
| Màu sắc | Tông be/nâu chủ đạo, nền xám, bảng và card sáng |
| Trạng thái | Màu đỏ, vàng, xanh lá |
| Header | Dùng chung cho Customer, Staff, Admin thông qua props |
| AdminSidebar | Component riêng cho giao diện Admin |
| FormField | Label đậm 14px, dấu bắt buộc màu đỏ |
| Input/Select | Cao 40px, bo góc 6px |
| Lỗi form | Màu đỏ, cỡ chữ 12px bên dưới trường |
| Button | Cao 40px, bo góc 6px |
| DataTable | Header căn giữa; dữ liệu số căn phải, văn bản căn trái |
| Pagination | Căn giữa bên dưới bảng |
| Notification | Hiển thị góc trên bên phải trong 2–3 giây |
| StatusBadge | Component dùng chung để hiển thị trạng thái |

## 3. Tài liệu liên quan

- `docs/ui-conventions.md`
- `frontend/src/components/common/`

## 4. Kết quả

Đã ghi nhận quy ước giao diện chung và áp dụng vào các component dùng chung của frontend.

Các component đã được triển khai trong code:

- DataTable
- FilterBar
- FormField
- Header
- Notification
- StatusBadge

RoomCard vẫn cần được xác nhận thêm về quy ước trước khi xem là thống nhất hoàn toàn.

## 5. Minh chứng và giới hạn

- Quy ước giao diện được lưu trong `docs/ui-conventions.md`.
- Code component là minh chứng cho phần triển khai.
- Không đính kèm ảnh trong file này; ảnh theo yêu cầu Issue sẽ được bổ sung trong PR.
- Không khẳng định các nội dung chưa được xác nhận là đã hoàn tất.

## 6. Kết luận

Đã hoàn thành phần tìm hiểu React và ghi nhận quy ước UI chung với Linh trong phạm vi các nội dung đã thống nhất.

**Trạng thái:** Đã thực hiện – RoomCard còn chờ xác nhận.