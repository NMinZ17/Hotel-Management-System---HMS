# Hotel Management System — HMS

Website quản lý khách sạn theo thiết kế 28 bảng, do nhóm bốn thành viên xây dựng từ số 0 với React, FastAPI và PostgreSQL.

**Tiến độ ghi nhận ngày 06/11/2026**

- Tổ chức công việc: đã tạo kế hoạch, hướng dẫn cá nhân, quy trình GitHub và 24 Issue có người phụ trách.
- Phát triển phần mềm: **0/24 công việc tuần được nghiệm thu; tất cả Chưa bắt đầu**. Chưa có backend/frontend/database chạy được được xác nhận trong repo.
- Chưa có kết quả kiểm thử, benchmark hoặc triển khai được xác nhận. Repository hiện chứa bộ tài liệu khởi động; các file code trong hướng dẫn là việc cần tạo.
- Lịch đề xuất: 09/11–20/12/2026; 16–20 giờ/người/tuần, bao gồm học, thực hiện, review và tích hợp.

Theo dõi tại [Issue tổng #1](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/1). Các trạng thái và báo cáo được cập nhật thủ công theo minh chứng; không có bot tự đồng bộ.

**Mỗi thành viên bắt đầu ở đây**

| Thành viên | Hướng dẫn 6 tuần | Công việc đầu tiên |
| --- | --- | --- |
| Nguyễn Nhật Minh (NMinZ17) | [Hướng dẫn Minh](docs/members/minh.md) | [#2](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/2) |
| Phan Thị Mai Trang (maitrang1112) | [Hướng dẫn Trang](docs/members/trang.md) | [#3](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/3) |
| Mai Ngọc Linh (maingoclinh1681) | [Hướng dẫn Linh](docs/members/linh.md) | [#4](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/4) |
| Đỗ Thị Thanh Thư (thanhthu-1666) | [Hướng dẫn Thư](docs/members/thu.md) | [#5](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/5) |

**Thứ tự đọc**

1. [Cài công cụ và chạy luồng đầu tiên](docs/getting-started.md).
2. [Cách nhận việc, commit, mở PR và cập nhật tiến độ](docs/github-workflow.md).
3. Hướng dẫn cá nhân trong bảng trên: mỗi tuần có thứ tự làm, phụ thuộc, file dự kiến, tiêu chí và minh chứng.
4. [Kế hoạch 6 tuần từ số 0](docs/ke-hoach-6-tuan.md), [hợp đồng tích hợp tạm](docs/api-contract.md), [cách lưu minh chứng](docs/testing/evidence-guide.md).

**Các mốc tuần**

| Tuần | Lịch đề xuất | Điều kiện nghiệm thu | Báo cáo |
| --- | --- | --- | --- |
| 1 | 09/11/2026–15/11/2026 | React đọc phòng từ PostgreSQL qua FastAPI; cả bốn máy chạy được. | [Tuần 1](docs/progress/w01.md) |
| 2 | 16/11/2026–22/11/2026 | Đăng nhập, tìm, đặt/hủy một phòng qua API thật; migration đủ 28 bảng. | [Tuần 2](docs/progress/w02.md) |
| 3 | 23/11/2026–29/11/2026 | Check-in, folio, hóa đơn, thanh toán, check-out; T01–T05 có log thật. | [Tuần 3](docs/progress/w03.md) |
| 4 | 30/11/2026–06/12/2026 | Ba luồng chạy đủ; kiểm tra phạm vi nhiều phòng/khách, giảm giá, đánh giá. | [Tuần 4](docs/progress/w04.md) |
| 5 | 07/12/2026–13/12/2026 | Sáu báo cáo, benchmark/index, backup/restore và 3 VM. | [Tuần 5](docs/progress/w05.md) |
| 6 | 14/12/2026–20/12/2026 | Regression, cài mới, release, báo cáo và demo. | [Tuần 6](docs/progress/w06.md) |

**Phạm vi**

Ưu tiên ba luồng đặt phòng/lưu trú, dịch vụ ghi phí và vận hành. Giữ ba vai trò ADMIN/STAFF/GUEST. Bản đầy đủ 28 bảng còn bao gồm đơn nhiều phòng/khách, một mã giảm giá và đánh giá; chưa chạy mục nào thì ghi thiếu, không dùng số bảng để tuyên bố hoàn thành.

Nhà hàng/kho riêng, lịch vui chơi/spa, đa khách sạn và cổng thanh toán thật nằm ngoài bản rút gọn. Thanh toán là ghi nhận tiền mặt/chuyển khoản; hóa đơn là nội bộ.

**Vị trí mã nguồn dự kiến**

```text
backend/       FastAPI, nghiệp vụ và kiểm thử — Minh, Trang phối hợp dữ liệu
frontend/      Một ứng dụng React dùng chung — Linh và Thư
database/      SQL migration, seed, reports, benchmarks — Trang
infra/         VM và NGINX — Minh/Thư/Trang theo thành phần
docs/          Hướng dẫn, kế hoạch, báo cáo và minh chứng
```

Các thư mục thực thi sẽ được tạo trong PR tương ứng. Tuần 1 không yêu cầu làm xong mọi màn: Trang seed phòng → Minh đọc DB qua API → Linh hiển thị → Thư kiểm tra và tổng hợp lỗi.

**Quy tắc nghiệm thu**

PR nhỏ dùng `Refs #Issue`; chỉ PR cuối đáp ứng hết điều kiện dùng `Closes #Issue`. Reviewer khác tác giả kiểm tra trước merge. Mỗi buổi comment đã làm, PR/commit, kết quả kiểm tra, blocker và buổi tiếp theo. Cuối tuần demo và cập nhật báo cáo qua PR.

Nếu cuối tuần 2 chưa đặt/hủy qua UI–API–DB thật, cần công bố nguy cơ trễ và điều chỉnh phạm vi/nguồn lực/thời hạn. Tuần 6 dùng để ổn định, không để dồn phân hệ mới.

**Nguồn phân công và thiết kế**

- [Hồ sơ phân công của nhóm](https://docs.google.com/document/d/1EurWhqdxOvEVQbDl4tMRdwi2VkauwpOoXqa5YHxWEAY/edit?tab=t.0). Hồ sơ gốc còn mô tả 42 bảng; kế hoạch này theo bản rút gọn 28.
- Tài liệu nhóm: HMS_ERD_28_bang.pdf và Bao_cao_HMS_IEEE.pdf. Hai tài liệu thiết kế không phải bằng chứng phần mềm đã chạy.
