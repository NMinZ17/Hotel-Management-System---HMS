# Bug log – HMS Week 2

**Mã công việc:** HMS-W2-THU  
**Issue:** #9 – Quản trị phòng, khung staff và request nghiệp vụ  
**Người ghi nhận:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần:** 16/11/2026–22/11/2026  
**Trạng thái:** Đang ghi nhận các điểm nghẽn tích hợp

## 1. Quy ước

- Chỉ ghi HTTP status khi request đã thực sự được gửi và nhận response.
- Không tự tạo response hoặc log giả.
- Endpoint chưa tồn tại hoặc chưa được công bố được đánh dấu BLOCKED.
- Lỗi thuộc Backend được chuyển cho thành viên phụ trách Backend.
- Không tự sửa endpoint của thành viên khác.

## 2. Danh sách vấn đề

### HMS-W2-BLK-01 – Chưa có API xác thực và phân quyền

| Thuộc tính | Nội dung |
|---|---|
| Loại | Integration blocker |
| Mức độ | High |
| Người phụ trách xử lý | Nguyễn Nhật Minh |
| Issue liên quan | #6 |
| Trạng thái | BLOCKED – chờ Backend |

**Bằng chứng kiểm tra:**

- Đã rà soát `backend/app/routers/`.
- Hiện chỉ thấy router `rooms.py`.
- Chưa tìm thấy endpoint đăng nhập/đăng ký.
- Chưa tìm thấy dependency hoặc middleware xác thực và kiểm tra vai trò.

**Đầu vào dự kiến:**

- Tài khoản Guest hợp lệ.
- Tài khoản Admin hợp lệ.
- Tài khoản Staff hợp lệ.
- Request không có thông tin xác thực.

**Kết quả mong đợi:**

- Đăng nhập thành công với tài khoản hợp lệ.
- Tài khoản không hợp lệ bị từ chối.
- Endpoint giới hạn quyền phải kiểm tra danh tính và vai trò ở Backend.

**Kết quả thực tế:**

Chưa gửi request thực tế vì endpoint xác thực chưa được tìm thấy. Không có HTTP status thực tế để ghi nhận.

**Việc cần phối hợp:**

Minh công bố endpoint, payload, response và cơ chế xác thực/phân quyền. Sau đó thực hiện lại bộ request.

---

### HMS-W2-BLK-02 – Chưa có API đặt phòng và hủy phòng

| Thuộc tính | Nội dung |
|---|---|
| Loại | Integration blocker |
| Mức độ | High |
| Người phụ trách xử lý | Nguyễn Nhật Minh |
| Issue liên quan | #6 |
| Trạng thái | BLOCKED – chờ Backend |

**Bằng chứng kiểm tra:**

Rà soát router Backend hiện tại chưa tìm thấy endpoint tìm phòng trống, đặt phòng, xem đơn của khách hoặc hủy phòng.

**Đầu vào dự kiến:**

- Ngày nhận phòng và trả phòng hợp lệ.
- Ngày nhận phòng bằng hoặc sau ngày hiện tại.
- Ngày trả phòng sau ngày nhận phòng.
- Mã phòng hợp lệ.
- Tài khoản thực hiện thao tác.

**Kết quả mong đợi:**

- Ngày không hợp lệ bị từ chối.
- Đặt phòng thành công khi đáp ứng điều kiện nghiệp vụ.
- Khách chỉ xem và hủy được đơn thuộc quyền của mình.
- Xung đột đặt phòng được Backend xử lý đúng.

**Kết quả thực tế:**

Chưa thể kiểm thử qua API thật vì chưa tìm thấy các endpoint nghiệp vụ tương ứng. Chưa có HTTP status thực tế.

**Việc cần phối hợp:**

Minh công bố endpoint và hợp đồng request/response. Sau đó phối hợp chạy các ca kiểm thử.

---

### HMS-W2-REVIEW-03 – Cần xác nhận trường dữ liệu phòng được công khai

| Thuộc tính | Nội dung |
|---|---|
| Loại | API contract / access review |
| Mức độ | Medium |
| Người phối hợp | Nguyễn Nhật Minh |
| Trạng thái | Chờ xác nhận hợp đồng dữ liệu |

**Bằng chứng kiểm tra:**

