# Kế hoạch HMS 6 tuần từ số 0

**Điểm xuất phát và mục tiêu**

Nhóm có bốn thành viên, gần như mới bắt đầu với React, FastAPI và PostgreSQL; dự án chưa có sản phẩm chạy được. Hai PDF thiết kế là tài liệu tham chiếu, không được tính là mã nguồn, migration hay kiểm thử đã hoàn thành.

Lịch đề xuất vẫn là 09/11-20/12/2026. Quỹ thời gian tạm tính 16-20 giờ/người/tuần, khoảng 384-480 giờ cho cả nhóm trong sáu tuần; đây là giả định lập kế hoạch, chưa phải cam kết của nhóm. Thời gian này bao gồm học, thực hiện, tích hợp và sửa lỗi. Với người mới, hoàn thiện toàn bộ thiết kế trong sáu tuần là mục tiêu gấp và cần kiểm tra tiến độ mỗi tuần.

Tuần 1 học và dựng một luồng nhỏ chạy đủ ba tầng; tuần 2-4 phát triển theo từng hành trình người dùng; tuần 5 đo dữ liệu và triển khai; tuần 6 nghiệm thu. Giao diện dùng một bộ mẫu đơn giản, cùng kiểu bảng, form và thông báo. Không dành riêng một tuần chỉ để học hoặc chỉ thiết kế Figma.

| Tuần | Trọng tâm | Sản phẩm phải demo được cuối tuần |
| --- | --- | --- |
| 1: 09-15/11 | Học công cụ và dựng nền tảng | Mở React, gọi FastAPI và đọc danh sách phòng từ PostgreSQL; cả bốn người tự chạy được |
| 2: 16-22/11 | Tài khoản, phòng và đặt/hủy cơ bản | Khách đăng nhập, tìm phòng, đặt một phòng, xem đơn và hủy; migration đủ 28 bảng |
| 3: 23-29/11 | Check-in, folio, hóa đơn và thanh toán | Đặt phòng đến check-out chạy bằng dữ liệu thật; kiểm thử tranh chấp và rollback có log |
| 4: 30/11-06/12 | Dịch vụ phòng và vận hành | Gọi dịch vụ, hoàn thành, ghi phí; dọn phòng và bảo trì; rà soát chức năng còn lại của bản 28 |
| 5: 07-13/12 | Báo cáo, dữ liệu lớn và 3 VM | Sáu báo cáo đơn giản, số đo trước/sau index, backup/restore và bản chạy trên 3 VM |
| 6: 14-20/12 | Sửa lỗi và bàn giao | Kiểm thử trên bản chốt, hướng dẫn chạy, báo cáo, video và release |

**Phạm vi và cách đánh giá hoàn thành**

Mức A là bản tối thiểu cần ưu tiên: ba vai trò ADMIN/STAFF/GUEST; tìm/đặt/hủy một phòng; check-in; folio, hóa đơn và ghi nhận tiền mặt/chuyển khoản; check-out; một luồng dịch vụ ghi phí đúng một lần; dọn phòng và bảo trì cơ bản; sáu báo cáo dạng bảng; migration 28 bảng, kiểm thử dữ liệu và triển khai theo yêu cầu môn học.

Mức B hoàn thiện thiết kế 28 bảng về nghiệp vụ: đơn nhiều phòng và nhiều khách, một mã giảm giá/đơn, đánh giá sau lưu trú, UI quản trị/audit đầy đủ hơn. Bắt đầu phần dữ liệu và hợp đồng API từ tuần 2, tích hợp dần ở tuần 3-4. Nếu các mục này chưa chạy thì phải ghi rõ bản tối thiểu đã đạt nhưng chưa hoàn thành toàn bộ thiết kế. Có đủ 28 bảng không đồng nghĩa đủ mọi chức năng.

Ngoài phạm vi bản 28: nhà hàng và kho nguyên liệu riêng, lịch spa/vui chơi, đa khách sạn, cổng thanh toán thật, giá động, hóa đơn điện tử và WebSocket. Các yêu cầu dữ liệu lớn/3 VM được giữ theo hồ sơ; kiểm tra lại tiêu chí giảng viên ở ngày đầu để xác định mục nào bắt buộc khi chấm.

**Phân công và cách hỗ trợ nhau**

