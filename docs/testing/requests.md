# API Request Testing – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần thực hiện:** Week 1 (09/11/2026 – 15/11/2026)  
**Trạng thái:** Draft – Kế hoạch kiểm thử, chưa xác nhận kết quả thực tế  
**Công cụ:** Postman  
**Backend dự kiến:** FastAPI

---

## 1. Mục đích

Tài liệu xác định các request và tình huống kiểm thử API cơ bản trong tuần 1, phục vụ quá trình tích hợp frontend, backend và database của Hotel Management System (HMS).

Phạm vi kiểm thử tập trung vào hai endpoint được đề xuất trong `docs/api-contract.md`:

- `GET /api/health`: kiểm tra trạng thái hoạt động của backend.
- `GET /api/rooms`: kiểm tra khả năng lấy danh sách phòng từ backend.

Ngoài ra, tài liệu đề xuất kiểm tra trường hợp danh sách phòng rỗng và trường hợp không thể kết nối backend.

Tài liệu này là kế hoạch kiểm thử. Chỉ cập nhật kết quả sau khi request được thực hiện trên môi trường thực tế.

## 2. Phạm vi và nguyên tắc kiểm thử

### 2.1. Phạm vi

| Nội dung | Phạm vi tuần 1 |
|---|---|
| Kiểm tra kết nối backend | Có |
| Kiểm tra endpoint health | Có |
| Kiểm tra lấy danh sách phòng | Có |
| Kiểm tra danh sách phòng rỗng | Có, khi có dữ liệu thử nghiệm phù hợp |
| Kiểm tra lỗi kết nối backend | Có |
| Kiểm tra giao diện hiển thị dữ liệu API | Sau khi frontend được merge và tích hợp |
| Kiểm thử nghiệp vụ đặt phòng, thanh toán, phân quyền | Không thuộc phạm vi kiểm thử API cơ bản tuần 1 |

Các kiểm thử nghiệp vụ T01–T08 và những kiểm thử bổ sung được thực hiện theo kế hoạch, issue và evidence guide tương ứng của dự án.

### 2.2. Nguyên tắc

- Căn cứ vào API contract đã được nhóm thống nhất.
- Không tự giả định cấu trúc response khi backend chưa xác nhận.
- Không tự ý thay đổi dữ liệu trên database dùng chung.
- Không sử dụng dữ liệu khách hàng thật hoặc thông tin nhạy cảm.
- Không ghi nhận request là đã kiểm thử nếu chưa thực sự chạy.
- Phân biệt rõ kết quả kỳ vọng và kết quả thực tế.
- Khi phát hiện lỗi, ghi lại request, thời điểm, môi trường, thông báo lỗi và các bước tái hiện.

## 3. Cấu hình kiểm thử

### 3.1. Công cụ và môi trường

| Thuộc tính | Giá trị |
|---|---|
| HTTP client | Postman |
| Backend framework | FastAPI |
| Base URL local dự kiến | `http://127.0.0.1:8000` |
| API prefix | `/api` |
| Database | PostgreSQL |
| Hệ điều hành máy dự kiến kiểm thử | Windows |
| Môi trường triển khai | Local hoặc VM theo điều kiện thực tế |
| Trạng thái kiểm thử | Chưa thực hiện |

Base URL local chỉ là địa chỉ dự kiến khi backend chạy trên chính máy kiểm thử. Nếu backend chạy trên máy khác hoặc VM, phải sử dụng địa chỉ thực tế được nhóm cung cấp.

### 3.2. Cấu hình biến môi trường trong Postman

Tạo một Environment trong Postman để quản lý các thông tin cấu hình dùng chung cho các request API.

Các biến cần khai báo:

| Variable | Initial Value | Current Value |
|---|---|---|
| `base_url` | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` |
| `api_prefix` | `/api` | `/api` |

Trong đó:

- `base_url`: Địa chỉ máy chủ Backend. Giá trị trên chỉ áp dụng khi Backend chạy local trên chính máy kiểm thử.
- `api_prefix`: Tiền tố đường dẫn API theo cấu hình dự kiến của dự án.

**Cách sử dụng biến trong request:**

- Kiểm tra trạng thái Backend:

  `{{base_url}}{{api_prefix}}/health`

- Lấy danh sách phòng:

  `{{base_url}}{{api_prefix}}/rooms`

**URL thực tế khi sử dụng cấu hình local:**

- Health: `http://127.0.0.1:8000/api/health`
- Rooms: `http://127.0.0.1:8000/api/rooms`

