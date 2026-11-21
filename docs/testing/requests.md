# API Request Testing – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần thực hiện:** Week 1 (09/11/2026 – 15/11/2026)  
**Ngày cập nhật:** 17/11/2026  
**Trạng thái:** Completed for Week 1 scope – Các request API, backend unittest và kiểm tra Frontend cơ bản đã thực hiện.

---

## 1. Mục đích

Ghi nhận các request và kết quả kiểm tra API của Hotel Management System (HMS) trong phạm vi công việc Week 1.

Tài liệu tập trung vào:
- Kiểm tra API Health và danh sách phòng.
- Kiểm tra phản hồi khi database không có dữ liệu hoặc không khả dụng.
- Ghi nhận kết quả backend unittest.
- Kiểm tra dependency và build Frontend.
- Ghi nhận các thao tác lọc, sắp xếp phòng đã xác minh.

Không mở rộng sang bộ kiểm thử nghiệp vụ T01–T08 trong phạm vi Week 1.

## 2. Môi trường kiểm thử

| Thành phần | Môi trường |
|---|---|
| Hệ điều hành | Windows local |
| Backend | FastAPI |
| Database | PostgreSQL 18 |
| Database phát triển | `hms_dev` |
| Database kiểm thử | `hms_test` |
| API local | `http://localhost:8000` |
| Công cụ gửi request | PowerShell `Invoke-RestMethod` |
| Công cụ kiểm thử tự động | Python `unittest`, FastAPI `TestClient` |
| Kiểm tra Frontend | npm build và thao tác giao diện |

Các request API được thực hiện bằng PowerShell. Không ghi nhận việc sử dụng Postman trong đợt kiểm thử này.

Database `hms_test` được sử dụng riêng cho kiểm thử tích hợp. Các test tạo schema riêng để cô lập dữ liệu kiểm thử; không chủ động xóa hoặc reset database `hms_dev`.

## 3. Chuẩn bị

1. Khởi động PostgreSQL local.
2. Khởi động backend FastAPI tại cổng 8000.
3. Kiểm tra kết nối database phát triển.
4. Chuẩn bị database `hms_test` riêng cho kiểm thử tích hợp.
5. Thực hiện request API và kiểm thử tự động theo từng trường hợp.

## 4. Kết quả kiểm tra API

### API-W1-01 – Health check

**Request**

```http
GET /api/health
```

**Công cụ:** PowerShell `Invoke-RestMethod`

**Kết quả kỳ vọng:**
- HTTP 200.
- API trả về trạng thái hoạt động.
- Health check không phụ thuộc kết nối database.

**Kết quả thực tế:**
- HTTP 200.
- Response:

```json
{
  "status": "ok",
  "service": "hms-api"
}
```

**Kết luận:** Đạt.

### API-W1-02 – Lấy danh sách phòng

**Request**

```http
GET /api/rooms
```

**Công cụ:** PowerShell `Invoke-RestMethod`

**Kết quả kỳ vọng:**
- API trả về danh sách phòng.
- Dữ liệu có cấu trúc phù hợp với response schema.
- Không phát sinh lỗi khi truy vấn database.

**Kết quả thực tế:**
- Request thành công.
- Nhận được 4 bản ghi phòng từ database local `hms_dev`.

**Kết luận:** Đạt.

### API-W1-03 – Danh sách phòng rỗng

**Test tự động:** `test_empty_database_returns_empty_array`

**Công cụ:** Python `unittest` và FastAPI `TestClient`.

**Chuẩn bị:**
- Sử dụng database kiểm thử riêng.
- Test tạo schema cô lập.
- Thực hiện kiểm thử trên dữ liệu rỗng trong schema đó.

**Kết quả kỳ vọng:**
- HTTP 200.
- Response là mảng rỗng `[]`.
- Không phát sinh lỗi khi không có phòng.