| Thành viên | Chịu trách nhiệm chính | Hỗ trợ để tránh nghẽn |
| --- | --- | --- |
| Nguyễn Nhật Minh | FastAPI, xác thực/phân quyền, transaction đặt/hủy, check-in/out, dịch vụ và thanh toán; tích hợp và release | Làm cùng Trang ở phần truy vấn và dữ liệu; không nhận cả việc viết SQL báo cáo, chạy mọi test và dựng mọi giao diện |
| Phan Thị Mai Trang | ERD, SQL migration 28 bảng, fixture/seed, index, SQL sáu báo cáo, backup/restore | Viết lớp truy vấn/hàm dữ liệu cho danh mục và báo cáo để Minh tích hợp; cùng kiểm tra số tiền và trạng thái DB |
| Mai Ngọc Linh | Frontend khách và lễ tân: đăng nhập, tìm/đặt/hủy, check-in/out, folio, hóa đơn/thanh toán | Dùng cùng mẫu form/bảng với Thư; kiểm tra luồng và thông báo lỗi, không tự tạo một bộ dữ liệu riêng khác API |
| Đỗ Thị Thanh Thư | Frontend báo cáo, dịch vụ/vận hành, VM1 và NGINX; tổng hợp log thử | Chuẩn bị request kiểm thử, chạy hai kết nối; cùng Minh kiểm tra triển khai, cùng Linh tích hợp UI |

Review chéo: Trang kiểm tra thay đổi dữ liệu/transaction của Minh; Minh kiểm tra SQL/migration của Trang; Linh và Thư kiểm tra UI của nhau. Minh chịu trách nhiệm cuối cho quyền API và release. Mỗi người học sâu phần mình làm, nhưng cả bốn đều cần biết chạy toàn bộ dự án và gọi một API.

**Tuần 1: học đúng phần cần và làm luồng đầu tiên**

| Ngày làm việc | Công việc của nhóm | Kết quả kiểm tra |
| --- | --- | --- |
| Ngày 1 | Thống nhất phạm vi 28, ba vai trò và luồng demo; kiểm tra yêu cầu chấm. Tạo repository, thư mục frontend/backend/database/docs, cài công cụ và ghi phiên bản | Cả nhóm clone, tạo nhánh, commit và mở PR thử được; xác định người cung cấp 3 VM |
| Ngày 2 | Học Git cơ bản; HTTP/JSON; React component/state/form; FastAPI route và request; PostgreSQL SELECT/INSERT, PK/FK | Mỗi người hiểu một request đi từ form tới API rồi tới DB |
| Ngày 3 | Trang tạo room_type/room và seed 5-10 phòng. Minh tạo API đọc danh sách phòng. Linh dựng React và trang phòng. Thư dựng layout admin và mẫu bảng/form | Có ba phần riêng chạy được, chưa cần đẹp |
| Ngày 4 | Ghép React -> FastAPI -> PostgreSQL; thống nhất tên trường, URL, dữ liệu lỗi và cấu hình môi trường | Danh sách phòng trên màn hình được lấy từ DB, không chỉ là mảng viết sẵn |
| Ngày 5 | Sửa lỗi cài đặt; viết README; người khác dựng lại theo hướng dẫn. Phác các màn còn lại; chuẩn bị dữ liệu tài khoản và khung đăng nhập | Cả bốn máy chạy được; có một PR đã review và merge |

Ngày 6-7 là thời gian dự phòng, tự ôn và sửa phần chưa chạy. Không yêu cầu tuần 1 hoàn thiện cả 28 bảng, đăng nhập hoàn chỉnh và mọi màn hình. Minh học route, validation, DB và lỗi API; Trang học SQL/ràng buộc/migration; Linh và Thư học React, form, gọi API và routing, trong chính bài thực hành này.

Điều kiện qua tuần 1: mỗi người tự chạy dự án; React đọc được dữ liệu PostgreSQL qua API; README có lệnh chạy và cấu hình mẫu không chứa mật khẩu thật. Nếu chưa đạt, dùng đầu tuần 2 xử lý ngay và giảm phần trang trí; không tiếp tục xây nhiều màn trên nền tảng chưa hoạt động.

**Tuần 2: tài khoản và đặt phòng cơ bản**