Khi Backend được triển khai trên máy khác hoặc VM, cần cập nhật `base_url` theo địa chỉ thực tế do nhóm cung cấp. Nếu API prefix thay đổi, cập nhật biến `api_prefix` theo cấu hình Backend đã xác nhận.

Không lưu mật khẩu, token hoặc thông tin kết nối database thật vào tài liệu hay repository.

## 4. Danh sách request kiểm thử

Lưu ý về trạng thái API: Hai endpoint GET /api/health và GET /api/rooms hiện được đề xuất trong docs/api-contract.md nhưng chưa xác nhận đã được triển khai trong mã nguồn Backend. Các request dưới đây là kế hoạch kiểm thử, chỉ thực hiện sau khi thành viên phụ trách Backend xác nhận endpoint đã sẵn sàng.

### API-W1-01 – Kiểm tra trạng thái backend

**Mục đích:** Xác nhận backend có thể nhận và xử lý request.

**Trạng thái hiện tại:** Bị chặn – Chờ Backend xác nhận endpoint GET /api/health đã được triển khai.

| Thuộc tính | Giá trị |
|---|---|
| Method | GET |
| Endpoint | `/api/health` |
| URL dự kiến | `{{base_url}}/api/health` |
| Request body | Không có |
| Điều kiện trước | Backend đã được khởi động |

**Các bước thực hiện:**

1. Khởi động backend theo hướng dẫn trong README.
2. Mở Postman.
3. Chọn method GET.
4. Nhập URL của endpoint.
5. Gửi request.
6. Ghi nhận HTTP status và response thực tế.

**Kết quả kỳ vọng:**

- Backend nhận được request.
- API phản hồi thành công theo thiết kế health check đã được backend xác nhận.
- Response có cấu trúc phù hợp với API contract chính thức.

**Kết quả thực tế:** Chưa kiểm thử.

**HTTP status thực tế:** Chưa ghi nhận.

---

### API-W1-02 – Lấy danh sách phòng

**Mục đích:** Kiểm tra khả năng lấy danh sách phòng từ backend để phục vụ frontend.

**Trạng thái hiện tại:** Bị chặn – Chờ Backend xác nhận endpoint GET /api/rooms đã được triển khai và cung cấp cấu trúc response chính thức.

| Thuộc tính | Giá trị |
|---|---|
| Method | GET |
| Endpoint | `/api/rooms` |
| URL dự kiến | `{{base_url}}/api/rooms` |
| Request body | Không có |
| Điều kiện trước | Backend hoạt động và database có dữ liệu phòng thử nghiệm |

**Các bước thực hiện:**

1. Khởi động PostgreSQL và database HMS theo hướng dẫn của nhóm.
2. Đảm bảo dữ liệu phòng thử nghiệm đã được khởi tạo.
3. Khởi động backend.
4. Gửi request GET đến `/api/rooms`.
5. Kiểm tra HTTP status và nội dung response.

**Các trường dữ liệu dự kiến theo API contract:**

| Trường | Ý nghĩa |
|---|---|
| `room_id` | Mã phòng |
| `room_number` | Số phòng |
| `room_type_id` | Mã loại phòng |
| `housekeeping_status` | Trạng thái vệ sinh |
| `maintenance_status` | Trạng thái bảo trì |

**Kết quả kỳ vọng:**

- API trả về danh sách phòng theo cấu trúc response đã được nhóm xác nhận.
- Các trường dữ liệu cần thiết được trả về đúng theo API contract.
- Dữ liệu phản ánh thông tin trong database.
- Không trả về những thông tin nội bộ hoặc nhạy cảm không cần thiết cho giao diện.

**Lưu ý:**

API contract hiện mới đề xuất các trường dữ liệu. Cấu trúc response chính thức (danh sách trực tiếp hay object bao ngoài), phân trang và các trường bổ sung cần được backend xác nhận trước khi frontend tích hợp.

**Kết quả thực tế:** Chưa kiểm thử.

**HTTP status thực tế:** Chưa ghi nhận.

---

### API-W1-03 – Kiểm tra danh sách phòng rỗng

**Mục đích:** Kiểm tra cách backend xử lý khi không có phòng để trả về.

**Trạng thái hiện tại:** Bị chặn – Chờ Backend xác nhận endpoint GET /api/rooms đã sẵn sàng và nhóm cung cấp database hoặc fixture thử nghiệm riêng không chứa dữ liệu phòng phù hợp.

| Thuộc tính | Giá trị |
|---|---|
| Method | GET |
| Endpoint | `/api/rooms` |
| URL dự kiến | `{{base_url}}/api/rooms` |
| Request body | Không có |
| Điều kiện trước | Có môi trường database thử nghiệm không chứa phòng phù hợp |