**Kết quả thực tế:**
- Test thành công.
- API trả về mảng rỗng theo kỳ vọng.

**Kết luận:** Đạt.

### API-W1-04 – Database không khả dụng

**Test tự động:** `test_database_failure_returns_safe_503`

**Công cụ:** Python `unittest` và FastAPI `TestClient`.

**Mục đích:**

Kiểm tra cách API xử lý khi không thể kết nối PostgreSQL trong khi tiến trình FastAPI vẫn đang hoạt động.

**Kết quả kỳ vọng:**
- API không trả về thông tin nội bộ hoặc thông tin kết nối nhạy cảm.
- Client nhận HTTP 503 với thông báo an toàn.
- Backend không bị dừng do lỗi kết nối database.

**Kết quả thực tế:**
- Test thành công.
- API trả HTTP 503 theo thiết kế.
- Có log lỗi kết nối database ở phía server.

**Lưu ý:** Test này kiểm tra lỗi kết nối database, không phải kiểm thử trường hợp tiến trình Backend bị dừng hoàn toàn.

**Kết luận:** Đạt.

## 5. Kết quả kiểm thử tự động Backend

**Lệnh đã chạy:**

```powershell
python -m unittest discover -s tests -v
```

**Kết quả:**

```text
Ran 11 tests in 6.706s

OK
```

11 test đều thành công:

| STT | Test | Kết quả |
|---|---|---|
| 1 | `test_cors_allows_configured_origins` | Passed |
| 2 | `test_cors_rejects_unconfigured_origin` | Passed |
| 3 | `test_database_failure_returns_safe_503` | Passed |
| 4 | `test_health_does_not_require_a_database_connection` | Passed |
| 5 | `test_home_redirects_to_api_documentation` | Passed |
| 6 | `test_invalid_filters_are_rejected_before_database_connection` | Passed |
| 7 | `test_committed_database_changes_appear_in_following_request` | Passed |
| 8 | `test_empty_database_returns_empty_array` | Passed |
| 9 | `test_invalid_filters_and_injection_are_rejected` | Passed |
| 10 | `test_room_contract_filters_inactive_rows_and_orders_stably` | Passed |
| 11 | `test_room_type_filter_and_pagination` | Passed |

**Kiểm tra dependency:**

```powershell
python -m pip check
```

Kết quả:

```text
No broken requirements found.
```

**Kết luận Backend:** 11/11 unittest Passed; không phát hiện dependency bị lỗi theo kết quả `pip check`.

## 6. Kiểm tra Frontend

**Lệnh build đã chạy:**

```powershell
npm --prefix frontend run build
```

**Kết quả:** Build thành công.

Các thao tác giao diện đã kiểm tra:

- Kết nối API và hiển thị danh sách 4 phòng.
- Lọc theo loại phòng.
- Sắp xếp giá tăng dần.
- Sắp xếp giá giảm dần.
- Lọc sức chứa từ 3 người trở lên.
- Xóa bộ lọc và khôi phục danh sách 4 phòng.

**Giới hạn:** Bộ lọc ngày chưa được xác nhận hoàn chỉnh trong đợt kiểm tra này.

## 7. Phạm vi và giới hạn kiểm thử

Trong Week 1, phạm vi kiểm tra tập trung vào API, Backend, Frontend cơ bản và môi trường chạy thử.

Các nội dung sau không thuộc phạm vi hoàn thành của tài liệu này:
- Bộ kiểm thử nghiệp vụ T01–T08.
- Kiểm thử transaction nghiệp vụ mở rộng.
- Kiểm thử đồng thời và benchmark hiệu năng.
- Kiểm thử toàn bộ luồng nghiệp vụ của hệ thống.

Không sử dụng kết quả 11/11 unittest để khẳng định các nghiệp vụ ngoài phạm vi đã được kiểm thử.

## 8. Minh chứng

Các tài liệu ghi nhận công việc theo ngày nằm trong:

`docs/evidence/w01/`