| Người | Việc cần hoàn thành | Sản phẩm |
| --- | --- | --- |
| Minh | Đăng ký/đăng nhập, kiểm tra ba vai trò; API phòng trống, đặt một phòng, danh sách đơn của mình và hủy. Giữ phòng cụ thể trong transaction, kiểm tra ngày và lịch; bắt đầu audit đặt/hủy | Luồng đặt/hủy qua API thật, mật khẩu băm, khách không đọc đơn người khác |
| Trang | Hoàn thiện migration 28 bảng theo nhóm, PK/FK/UNIQUE/CHECK và chống chồng lịch. Seed nhỏ có tài khoản thử, phòng, khách và dịch vụ. Chuẩn bị SQL đối chiếu và fixture cho hai khách tranh một phòng | Database mới dựng lại được; dữ liệu mẫu có chủ đích; danh sách quy tắc phải kiểm tra tại API |
| Linh | Đăng nhập, tìm phòng, đặt một phòng, xem lịch sử/chi tiết và hủy. Dùng mock theo hợp đồng trong lúc API đang viết; chuyển sang API thật từng màn | Một người dùng thực hiện được toàn bộ đặt/hủy trên giao diện |
| Thư | Trang admin quản lý loại phòng/phòng dạng bảng và form cơ bản; khung trang nhân viên; bộ request kiểm thử đăng nhập/đặt/hủy. Ghi lại lỗi tích hợp | Màn danh mục đơn giản và log lỗi có thể tái hiện |

Hoàn thiện hợp đồng cho đơn nhiều phòng, khách đi cùng và giảm giá trong tuần này, nhưng lấy trường hợp một phòng làm bước chạy đầu tiên. Không học toàn bộ công nghệ trước khi thực hiện chức năng. Viết SQL migration thành các file có thứ tự; chọn một cách quản lý migration và dùng thống nhất.

Điều kiện qua tuần 2: gọi API thật từ UI để đặt/hủy thành công; hai đơn tuần tự cùng phòng/cùng ngày bị chặn; hủy giữ nguyên lịch sử và cho phép đặt lại. Từ tuần này, mọi thay đổi được tích hợp ít nhất hai lần/tuần.

Mốc cảnh báo: nếu cuối tuần 2 vẫn chưa đặt phòng được từ giao diện tới DB, chưa có cơ sở giữ lời hứa hoàn thiện toàn bộ thiết kế trong sáu tuần. Nhóm cần chọn giảm phần Mức B hoặc xin thêm thời gian; không đẩy toàn bộ công việc sang tuần cuối.

**Tuần 3: lưu trú, tiền và bằng chứng transaction**

| Người | Việc cần hoàn thành | Sản phẩm |
| --- | --- | --- |
| Minh | Check-in tạo stay/stay_room/folio; kiểm tra sạch và không bảo trì. Tính tiền phòng theo giá snapshot, tạo hóa đơn, ghi nhận tiền mặt/chuyển khoản và check-out. Chống gọi lặp sinh phí/tiền trùng | Một lượt đặt -> check-in -> xem chi phí -> thanh toán -> check-out chạy đủ |
| Trang | Fixture tính tiền có đáp án tính tay; SQL kiểm tra rollback và trạng thái cuối; cùng Minh hoàn thiện khóa và chống chồng lịch. Chuẩn bị truy vấn sáu báo cáo | Số tiền đối chiếu được; dữ liệu không mồ côi; SQL kiểm chứng |
| Linh | Màn lễ tân danh sách đặt, check-in, folio, hóa đơn và thanh toán/check-out; màn khách xem chi phí. Tích hợp khách đi cùng/giảm giá nếu phần API tương ứng đã đạt | Luồng khách/lễ tân dùng dữ liệu thật, có thông báo thiếu tiền/phòng không hợp lệ |
| Thư | Chạy hai kết nối tranh phòng, ngày liền kề, ngày sai, rollback và hủy lặp; lưu log cùng Trang. Thử đưa khung frontend/API lên VM1/VM2 khi có tài nguyên; chuẩn bị trang dịch vụ | Hồ sơ kiểm thử đặt phòng và bản triển khai thử đầu tiên |

Nghiệm thu: T01-T05 có log chạy thực và SQL xác nhận. Hai khách tranh phòng cuối cùng cho một thành công, một xung đột; hai khoảng ngày liền kề được phép. Check-out v1 chỉ hoàn tất khi thu đủ. Tiền dùng kiểu số chính xác và kiểm tra phía backend; UI không tự quyết định số phải thu.

Đơn nhiều phòng cần transaction toàn bộ: nếu một phòng không giữ được thì không để lại đơn dở dang. Nếu tìm theo loại phòng, thử phòng ứng viên khác khi một phòng vừa bị tranh mất. Hoàn thiện và kiểm thử mục này trong tuần 3-4 nếu mục tiêu là toàn bộ bản 28.

**Tuần 4: dịch vụ, dọn phòng và bảo trì**

