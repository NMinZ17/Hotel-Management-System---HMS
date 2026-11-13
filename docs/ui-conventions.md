# UI Conventions – HMS

**Mã công việc:** HMS-W1-THU  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Trạng thái:** Draft – Đề xuất, chờ thống nhất với nhóm  
**Phạm vi:** Quy ước giao diện dùng chung cho hệ thống quản lý khách sạn (HMS).

## 1. Mục đích

Tài liệu này đề xuất các quy ước giao diện dùng chung nhằm đảm bảo tính nhất quán giữa các trang trong hệ thống HMS. Các quy ước sẽ được điều chỉnh sau khi thống nhất với thành viên phụ trách frontend và API.

## 2. Ngôn ngữ và cách trình bày

- Ngôn ngữ giao diện chính: Tiếng Việt.
- Tên trường dữ liệu cần rõ ràng, dễ hiểu và phù hợp với nghiệp vụ khách sạn.
- Các nút thao tác cần sử dụng động từ cụ thể, ví dụ: Thêm, Sửa, Xóa, Lưu, Hủy.
- Các trang quản trị cần có bố cục nhất quán, dễ theo dõi và thao tác.

## 3. Quy ước về bố cục

- Các trang quản trị dự kiến sử dụng những khu vực sau:
  - Sidebar: Điều hướng giữa các chức năng.
  - Header: Hiển thị tên trang và thông tin tài khoản.
  - Main content: Hiển thị nội dung chính.
  - Notification: Thông báo kết quả thao tác hoặc lỗi.
- Bố cục cần đảm bảo tính nhất quán giữa các trang và có khả năng thích ứng với kích thước màn hình khác nhau (Responsive Layout).
- Trên màn hình nhỏ, Sidebar có thể chuyển thành menu thu gọn.
- Bảng dữ liệu cần có phương án hiển thị phù hợp trên màn hình nhỏ, tránh làm vỡ bố cục.
- Bố cục cụ thể sẽ được thống nhất cùng thành viên phụ trách khởi tạo frontend.

## 4. Quy ước về bảng dữ liệu

- Các bảng dữ liệu nên có:
  - Tiêu đề bảng hoặc tên chức năng.
  - Tên cột rõ ràng.
  - Dữ liệu được trình bày thống nhất.
  - Trạng thái hiển thị dễ nhận biết.
  - Các thao tác phù hợp như xem chi tiết, chỉnh sửa hoặc xóa nếu nghiệp vụ cho phép.
  - Phân trang khi số lượng dữ liệu lớn và API hỗ trợ.
- Trong quá trình tải hoặc xử lý dữ liệu:
  - Loading: Hiển thị trạng thái đang tải.
  - Empty State: Hiển thị khi không có dữ liệu.
  - Error State: Hiển thị thông báo khi không thể tải dữ liệu.

## 5. Quy ước về biểu mẫu

- Các biểu mẫu cần đảm bảo:
  - Mỗi trường có nhãn (Label) rõ ràng.
  - Trường bắt buộc được đánh dấu.
  - Dữ liệu nhập cần được kiểm tra hợp lệ.
  - Hiển thị thông báo khi dữ liệu không hợp lệ.
  - Có nút Lưu và Hủy phù hợp với từng thao tác.
  - Nút gửi biểu mẫu cần có trạng thái đang xử lý để hạn chế gửi lặp ngoài ý muốn.
  - Không tự ý xác định kiểu dữ liệu, trường bắt buộc hoặc quy tắc nghiệp vụ nếu chưa được xác nhận trong API contract hoặc tài liệu nghiệp vụ.
  - Các nút và trường nhập liệu cần có nội dung hoặc nhãn rõ ràng, dễ hiểu.

## 6. Quy ước về trạng thái và thông báo

- Các thành phần giao diện cần xử lý tối thiểu những trạng thái sau:
  - Loading: Đang tải dữ liệu hoặc xử lý thao tác.
  - Success: Thao tác thành công.
  - Error: Có lỗi khi tải hoặc xử lý dữ liệu.
  - Empty: Không có dữ liệu để hiển thị.
- Cần phân biệt:
  - Lỗi validation: Dữ liệu người dùng nhập không hợp lệ.
  - Lỗi API: Request không thành công hoặc backend trả về lỗi.
  - Lỗi kết nối: Không thể kết nối đến backend.
- Thông báo lỗi cần dễ hiểu và không hiển thị thông tin nhạy cảm như mật khẩu, token hoặc thông tin kết nối cơ sở dữ liệu.
- Màu sắc của các trạng thái cần được sử dụng thống nhất giữa các trang.
- Không chỉ sử dụng màu sắc để biểu thị trạng thái; cần kết hợp nội dung chữ hoặc biểu tượng phù hợp.

## 7. Quy ước hiển thị trạng thái phòng

- Cần phân biệt rõ hai nhóm trạng thái:
  - Trạng thái vệ sinh (housekeeping_status): Phản ánh tình trạng dọn dẹp phòng.
  - Trạng thái bảo trì (maintenance_status): Phản ánh tình trạng kỹ thuật hoặc bảo trì phòng.
- Không đồng nhất trạng thái phòng sạch với trạng thái phòng có thể đặt. Việc xác định phòng có thể đặt cần dựa trên quy tắc nghiệp vụ và dữ liệu do backend cung cấp.
- Các giá trị trạng thái cụ thể cần được xác nhận với thành viên phụ trách database và backend trước khi triển khai.
- Việc hiển thị trạng thái phòng trên giao diện cần sử dụng đúng tên trường và giá trị do API cung cấp; frontend không tự suy diễn hoặc thay đổi trạng thái nghiệp vụ.

## 8. Các thành phần giao diện dùng chung dự kiến

| Thành phần | Mục đích |
| :--- | :--- |
| DataTable | Hiển thị danh sách dữ liệu |
| FormField | Hiển thị trường nhập liệu |
| Loading | Thông báo đang tải dữ liệu |
| EmptyState | Hiển thị khi danh sách rỗng |
| Notification | Thông báo kết quả thao tác |
| StatusBadge | Hiển thị trạng thái nghiệp vụ |
| ConfirmDialog | Xác nhận trước các thao tác quan trọng |

Đây là danh sách đề xuất, chưa phải các component đã được triển khai.

## 9. Các nội dung cần thống nhất với nhóm

- Màu sắc và phong cách giao diện chung.
- Cấu trúc Sidebar và Header.
- Quy ước đặt tên component.
- Cấu trúc dữ liệu trả về từ API.
- Danh sách giá trị trạng thái phòng chính thức.
- Cách hiển thị thông báo lỗi từ backend.

## 10. Trạng thái tài liệu

Tài liệu hiện ở mức đề xuất cho tuần 1. Sau khi frontend được khởi tạo và các thành viên thống nhất quy ước, nội dung sẽ được cập nhật theo triển khai thực tế.