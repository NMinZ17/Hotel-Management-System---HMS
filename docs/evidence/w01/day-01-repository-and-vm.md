# Day 1 – Repository, GitHub và chuẩn bị môi trường VM

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Ngày thực hiện:** 09/11/2026

## 1. Mục tiêu

- Kiểm tra repository và branch làm việc.
- Ghi nhận tình trạng quyền truy cập GitHub.
- Kiểm tra ba máy ảo VirtualBox phục vụ thử nghiệm kiến trúc ba tầng.
- Ghi nhận cấu hình CPU, RAM, ổ đĩa và mạng của từng VM.
- Kiểm tra khả năng giao tiếp giữa Frontend, Backend và Database.
- Xác định những vấn đề cần thống nhất trước khi sử dụng VM chung.

## 2. Repository và GitHub

### 2.1. Repository cục bộ

Repository đã có mặt tại:

`D:\Projects\Hotel-Management-System---HMS`

Branch đang sử dụng:

`Thanh-Thư`

Repository có các thành phần chính:

- `frontend/`
- `backend/`
- `database/`
- `docs/`

### 2.2. Trạng thái quyền GitHub

Đã kiểm tra repository và branch làm việc cục bộ.

Các nội dung chưa được xác minh bằng thao tác kiểm thử riêng:

- Quyền quản lý repository.
- Quyền tạo Pull Request.
- Quyền merge Pull Request.
- Quyền truy cập của tất cả thành viên trong nhóm.

**Kết luận:** Chưa đủ cơ sở để xác nhận toàn bộ quyền GitHub của nhóm đã được kiểm tra hoàn tất.

## 3. Chuẩn bị môi trường VirtualBox

### 3.1. Danh sách máy ảo

Đã tạo và kiểm tra ba VM trên máy cá nhân bằng Oracle VirtualBox.

| Tên máy ảo | Vai trò | UUID |
|---|---|---|
| HMS-VM1-Frontend | Frontend | `34977634-5f6b-49f4-aa3f-f059621251d3` |
| HMS-VM2-Backend | Backend/API | `3c65ec7e-a6a4-4326-8585-8494d219a2ba` |
| HMS-VM3-Database | PostgreSQL | `cf9cb7f9-b975-48a8-a896-97bbaba7cf97` |

Tại thời điểm kiểm tra, cả ba VM đều có trạng thái `Running`.

### 3.2. Cấu hình tài nguyên

| Máy ảo | CPU | RAM | Dung lượng tối đa ổ đĩa ảo |
|---|---:|---:|---:|
| HMS-VM1-Frontend | 1 vCPU | 1536 MB | 15360 MB |
| HMS-VM2-Backend | 1 vCPU | 1536 MB | 15360 MB |
| HMS-VM3-Database | 1 vCPU | 1536 MB | 15360 MB |
| **Tổng** | **3 vCPU** | **4608 MB** | **46080 MB** |

Thông tin ổ đĩa:

- Định dạng: VDI.
- Loại: `normal (base)`.
- Không bật mã hóa.

**Lưu ý:** Dung lượng trong bảng là dung lượng tối đa của ổ đĩa ảo (`Capacity`), không phải dung lượng thực tế đang chiếm trên ổ đĩa Windows.

### 3.3. Hệ điều hành và cấu hình mạng

Hệ điều hành được cấu hình trong VirtualBox:

`Ubuntu 24.04 LTS (64-bit)`

Phiên bản hệ điều hành thực tế bên trong từng Guest OS chưa được xác minh độc lập.

Cả ba VM đều có hai network adapter:

- Adapter 1: NAT.
- Adapter 2: Host-only Interface – `VirtualBox Host-Only Ethernet Adapter`.

Địa chỉ IP lấy từ kết quả `ip -brief address` bên trong từng VM:

| Máy ảo | Interface Host-only | Địa chỉ IP |
|---|---|---|
| HMS-VM1-Frontend | enp0s8 | `192.168.56.103/24` |
| HMS-VM2-Backend | enp0s8 | `192.168.56.102/24` |
| HMS-VM3-Database | enp0s8 | `192.168.56.101/24` |

