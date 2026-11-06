# Hướng dẫn Phan Thị Mai Trang

GitHub: maitrang1112. Vai trò: CSDL và backend dữ liệu. Reviewer chính: NMinZ17.

Trạng thái ban đầu 06/11/2026: cả sáu công việc chưa bắt đầu. Lịch 09/11–20/12 là đề xuất; 16–20 giờ/tuần gồm học, thực hiện, review và tích hợp. Chỉ đánh dấu xong khi có minh chứng, không theo số commit.

**Học để làm ngay**

- PostgreSQL: SELECT, JOIN, INSERT, UPDATE; PK/FK/UNIQUE/CHECK.
- Migration có thứ tự, transaction, index và EXPLAIN.
- Fixture tính tay, sinh dữ liệu theo quan hệ và backup/restore.

Đọc [khởi động](../getting-started.md), [quy trình GitHub](../github-workflow.md) và [hợp đồng API](../api-contract.md). Tên file bên dưới là vị trí dự kiến cần tạo trong quá trình làm, chưa có nghĩa chúng đã tồn tại.

## Tuần 1: Tạo dữ liệu phòng đầu tiên và bản đồ 28 bảng

Mã HMS-W1-TRANG; lịch 09/11/2026–15/11/2026; Issue: [#3](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/3).

Phụ thuộc: có thể bắt đầu ngay; phối hợp dữ liệu/hợp đồng trong tuần 1.

**Thứ tự thực hiện**

1. Ngày 1: đọc ERD 28; liệt kê bảng/PK/FK, tách mô hình dữ liệu với phần đã thực thi.
2. Ngày 2: cài PostgreSQL; tạo DB phát triển riêng và kết nối bằng psql hoặc pgAdmin; ghi phiên bản.
3. Ngày 3: viết migration room_type và room theo đúng cột ERD; seed 5–10 phòng, tối thiểu hai loại.
4. Ngày 4: cùng Minh kiểm tra SELECT; giải thích giá, trạng thái sạch và trạng thái bảo trì là các trường khác nhau.
5. Ngày 5: thử dựng lại trên DB rỗng và ghi thứ tự chạy, kết quả truy vấn; gửi PR cho Minh.

**File dự kiến**

- `database/migrations/001_rooms.sql`
- `database/seeds/001_rooms.sql`
- `docs/data-dictionary.md`
- `docs/database-setup.md`

**Điều kiện nghiệm thu**

- [ ] Migration và seed chạy được trên DB mới; không sửa tay bằng GUI mà thiếu script tương ứng.
- [ ] Minh và Linh đọc được cùng một bộ dữ liệu phòng.
- [ ] Từ điển nháp liệt kê đủ 28 bảng và những bảng chưa tạo.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 2: Hoàn thiện migration 28 bảng và fixture thử

Mã HMS-W2-TRANG; lịch 16/11/2026–22/11/2026; Issue: [#7](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/7).

Phụ thuộc: HMS-W1-TRANG.

**Thứ tự thực hiện**

1. Tạo các migration tiếp theo theo thứ tự FK; đồng bộ tên cột/kiểu với ERD và ghi lại mọi thay đổi đã thống nhất.
2. Thêm PK/FK/UNIQUE/CHECK, extension/ràng buộc chống lịch chồng lấn; phân biệt quy tắc DDL với quy tắc phải làm ở transaction.
3. Seed ba vai trò, tài khoản thử, khách, nhân viên, phòng và dịch vụ bằng dữ liệu giả.
4. Tạo SQL đếm bảng schema hms, kiểm tra quan hệ mồ côi và lịch phòng; chuẩn bị fixture hai khách tranh phòng cuối cùng.
5. Nhờ Minh chạy từ DB rỗng; lưu lệnh, kết quả và cập nhật từ điển.

**File dự kiến**

- `database/migrations/`
- `database/seeds/`
- `database/checks/`
- `docs/data-dictionary.md`

**Điều kiện nghiệm thu**

- [ ] Schema nghiệp vụ có đúng 28 bảng; DB mới dựng được theo script.
- [ ] FK và ràng buộc thử âm hoạt động; không dùng dữ liệu khách thật.
- [ ] Fixture nhỏ tái tạo được, giá trị kỳ vọng được ghi rõ.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 3: Fixture tiền và SQL kiểm chứng transaction

Mã HMS-W3-TRANG; lịch 23/11/2026–29/11/2026; Issue: [#11](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/11).

Phụ thuộc: HMS-W2-TRANG.

**Thứ tự thực hiện**

1. Tạo fixture có số tiền tính tay: số đêm, nhiều dòng phí, giảm giá và nhiều payment của một hóa đơn.
2. Viết truy vấn xác nhận đầu đơn/chi tiết/audit trước và sau rollback; kiểm tra lịch phòng và quan hệ stay/folio/invoice.
3. Đối chiếu log hai kết nối với trạng thái DB; không dùng test tuần tự làm bằng chứng concurrency.
4. Viết SQL nháp R01–R06 với định nghĩa ngày và mẫu số rõ ràng; tránh nhân bản tổng khi JOIN.
5. Review phần khóa, transaction và kiểu dữ liệu tiền trong PR của Minh.

**File dự kiến**

- `database/seeds/financial_fixture.sql`
- `database/checks/`
- `database/reports/`
- `docs/evidence/w03/`

**Điều kiện nghiệm thu**

- [ ] Có bảng đáp án kỳ vọng và SQL tính lại cho cùng fixture.
- [ ] Có SQL chứng minh rollback, hủy lặp và không trùng lịch.
- [ ] R01–R06 có truy vấn ban đầu và giới hạn cách hiểu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 4: SQL sáu báo cáo và script seed lớn

Mã HMS-W4-TRANG; lịch 30/11/2026–06/12/2026; Issue: [#15](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/15).

Phụ thuộc: HMS-W3-TRANG.

**Thứ tự thực hiện**

1. Chốt R01 giá trị hóa đơn, R02 tiền thu, R03 tỷ lệ phòng đã đặt, R04 phí dịch vụ, R05 công nợ, R06 vận hành.
2. Tạo fixture nhiều payment và nhiều folio_item để phát hiện nhân bản SUM; so kết quả với đáp án tính tay.
3. Viết seed xác định bằng seed cố định, theo quan hệ và lịch phòng hợp lệ; thử mức nhỏ trước.
4. Phân bố phí theo nhiều ngày/folio, không dồn toàn bộ một folio và không ép mọi bảng 100k dòng.
5. Đối chiếu migration/từ điển/ERD và hỗ trợ Minh lớp truy vấn cho API báo cáo.

**File dự kiến**

- `database/reports/`
- `database/seeds/`
- `docs/evidence/w04/`
- `docs/data-dictionary.md`

**Điều kiện nghiệm thu**

- [ ] Sáu SQL có kết quả kỳ vọng đúng, ghi rõ giới hạn chỉ tiêu.
- [ ] Script seed chạy được từ fixture nhỏ và có kế hoạch tăng quy mô.
- [ ] Schema/từ điển phản ánh bản triển khai.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 5: Benchmark dữ liệu lớn, index và restore

Mã HMS-W5-TRANG; lịch 07/12/2026–13/12/2026; Issue: [#19](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/19).

Phụ thuộc: HMS-W4-TRANG.

**Thứ tự thực hiện**

1. Sinh mục tiêu 120k folio_item, 30k housekeeping_task, 25k service_order_item và số reservation/stay/folio hợp lý khoảng 10–12k mỗi bảng.
2. Ghi số dòng thực, phiên bản, máy/VM và seed; chạy ANALYZE trước phép đo.
3. Đo truy vấn lọc folio_id/thời gian, ORDER BY occurred_at DESC, folio_item_id DESC LIMIT 50 trước index.
4. Tạo index ứng viên (folio_id, occurred_at DESC, folio_item_id DESC); đo cùng truy vấn/dữ liệu ít nhất ba lần mỗi phương án bằng EXPLAIN (ANALYZE, BUFFERS).
5. Backup DB thử, restore vào DB riêng và xác nhận số dòng, quan hệ, một số hóa đơn và báo cáo.

**File dự kiến**

- `database/benchmarks/`
- `database/seeds/`
- `docs/evidence/w05/`
- `docs/deployment/backup-restore.md`

**Điều kiện nghiệm thu**

- [ ] Có file kế hoạch trước/sau và số đo thực, không bịa mức tăng tốc.
- [ ] Bộ dữ liệu tôn trọng FK/lịch phòng, có seed tái tạo.
- [ ] Restore thực hiện được và kết quả đối chiếu được lưu.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

## Tuần 6: Nghiệm thu DB và hoàn thiện báo cáo dữ liệu

Mã HMS-W6-TRANG; lịch 14/12/2026–20/12/2026; Issue: [#23](https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/23).

Phụ thuộc: HMS-W5-TRANG.

**Thứ tự thực hiện**

1. Dựng DB mới từ migration và seed bàn giao; đối chiếu đủ 28 bảng và phiên bản schema.
2. Chạy lại rollback, số tiền và báo cáo trên fixture; xác nhận kết quả gắn với commit chốt.
3. Thử restore và kiểm tra dữ liệu đã commit sau restart DB thử, phối hợp Minh.
4. Hoàn thiện ERD/từ điển, phần index và số đo thực; không thay số chưa đo bằng kỳ vọng.
5. Nhờ thành viên khác làm theo hướng dẫn và ghi chỗ chưa rõ để sửa.

**File dự kiến**

- `database/`
- `docs/evidence/w06/`
- `docs/release/database-report.md`

**Điều kiện nghiệm thu**

- [ ] DB cài mới/restore được từ tài liệu và script.
- [ ] Có log độ bền dữ liệu sau restart, fixture/đáp án và số đo.
- [ ] Tài liệu DB khớp bản release.

**Cập nhật GitHub**

Mỗi buổi comment đã làm, kiểm tra, blocker và bước tiếp theo vào Issue. PR nhỏ dùng Refs #Issue; PR cuối mới dùng Closes #Issue khi đủ toàn bộ tiêu chí. Đính kèm commit/PR, ảnh hoặc log và nhờ NMinZ17 review. Nếu thiếu API/SQL từ người khác, ghi mã Issue phụ thuộc và tiếp tục mock theo hợp đồng ở phần không bị chặn.

**Buổi làm đầu tiên**

Clone repo, mở Issue tuần 1, tạo nhánh riêng, kiểm tra công cụ. Thực hiện bước nhỏ đầu tiên rồi comment kết quả thực. Nếu vướng quá một buổi, gửi log/request/dữ liệu mẫu vào Issue để nhóm hỗ trợ.
