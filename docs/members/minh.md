# Hướng dẫn Nguyễn Nhật Minh

GitHub: NMinZ17. Vai trò: Backend, tích hợp và release. Reviewer chính: maitrang1112.

Trạng thái ban đầu 06/11/2026: cả sáu công việc chưa bắt đầu. Lịch 09/11–20/12 là đề xuất; 16–20 giờ/tuần gồm học, thực hiện, review và tích hợp. Chỉ đánh dấu xong khi có minh chứng, không theo số commit.

**Học để làm ngay**

- Python: hàm, kiểu dữ liệu, exception và virtual environment.
- HTTP/JSON, FastAPI route, validation và dependency.
- Truy vấn có bind parameter, transaction, khóa dòng và quyền đối tượng.

Đọc [khởi động](../getting-started.md), [quy trình GitHub](../github-workflow.md) và [hợp đồng API](../api-contract.md). Tên file bên dưới là vị trí dự kiến cần tạo trong quá trình làm, chưa có nghĩa chúng đã tồn tại.

## Tuần 1: Dựng FastAPI và API đọc danh sách phòng

Mã HMS-W1-MINH; lịch 09/11/2026–15/11/2026; Issue: [#2](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/2).

Phụ thuộc: có thể bắt đầu ngay; phối hợp dữ liệu/hợp đồng trong tuần 1.

**Thứ tự thực hiện**

1. Ngày 1: clone repo, tạo nhánh riêng; kiểm tra Python/Git và ghi phiên bản dùng chung.
2. Ngày 2: tạo virtual environment, học route GET và response JSON; viết GET /api/health.
3. Ngày 3: nhận schema/seed từ Trang; kết nối PostgreSQL bằng cấu hình môi trường; viết GET /api/rooms có bind parameter.
4. Ngày 4: thống nhất response room_id, room_number, room_type_id, housekeeping_status, maintenance_status; ghép với Linh và sửa CORS hoặc proxy phát triển.
5. Ngày 5: ghi lệnh chạy và lỗi cài đặt; nhờ Trang dựng backend từ đầu; mở PR nhỏ để review.

**File dự kiến**

- `backend/app/main.py`
- `backend/app/db.py`
- `backend/app/routers/rooms.py`
- `backend/requirements.txt`
- `docs/api-contract.md`

**Điều kiện nghiệm thu**

- [ ] GET /api/health trả 200; GET /api/rooms đọc DB thật, không phải danh sách cố định trong code.
- [ ] Thay dữ liệu seed rồi tải lại thì frontend hiển thị dữ liệu mới.
- [ ] requirements có phiên bản đã kiểm tra; có PR và hướng dẫn chạy.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 2: Xác thực, tìm phòng và đặt/hủy cơ bản

Mã HMS-W2-MINH; lịch 16/11/2026–22/11/2026; Issue: [#6](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/6).

Phụ thuộc: HMS-W1-MINH, HMS-W1-TRANG.

**Thứ tự thực hiện**

1. Chốt hợp đồng đăng ký/đăng nhập và thông báo lỗi với Linh; băm mật khẩu, xác định ADMIN/STAFF/GUEST.
2. Viết phòng trống theo loại phòng và khoảng ngày; xác thực check-out sau check-in, số khách hợp lệ.
3. Đặt một phòng vật lý bằng transaction: khóa phòng, đọc lại lịch, tạo đầu đơn/chi tiết/khách/audit rồi commit.
4. Khách chỉ đọc/hủy đơn của mình; hủy cập nhật cả đầu đơn và chi tiết, giữ lịch sử.
5. Chuẩn bị hợp đồng đơn nhiều phòng, khách đi cùng và một mã giảm giá; không kết luận hết phòng chỉ vì một ứng viên bị tranh mất.

**File dự kiến**

- `backend/app/routers/auth.py`
- `backend/app/routers/reservations.py`
- `backend/app/services/booking.py`
- `backend/tests/`

**Điều kiện nghiệm thu**

- [ ] UI đặt/hủy qua API thật; không trả thành công nếu transaction thất bại.
- [ ] Đặt trùng tuần tự và ngày sai bị từ chối; hủy lặp không làm sai trạng thái.
- [ ] Kiểm tra quyền nằm tại API; log không chứa mật khẩu hay chuỗi kết nối.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 3: Check-in/out, folio, hóa đơn và thanh toán

Mã HMS-W3-MINH; lịch 23/11/2026–29/11/2026; Issue: [#10](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/10).

Phụ thuộc: HMS-W2-MINH, HMS-W2-TRANG.

**Thứ tự thực hiện**

1. Check-in xác nhận đơn hợp lệ, phòng CLEAN và không BLOCKED; tạo stay/stay_room/folio trong một transaction.
2. Tính tiền phòng từ số đêm và giá snapshot; ghi giảm giá theo quy tắc; giữ tiền chính xác.
3. Tạo hóa đơn/ghi nhận tiền mặt hoặc chuyển khoản; kiểm tra tổng thu không vượt phải trả và chống request lặp.
4. Check-out yêu cầu thu đủ, không còn dịch vụ đang xử lý; chốt dữ liệu, chuyển phòng DIRTY và tạo nhiệm vụ dọn.
5. Chạy cùng Thư/Trang các test đặt tranh chấp/rollback; bổ sung đơn nhiều phòng với khóa thứ tự và tính nguyên tử.

**File dự kiến**

- `backend/app/services/stays.py`
- `backend/app/services/billing.py`
- `backend/app/routers/stays.py`
- `backend/tests/`

**Điều kiện nghiệm thu**

- [ ] Đặt -> check-in -> folio -> thanh toán -> check-out chạy đủ, số tiền khớp fixture.
- [ ] Thao tác lặp không sinh thêm stay/folio/hóa đơn/tiền; lỗi giữa transaction rollback.
- [ ] T01–T05 có minh chứng; đơn nhiều phòng chưa đạt phải ghi rõ thiếu, không đánh dấu hoàn thiện.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 4: Dịch vụ, vận hành, quyền và nghiệp vụ bổ sung

Mã HMS-W4-MINH; lịch 30/11/2026–06/12/2026; Issue: [#14](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/14).

Phụ thuộc: HMS-W3-MINH.

**Thứ tự thực hiện**

1. API tạo/nhận/hoàn thành dịch vụ; khóa folio trước đơn dịch vụ và ghi phí/đổi trạng thái/audit trong một transaction.
2. Đảm bảo source_key/quan hệ UNIQUE ngăn tính phí hai lần; không ghi thêm phí sau chốt.
3. API giao/hoàn thành dọn phòng và bảo trì; không gộp trạng thái sạch với trạng thái sửa chữa.
4. Hoàn thiện nhiều phòng/nhiều khách, một mã giảm giá và đánh giá sau check-out nếu chưa xong.
5. Rà quyền từng đối tượng cho GUEST/STAFF/ADMIN và đồng bộ OpenAPI; chốt danh sách chức năng còn thiếu cuối tuần.

**File dự kiến**

- `backend/app/services/`
- `backend/app/routers/`
- `backend/tests/`

**Điều kiện nghiệm thu**

- [ ] Ba luồng chính chạy được; lỗi ghi phí rollback trạng thái dịch vụ.
- [ ] T06–T08 và kiểm tra quyền có thể chạy; mỗi mục mức B có trạng thái rõ.
- [ ] Không còn thay đổi chức năng mới sau mốc khóa tuần 4 trừ xử lý phần đã cam kết.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 5: API báo cáo, triển khai VM2 và bản ứng viên

Mã HMS-W5-MINH; lịch 07/12/2026–13/12/2026; Issue: [#18](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/18).

Phụ thuộc: HMS-W4-MINH, HMS-W4-TRANG.

**Thứ tự thực hiện**

1. Đưa SQL báo cáo qua endpoint admin, validate bộ lọc ngày và giới hạn dữ liệu trả về.
2. Bổ sung phân trang các danh sách cần thiết, sửa vấn đề phát hiện bởi dữ liệu lớn.
3. Dựng FastAPI trên VM2 theo cấu hình mẫu; kết nối VM3 với Trang và VM1 với Thư.
4. Chạy lại transaction trong môi trường triển khai; ghi commit của bản ứng viên.
5. Viết start/restart/rollback và phối hợp backup/restore; không đẩy cấu hình bí mật lên GitHub.

**File dự kiến**

- `backend/app/routers/reports.py`
- `infra/`
- `docs/deployment/`
- `docs/evidence/w05/`

**Điều kiện nghiệm thu**

- [ ] Ba VM kết nối và chạy ba luồng qua địa chỉ triển khai.
- [ ] API sáu báo cáo khớp SQL fixture và chỉ admin được xem báo cáo quản trị.
- [ ] Có commit bản ứng viên và hướng dẫn vận hành cơ bản.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 6: Chốt release và sửa lỗi nghiệp vụ

Mã HMS-W6-MINH; lịch 14/12/2026–20/12/2026; Issue: [#22](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/22).

Phụ thuộc: HMS-W5-MINH.

**Thứ tự thực hiện**

1. Ngày 1–2 xử lý lỗi API/transaction được Thư/Linh tái hiện; chạy lại test liên quan.
2. Ngày 3 chốt commit ứng viên và kiểm tra cài mới cùng Trang.
3. Ngày 4 thử restart/rollback trên môi trường thử và chạy lại qua ba VM.
4. Ngày 5 tổng duyệt demo; xác nhận danh sách phần chưa đạt và giới hạn.
5. Ngày 6–7 chỉ sửa lỗi chặn bàn giao; tag release sau khi nhóm review bằng chứng.

**File dự kiến**

- `README.md`
- `docs/release/`
- `backend/`
- `infra/`

**Điều kiện nghiệm thu**

- [ ] Không còn lỗi đặt trùng/sai tiền/sai quyền/mất dữ liệu hay chặn ba luồng.
- [ ] Có release/tag và commit tương ứng hướng dẫn/cấu hình/DB.
- [ ] Phần chưa hoàn thành không bị ghi thành hoàn tất.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maitrang1112 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

**Buổi làm đầu tiên**

Clone repo, mở Issue tuần 1, tạo nhánh riêng, kiểm tra công cụ. Thực hiện bước nhỏ đầu tiên rồi comment kết quả thực. Nếu vướng quá một buổi, gửi log/request/dữ liệu mẫu vào Issue để nhóm hỗ trợ.
