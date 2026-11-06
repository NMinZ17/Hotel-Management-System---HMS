# Cách làm việc và cập nhật tiến độ trên GitHub

Ngày thiết lập: 06/11/2026. Đây là hướng dẫn thao tác; các lệnh dưới đây chưa có nghĩa phần mềm đã được viết hoặc đã chạy.

**1. Bắt đầu một công việc**

1. Mở Issue được giao trong tuần, đọc phụ thuộc và điều kiện đạt. Bấm vào tài khoản assignee để kiểm tra đúng người.
2. Nếu phụ thuộc chưa xong, trao đổi dữ liệu mẫu/hợp đồng với người phụ trách; chỉ ghi đang làm phần có thể thực hiện.
3. Comment trạng thái `Đang làm`, việc cụ thể hôm nay và dự kiến PR. Issue vẫn mở.
4. Tạo một nhánh nhỏ từ main mới nhất. Mỗi máy cần cài Git trước.

```powershell
git clone https://github.com/NMinZ17/Hotel-Management-System---HMS.git
Set-Location Hotel-Management-System---HMS
git switch main
git pull --ff-only
git switch -c feat/w01-minh-room-api
```

Lệnh clone chỉ dùng lần đầu; những lần sau vào thư mục repo rồi bắt đầu từ `git switch main`. Đổi tên nhánh theo người và công việc. Kiểm tra `git status` trước khi chuyển nhánh; nếu còn thay đổi, commit phần đang làm hoặc xử lý rõ ràng, không chạy lệnh xóa/reset để bỏ qua.

**2. Commit và mở Pull Request**

```powershell
git status
git diff
git add backend/app/routers/rooms.py
git commit -m "feat: add room list API"
git push -u origin feat/w01-minh-room-api
```

Đường dẫn trong ví dụ chỉ tồn tại sau khi tác giả tạo file. Chọn đúng file đã sửa; không upload .env, mật khẩu, node_modules, .venv, backup DB hoặc dữ liệu khách thật. Các phiên bản thư viện đã kiểm tra và lockfile cần được commit.

Trên GitHub: Pull requests -> New pull request -> base `main`, compare nhánh của mình. Điền vấn đề/hành vi mới, liên kết Issue, cách kiểm thử và kết quả thực. PR chưa đủ thì để Draft; nhờ reviewer kiểm tra trước khi merge. Chia PR theo phần chạy/kiểm tra được, không chờ hết tuần mới mở một PR lớn.

Với Issue tuần có nhiều đầu việc, các PR nhỏ dùng `Refs #số-issue` để giữ Issue mở. Chỉ PR cuối đáp ứng toàn bộ tiêu chí mới dùng `Closes #số-issue`. GitHub tự đóng khi PR đó merge vào nhánh mặc định; vì vậy phải đọc đủ tiêu chí trước khi dùng từ khóa này. [Cơ chế liên kết PR và Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

**3. Cập nhật cuối mỗi buổi làm**

Sao chép mẫu sau vào comment của Issue đang làm; thay bằng thông tin thật, để Chưa chạy nếu chưa kiểm thử.

```text
Ngày: DD/MM/YYYY
Trạng thái: Chưa bắt đầu / Đang làm / Chờ review / Bị chặn / Hoàn thành
Đã làm: ...
Minh chứng: link commit/PR/ảnh/log ...
Đã kiểm tra: lệnh, dữ liệu, kết quả thực hoặc Chưa chạy ...
Bị chặn bởi: Issue/API/dữ liệu cụ thể, người cần phối hợp ...
Buổi tiếp theo: ...
```

Đánh dấu các checkbox đã thực hiện trong nội dung Issue; bước làm xong chưa đồng nghĩa nghiệm thu đạt. Học xong một bài hoặc commit lên nhánh riêng chưa đủ để ghi cả chức năng đã hoàn thành.

**4. Thống nhất trạng thái và nghiệm thu**

| Trạng thái | Bằng chứng | Trạng thái Issue |
| --- | --- | --- |
| Chưa bắt đầu | Chưa có triển khai | Open |
| Đang làm | Có mô tả đang làm/nhánh/commit | Open |
| Chờ review | Có PR và kết quả tự kiểm tra | Open |
| Bị chặn | Có lỗi/phụ thuộc cụ thể và người phối hợp | Open |
| Hoàn thành | PR cần thiết đã merge, đủ tiêu chí và có minh chứng thực | Closed |

Reviewer đọc diff, thử ca chính/ca lỗi liên quan, ghi kết quả hoặc yêu cầu sửa. Minh merge sau review, hoặc người có quyền được nhóm thống nhất; không tự coi PR đã mở là PR đã được chấp nhận. Sửa lỗi xong cần chạy lại ca liên quan.

**5. Báo cáo tuần**

Mỗi người cập nhật `docs/progress/w01.md` (đổi theo tuần) qua PR: link Issue, trạng thái, minh chứng và blocker. Minh đối chiếu Issue tổng và duyệt báo cáo sau demo. Checklist trên Issue tổng và báo cáo tuần hiện được cập nhật thủ công; không có bot đồng bộ trạng thái. Khi đóng/mở lại Issue, Minh cập nhật checkbox và số việc tương ứng trong buổi tổng hợp.

Đếm số Issue đã nghiệm thu/24 để theo dõi việc bàn giao, không gọi đó là phần trăm độ hoàn thiện phần mềm vì các Issue khác kích thước. Số commit không phải tiến độ chức năng. Nếu đổi phạm vi/thời gian, sửa cả Issue và báo cáo, ghi lý do thay vì âm thầm coi hoàn tất.

Hai buổi tích hợp ngắn và một buổi demo mỗi tuần, tính trong 16–20 giờ/người/tuần. Nếu vướng quá một buổi, comment request/log/dữ liệu thử và người hỗ trợ ngay.