Bao gồm:
- `day-01-repository-and-vm.md`
- `day-02-ui-conventions.md`
- `day-03-shared-components.md`
- `day-04-api-requests.md`

Ảnh chụp màn hình và log bổ sung sẽ được đính kèm PR hoặc Issue khi hoàn thiện phần nộp minh chứng. Không tạo log hoặc ảnh giả để thay thế kết quả thực tế.

Hướng dẫn ghi nhận minh chứng:

`docs/testing/evidence-guide.md`

## 9. Ghi chú phối hợp

- Backend sử dụng FastAPI và PostgreSQL.
- Frontend lấy dữ liệu phòng từ API Backend.
- Database kiểm thử được tách khỏi database phát triển.
- Không sử dụng kết quả kiểm thử trên dữ liệu cô lập để khẳng định các nghiệp vụ chưa được kiểm tra.
- Các vấn đề phát sinh cần được ghi nhận trong Issue tương ứng để reviewer theo dõi.

## 10. Kết luận

**Trạng thái: Hoàn thành phạm vi kiểm tra Week 1.**

Các nội dung đã thực hiện và có kết quả ghi nhận:

- API Health check: Đạt.
- API lấy danh sách phòng: Đạt.
- Kiểm thử danh sách phòng rỗng: Đạt.
- Kiểm thử lỗi kết nối database: Đạt.
- Backend unittest: 11/11 Passed.
- Kiểm tra dependency: Không phát hiện lỗi.
- Frontend build: Thành công.
- Kiểm tra thao tác lọc và sắp xếp phòng cơ bản: Đã thực hiện.
- Kiểm tra bộ lọc ngày: Chưa xác nhận hoàn chỉnh.

Kết luận này chỉ áp dụng cho phạm vi Week 1 đã thực hiện, không đại diện cho việc toàn bộ hệ thống HMS đã hoàn thành kiểm thử.

# WEEK 2 – REQUEST KIỂM THỬ NGHIỆP VỤ

**Mã công việc:** HMS-W2-THU  
**Issue:** #9 – Quản trị phòng, khung staff và request nghiệp vụ  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Thời gian:** 16/11/2026 – 22/11/2026  
**Trạng thái:** In progress – Một số request chờ Backend công bố endpoint.

## 11. Mục đích kiểm thử Week 2

Bổ sung bộ request phục vụ kiểm tra tích hợp các nghiệp vụ:

- Đăng ký và đăng nhập.
- Tìm kiếm phòng.
- Đặt phòng và kiểm tra ngày không hợp lệ.
- Xem và hủy đặt phòng.
- Kiểm tra truy cập đơn đặt phòng không thuộc tài khoản hiện tại.
- Kiểm tra phân quyền giữa Guest, Staff và Admin.

Phần kiểm thử được thực hiện theo API contract do thành viên phụ trách Backend công bố. Không tự tạo hoặc sửa endpoint thuộc phạm vi Backend của thành viên khác.

## 12. Môi trường và biến kiểm thử

| Thành phần | Giá trị |
|---|---|
| Backend URL | `http://localhost:8000` |
| Công cụ | PowerShell Invoke-RestMethod |
| API hiện có đã xác nhận | `GET /api/health`, `GET /api/rooms` |
| API nghiệp vụ | Chờ Backend công bố |
| Dữ liệu tài khoản | Tài khoản kiểm thử riêng |
| Token | Lấy từ response đăng nhập sau khi API được công bố |

Khai báo biến môi trường:

```powershell
$BaseUrl = "http://localhost:8000"

$GuestToken = $env:HMS_GUEST_TOKEN
$OtherGuestToken = $env:HMS_OTHER_GUEST_TOKEN
$StaffToken = $env:HMS_STAFF_TOKEN
$AdminToken = $env:HMS_ADMIN_TOKEN
```

Không ghi mật khẩu hoặc token thật vào file tài liệu, Git hay ảnh chụp màn hình.

