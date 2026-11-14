# API Request Testing – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần thực hiện:** 09/11/2026 – 15/11/2026  
**Cập nhật lần cuối:** 14/11/2026  
**Trạng thái:** Draft – Chuẩn bị kịch bản, chờ xác nhận và kiểm thử với backend

---

## 1. Mục đích

Tài liệu này ghi lại kế hoạch kiểm thử các API cơ bản của hệ thống HMS trong tuần 1, sử dụng Postman để gửi request và kiểm tra response.

Các mục tiêu chính:

- Kiểm tra khả năng kết nối giữa Postman và backend.
- Kiểm tra response của API sức khỏe hệ thống và API danh sách phòng khi backend hỗ trợ.
- Ghi nhận mã HTTP, cấu trúc response và lỗi phát sinh.
- Phân biệt kết quả mong đợi với kết quả thực tế.
- Cung cấp bằng chứng kiểm thử để nhóm phối hợp xử lý.

**Lưu ý:** Tài liệu này là kế hoạch kiểm thử. Không xem các API được đề xuất trong tài liệu API contract là API đã triển khai nếu chưa kiểm tra trực tiếp trên backend.

## 2. Phạm vi kiểm thử

| Nội dung | Phạm vi |
|---|---|
| Công cụ | Postman |
| Backend | FastAPI |
| Địa chỉ backend dự kiến | `http://localhost:8000` |
| API kiểm tra sức khỏe | `GET /api/health` |
| API danh sách phòng | `GET /api/rooms` |
| Kiểm tra lỗi kết nối | Backend chưa chạy hoặc không truy cập được |
| Kiểm tra dữ liệu rỗng | API danh sách phòng không có dữ liệu |

Các endpoint `/api/health` và `/api/rooms` được ghi nhận trong tài liệu API contract là endpoint dự kiến. Cần xác nhận với thành viên phụ trách backend trước khi kết luận chúng đã được triển khai.

## 3. Chuẩn bị kiểm thử

### 3.1. Điều kiện cần

- Đã cài đặt Postman.
- Backend FastAPI đã được cài đặt và khởi chạy.
- Đã xác nhận địa chỉ và cổng backend đang sử dụng.
- Đã thống nhất endpoint và cấu trúc response với thành viên phụ trách backend.

### 3.2. Cấu hình request

Nếu backend chạy tại máy cá nhân theo cấu hình dự kiến:

```text
Base URL: http://localhost:8000
```

Các request sử dụng Base URL:

```text
{{baseUrl}}/api/health
{{baseUrl}}/api/rooms
```

Có thể tạo biến môi trường trong Postman:

| Variable | Initial value |
|---|---|
| `baseUrl` | `http://localhost:8000` |

Nếu backend sử dụng địa chỉ hoặc cổng khác, cần cập nhật biến này theo cấu hình thực tế.

## 4. Danh sách kịch bản kiểm thử

### API-W1-01: Kiểm tra trạng thái backend

**Mục đích:** Kiểm tra backend có phản hồi request hay không.

- Method: `GET`
- URL dự kiến: `{{baseUrl}}/api/health`
- Body: Không có.

**Kết quả mong đợi:**

- Backend phản hồi thành công.
- HTTP status dự kiến: `200 OK`.
- Response có cấu trúc thể hiện trạng thái hoạt động của hệ thống theo API contract đã thống nhất.

**Kết quả thực tế:**

- Trạng thái: Chưa chạy.
- HTTP status: Chưa ghi nhận.
- Response: Chưa ghi nhận.
- Nguyên nhân: Chưa xác nhận endpoint đã được triển khai trên backend.

### API-W1-02: Lấy danh sách phòng

**Mục đích:** Kiểm tra API trả về danh sách phòng và cấu trúc dữ liệu.

- Method: `GET`
- URL dự kiến: `{{baseUrl}}/api/rooms`
- Body: Không có.

**Kết quả mong đợi:**