| Người | Việc cần hoàn thành | Sản phẩm |
| --- | --- | --- |
| Minh | API gọi/nhận/hoàn thành dịch vụ; ghi folio_item đúng một lần cùng transaction. API giao/hoàn thành dọn phòng, bảo trì và đánh giá. Rà quyền đối tượng; kiểm tra chốt folio đồng thời với ghi phí | Ba luồng chính chạy xuyên suốt, không phát sinh phí sau chốt |
| Trang | Dữ liệu thử dịch vụ, nhiều payment/dòng phí, dọn phòng và bảo trì. SQL báo cáo theo định nghĩa thống nhất; script seed lớn theo từng mức, không ép mọi bảng cùng số dòng | Fixture kiểm chứng; script seed bắt đầu chạy được; SQL R01-R06 |
| Linh | Khách gọi dịch vụ, xem phí; hoàn thiện giao diện lễ tân. Tích hợp đơn nhiều phòng, khách đi cùng, giảm giá và đánh giá theo hợp đồng đã chuẩn bị | UI khách/lễ tân hoàn thiện phạm vi đã chốt; danh sách Mức B đã đạt/chưa đạt rõ ràng |
| Thư | UI staff/admin nhận đơn dịch vụ, giao và hoàn thành nhiệm vụ dọn/bảo trì. Dựng sáu báo cáo dạng bảng, một bộ lọc ngày chung; thử các ca quyền truy cập | Màn vận hành chạy thật và dashboard khung đơn giản |

Nghiệm thu: gọi hoàn thành dịch vụ hai lần chỉ có một khoản phí/chi tiết; lỗi ghi phí rollback trạng thái. Check-out tạo nhiệm vụ dọn; CLEAN/DIRTY/CLEANING độc lập AVAILABLE/BLOCKED. Chỉ mở bảo trì khi không còn phiếu đang mở. STAFF chỉ xử lý việc được giao; GUEST chỉ truy cập dữ liệu của mình.

Khóa bổ sung chức năng cuối tuần 4. Nếu còn chức năng Mức A chưa chạy thì ưu tiên sửa ngay; phần làm đẹp và Mức B chưa xong phải ghi backlog. Nếu đề yêu cầu toàn bộ Mức B, cần công bố nguy cơ trễ và điều chỉnh nguồn lực/thời hạn, không ghi nhận hoàn thành toàn bộ.

**Tuần 5: báo cáo, dữ liệu lớn và triển khai**

| Người | Việc cần hoàn thành | Sản phẩm |
| --- | --- | --- |
| Minh | Đưa SQL báo cáo qua API; phân trang danh sách cần thiết; triển khai FastAPI trên VM2 và điều phối kết nối ba VM. Kiểm tra lại transaction trong môi trường triển khai | Bản ứng viên phát hành, cấu hình và commit xác định |
| Trang | Seed dữ liệu theo quan hệ thực: mục tiêu 120.000 folio_item, 30.000 housekeeping_task, 25.000 service_order_item; số reservation/stay/folio khoảng 10.000-12.000 mỗi bảng khi phù hợp. ANALYZE, đo trước/sau index và backup/restore vào DB riêng | Số dòng thực tế, kế hoạch truy vấn, số đo ít nhất ba lần/phương án và log restore |
| Linh | Kiểm thử luồng khách/lễ tân trên dữ liệu lớn và địa chỉ triển khai; sửa lỗi phân trang/loading/form; viết hướng dẫn sử dụng | Luồng chính ổn định và hướng dẫn khách/lễ tân |
| Thư | Hoàn thiện sáu báo cáo dạng bảng; VM1 phục vụ React và reverse proxy NGINX tới VM2; kiểm tra routing, lọc dữ liệu và các ca regression | Dashboard khớp SQL; cấu hình VM1; log kiểm thử qua proxy |

Mô hình triển khai: VM1 React + NGINX do Thư chính; VM2 FastAPI do Minh chính; VM3 PostgreSQL do Trang phụ trách dữ liệu, Minh phối hợp triển khai. Kiểm tra quyền truy cập/tài nguyên từ tuần 1; không đợi tuần 5 mới xin VM.

Sáu báo cáo: R01 giá trị hóa đơn; R02 tiền đã thu; R03 tỷ lệ phòng đã đặt; R04 phí dịch vụ đã ghi; R05 công nợ; R06 số nhiệm vụ dọn/bảo trì theo trạng thái. Bảng số liệu và bộ lọc là đủ cho bản tối thiểu; biểu đồ đẹp làm sau. Không cộng R01 và R02 thành một doanh thu; không nối nhiều payment với nhiều folio_item rồi SUM làm nhân bản tiền.