Địa chỉ NAT được ghi nhận trên cả ba VM:

`10.0.2.15/24`

Mạng Host-only được sử dụng để các VM và máy chủ Windows giao tiếp trong mạng nội bộ VirtualBox. NAT phục vụ kết nối mạng đi ra.

**Giới hạn:** Host-only không tự động cho phép các thành viên khác trên máy tính riêng truy cập VM. Khả năng truy cập từ máy của thành viên khác chưa được kiểm chứng.

### 3.4. Trạng thái hạ tầng

Ba VM hiện tại là môi trường thử nghiệm cá nhân, chưa phải hạ tầng chính thức hoặc môi trường dùng chung của nhóm.

Các nội dung cần thống nhất:

- Nhà cung cấp hoặc nền tảng triển khai VM chính thức.
- Cấu hình CPU, RAM và dung lượng lưu trữ.
- Quyền quản lý và phân quyền truy cập.
- Cách kết nối từ máy tính của các thành viên.
- Lịch sử dụng và người phụ trách vận hành.

## 4. Kiểm tra kết nối kiến trúc ba tầng

### 4.1. Frontend → Backend: API Health

Từ HMS-VM1-Frontend, thực hiện:

```bash
curl -i http://192.168.56.102:8000/api/health
```

Kết quả:

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

{"status":"ok","service":"hms-api"}
```

**Kết luận:** API Health hoạt động và Frontend VM truy cập được Backend VM qua mạng Host-only.

### 4.2. Frontend → Backend: API Rooms

Từ HMS-VM1-Frontend, thực hiện:

```bash
curl -i http://192.168.56.102:8000/api/rooms
```

Kết quả:

```text
HTTP/1.1 200 OK
server: uvicorn
content-type: application/json
```

API trả về danh sách gồm 4 phòng từ cơ sở dữ liệu.

**Kết luận:** Endpoint `/api/rooms` trả về HTTP 200 và dữ liệu phòng.

### 4.3. Kiểm tra Backend khởi động và kết nối Database

Trên HMS-VM2-Backend, log khởi động ghi nhận:

- PostgreSQL kết nối thành công.
- Tìm thấy bảng `room` và `room_type`.
- API chạy tại `0.0.0.0:8000`.
- FastAPI thông báo `Application startup complete`.

Log truy cập ghi nhận hai request từ IP `192.168.56.103`:

```text
192.168.56.103 - "GET /api/health HTTP/1.1" 200 OK

192.168.56.103 - "GET /api/rooms HTTP/1.1" 200 OK
```

Sau khi kiểm tra, tiến trình API được dừng bằng `Ctrl+C` và ghi nhận shutdown hoàn tất.

### 4.4. Kiểm tra PostgreSQL trên Database VM

Trên HMS-VM3-Database, kiểm tra sự tồn tại của hai bảng:

```sql
SELECT
    to_regclass('public.room') AS room,
    to_regclass('public.room_type') AS room_type;
```

Kết quả:

```text
   room   |  room_type
----------+-------------
 room     | room_type
(1 row)
```

Kiểm tra cổng PostgreSQL:

```bash
sudo ss -lntp | grep 5432
```

Kết quả:

```text
LISTEN 0 200 192.168.56.101:5432 0.0.0.0:* users:(("postgres",pid=787,fd=6))
```

**Kết luận:** PostgreSQL đang lắng nghe trên địa chỉ `192.168.56.101`, cổng `5432`.

### 4.5. Kiểm tra kết nối Backend → Database

Từ HMS-VM2-Backend, thực hiện:

```bash
nc -vz 192.168.56.101 5432
```

Kết quả:

```text
succeeded
```

**Kết luận:** Backend VM thiết lập được kết nối TCP tới PostgreSQL VM qua cổng 5432.

**Lưu ý:** Kiểm tra TCP thành công xác nhận khả năng kết nối mạng, không thay thế việc kiểm tra đăng nhập PostgreSQL và truy vấn SQL trực tiếp từ Backend VM. Việc Backend khởi động và ghi nhận PostgreSQL kết nối thành công đã được xác nhận riêng qua log ứng dụng.

## 5. Sơ đồ kiến trúc môi trường thử nghiệm

```text
             HOST WINDOWS
                  |
          VirtualBox Host-only
                  |
       +----------+----------+
       |          |          |
       v          v          v
   VM1 Frontend  VM2 Backend  VM3 Database
   192.168.56.103  .102       .101
       |          |          |
       | HTTP     | TCP      | PostgreSQL
       +--------->+----------+
       |          |          |
       | /api/    | :5432    |
       | health   |          |
       | /api/rooms          |
       +-------------------->
