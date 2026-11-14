# Hotel Management System — HMS

Website quản lý khách sạn theo thiết kế 28 bảng, do nhóm bốn thành viên xây dựng từ số 0 với React, FastAPI và PostgreSQL.

**Backend tuần 1**

FastAPI đã có `GET /api/health` và `GET /api/rooms` đọc PostgreSQL, lọc loại phòng, phân trang và xử lý lỗi. Schema/seed của Trang được lưu trong `database/`, có 28 bảng và 4 phòng mẫu. Kết quả kiểm tra và các việc cần phối hợp nằm trong [báo cáo kiểm thử backend](docs/testing/backend-week1.md).

**Chạy dự án**

Thiết lập Python, database và `.env` theo [hướng dẫn backend](docs/backend-week1.md#thiết-lập-lần-đầu). Mỗi lần chạy, mở PowerShell tại gốc repository:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backend\scripts\start.ps1
```

API: [health](http://127.0.0.1:8000/api/health), [danh sách phòng](http://127.0.0.1:8000/api/rooms), [Swagger UI](http://127.0.0.1:8000/docs). Xem [hợp đồng API](docs/api-contract.md) để ghép frontend.

Theo dõi công việc tại [Issue tổng #1](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/1).

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
4. [Kế hoạch 6 tuần](docs/ke-hoach-6-tuan.md), [hợp đồng API](docs/api-contract.md), [cách lưu minh chứng](docs/testing/evidence-guide.md).

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

**Cấu trúc dự án**

```text
backend/       FastAPI, nghiệp vụ và kiểm thử — Minh, Trang phối hợp dữ liệu
database/      Schema và seed PostgreSQL — Trang
docs/          Hướng dẫn, kế hoạch, báo cáo và minh chứng
```

Frontend React do Linh và Thư phối hợp trong cùng một ứng dụng; cấu hình VM/NGINX được bổ sung theo kế hoạch triển khai. Luồng tuần 1: Trang seed phòng → Minh đọc DB qua API → Linh hiển thị → Thư kiểm tra và tổng hợp lỗi.

**Quy tắc nghiệm thu**

PR nhỏ dùng `Refs #Issue`; chỉ PR cuối đáp ứng hết điều kiện dùng `Closes #Issue`. Reviewer khác tác giả kiểm tra trước merge. Mỗi buổi comment đã làm, PR/commit, kết quả kiểm tra, blocker và buổi tiếp theo. Cuối tuần demo và cập nhật báo cáo qua PR.

Nếu cuối tuần 2 chưa đặt/hủy qua UI–API–DB thật, cần công bố nguy cơ trễ và điều chỉnh phạm vi/nguồn lực/thời hạn. Tuần 6 dùng để ổn định, không để dồn phân hệ mới.

**Nguồn phân công và thiết kế**

- [Hồ sơ phân công của nhóm](https://docs.google.com/document/d/1EurWhqdxOvEVQbDl4tMRdwi2VkauwpOoXqa5YHxWEAY/edit?tab=t.0). Hồ sơ gốc còn mô tả 42 bảng; kế hoạch này theo bản rút gọn 28.
- Tài liệu nhóm: HMS_ERD_28_bang.pdf và Bao_cao_HMS_IEEE.pdf. Hai tài liệu thiết kế không phải bằng chứng phần mềm đã chạy.