## 13. Danh sách request kiểm thử

### W2-REQ-01 – Lấy danh sách phòng

- **Method:** GET
- **Endpoint:** `/api/rooms`
- **Trạng thái:** Đã có endpoint.
- **Mục đích:** Kiểm tra danh sách phòng và dữ liệu loại phòng.
- **Query parameters đã xác nhận:**
  - `room_type_id`
  - `limit`
  - `offset`

```powershell
Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/rooms"
```

**Kiểm tra:**
- API trả về danh sách phòng.
- Dữ liệu phân trang hoạt động đúng.
- Lọc theo loại phòng hoạt động đúng.
- Xác minh các trường được phép công khai theo API contract.
- Không mặc định coi `housekeeping_status` hoặc `maintenance_status` là dữ liệu công khai khi chưa có xác nhận.

### W2-REQ-02 – Đăng ký tài khoản

- **Method:** POST
- **Endpoint dự kiến:** `/api/auth/register`
- **Trạng thái:** BLOCKED – Chờ Backend xác nhận endpoint và request schema.
- **Mục đích:** Kiểm tra đăng ký tài khoản mới.

**Dữ liệu cần chuẩn bị:**
- Email chưa được sử dụng.
- Mật khẩu kiểm thử.
- Thông tin người dùng theo schema Backend công bố.

**Kết quả mong đợi:**
- Đăng ký thành công khi dữ liệu hợp lệ.
- Có thông báo phù hợp khi email đã tồn tại hoặc dữ liệu không hợp lệ.
- Không trả về mật khẩu dạng văn bản thuần.

### W2-REQ-03 – Đăng nhập thành công

- **Method:** POST
- **Endpoint dự kiến:** `/api/auth/login`
- **Trạng thái:** BLOCKED – Chờ Backend xác nhận endpoint và request schema.
- **Mục đích:** Kiểm tra đăng nhập và nhận token.

**Dữ liệu cần chuẩn bị:**
- Tài khoản Guest kiểm thử.
- Mật khẩu tương ứng.

**Kết quả mong đợi:**
- Đăng nhập thành công với tài khoản hợp lệ.
- Response có thông tin xác thực theo API contract.
- Lưu token vào biến môi trường để sử dụng ở các request tiếp theo.

### W2-REQ-04 – Đăng nhập thất bại

- **Method:** POST
- **Endpoint dự kiến:** `/api/auth/login`
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra tài khoản hoặc mật khẩu không hợp lệ.

**Các trường hợp:**
- Email không tồn tại.
- Mật khẩu không đúng.
- Thiếu trường bắt buộc.
- Dữ liệu đầu vào sai định dạng.

**Kết quả mong đợi:**
- Request bị từ chối phù hợp.
- HTTP status và response body được ghi lại theo kết quả thực tế.
- Không để lộ thông tin nhạy cảm của tài khoản.

### W2-REQ-05 – Tìm kiếm phòng theo ngày

- **Method:** Chờ API contract.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra khả năng tìm phòng theo khoảng thời gian lưu trú.

**Dữ liệu cần kiểm tra:**
- Ngày nhận phòng.
- Ngày trả phòng.
- Số lượng khách.
- Loại phòng nếu API hỗ trợ.

**Kết quả mong đợi:**
- Trả về phòng phù hợp với điều kiện tìm kiếm.
- Không trả về phòng không khả dụng trong khoảng ngày được yêu cầu.
- Kết quả phải dựa trên trạng thái đặt phòng thực tế.

### W2-REQ-06 – Đặt phòng

- **Method:** Chờ API contract.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra tạo đơn đặt phòng.

**Dữ liệu cần chuẩn bị:**
- Guest đã đăng nhập.
- Phòng cần đặt.
- Ngày nhận phòng.
- Ngày trả phòng.
- Số lượng khách.