```

Môi trường thử nghiệm sử dụng ba VM riêng biệt cho Frontend, Backend và Database. Các VM giao tiếp qua mạng Host-only.

Sơ đồ thể hiện kiến trúc logic và các kết nối đã kiểm tra, không phải sơ đồ hạ tầng triển khai chính thức của nhóm.

## 6. Những nội dung đã hoàn thành

- [x] Repository cục bộ đã sẵn sàng.
- [x] Xác định branch làm việc `Thanh-Thư`.
- [x] VirtualBox nhận diện đủ ba VM.
- [x] Ghi nhận cấu hình CPU, RAM và ổ đĩa ảo.
- [x] Ghi nhận cấu hình mạng NAT và Host-only.
- [x] Xác định IP Host-only của ba VM.
- [x] Frontend truy cập Backend qua API Health.
- [x] Frontend truy cập API Rooms và nhận dữ liệu.
- [x] Backend khởi động thành công và ghi nhận kết nối PostgreSQL.
- [x] PostgreSQL xác nhận hai bảng `room`, `room_type`.
- [x] PostgreSQL lắng nghe tại `192.168.56.101:5432`.
- [x] Backend kiểm tra TCP tới Database thành công.

## 7. Nội dung chưa xác minh và vấn đề cần theo dõi

### 7.1. Nội dung chưa xác minh

- [ ] Quyền GitHub của tất cả thành viên, bao gồm quyền tạo PR và merge.
- [ ] Các thành viên khác truy cập được ba VM từ máy tính riêng.
- [ ] Thống nhất hạ tầng VM chính thức và lịch sử dụng VM chung.
- [ ] Kiểm tra đăng nhập PostgreSQL và truy vấn SQL trực tiếp từ Backend VM bằng một phép thử riêng.

### 7.2. Cảnh báo tài nguyên VM

Trong Terminal của VM2 và VM3 xuất hiện thông báo:

```text
watchdog: BUG: soft lockup - CPU#0 stuck for ...
```

Đây là cảnh báo cần theo dõi về độ ổn định và tài nguyên VM.

Chưa có đủ dữ liệu để kết luận nguyên nhân hoặc mức độ ảnh hưởng đến toàn hệ thống.

## 8. Kết luận Day 1

Đã hoàn thành việc kiểm tra repository cục bộ, ghi nhận cấu hình ba VM thử nghiệm và xác minh các kết nối cơ bản trong kiến trúc ba tầng.

Các kết quả chính:

- Frontend VM gọi được API Health và API Rooms trên Backend VM.
- Backend VM khởi động thành công và kết nối PostgreSQL.
- Database VM có hai bảng `room`, `room_type` và đang lắng nghe trên cổng 5432.
- Kết nối TCP từ Backend VM tới Database VM thành công.

Tuy nhiên, ba VM hiện tại chỉ là môi trường thử nghiệm cá nhân. Quyền GitHub của toàn nhóm, khả năng truy cập VM từ máy của thành viên khác và phương án hạ tầng dùng chung vẫn cần được xác nhận.

**Trạng thái Day 1:** Hoàn thành phần kiểm tra repository và môi trường VM cá nhân; còn nội dung cần thống nhất ở cấp nhóm.