`GET /api/rooms` hiện trả về:

- `room_id`
- `room_number`
- `room_type_id`
- `floor`
- `housekeeping_status`
- `maintenance_status`
- `room_type.name`
- `room_type.max_guests`
- `room_type.base_price`

**Vấn đề cần xác nhận:**

Hai trường `housekeeping_status` và `maintenance_status` có tính chất vận hành nội bộ. Cần xác nhận chúng có được phép xuất hiện trong response dành cho người dùng công khai hay không.

**Kết quả thực tế:**

Đã xác nhận hai trường có trong schema và response mapping hiện tại. Chưa kết luận về quyền truy cập vì chưa có hợp đồng phân loại dữ liệu chính thức.

**Việc cần phối hợp:**

Minh xác nhận trường công khai và trường chỉ dành cho Admin/Staff. Không tự thay đổi schema hoặc endpoint.

## 3. Nguyên tắc đóng vấn đề

Chỉ chuyển BLOCKED sang VERIFIED khi:

1. Endpoint được công bố.
2. Request thực tế được gửi.
3. Ghi lại HTTP status và response.
4. Có log hoặc ảnh chụp minh chứng.
5. Reviewer xác nhận kết quả.



---

### HMS-W2-FE-04 – Sai đường dẫn import sau khi refactor Admin

| Thuộc tính | Nội dung |
|---|---|
| Loại | Frontend / Build |
| Mức độ | Medium |
| Người xử lý | Đỗ Thị Thanh Thư |
| Issue liên quan | #9 |
| Trạng thái | FIXED |

**Mô tả:**

Sau khi di chuyển `RoomsPage.jsx` vào thư mục `views`, đường dẫn import API không còn phù hợp với vị trí mới.

**Nguyên nhân:**

Đường dẫn tương đối chưa được cập nhật sau khi thay đổi cấu trúc thư mục.

**Cách xử lý:**

Đã cập nhật đường dẫn import API thành `../../../lib/api.js`.

**Kết quả:**

Người phụ trách xác nhận đã sửa thành công.

**Minh chứng:**

- Có thông tin lỗi import trong lịch sử làm việc.
- Không lưu ảnh chụp màn hình tại thời điểm phát sinh lỗi.
- Không có ảnh minh chứng được đính kèm.

---

### HMS-W2-FE-05 – Không tìm thấy StaffBookingsPage.jsx

| Thuộc tính | Nội dung |
|---|---|
| Loại | Frontend / Import |
| Mức độ | Medium |
| Người xử lý | Đỗ Thị Thanh Thư |
| Issue liên quan | #9 |
| Trạng thái | FIXED |

**Mô tả:**

`StaffPages.jsx` tham chiếu `StaffBookingsPage.jsx`, nhưng Vite không tìm thấy module tại đường dẫn được khai báo.

**Bằng chứng:**

Vite đã báo lỗi `Failed to resolve import`.

**Cách xử lý:**

Đã xử lý lỗi import và người phụ trách xác nhận sửa thành công.

**Minh chứng:**

- Có thông tin lỗi trong lịch sử làm việc.
- Không lưu ảnh chụp màn hình tại thời điểm phát sinh lỗi.
- Không có ảnh minh chứng được đính kèm.

---

## 4. Tổng kết Issue #9 – Week 2

| Mã | Nội dung | Trạng thái |
|---|---|---|
| HMS-W2-BLK-01 | Chưa có API xác thực và phân quyền | BLOCKED |
| HMS-W2-BLK-02 | Chưa có API đặt phòng và hủy phòng | BLOCKED |
| HMS-W2-REVIEW-03 | Xác nhận trường dữ liệu phòng công khai | Chờ xác nhận |
| HMS-W2-FE-04 | Sai đường dẫn import Admin | FIXED |
| HMS-W2-FE-05 | Không tìm thấy StaffBookingsPage.jsx | FIXED |

**Kết luận:**

- Hai lỗi import Frontend đã được sửa thành công.
- Hai blocker Backend đang chờ Nguyễn Nhật Minh công bố API.
- Vấn đề phân loại dữ liệu phòng đang chờ xác nhận API contract.
- Không ghi HTTP status giả định.
- Không tạo ảnh minh chứng không có thật.

**Người phụ trách Issue #9:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681