**Kết quả mong đợi:**
- Tạo đơn đặt phòng thành công khi dữ liệu hợp lệ.
- Không cho phép đặt phòng không khả dụng.
- Kiểm tra dữ liệu đơn đặt phòng sau khi tạo.
- Không tự giả định cấu trúc request hoặc response khi Backend chưa công bố.

### W2-REQ-07 – Kiểm tra ngày không hợp lệ

- **Method:** Chờ API tìm kiếm hoặc đặt phòng được công bố.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra xử lý dữ liệu ngày.

| Mã | Dữ liệu kiểm thử | Kết quả mong đợi |
|---|---|---|
| DATE-01 | Ngày nhận phòng sau ngày trả phòng | Từ chối dữ liệu |
| DATE-02 | Ngày nhận phòng bằng ngày trả phòng | Xử lý theo quy tắc API contract |
| DATE-03 | Ngày nhận phòng trong quá khứ | Từ chối nếu nghiệp vụ không cho phép |
| DATE-04 | Thiếu ngày nhận phòng | Báo lỗi dữ liệu bắt buộc |
| DATE-05 | Sai định dạng ngày | Báo lỗi định dạng |

HTTP status thực tế sẽ được ghi lại sau khi Backend có endpoint.

### W2-REQ-08 – Xem danh sách đặt phòng của tài khoản

- **Method:** Chờ API contract.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra tài khoản Guest xem được đơn đặt phòng của chính mình.

**Kết quả mong đợi:**
- Guest xem được các đơn thuộc tài khoản hiện tại.
- Không hiển thị đơn đặt phòng của Guest khác.
- Dữ liệu trả về phù hợp với quyền của người dùng.

### W2-REQ-09 – Truy cập đơn đặt phòng sai chủ sở hữu

- **Method:** Chờ API contract.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra quyền truy cập tài nguyên.

**Chuẩn bị:**
- Guest A có một đơn đặt phòng.
- Guest B có token riêng.
- Lấy mã đơn đặt phòng thuộc Guest A.

**Thao tác kiểm thử:**
- Đăng nhập bằng Guest B.
- Gửi request truy cập đơn đặt phòng của Guest A.

**Kết quả mong đợi:**
- Guest B không được xem hoặc thao tác trên đơn của Guest A.
- Backend phải kiểm tra quyền sở hữu tài nguyên.
- Không coi việc ẩn nút trên Frontend là cơ chế bảo mật.

### W2-REQ-10 – Hủy đặt phòng

- **Method:** Chờ API contract.
- **Endpoint:** Chưa được xác nhận.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra nghiệp vụ hủy đặt phòng.

**Kết quả mong đợi:**
- Người dùng có quyền được hủy đơn theo quy tắc nghiệp vụ.
- Không cho phép Guest hủy đơn của Guest khác.
- Không cho phép hủy đơn không tồn tại.
- Kiểm tra trạng thái đơn sau khi hủy.
- Ghi nhận HTTP status và response thực tế.

### W2-REQ-11 – Kiểm tra phân quyền Guest, Staff và Admin

- **Method:** Chờ API contract.
- **Endpoint:** Các endpoint cần kiểm tra theo từng nhóm quyền.
- **Trạng thái:** BLOCKED – Chờ Backend công bố.
- **Mục đích:** Kiểm tra quyền truy cập theo vai trò.

| Vai trò | Nội dung cần kiểm tra |
|---|---|
| Guest | Truy cập chức năng dành cho khách |
| Staff | Truy cập chức năng nghiệp vụ được cấp quyền |
| Admin | Truy cập chức năng quản trị được cấp quyền |

**Kết quả mong đợi:**
- Người dùng chỉ truy cập được chức năng phù hợp với quyền được cấp.
- Backend thực hiện xác thực và phân quyền.
- Request không có token hoặc token không hợp lệ phải bị từ chối.
- Không dựa riêng vào việc ẩn nút hoặc ẩn trang trên Frontend để kết luận an toàn.

