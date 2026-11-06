# Hướng dẫn Đỗ Thị Thanh Thư

GitHub: thanhthu-1666. Vai trò: Frontend báo cáo/vận hành, VM1 và kiểm thử. Reviewer chính: maingoclinh1681.

Trạng thái ban đầu 06/11/2026: cả sáu công việc chưa bắt đầu. Lịch 09/11–20/12 là đề xuất; 16–20 giờ/tuần gồm học, thực hiện, review và tích hợp. Chỉ đánh dấu xong khi có minh chứng, không theo số commit.

**Học để làm ngay**

- React dùng chung form/bảng/layout với Linh.
- HTTP request, Postman hoặc công cụ tương đương; log và bước tái hiện.
- NGINX: phục vụ React build, proxy API, routing và kiểm tra dịch vụ.

Đọc [khởi động](../getting-started.md), [quy trình GitHub](../github-workflow.md) và [hợp đồng API](../api-contract.md). Tên file bên dưới là vị trí dự kiến cần tạo trong quá trình làm, chưa có nghĩa chúng đã tồn tại.

## Tuần 1: Thiết kế layout chung, request thử và kiểm tra VM

Mã HMS-W1-THU; lịch 09/11/2026–15/11/2026; Issue: [#5](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/5).

Phụ thuộc: có thể bắt đầu ngay; phối hợp dữ liệu/hợp đồng trong tuần 1.

**Thứ tự thực hiện**

1. Ngày 1: clone repo; kiểm tra quyền GitHub; hỏi thông tin tài nguyên ba VM, người cung cấp và thời điểm có thể dùng.
2. Ngày 2: học React qua layout quản trị; thống nhất màu, form, bảng, thông báo với Linh.
3. Ngày 3: tạo các component dùng chung sau khi nhánh khởi tạo frontend của Linh đã merge; không chạy create-vite lần thứ hai.
4. Ngày 4: chuẩn bị request /api/health và /api/rooms, ghi response mong đợi/thực tế và lỗi tái hiện được.
5. Ngày 5: cùng nhóm thử cả ba tầng; kiểm tra README trên máy khác; ghi sơ đồ VM1/VM2/VM3 đề xuất.

**File dự kiến**

- `docs/ui-conventions.md`
- `docs/testing/requests.md`
- `docs/deployment/prerequisites.md`
- `frontend/src/components/`

**Điều kiện nghiệm thu**

- [ ] Có mẫu bảng/form mà cả hai frontend dùng được và request thử tuần 1.
- [ ] Đã ghi tình trạng tài nguyên VM, không đánh dấu đã triển khai khi chưa có máy.
- [ ] Mỗi người đã tự chạy frontend/API/DB theo README hoặc có blocker cụ thể.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 2: Quản trị phòng, khung staff và request nghiệp vụ

Mã HMS-W2-THU; lịch 16/11/2026–22/11/2026; Issue: [#9](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/9).

Phụ thuộc: HMS-W1-THU, HMS-W1-LINH.

**Thứ tự thực hiện**

1. Dùng layout chung làm bảng/form loại phòng, phòng và tiện nghi theo endpoint đã được Minh công bố.
2. Phân biệt dữ liệu công khai với trường admin/staff; không dựa riêng vào việc ẩn nút để khẳng định an toàn.
3. Tạo bộ request đăng nhập, tìm/đặt/hủy, ngày sai và truy cập sai chủ.
4. Tạo lỗi tái hiện được cho vấn đề tích hợp; ghi đầu vào, HTTP status, kết quả thực tế và ảnh/log.
5. Kiểm tra tình trạng VM và chuẩn bị config mẫu, chưa ghi là đã deploy.

**File dự kiến**

- `frontend/src/pages/admin/`
- `frontend/src/pages/staff/`
- `docs/testing/requests.md`
- `docs/testing/bug-log.md`

**Điều kiện nghiệm thu**

- [ ] Admin có màn danh mục tối thiểu dùng API thật hoặc blocker API cụ thể.
- [ ] Request dùng biến môi trường, không chứa tài khoản/URL bí mật trong repo.
- [ ] Danh sách lỗi có mã Issue và người xử lý.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 3: Chạy T01–T05 và triển khai thử

Mã HMS-W3-THU; lịch 23/11/2026–29/11/2026; Issue: [#13](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/13).

Phụ thuộc: HMS-W2-THU, HMS-W2-MINH, HMS-W2-TRANG.

**Thứ tự thực hiện**

1. Chuẩn bị hai kết nối độc lập có điểm bắt đầu gần nhau; cùng Minh cấu hình fixture phòng cuối cùng.
2. Chạy T01 tranh phòng, T02 ngày liền kề, T03 ngày sai, T04 lỗi giữa transaction, T05 hủy lặp/đặt lại.
3. Lưu request/response hoặc log hai luồng, thời điểm, commit và câu SQL Trang xác nhận.
4. Thử dựng frontend/API trên VM1/VM2 khi có tài nguyên; ghi đúng các bước và giới hạn còn thiếu.
5. Chuẩn bị UI nhận dịch vụ và danh sách công việc cho tuần 4.

**File dự kiến**

- `docs/testing/test-cases.md`
- `docs/evidence/w03/`
- `infra/nginx/`
- `docs/deployment/`

**Điều kiện nghiệm thu**

- [ ] T01 có một thành công, một xung đột và đúng một đơn mới hợp lệ.
- [ ] T02–T05 có kết quả thực; ca chưa chạy ghi Chưa chạy kèm lý do.
- [ ] Có hướng dẫn triển khai thử hoặc blocker tài nguyên cụ thể.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 4: UI dịch vụ, dọn phòng, bảo trì và regression

Mã HMS-W4-THU; lịch 30/11/2026–06/12/2026; Issue: [#17](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/17).

Phụ thuộc: HMS-W3-THU, HMS-W2-THU.

**Thứ tự thực hiện**

1. Làm màn phân công/nhận/hoàn thành dịch vụ, danh sách dọn phòng và phiếu bảo trì.
2. Kiểm tra staff chỉ thao tác việc được giao; hiển thị CLEAN/DIRTY/CLEANING và AVAILABLE/BLOCKED tách biệt.
3. Dựng khung sáu báo cáo dạng bảng và bộ lọc ngày; dùng response đã thống nhất với Trang/Minh.
4. Chạy T06 hoàn thành dịch vụ lặp, T07 quyền sở hữu, T08 chốt/thanh toán lặp.
5. Chạy check-out đồng thời hoàn thành dịch vụ; kiểm tra trạng thái cuối với Trang và ghi log.

**File dự kiến**

- `frontend/src/pages/staff/`
- `frontend/src/pages/admin/`
- `docs/testing/test-cases.md`
- `docs/evidence/w04/`

**Điều kiện nghiệm thu**

- [ ] Staff hoàn thành dịch vụ và phí xuất hiện đúng một lần ở folio.
- [ ] T01–T08 có kết quả thực hoặc blocker được ghi rõ; lỗi có Issue.
- [ ] Màn vận hành có thể demo cùng Linh; dashboard có khung cho sáu chỉ tiêu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 5: Dashboard, VM1/NGINX và kiểm thử qua proxy

Mã HMS-W5-THU; lịch 07/12/2026–13/12/2026; Issue: [#21](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/21).

Phụ thuộc: HMS-W4-THU, HMS-W4-TRANG.

**Thứ tự thực hiện**

1. Hiển thị sáu báo cáo dạng bảng và bộ lọc; ghi rõ R01/R02 khác thời điểm, R03 không phải công suất thực ở.
2. Build React, phục vụ bằng NGINX trên VM1 và proxy /api sang VM2.
3. Kiểm tra tải lại URL sâu, asset, API qua proxy và cấu hình endpoint theo môi trường.
4. Chạy regression qua VM1 bằng ba vai trò, đối chiếu dashboard với SQL của Trang.
5. Viết start/restart/config và kịch bản demo, ghi cấu hình mẫu không chứa bí mật.

**File dự kiến**

- `frontend/src/pages/admin/ReportsPage.jsx`
- `infra/nginx/`
- `docs/deployment/vm1.md`
- `docs/evidence/w05/`

**Điều kiện nghiệm thu**

- [ ] React tải được và gọi backend qua proxy; URL sâu tải lại không lỗi.
- [ ] Sáu báo cáo có dữ liệu đúng, không nhân bản tổng tiền.
- [ ] Minh chạy lại được cấu hình VM1 theo tài liệu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 6: Regression cuối, hồ sơ nghiệm thu và demo

Mã HMS-W6-THU; lịch 14/12/2026–20/12/2026; Issue: [#25](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/25).

Phụ thuộc: HMS-W5-THU.

**Thứ tự thực hiện**

1. Chạy T01–T08 qua môi trường phù hợp, lưu request, log, commit và SQL đối chiếu cùng Trang.
2. Kiểm tra routing/proxy/restart và quyền ba vai trò trên VM1.
3. Tập hợp báo cáo sáu tuần, chứng cứ review, benchmark, backup/restore và lỗi đã xử lý.
4. Tổng duyệt ba luồng với cả nhóm; ghi lỗi chặn demo và chạy lại sau sửa.
5. Đối chiếu Issue tổng, tiến độ từng người và trạng thái thực; chỉ đóng việc khi nghiệm thu đủ.

**File dự kiến**

- `docs/testing/`
- `docs/evidence/w06/`
- `docs/release/`
- `infra/nginx/`

**Điều kiện nghiệm thu**

- [ ] Hồ sơ cuối có kết quả thực, không đánh dấu ca chưa chạy là đạt.
- [ ] Video/kịch bản thể hiện đúng bản chạy và đóng góp từng người.
- [ ] Issue tổng và báo cáo cuối phản ánh đúng việc hoàn thành/thiếu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ maingoclinh1681 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

**Buổi làm đầu tiên**

Clone repo, mở Issue tuần 1, tạo nhánh riêng, kiểm tra công cụ. Thực hiện bước nhỏ đầu tiên rồi comment kết quả thực. Nếu vướng quá một buổi, gửi log/request/dữ liệu mẫu vào Issue để nhóm hỗ trợ.
