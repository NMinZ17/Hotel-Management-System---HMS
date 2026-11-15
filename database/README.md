# Dữ liệu HMS

`schema.sql` và `seed.sql` giữ nguyên nội dung của Phan Thị Mai Trang tại [PR #26](https://github.com/NMinZ17/Hotel-Management-System---HMS/pull/26), commit `82f9a4339cb54b96ecb3a07a0c518ea395365eb2`. Chúng được dùng để dựng database và kiểm tra kết nối backend.

- Schema: 28 bảng, bao gồm `room_type` và `room`.
- Seed: 3 loại phòng và 4 phòng; phòng 101/102 là Standard, 201 là Deluxe, 202 là Suite.
- Chạy schema trước, seed sau, trên database phát triển rỗng.

```powershell
createdb -h 127.0.0.1 -U postgres hms_dev
psql -h 127.0.0.1 -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/schema.sql
psql -h 127.0.0.1 -U postgres -d hms_dev -v ON_ERROR_STOP=1 -f database/seed.sql
```

Đổi tài khoản và cổng theo PostgreSQL trên máy. Database phát triển hiện tại của Minh dùng cổng `55441` và đã có dữ liệu; không cần nạp lại. Xem [cài và chạy backend](../docs/backend-week1.md).