- Backend phản hồi thành công khi endpoint được triển khai.
- HTTP status dự kiến: `200 OK`.
- Response trả về danh sách phòng theo cấu trúc API contract.
- Các trường dữ liệu cần được thống nhất với frontend, đặc biệt là mã phòng, số phòng, tầng, loại phòng và trạng thái phòng.

**Kết quả thực tế:**

- Trạng thái: Chưa chạy.
- HTTP status: Chưa ghi nhận.
- Response: Chưa ghi nhận.
- Nguyên nhân: Chưa xác nhận endpoint đã được triển khai và có dữ liệu kiểm thử.

### API-W1-03: Kiểm tra danh sách phòng rỗng

**Mục đích:** Kiểm tra API xử lý trường hợp hệ thống chưa có phòng nào.

- Method: `GET`
- URL dự kiến: `{{baseUrl}}/api/rooms`
- Body: Không có.

**Kết quả mong đợi:**

- API phản hồi theo quy ước đã thống nhất.
- Nếu API trả về danh sách rỗng, response có thể chứa mảng `[]`.
- Frontend cần có trạng thái thông báo chưa có dữ liệu, thay vì hiển thị lỗi hoặc bảng trống không giải thích.

**Kết quả thực tế:**

- Trạng thái: Chưa chạy.
- HTTP status: Chưa ghi nhận.
- Response: Chưa ghi nhận.
- Nguyên nhân: Chưa có môi trường backend và dữ liệu phù hợp để kiểm thử trường hợp này.

### API-W1-04: Kiểm tra lỗi kết nối backend

**Mục đích:** Kiểm tra cách nhận biết và ghi nhận lỗi khi backend không hoạt động hoặc không thể truy cập.

- Method: `GET`
- URL: `{{baseUrl}}/api/health`
- Điều kiện: Backend không chạy hoặc địa chỉ kết nối không hợp lệ.

**Kết quả mong đợi:**

- Request không nhận được response thành công.
- Postman hiển thị lỗi kết nối phù hợp.
- Ghi nhận thông báo lỗi, thời điểm kiểm thử và cấu hình request.
- Frontend cần có thông báo lỗi kết nối dễ hiểu khi gặp tình huống tương tự.

**Kết quả thực tế:**

- Trạng thái: Chưa chạy.
- Lỗi thực tế: Chưa ghi nhận.
- Nguyên nhân: Chưa thực hiện kiểm thử có chủ đích trong môi trường phù hợp.

## 5. Bảng tổng hợp kết quả

| Mã test | Nội dung | Trạng thái | Kết quả |
|---|---|---|---|
| API-W1-01 | Kiểm tra trạng thái backend | Chưa chạy | Chờ xác nhận endpoint |
| API-W1-02 | Lấy danh sách phòng | Chưa chạy | Chờ xác nhận endpoint |
| API-W1-03 | Danh sách phòng rỗng | Chưa chạy | Chờ backend và dữ liệu |
| API-W1-04 | Lỗi kết nối backend | Chưa chạy | Chưa có kết quả thực tế |

**Quy ước trạng thái:**

- `Chưa chạy`: Chưa gửi request kiểm thử.
- `Đạt`: Kết quả thực tế đáp ứng kết quả mong đợi.
- `Không đạt`: Kết quả thực tế không đáp ứng kết quả mong đợi.
- `Bị chặn`: Không thể kiểm thử do thiếu backend, endpoint, dữ liệu hoặc quyền truy cập.

Không chuyển trạng thái sang `Đạt` nếu chưa có response thực tế làm bằng chứng.

## 6. Ghi nhận lỗi khi kiểm thử

Khi một request không đạt hoặc phát sinh lỗi, ghi lại các thông tin sau:

| Thông tin | Nội dung cần ghi |
|---|---|
| Mã test | Ví dụ: API-W1-02 |
| Thời gian | Ngày và giờ kiểm thử |
| Method và URL | Request đã gửi |
| HTTP status | Mã trạng thái nhận được, nếu có |
| Response/Error | Nội dung phản hồi hoặc thông báo lỗi |
| Kết quả mong đợi | Kết quả theo API contract |
| Kết quả thực tế | Kết quả nhận được |
| Người phối hợp | Thành viên phụ trách backend hoặc frontend |
| Hướng xử lý | Cách khắc phục hoặc nội dung cần xác nhận |

Không đưa mật khẩu, access token hoặc thông tin xác thực cá nhân vào ảnh chụp và tài liệu báo cáo.

## 7. Lưu bằng chứng kiểm thử

Việc lưu bằng chứng kiểm thử phải tuân thủ quy ước chung của dự án được mô tả trong:

```text
docs/testing/evidence-guide.md
```

Đối với công việc thuộc tuần 1, minh chứng được lưu theo cấu trúc:

```text
docs/evidence/w01/
```

Tên file minh chứng đề xuất:

```text
API-W1-01.md
API-W1-02.md
API-W1-03.md
API-W1-04.md
```

Mỗi file minh chứng cần tuân thủ các trường thông tin và định dạng được quy định trong `evidence-guide.md`, bao gồm mã test, thời gian thực hiện, môi trường, request, kết quả kỳ vọng, kết quả thực tế và kết luận.

**Nguyên tắc lưu bằng chứng:**

- Chỉ tạo và cập nhật minh chứng khi đã thực hiện kiểm thử thực tế.
- Không tạo ảnh chụp, log hoặc response giả để thay thế kết quả kiểm thử.
- Không ghi nhận trạng thái `Đạt` khi chưa có bằng chứng phù hợp.
- Không đưa mật khẩu, access token hoặc dữ liệu cá nhân thật vào minh chứng.
- Không commit backup database hoặc thông tin kết nối nhạy cảm vào repository.
- Nếu chưa thực hiện kiểm thử, giữ trạng thái `Chưa chạy` hoặc `Bị chặn` và ghi rõ lý do trong tài liệu này.

## 8. Phối hợp với các thành viên

| Thành viên phụ trách | Nội dung cần phối hợp |
|---|---|
| Backend | Xác nhận endpoint, method, response và trạng thái triển khai |
| Database | Xác nhận dữ liệu phòng phục vụ kiểm thử |
| Frontend | Thống nhất cấu trúc response để frontend xử lý dữ liệu và trạng thái lỗi |
| Người phụ trách Issue #5 | Chuẩn bị request, kiểm thử khi đủ điều kiện và ghi nhận kết quả |

Tài liệu này chỉ tập trung vào việc chuẩn bị và kiểm thử request API cơ bản. Việc kiểm thử toàn bộ nghiệp vụ backend, tích hợp cơ sở dữ liệu và triển khai ba tầng không thuộc phạm vi chi tiết của tài liệu này.

Thông tin về môi trường, công cụ, yêu cầu máy chủ ảo và trạng thái triển khai được ghi tại:

```text
docs/deployment/prerequisites.md
```

## 9. Kết luận và công việc tiếp theo

Hiện tại, tài liệu đã chuẩn bị bốn kịch bản kiểm thử cơ bản cho API HMS. Tuy nhiên, chưa thể xác nhận các kịch bản đã đạt vì cần kiểm tra trực tiếp với backend và API contract đã thống nhất.

**Công việc tiếp theo:**

1. Trao đổi với thành viên backend để xác nhận `/api/health` và `/api/rooms` đã được triển khai hay chưa.
2. Xác nhận Base URL, cổng và cấu trúc response thực tế.
3. Gửi request bằng Postman khi backend sẵn sàng.
4. Cập nhật HTTP status, response, trạng thái test và minh chứng theo `docs/testing/evidence-guide.md`.
5. Thông báo các lỗi phát hiện được cho thành viên phụ trách để phối hợp xử lý.

**Trạng thái tổng thể:** Draft – Đã chuẩn bị kịch bản kiểm thử, chưa có kết quả kiểm thử API thực tế.