## 14. Bảng ghi nhận kết quả chạy request

Chỉ điền HTTP status, response và kết quả sau khi request thực sự được chạy.

| Mã request | Ngày chạy | Endpoint | HTTP status | Kết quả thực tế | Minh chứng | Issue liên quan |
|---|---|---|---|---|---|---|
| W2-REQ-01 | 21/11/2026 | GET /api/rooms | HTTP 200; tham số sai HTTP 422 | VERIFIED – Danh sách, phân trang và lọc đạt | Log PowerShell | - |
| W2-REQ-02 | Chờ cập nhật | POST /api/auth/register | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-03 | Chờ cập nhật | POST /api/auth/login | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-04 | Chờ cập nhật | POST /api/auth/login | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-05 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-06 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-07 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-08 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-09 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-10 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |
| W2-REQ-11 | Chờ cập nhật | Chưa xác nhận | BLOCKED | Chờ Backend | - | Chờ xác nhận |

## 15. Quy tắc ghi nhận lỗi tích hợp

Khi phát hiện lỗi, ghi đầy đủ:

1. Mã request.
2. Ngày và môi trường chạy.
3. Endpoint và HTTP method.
4. Dữ liệu đầu vào đã loại bỏ thông tin nhạy cảm.
5. HTTP status thực tế.
6. Response thực tế.
7. Kết quả mong đợi.
8. Kết quả thực tế.
9. Ảnh chụp màn hình hoặc log.
10. Issue liên quan và người phụ trách.

Không ghi nhận lỗi giả định như lỗi đã tái hiện. Các trường hợp đang chờ Backend phải được đánh dấu BLOCKED.

## 16. Tổng kết Week 2

- Đã bổ sung danh sách request kiểm thử nghiệp vụ cần thiết.
- Đã xác định API hiện có: `GET /api/health` và `GET /api/rooms`.
- Các request đăng nhập, đặt phòng, hủy phòng và kiểm tra quyền cần chờ Backend công bố endpoint, schema và cơ chế xác thực.
- Chưa ghi HTTP status hoặc response giả định cho các API chưa có.
- Tiếp tục cập nhật kết quả chạy thực tế và minh chứng sau khi tích hợp Backend.

**Phạm vi phụ trách:** Thanh Thư thực hiện phần giao diện Admin/Staff, tích hợp theo API contract đã công bố và chuẩn bị request kiểm thử. Không tự ý thay đổi endpoint hoặc logic Backend thuộc thành viên khác.

## 17. Kết quả thực tế W2-REQ-01

**Ngày kiểm thử:** 21/11/2026  
**Môi trường:** Windows local – FastAPI tại http://localhost:8000

| STT | Nội dung kiểm thử | Kết quả thực tế | Đánh giá |
|---|---|---|---|
| 1 | GET /api/health | HTTP 200, status ok | Passed |
| 2 | GET /api/rooms | HTTP 200, nhận 4 phòng | Passed |
| 3 | limit=2&offset=0 | HTTP 200, nhận 2 phòng | Passed |
| 4 | oom_type_id=1 | HTTP 200, nhận phòng 101 và 102 | Passed |
| 5 | limit=0 | HTTP 422 | Passed |
| 6 | limit=201 | HTTP 422 | Passed |
| 7 | offset=-1 | HTTP 422 | Passed |
| 8 | oom_type_id=0 | HTTP 422 | Passed |

**Kết luận:** Các trường hợp đã kiểm tra đều cho kết quả đúng với giới hạn và hành vi được khai báo trong API.

**Minh chứng:** Log PowerShell. Không yêu cầu ảnh chụp màn hình trong phạm vi công việc này.

**Trạng thái W2-REQ-01:** VERIFIED.

Lưu ý: housekeeping_status và maintenance_status vẫn chờ xác nhận phạm vi dữ liệu được phép công khai.
