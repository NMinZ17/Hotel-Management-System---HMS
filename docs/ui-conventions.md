# UI Conventions – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Phối hợp thống nhất UI:** Linh  
**Trạng thái:** Đã thống nhất quy ước UI với thành viên phụ trách frontend  
**Phạm vi:** Quy ước giao diện dùng chung cho Customer và Staff/Admin trong hệ thống quản lý khách sạn HMS.

## 1. Mục đích

Tài liệu quy định các quy ước giao diện dùng chung cho hệ thống HMS, nhằm đảm bảo tính nhất quán giữa các trang Customer và Staff/Admin.

Các component dùng chung cần được thiết kế theo hướng tái sử dụng, hạn chế trùng lặp và thuận tiện cho việc mở rộng, bảo trì.

AdminSidebar được xem là component riêng của khu vực Admin, không thuộc nhóm component dùng chung.

## 2. Quy ước màu sắc và trình bày

### 2.1. Màu sắc chủ đạo

Các màu sắc giao diện được thống nhất như sau:

- **Màu chủ đạo:** Be và nâu.
- **Màu nền trang chính:** Xám.
- **Màu nền bảng và thẻ:** Các tông màu sáng.
- **Màu trạng thái:** Ba màu cơ bản gồm đỏ, vàng và xanh lá.

Quy ước sử dụng:

- Tái sử dụng mã màu đã được định nghĩa trong các component frontend hiện có.
- Không tự ý tạo thêm mã màu khác khi chưa thống nhất.
- Màu trạng thái cần được sử dụng nhất quán giữa các trang.
- Không chỉ dùng màu sắc để biểu thị trạng thái; cần kết hợp nội dung chữ hoặc biểu tượng phù hợp.

### 2.2. Ngôn ngữ và nội dung

- Ngôn ngữ giao diện chính: Tiếng Việt.
- Nhãn trường dữ liệu cần rõ ràng, dễ hiểu và phù hợp nghiệp vụ khách sạn.
- Nút thao tác sử dụng động từ cụ thể như Thêm, Sửa, Xóa, Lưu, Hủy, Đặt phòng.
- Placeholder cần hướng dẫn rõ dữ liệu hoặc định dạng cần nhập.

## 3. Quy ước bố cục và Header

### 3.1. Header

Header của Customer và Staff/Admin sử dụng chung một component, cho phép truyền props để tùy chỉnh nội dung và cách hiển thị theo từng khu vực.

Mục tiêu:

- Đảm bảo giao diện nhất quán.
- Tránh triển khai hai Header riêng có chức năng trùng lặp.
- Cho phép điều chỉnh nội dung theo từng trang hoặc vai trò người dùng.

### 3.2. AdminSidebar

- AdminSidebar là component riêng của khu vực Admin.
- Không đưa AdminSidebar vào nhóm component dùng chung giữa Customer và Staff/Admin.
- Các trang Admin có thể sử dụng AdminSidebar kết hợp với Header chung.

### 3.3. Main content

- Nội dung chính được trình bày trong khu vực riêng của từng trang.
- Bố cục cần đảm bảo khả năng thích ứng với kích thước màn hình.
- Các thành phần dùng chung được tổ chức trong thư mục `frontend/src/components/common/`.

## 4. Quy chuẩn FormField và biểu mẫu

Component FormField được sử dụng để thống nhất cách hiển thị trường nhập liệu.

### 4.1. Label

- Chữ in đậm.
- Kích thước chữ: 14px.
- Trường bắt buộc có dấu `*` màu đỏ bên cạnh nhãn.

### 4.2. Input và Select

- Chiều cao: 40px.
- Bo góc: 6px.
- Placeholder hướng dẫn rõ định dạng hoặc nội dung cần nhập.
- Các trường nhập liệu cần có kích thước và cách trình bày nhất quán.

### 4.3. Error text

- Hiển thị ngay bên dưới trường nhập liệu có lỗi.
- Màu chữ đỏ.
- Kích thước chữ: 12px.
- Nội dung cần nêu rõ vấn đề để người dùng có thể sửa.

### 4.4. Button

- Chiều cao: 40px.
- Bo góc: 6px.
- Nội dung nút cần thể hiện rõ hành động.

### 4.5. Nguyên tắc validation

- Kiểm tra dữ liệu nhập theo quy tắc nghiệp vụ và API contract.
- Không tự ý xác định trường bắt buộc hoặc điều kiện nghiệp vụ khi chưa có căn cứ.
- Khi đang xử lý yêu cầu, cần hạn chế việc người dùng gửi lặp thao tác.

## 5. Quy chuẩn DataTable

Component DataTable được sử dụng để hiển thị dữ liệu dạng bảng.

### 5.1. Tiêu đề và dữ liệu

- Tiêu đề cột: Căn giữa.
- Dữ liệu dạng số: Căn phải.
- Dữ liệu dạng chữ: Căn trái.
- Tên cột cần rõ ràng, phù hợp với nội dung dữ liệu.

### 5.2. Phân trang

- Phân trang được đặt chính giữa, bên dưới bảng dữ liệu.
- Chỉ sử dụng khi phù hợp với lượng dữ liệu và khả năng hỗ trợ của API.

### 5.3. Loading

Trong quá trình tải dữ liệu hoặc xử lý yêu cầu, hiển thị thông báo phù hợp:

- `Đang tải dữ liệu…`
- `Đang xử lý yêu cầu…`

### 5.4. Empty

Khi không có dữ liệu phù hợp, hiển thị:

