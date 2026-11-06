# Hướng dẫn Mai Ngọc Linh

GitHub: maingoclinh1681. Vai trò: Frontend khách và lễ tân. Reviewer chính: thanhthu-1666.

Trạng thái ban đầu 06/11/2026: cả sáu công việc chưa bắt đầu. Lịch 09/11–20/12 là đề xuất; 16–20 giờ/tuần gồm học, thực hiện, review và tích hợp. Chỉ đánh dấu xong khi có minh chứng, không theo số commit.

**Học để làm ngay**

- JavaScript: mảng/object, import/export, async/await, fetch.
- React: component, props/state, form và routing.
- Loading, empty/error state, gọi API và kiểm thử hành trình người dùng.

Đọc [khởi động](../getting-started.md), [quy trình GitHub](../github-workflow.md) và [hợp đồng API](../api-contract.md). Tên file bên dưới là vị trí dự kiến cần tạo trong quá trình làm, chưa có nghĩa chúng đã tồn tại.

## Tuần 1: Dựng React và hiển thị phòng qua API

Mã HMS-W1-LINH; lịch 09/11/2026–15/11/2026; Issue: [#4](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/4).

Phụ thuộc: có thể bắt đầu ngay; phối hợp dữ liệu/hợp đồng trong tuần 1.

**Thứ tự thực hiện**

1. Ngày 1: clone repo; kiểm tra Node/npm; thống nhất cùng Thư chỉ có một ứng dụng frontend.
2. Ngày 2: tạo Vite React bằng JavaScript; học component, state và fetch; commit package-lock.
3. Ngày 3: làm trang phòng và một API client; dùng mock theo hợp đồng tạm khi Minh chưa có endpoint.
4. Ngày 4: thay mock bằng GET /api/rooms; có trạng thái đang tải, lỗi và không có dữ liệu.
5. Ngày 5: nhờ Thư chạy thử; ghi lỗi vào Issue và mở PR, tránh tự sửa phần backend của Minh.

**File dự kiến**

- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/pages/RoomsPage.jsx`
- `frontend/src/lib/api.js`
- `frontend/.env.example`

**Điều kiện nghiệm thu**

- [ ] Trang phòng hiển thị dữ liệu thật từ backend, có thông báo khi API dừng.
- [ ] Các lệnh npm install/npm run dev được ghi rõ; không commit node_modules.
- [ ] Thư khởi động lại được frontend từ repository.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 2: Giao diện đăng nhập và đặt/hủy phòng

Mã HMS-W2-LINH; lịch 16/11/2026–22/11/2026; Issue: [#8](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/8).

Phụ thuộc: HMS-W1-LINH, HMS-W1-MINH.

**Thứ tự thực hiện**

1. Làm form đăng nhập/đăng ký và hiển thị trạng thái đăng nhập; phối hợp hợp đồng xác thực với Minh.
2. Làm tìm phòng theo ngày/loại phòng; form đặt một phòng và xem xác nhận từ API.
3. Làm danh sách/chi tiết đơn của khách và thao tác hủy có phản hồi rõ.
4. Hiển thị lỗi ngày sai, hết phòng và xung đột; chặn gửi lặp trong lúc request đang xử lý.
5. Kiểm tra khách A không mở được dữ liệu khách B; chuẩn bị form nhiều khách/giảm giá theo hợp đồng đã chốt.

**File dự kiến**

- `frontend/src/pages/LoginPage.jsx`
- `frontend/src/pages/BookingPage.jsx`
- `frontend/src/pages/MyReservationsPage.jsx`
- `frontend/src/lib/api.js`

**Điều kiện nghiệm thu**

- [ ] Khách thực hiện trọn tìm -> đặt -> xem -> hủy trên giao diện với DB thật.
- [ ] Có loading/empty/error; dữ liệu không chỉ nằm trong local mock.
- [ ] Có ảnh/video demo và request chứng minh lỗi/quyền xử lý đúng.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 3: Giao diện lễ tân và chi phí lưu trú

Mã HMS-W3-LINH; lịch 23/11/2026–29/11/2026; Issue: [#12](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/12).

Phụ thuộc: HMS-W2-LINH.

**Thứ tự thực hiện**

1. Làm màn lễ tân tìm đơn, xem chi tiết và check-in, có lý do rõ khi phòng bẩn/bảo trì.
2. Hiển thị folio, tiền phòng, giảm giá, tổng phải trả và trạng thái hóa đơn từ API.
3. Làm ghi nhận tiền mặt/chuyển khoản và check-out; hiển thị công nợ hoặc dịch vụ chưa xong.
4. Kiểm tra tải lại trang và trạng thái sau gửi request; chống bấm lặp ở UI và phối hợp backend bảo vệ.
5. Tích hợp khách đi cùng, giảm giá hoặc nhiều phòng khi API đã đạt; ghi phần thiếu trong Issue.

**File dự kiến**

- `frontend/src/pages/reception/`
- `frontend/src/pages/MyFolioPage.jsx`
- `docs/evidence/w03/`

**Điều kiện nghiệm thu**

- [ ] Lễ tân hoàn thành một lượt lưu trú; khách xem được folio của mình.
- [ ] Không tự tính lại giá phải thu khác backend; thông báo lỗi rõ.
- [ ] Có video/ảnh luồng chính và danh sách phần hoàn thiện bản 28 còn thiếu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 4: Gọi dịch vụ và hoàn thiện UI khách/lễ tân

Mã HMS-W4-LINH; lịch 30/11/2026–06/12/2026; Issue: [#16](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/16).

Phụ thuộc: HMS-W3-LINH.

**Thứ tự thực hiện**

1. Khách đang ở tạo đơn dịch vụ, xem trạng thái và chi phí được ghi vào folio.
2. Hoàn thiện đơn nhiều phòng, khách đi cùng, giảm giá và đánh giá sau check-out theo API.
3. Rà soát form, màn rỗng/lỗi, tải lại dữ liệu và trạng thái hóa đơn trên màn hình nhỏ.
4. Thử tài khoản A truy cập ID của B; cùng Thư ghi lỗi và gửi Minh nếu backend chưa chặn.
5. Chạy ba luồng xuyên suốt, ghi mục chưa đạt thay vì chỉ đánh dấu có màn hình.

**File dự kiến**

- `frontend/src/pages/guest/`
- `frontend/src/pages/reception/`
- `docs/evidence/w04/`

**Điều kiện nghiệm thu**

- [ ] Luồng khách/lễ tân dùng dữ liệu thật và phản ánh đúng thay đổi từ staff.
- [ ] Mục mức B được ghi Đạt/Chưa đạt kèm Issue/PR tương ứng.
- [ ] Không có sai lệch giá hoặc quyền bị che bởi UI.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 5: Kiểm thử UI với dữ liệu lớn và viết hướng dẫn

Mã HMS-W5-LINH; lịch 07/12/2026–13/12/2026; Issue: [#20](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/20).

Phụ thuộc: HMS-W4-LINH.

**Thứ tự thực hiện**

1. Chạy tìm/đặt/hủy, check-in/out, folio và thanh toán trên địa chỉ triển khai.
2. Kiểm tra dữ liệu lớn, phân trang, trạng thái tải và lỗi mạng; sửa lỗi cản trở luồng.
3. Đối chiếu số tiền trên màn hình với API/SQL cùng Trang.
4. Viết hướng dẫn khách và lễ tân theo từng bước, tài khoản giả và ảnh không chứa dữ liệu riêng tư.
5. Chuẩn bị phần demo cá nhân và bàn giao UI cho Thư kiểm tra lại.

**File dự kiến**

- `frontend/src/`
- `docs/user-guide/guest-reception.md`
- `docs/evidence/w05/`

**Điều kiện nghiệm thu**

- [ ] UI hoạt động qua VM1, không chỉ trên máy phát triển.
- [ ] Người khác làm theo hướng dẫn hoàn thành một lượt lưu trú.
- [ ] Ảnh/video có commit và dữ liệu thử rõ.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 6: Nghiệm thu khách/lễ tân và demo

Mã HMS-W6-LINH; lịch 14/12/2026–20/12/2026; Issue: [#24](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/24).

Phụ thuộc: HMS-W5-LINH.

**Thứ tự thực hiện**

1. Kiểm thử chấp nhận toàn bộ hành trình khách và lễ tân qua VM1.
2. Xác nhận số tiền/trạng thái sau đặt, dịch vụ và check-out; ghi lỗi với bước tái hiện.
3. Sửa lỗi UI gây cản trở sử dụng, chạy lại ca liên quan; không thêm tính năng mới.
4. Quay phần demo, cập nhật ảnh/hướng dẫn theo commit chốt.
5. Thử dựng/chạy từ README của người khác và xác nhận điều kiện bàn giao.

**File dự kiến**

- `docs/user-guide/`
- `docs/evidence/w06/`
- `frontend/`

**Điều kiện nghiệm thu**

- [ ] Luồng khách/lễ tân đạt trên bản chốt, có checklist và ảnh/video.
- [ ] Hướng dẫn phù hợp UI hiện tại và tài khoản thử.
- [ ] Mọi phần chưa đạt có Issue và không bị ẩn.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ thanhthu-1666 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

**Buổi làm đầu tiên**

Clone repo, mở Issue tuần 1, tạo nhánh riêng, kiểm tra công cụ. Thực hiện bước nhỏ đầu tiên rồi comment kết quả thực. Nếu vướng quá một buổi, gửi log/request/dữ liệu mẫu vào Issue để nhóm hỗ trợ.