Đo cùng dữ liệu/truy vấn trước và sau index, giữ kết quả trước khi tạo index thử. Dùng EXPLAIN (ANALYZE, BUFFERS), lưu kế hoạch và thời gian từng lần hoặc trung vị. Không ghi tỷ lệ tăng tốc kỳ vọng như kết quả đã đo.

**Tuần 6: kiểm thử, sửa lỗi và bàn giao**

| Thời điểm | Công việc và người chính | Điều kiện hoàn tất |
| --- | --- | --- |
| Ngày 1-2 | Thư chạy regression; Linh kiểm thử khách/lễ tân; Minh sửa API; Trang đối chiếu DB và số tiền | Lỗi có bước tái hiện; sửa lỗi xong chạy lại ca liên quan |
| Ngày 3 | Minh chốt ứng viên; Trang thử dựng DB từ migration/seed; thành viên khác làm theo README | Môi trường mới chạy được, không phụ thuộc thao tác nhớ riêng của một người |
| Ngày 4 | Kiểm thử qua VM1; restart và kiểm tra dữ liệu đã commit; backup/restore và thử quay lại bản trước | Có log thực nghiệm, commit và môi trường rõ ràng |
| Ngày 5 | Tổng duyệt demo, hoàn thiện báo cáo và video; cả bốn trình bày phần mình làm | Kịch bản đủ ba vai trò và ba luồng; số đo/bằng chứng dùng bản chốt |
| Ngày 6-7 | Dự phòng sửa lỗi chặn nộp; Minh tag release và nhóm bàn giao | Không còn lỗi đặt trùng, sai tiền, sai quyền, mất dữ liệu hoặc luồng chính bị chặn |

Tuần này không được dùng làm tuần viết mới phân hệ còn thiếu. Kiểm tra tối thiểu T01-T08: tranh phòng; ngày liền kề; ngày sai; rollback; hủy lặp/đặt lại; hoàn thành dịch vụ lặp; quyền sở hữu dữ liệu; thanh toán/chốt folio lặp. Bổ sung trạng thái dọn/bảo trì và độ đúng sáu báo cáo. Người viết chức năng không tự xác nhận toàn bộ kết quả của mình.

**Gói bàn giao và nhịp làm việc**

- [ ] Mã nguồn React/FastAPI, dependency, phiên bản và commit/tag; hướng dẫn cài mới, cấu hình mẫu và tài khoản thử ba vai trò.
- [ ] Migration 28 bảng, ERD/từ điển đồng bộ, seed nhỏ có đáp án và seed lớn có thể tái tạo.
- [ ] Ba luồng chính chạy thật; bảng phạm vi Mức A/Mức B ghi rõ mục đã đạt, chưa đạt và giới hạn.
- [ ] Sáu báo cáo có fixture đối chiếu; số đo index thực; log T01-T08, backup/restore và kiểm tra dữ liệu sau restart.
- [ ] Cấu hình 3 VM/NGINX, hướng dẫn chạy lại/quay lại bản trước, báo cáo, kịch bản và video demo.

Mỗi tuần có hai buổi tích hợp ngắn và một buổi demo, tính trong 16-20 giờ. Mỗi Issue chỉ nên có một đầu ra nhỏ, làm trong khoảng nửa ngày đến một ngày: một API hoặc một màn gắn với dữ liệu rõ ràng. Nếu mắc lỗi quá một buổi, mang request, log và dữ liệu mẫu để cả nhóm xử lý. Không làm riêng sáu tuần rồi ghép cuối cùng.

Ngày đầu tiên cần làm ngay: tạo repo và README; cài bộ công cụ; chốt một mẫu dữ liệu phòng; Minh dựng GET phòng, Trang tạo bảng/seed, Linh hiển thị phòng, Thư tạo layout và request thử. Đây là bước đầu để biến kế hoạch thành sản phẩm.

Tham chiếu: phân công trong Google Docs của nhóm và HMS_ERD_28_bang.pdf, Bao_cao_HMS_IEEE.pdf. Kế hoạch này thay giả định có thể tái sử dụng sản phẩm bằng việc bắt đầu toàn bộ phần thực thi từ đầu; ngày bắt đầu và quỹ giờ có thể được điều chỉnh khi nhóm xác nhận.
