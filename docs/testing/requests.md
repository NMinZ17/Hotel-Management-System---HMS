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