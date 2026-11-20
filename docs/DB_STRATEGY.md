# Chiến lược Phân tách Cơ sở dữ liệu & Nạp dữ liệu mẫu (Seed Strategy)

## 1. Kiến trúc tách 3 môi trường cơ sở dữ liệu

Hệ thống Quản lý Khách sạn (HMS) tách biệt hoàn toàn 3 cơ sở dữ liệu trên PostgreSQL 14+ nhằm đảm bảo an toàn dữ liệu phát triển, tính lặp lại của kiểm thử tự động và độ chính xác khi đo hiệu năng:

| Thuộc tính | `hms_dev` (Phát triển) | `hms_test` (Kiểm thử tự động) | `hms_bench` (Đo hiệu năng) |
| :--- | :--- | :--- | :--- |
| **User sở hữu** | `hms_dev_user` | `hms_test_user` | `hms_bench_user` |
| **Mục đích** | Lập trình API, debug giao diện, kiểm tra thủ công các trạng thái đặt phòng/lưu trú. | Chạy Integration Test & kiểm tra 12 quy tắc toàn vẹn dữ liệu tự động. | Đo độ trễ index GiST, truy vấn tìm phòng trống và báo cáo doanh thu tải lớn. |
| **Kịch bản Seed** | `01_master_seed.sql` + `02_dev_fixture.sql` | `01_master_seed.sql` + `03_test_fixture.sql` | `01_master_seed.sql` + `04_bench_seed.sql` |
| **Cơ chế reset** | Chạy `V001__rollback_hms_schema.sql` rồi migrate & seed lại khi cần. | Bọc mọi test case trong `BEGIN; ... ROLLBACK;` hoặc nhân bản từ template DB. | Giữ cố định tập dữ liệu lớn (100.000 đặt phòng) và chạy `VACUUM ANALYZE`. |

---

## 2. Chiến lược Seed 4 tầng

1. **Tầng 1 — Master Seed (`01_master_seed.sql`):**
   - Nạp danh mục gốc ít thay đổi (`hotel`, `room_type`, `amenity`, `role`, `service`, `discount`).
   - Sử dụng `ON CONFLICT DO NOTHING` và tự đồng bộ `IDENTITY` sequence nên có thể chạy lại nhiều lần trên cả 3 môi trường mà không gây lỗi trùng khóa.
2. **Tầng 2 — Dev Fixture (`02_dev_fixture.sql`):**
   - Chỉ nạp cho `hms_dev`, tái hiện đủ 3 trạng thái thực tế của khách sạn: đặt phòng tương lai (`CONFIRMED`), lượt ở đã thanh toán xong (`CHECKED_OUT`), và khách đang ở tại phòng (`IN_HOUSE`) kèm công việc dọn buồng/bảo trì đang mở.
3. **Tầng 3 — Test Fixture (`03_test_fixture.sql`):**
   - Chỉ nạp cho `hms_test`, giữ tập bản ghi tối thiểu với ID cố định (deterministic) để các bài kiểm thử tự động luôn tham chiếu đúng dữ liệu đầu vào.
4. **Tầng 4 — Benchmark Seed (`04_bench_seed.sql`):**
   - Chỉ nạp cho `hms_bench`, sử dụng `generate_series` sinh **200 phòng**, **20.000 khách**, **100.000 đơn đặt phòng** chia theo các khung 3 ngày liền kề `[start, start + 3)` đảm bảo 0% xung đột ràng buộc `EXCLUDE USING gist`, kèm **70.400 lượt lưu trú** và chạy `VACUUM ANALYZE` ở cuối.

---

## 3. Hướng dẫn triển khai từ đầu bằng dòng lệnh

### Bước 1: Tạo 3 cơ sở dữ liệu và 3 tài khoản riêng biệt
```bash
psql -U postgres -v ON_ERROR_STOP=1 -f database/scripts/init_databases.sql
```

### Bước 2: Thiết lập môi trường Phát triển (`hms_dev`)
```bash
psql -U hms_dev_user -d hms_dev -v ON_ERROR_STOP=1 -f database/migrations/V001__init_hms_schema.sql
psql -U hms_dev_user -d hms_dev -v ON_ERROR_STOP=1 -f database/seeds/01_master_seed.sql
psql -U hms_dev_user -d hms_dev -v ON_ERROR_STOP=1 -f database/seeds/02_dev_fixture.sql
```

### Bước 3: Thiết lập môi trường Kiểm thử (`hms_test`) và chạy bộ test Transaction
```bash
psql -U hms_test_user -d hms_test -v ON_ERROR_STOP=1 -f database/migrations/V001__init_hms_schema.sql
psql -U hms_test_user -d hms_test -v ON_ERROR_STOP=1 -f database/seeds/01_master_seed.sql
psql -U hms_test_user -d hms_test -v ON_ERROR_STOP=1 -f database/seeds/03_test_fixture.sql
psql -U hms_test_user -d hms_test -v ON_ERROR_STOP=1 -f database/tests/verify_rules.sql
```

### Bước 4: Thiết lập môi trường Benchmark (`hms_bench`)
```bash
psql -U hms_bench_user -d hms_bench -v ON_ERROR_STOP=1 -f database/migrations/V001__init_hms_schema.sql
psql -U hms_bench_user -d hms_bench -v ON_ERROR_STOP=1 -f database/seeds/01_master_seed.sql
psql -U hms_bench_user -d hms_bench -v ON_ERROR_STOP=1 -f database/seeds/04_bench_seed.sql
```

### Bước 5: Hoàn tác schema về DB rỗng (khi cần làm lại từ đầu)
```bash
psql -U hms_dev_user -d hms_dev -v ON_ERROR_STOP=1 -f database/migrations/V001__rollback_hms_schema.sql
```