**Các bước thực hiện:**

1. Sử dụng database hoặc fixture thử nghiệm riêng.
2. Đảm bảo không có bản ghi phòng phù hợp với điều kiện truy vấn.
3. Gửi request GET đến `/api/rooms`.
4. Kiểm tra HTTP status và response.

**Kết quả kỳ vọng:**

- API xử lý được trường hợp không có dữ liệu.
- Response thể hiện danh sách rỗng theo cấu trúc đã thống nhất.
- Không phát sinh lỗi ngoài dự kiến chỉ vì danh sách không có phần tử.

**Lưu ý:**

- Không tự ý xóa dữ liệu phòng trong database dùng chung để tạo tình huống kiểm thử.
- Không giả định response phải là `[]` nếu backend chưa xác nhận cấu trúc response.
- Chỉ thực hiện kiểm thử khi có database hoặc fixture thử nghiệm phù hợp.
- Nếu chưa có môi trường hoặc fixture phù hợp, đánh dấu test là Bị chặn.

**Kết quả thực tế:** Chưa kiểm thử.

**HTTP status thực tế:** Chưa ghi nhận.

---

### API-W1-04 – Kiểm tra khi backend không thể kết nối

**Mục đích:** Kiểm tra cách client nhận biết và xử lý tình huống backend không hoạt động.

**Trạng thái hiện tại:** Chưa kiểm thử – Chờ xác nhận môi trường Backend thử nghiệm và địa chỉ kết nối được sử dụng. Chỉ thực hiện trên môi trường thử nghiệm được phép.

| Thuộc tính | Giá trị |
|---|---|
| Method | GET |
| Endpoint | `/api/health` |
| URL dự kiến | `{{base_url}}/api/health` |
| Request body | Không có |
| Điều kiện trước | Backend không chạy hoặc địa chỉ kiểm thử không thể kết nối |

**Các bước thực hiện:**

1. Sử dụng môi trường local hoặc môi trường thử nghiệm được phép.
2. Đảm bảo địa chỉ kiểm thử không thể kết nối đến backend.
3. Gửi request GET đến `/api/health`.
4. Ghi nhận thông báo lỗi kết nối.
5. Nếu frontend đã được tích hợp, kiểm tra giao diện khi API không phản hồi.

**Kết quả kỳ vọng:**

- Client nhận biết được lỗi kết nối.
- Postman hiển thị thông báo lỗi phù hợp.
- Frontend không hiển thị dữ liệu giả hoặc dữ liệu cũ như thể request vừa thành công.
- Giao diện có thông báo phù hợp khi không thể tải dữ liệu.

**Lưu ý:**

Khi backend không thể kết nối, Postman có thể không nhận được HTTP status vì không có phản hồi HTTP từ server. Cần ghi lại lỗi kết nối thực tế, không tự ghi HTTP 500.

Chỉ thực hiện trên môi trường thử nghiệm được phép, không chủ động dừng backend dùng chung của nhóm.

**Kết quả thực tế:** Chưa kiểm thử.

**HTTP status thực tế:** Không áp dụng khi không nhận được phản hồi HTTP.

## 5. Bảng theo dõi kết quả kiểm thử

Bảng này dùng để theo dõi tiến độ thực hiện. Không được đánh dấu Đạt nếu chưa có kết quả thực tế và bằng chứng phù hợp.

| Mã test | Nội dung | Trạng thái ban đầu | Kết quả |
|---|---|---|---|
| API-W1-01 | Kiểm tra trạng thái backend | Chưa chạy | Chưa ghi nhận |
| API-W1-02 | Lấy danh sách phòng | Chưa chạy | Chưa ghi nhận |
| API-W1-03 | Kiểm tra danh sách phòng rỗng | Chưa chạy | Chưa ghi nhận |
| API-W1-04 | Kiểm tra lỗi kết nối backend | Chưa chạy | Chưa ghi nhận |

Quy ước cập nhật:

- **Chưa chạy:** Chưa thực hiện request.
- **Đạt:** Kết quả thực tế đáp ứng tiêu chí kỳ vọng.
- **Không đạt:** Kết quả thực tế không đáp ứng tiêu chí kỳ vọng.
- **Bị chặn:** Chưa thể kiểm thử do thiếu backend, database, dữ liệu hoặc quyền truy cập.

Khi cập nhật trạng thái, cần ghi rõ nguyên nhân và bằng chứng tương ứng.

## 6. Thông tin cần xác nhận với thành viên backend và database

Trước khi thực hiện kiểm thử chính thức, cần phối hợp với thành viên phụ trách để xác nhận:

