# Evidence – Ngày 4: API Requests

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người thực hiện:** Đỗ Thị Thanh Thư  
**Ngày ghi nhận:** 17/11/2026  
**Nhánh:** `Thanh-Thư`  
**Môi trường:** Windows local, Python, FastAPI, PostgreSQL 18

## 1. Mục tiêu

Chuẩn bị và kiểm tra hai API:

- `GET /api/health`
- `GET /api/rooms`

Ghi nhận response kỳ vọng, response thực tế và khả năng xử lý lỗi kết nối database.

## 2. API-W1-01 – Health check

**Request:**

```http
GET /api/health
```

**Kết quả kỳ vọng:**

- HTTP 200.
- API trả trạng thái hoạt động.

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

## 3. API-W1-02 – Danh sách phòng

**Request:**

```http
GET /api/rooms
```

**Kết quả kỳ vọng:**

- Request thành công.
- API trả danh sách phòng theo response schema.

**Kết quả thực tế:**

- Request thành công.
- Nhận được 4 bản ghi phòng từ database local `hms_dev`.

**Kết luận:** Đạt.

## 4. API-W1-03 – Danh sách phòng rỗng

**Test:** `test_empty_database_returns_empty_array`

**Công cụ:** Python unittest và FastAPI TestClient.

**Kết quả kỳ vọng:**

- HTTP 200.
- Response `[]`.

**Kết quả thực tế:**

- Test thành công trên schema kiểm thử cô lập.
- API trả về mảng rỗng.

**Kết luận:** Đạt.

## 5. API-W1-04 – Lỗi kết nối database

**Test:** `test_database_failure_returns_safe_503`

**Kết quả kỳ vọng:**

- HTTP 503.
- Thông báo lỗi an toàn.
- Không làm lộ thông tin kết nối nội bộ.

**Kết quả thực tế:**

- Test thành công.
- API trả HTTP 503 khi database không kết nối được.

**Lưu ý:** Đây là kiểm thử lỗi database, không phải kiểm thử tắt tiến trình backend.

**Kết luận:** Đạt.

## 6. Kiểm thử tự động backend

**Lệnh:**

```powershell
python -m unittest discover -s tests -v
```

**Kết quả:**

```text
Ran 11 tests in 6.706s

OK
```

**Kết luận:** 11/11 test thành công.

## 7. Kiểm tra dependency

**Lệnh:**

```powershell
python -m pip check
```

**Kết quả:**

```text
No broken requirements found.
```

**Kết luận:** Không phát hiện dependency bị thiếu hoặc xung đột theo kết quả `pip check`.

## 8. Giới hạn minh chứng

- Đây là kết quả kiểm thử local.
- Chưa đính kèm log terminal gốc hoặc ảnh chụp màn hình.
- Chưa lưu SQL xác nhận trạng thái database thành minh chứng riêng.
- Chưa xác nhận commit hash tại thời điểm chạy.
- Chưa có xác nhận reviewer.

## 9. Kết luận

Các API và test tự động nêu trên đã có kết quả chạy thực tế và đạt theo phạm vi tương ứng.

**Trạng thái:** Đã kiểm thử local – cần bổ sung thông tin môi trường, commit và người kiểm tra trước khi nộp minh chứng hoàn chỉnh.