# Lưu minh chứng kiểm thử

Tạo `docs/evidence/wXX/<ma-test>.md` khi thực sự chạy. Không tạo log hoặc ảnh giả để lấp checklist. Log dài/ảnh/video lớn dùng tệp đính kèm Issue hoặc liên kết phù hợp, không commit backup DB.

```text
Mã test / Issue:
Ngày chạy:
Người chạy và người kiểm tra:
Commit / nhánh:
Python, PostgreSQL, OS và môi trường:
Dữ liệu/fixture và bước chuẩn bị:
Request hoặc lệnh:
Kết quả kỳ vọng:
Kết quả thực tế:
SQL xác nhận trạng thái cuối:
Kết luận: Đạt / Không đạt / Chưa chạy
PR/ảnh/log và lỗi còn mở:
```

| Test | Tiêu chí |
| --- | --- |
| T01 | Hai kết nối cùng phòng cuối/cùng ngày: một thành công, một xung đột, DB đúng một đơn mới hợp lệ |
| T02 | Ngày liền kề được chấp nhận |
| T03 | Ngày sai bị từ chối, không ghi dữ liệu |
| T04 | Lỗi giữa transaction rollback đầu đơn, chi tiết, khách/giảm giá và audit đã ghi trong transaction |
| T05 | Hủy lặp không giải phóng sai; đặt lại được |
| T06 | Hoàn thành dịch vụ lặp chỉ một phí/chi tiết; lỗi ghi phí rollback trạng thái |
| T07 | Khách không đọc/sửa dữ liệu người khác, staff chỉ làm việc được giao |
| T08 | Thanh toán/chốt lặp không sinh trùng; không ghi phí sau chốt |

Bổ sung: đơn nhiều phòng nguyên tử; phòng bẩn/bảo trì không check-in; trạng thái dọn và sửa độc lập; sáu báo cáo khớp fixture; restore và dữ liệu sau restart. Test đồng thời cần hai kết nối thực và log, kiểm thử tuần tự không thay thế. Benchmark lưu số dòng, seed, máy/phiên bản, EXPLAIN (ANALYZE, BUFFERS) ít nhất ba lần trước/sau trên cùng dữ liệu; ghi kết quả thực kể cả không nhanh hơn.