### 6.1. Backend

- Backend đã có thể khởi động và nhận request chưa?
- Base URL chính thức là gì?
- Endpoint `/api/health` đã được triển khai chưa?
- Endpoint `/api/rooms` đã được triển khai chưa?
- Response của từng endpoint có cấu trúc chính thức như thế nào?
- API sử dụng HTTP status nào khi thành công và khi xảy ra lỗi?
- Có cần xác thực đối với hai endpoint trên không?

### 6.2. Database

- Database thử nghiệm đã được khởi tạo chưa?
- Đã có dữ liệu phòng mẫu chưa?
- Những trường nào trong response được lấy từ bảng nào?
- Có fixture hoặc hướng dẫn tạo dữ liệu kiểm thử không?
- Có môi trường riêng để kiểm tra trường hợp danh sách phòng rỗng không?

### 6.3. Frontend

Sau khi PR khởi tạo Frontend được review, merge vào nhánh tích hợp theo quy trình GitHub của nhóm và xác nhận có thể chạy.

- Kiểm tra frontend có lấy được danh sách phòng từ API không.
- Kiểm tra dữ liệu hiển thị có đúng với response không.
- Kiểm tra trạng thái Loading.
- Kiểm tra trạng thái Empty khi danh sách rỗng.
- Kiểm tra thông báo lỗi khi API không thể kết nối.

## 7. Quy trình ghi nhận lỗi

Khi phát hiện lỗi, ghi lại các thông tin:

1. Mã test liên quan.
2. Ngày và thời điểm thực hiện.
3. Môi trường kiểm thử.
4. Method và URL.
5. Các bước tái hiện lỗi.
6. HTTP status hoặc thông báo lỗi thực tế.
7. Response thực tế nếu có.
8. Kết quả kỳ vọng và kết quả thực tế.
9. Ảnh chụp hoặc log làm bằng chứng.
10. Thành viên phụ trách cần phối hợp xử lý.

Không đưa mật khẩu, token, thông tin kết nối hoặc dữ liệu cá nhân thật vào log được commit.

## 8. Lưu minh chứng kiểm thử

Tuân thủ quy định chung tại:

`docs/testing/evidence-guide.md`

Khi thực sự chạy kiểm thử, lưu minh chứng theo cấu trúc:

`docs/evidence/wXX/<ma-test>.md`

Ví dụ, nếu kiểm thử API-W1-01 trong tuần 1:

`docs/evidence/w01/API-W1-01.md`

Mỗi minh chứng cần ghi nhận các thông tin theo evidence guide, bao gồm:

- Mã test và Issue liên quan.
- Ngày chạy.
- Người chạy và người kiểm tra.
- Commit và nhánh.
- Phiên bản môi trường.
- Dữ liệu thử nghiệm và bước chuẩn bị.
- Request hoặc lệnh đã chạy.
- Kết quả kỳ vọng và thực tế.
- SQL xác nhận trạng thái cuối nếu có thay đổi dữ liệu cần kiểm tra.
- Kết luận: Đạt / Không đạt / Chưa chạy.
- PR, ảnh, log và lỗi còn mở.

Đối với các request GET không làm thay đổi dữ liệu, cần ghi rõ SQL xác nhận trạng thái cuối là không áp dụng nếu không cần thiết.

Không tạo file minh chứng, log hoặc ảnh giả khi chưa thực hiện kiểm thử. Log dài, ảnh hoặc video lớn được đính kèm vào Issue hoặc liên kết phù hợp thay vì commit trực tiếp vào repository. Không commit backup database.

## 9. Tiến độ và trạng thái tài liệu

Tài liệu được xây dựng trong phạm vi Issue #5 của tuần 1.

**Trạng thái hiện tại:**

- Đã xác định các endpoint cần kiểm thử theo API contract đề xuất.
- Đã xây dựng các tình huống request cơ bản.
- Đã xác định các thông tin cần backend và database xác nhận.
- Chưa xác nhận toàn bộ endpoint đã được triển khai.
- Chưa ghi nhận kết quả kiểm thử thực tế.
- Chưa có minh chứng kiểm thử thực tế.

**Điều kiện cập nhật hoàn thành:**

- Backend xác nhận endpoint và response.
- Các request được thực hiện trên môi trường phù hợp.
- Kết quả thực tế được ghi nhận đầy đủ.
- Các lỗi phát hiện được báo lại cho thành viên phụ trách.
- Minh chứng được lưu theo quy định của dự án.

Tài liệu sẽ được cập nhật khi API contract hoặc cách triển khai thực tế có thay đổi.