`Không tìm thấy dữ liệu phù hợp với yêu cầu`

Nếu người dùng đang sử dụng bộ lọc, cần có nút xóa bộ lọc để khôi phục danh sách.

### 5.5. Error

- Hiển thị khung cảnh báo màu đỏ.
- Nội dung thể hiện lỗi xảy ra.
- Thông báo cần dễ hiểu và không để lộ thông tin nhạy cảm.

## 6. Quy chuẩn Notification và StatusBadge

### 6.1. Notification

Component Notification được sử dụng để thông báo kết quả thao tác.

Quy ước:

- Vị trí hiển thị: Góc trên bên phải giao diện.
- Xuất hiện sau thao tác của người dùng, ví dụ: đặt phòng hoặc thực hiện các thao tác dữ liệu.
- Thời gian hiển thị dự kiến: 2–3 giây.
- Màu chữ được thể hiện theo trạng thái thông báo.
- Nội dung ngắn gọn, dễ hiểu.

Các trạng thái cần hỗ trợ:

- Success: Thao tác thành công.
- Error: Thao tác thất bại.
- Warning: Cảnh báo người dùng.
- Info: Thông tin bổ sung khi cần thiết.

### 6.2. StatusBadge

- Sử dụng component StatusBadge hiện có.
- Hiển thị trạng thái dưới dạng nhãn trực quan.
- Màu sắc sử dụng theo quy ước màu trạng thái chung.
- Nội dung chữ cần thể hiện rõ trạng thái, không chỉ dựa vào màu sắc.

Đối với trạng thái phòng, cần phân biệt:
- `housekeeping_status`: Trạng thái vệ sinh phòng.
- `maintenance_status`: Trạng thái bảo trì phòng.

Không đồng nhất trạng thái vệ sinh với trạng thái có thể đặt phòng. Việc xác định phòng có thể đặt phải tuân theo quy tắc nghiệp vụ và dữ liệu backend.

## 7. Danh sách component dùng chung

Các component dùng chung được thống nhất gồm:

| Component | Chức năng |
|---|---|
| Header | Hiển thị khu vực tiêu đề và nội dung điều hướng chung, tùy chỉnh bằng props |
| FilterBar | Tổ chức các trường lọc và thao tác đặt lại bộ lọc |
| DataTable | Hiển thị danh sách dữ liệu dạng bảng |
| FormField | Hiển thị trường nhập liệu theo quy chuẩn chung |
| StatusBadge | Hiển thị trạng thái nghiệp vụ |
| Notification | Thông báo kết quả thao tác |

Các component trên được tổ chức trong `frontend/src/components/common/`.

**Component riêng của Admin:**

- AdminSidebar: Phục vụ điều hướng trong khu vực Admin, không thuộc nhóm component dùng chung.

## 8. Quy ước bộ lọc và dữ liệu phòng

### 8.1. Bộ lọc

Các bộ lọc tầng và giá phòng được xác nhận có API hỗ trợ.

Nguyên tắc:

- Frontend gửi điều kiện lọc theo API contract.
- Không tự lọc theo những trường chưa được backend hỗ trợ.
- Khi xóa bộ lọc, danh sách cần được khôi phục theo dữ liệu mặc định.
- Giao diện cần phản ánh đúng điều kiện lọc đang được áp dụng.

### 8.2. Hình ảnh phòng

Hình ảnh phòng dự kiến được lấy từ database.

Frontend cần sử dụng dữ liệu hình ảnh được backend cung cấp, không tự giả định đường dẫn hoặc nguồn ảnh khi chưa có API contract tương ứng.

### 8.3. Thông tin thanh toán

Trường thông tin thanh toán được giữ lại trong biểu mẫu đặt phòng.

Cách hiển thị và xử lý dữ liệu thanh toán cần phù hợp với nghiệp vụ và API contract.

## 9. Kiểm tra triển khai thực tế

Các component dùng chung đã được triển khai trong frontend:

- DataTable.
- FilterBar.
- FormField.
- Header.
- Notification.
- StatusBadge.

Các chức năng frontend đã được kiểm tra trên môi trường local:

- Hiển thị danh sách phòng từ API.
- Lọc theo loại phòng.
- Sắp xếp giá phòng tăng dần và giảm dần.
- Lọc theo sức chứa.
- Xóa bộ lọc và khôi phục danh sách.
- Kiểm tra giao diện component dùng chung.
- Kiểm tra quá trình build frontend.

Các quy chuẩn được thống nhất với Linh là cơ sở để tiếp tục điều chỉnh giao diện giữa Customer và Staff/Admin.

## 10. Nội dung cần xác nhận thêm

Một số nội dung liên quan đến wireframe và nghiệp vụ cần được xác nhận trước khi triển khai chi tiết:

- RoomCard hiển thị thông tin loại phòng hay từng phòng vật lý.
- Cấu trúc dữ liệu và API cung cấp hình ảnh phòng từ database.
- Cấu trúc trường thanh toán và cách xử lý trong quy trình đặt phòng.
- Chi tiết tham số API cho bộ lọc tầng và giá phòng.

## 11. Trạng thái tài liệu

Các quy ước về màu sắc, Header, FormField, DataTable, Notification, StatusBadge và danh sách component dùng chung đã được thống nhất với thành viên phụ trách frontend.

Tài liệu được cập nhật theo thỏa thuận phối hợp cho Issue #5. Những nội dung liên quan đến dữ liệu nghiệp vụ và chi tiết API sẽ tiếp tục được đối chiếu với backend/database trước khi hoàn thiện triển khai.