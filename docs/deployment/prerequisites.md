# Deployment Prerequisites – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần thực hiện:** Week 1 (09/11/2026 – 15/11/2026)  
**Trạng thái:** Draft – Đã chuẩn bị và kiểm tra môi trường cá nhân; chờ nhóm thống nhất hạ tầng VM chính thức  
**Ngày cập nhật:** 17/11/2026

---

## 1. Mục đích

Tài liệu ghi nhận các yêu cầu chuẩn bị môi trường phát triển và thông tin kiểm tra khả năng sẵn sàng của môi trường triển khai hệ thống Hotel Management System (HMS).

Nội dung tập trung vào:

- Kiểm tra các công cụ phát triển trên máy của người phụ trách.
- Ghi nhận công nghệ và thành phần cần thiết cho Frontend, Backend và Database.
- Kiểm tra mã nguồn, cấu hình và khả năng khởi chạy các thành phần.
- Chuẩn bị ba VM thử nghiệm theo kiến trúc Frontend – Backend – Database.
- Kiểm tra kết nối mạng giữa ba VM.
- Đề xuất phương án triển khai để nhóm xem xét và thống nhất.
- Xác định những điều kiện còn thiếu trước khi triển khai môi trường dùng chung.

**Phạm vi:** Đây là tài liệu chuẩn bị môi trường và ghi nhận kết quả kiểm tra ban đầu. Ba VM hiện tại do người phụ trách tự tạo trên máy cá nhân, chưa được nhóm thống nhất là hạ tầng triển khai chính thức.

Những nội dung chưa được xác nhận sẽ được ghi rõ là Pending, Chờ nhóm xác nhận hoặc Chưa kiểm tra.

## 2. Công nghệ và công cụ sử dụng

| Thành phần | Công nghệ / Công cụ | Mục đích |
|---|---|---|
| Frontend | React + Vite | Xây dựng giao diện người dùng |
| Backend | Python + FastAPI | Xây dựng REST API |
| ASGI Server | Uvicorn | Khởi chạy ứng dụng FastAPI |
| Database | PostgreSQL | Lưu trữ dữ liệu hệ thống |
| Database Driver | Psycopg | Kết nối PostgreSQL từ Backend |
| Data Validation | Pydantic | Kiểm tra và xử lý dữ liệu đầu vào |
| Environment Config | python-dotenv | Đọc cấu hình môi trường |
| API Testing | PowerShell / curl / unittest | Gửi request và kiểm thử API |
| API Client | Postman | Kiểm thử API thủ công |
| Web Server / Reverse Proxy | NGINX (dự kiến) | Phục vụ frontend và chuyển tiếp request API nếu nhóm lựa chọn |
| Code Editor | Visual Studio Code | Phát triển và chỉnh sửa mã nguồn |
| Version Control | Git + GitHub | Quản lý mã nguồn và phối hợp nhóm |
| Virtualization | Oracle VirtualBox | Tạo và quản lý VM thử nghiệm |

**Lưu ý:**

- Các công nghệ Backend cần đối chiếu với `backend/requirements.txt`.
- NGINX là phương án dự kiến, chưa phải cấu hình triển khai chính thức.
- Phiên bản công cụ cần căn cứ vào cấu hình repository và sự thống nhất của nhóm.
- Không mặc định môi trường cá nhân của người phụ trách giống môi trường của tất cả thành viên.

## 3. Yêu cầu môi trường phát triển trên máy thành viên

### 3.1. Công cụ cần cài đặt

| Công cụ | Mục đích | Lệnh kiểm tra |
|---|---|---|
| Git | Quản lý mã nguồn | `git --version` |
| Node.js | Chạy môi trường Frontend | `node --version` |
| npm | Quản lý package Frontend | `npm --version` |
| Python | Chạy Backend | `python --version` |
| PostgreSQL | Quản lý Database | `psql --version` |
| pgAdmin 4 | Quản trị Database bằng giao diện | Mở pgAdmin 4 |
| Postman | Kiểm thử API | Mở Postman |
| Visual Studio Code | Chỉnh sửa mã nguồn | Mở VS Code |
| Oracle VirtualBox | Quản lý máy ảo | `VBoxManage --version` |

### 3.2. Phiên bản đã kiểm tra trên máy phụ trách

Các phiên bản dưới đây là thông tin đã kiểm tra trên máy Windows cá nhân, không đại diện cho toàn bộ máy thành viên hoặc các VM.

| Công cụ | Phiên bản |
|---|---|
| Git | 2.55.0.windows.5 |
| Node.js | v26.13.0 |
| npm | 11.20.0 |
| Python | 3.13.15 |
| PostgreSQL / psql | 18.6 |
| Oracle VirtualBox | Đã cài đặt và sử dụng |

Các thành viên cần tự kiểm tra phiên bản trên máy của mình và đối chiếu với yêu cầu của repository.

### 3.3. Kiểm tra sau khi cài đặt

Mở PowerShell hoặc Terminal:

```powershell
git --version
node --version
npm --version
python --version
psql --version
```

Nếu lệnh không được nhận diện, kiểm tra lại quá trình cài đặt và biến môi trường PATH.

Việc kiểm tra phiên bản không đồng nghĩa với việc các dịch vụ của dự án đã hoạt động thành công.

## 4. Yêu cầu môi trường chạy hệ thống

### 4.1. Frontend

Frontend sử dụng React và Vite theo cấu hình repository.

Các yêu cầu:

- Cài đặt dependencies theo `package.json` và `package-lock.json`.
- Chạy Frontend bằng Vite trong môi trường phát triển.
- Build thành các tệp tĩnh khi cần chuẩn bị triển khai.
- Cấu hình địa chỉ API phù hợp với môi trường chạy.
- NGINX chỉ được sử dụng nếu nhóm thống nhất phương án này.

Các lệnh kiểm tra:

```powershell
npm --prefix frontend run build
```

**Trạng thái thực tế:**

- Mã nguồn Frontend đã được chuẩn bị.
- Các shared components đã được xây dựng.
- Lệnh `npm --prefix frontend run build` đã chạy thành công.
- Giao diện đã được kiểm tra với API, hiển thị 4 phòng, lọc loại phòng, sắp xếp giá và lọc sức chứa.
- Chưa xác nhận toàn bộ chức năng giao diện và chưa kiểm tra triển khai Frontend bằng NGINX.

### 4.2. Backend

Backend sử dụng Python và FastAPI.

Các thư viện được khai báo trong `backend/requirements.txt`:

| Thư viện | Mục đích |
|---|---|
| FastAPI | Xây dựng REST API |
| Uvicorn | Chạy ứng dụng ASGI |
| Psycopg | Kết nối PostgreSQL |
| Pydantic | Kiểm tra dữ liệu |
| python-dotenv | Đọc cấu hình môi trường |

Các thư viện phục vụ kiểm thử được khai báo riêng trong `backend/requirements-dev.txt`.

File mã nguồn chính:

- `backend/app/main.py`
- `backend/app/config.py`
- `backend/app/db.py`
- `backend/app/routers/rooms.py`
- `backend/app/schemas.py`

Các lệnh cài đặt và khởi chạy trong môi trường phát triển:

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

**Trạng thái thực tế:**

- Backend đã được chuẩn bị và chạy trên môi trường thử nghiệm.
- API Health trả HTTP 200.
- API Rooms trả HTTP 200 và danh sách 4 phòng.
- Backend đã kết nối được PostgreSQL trong quá trình kiểm tra.
- Bộ unittest Backend có 11/11 test thành công.
- `python -m pip check` trả về `No broken requirements found.`

Lệnh kiểm thử:

```powershell
python -m unittest discover -s tests -v
```

### 4.3. Database

Dự án sử dụng PostgreSQL.

Các file SQL trong repository:

| File | Chức năng |
|---|---|
| `database/schema.sql` | Khởi tạo cấu trúc bảng |
| `database/seed.sql` | Thêm dữ liệu mẫu |
| `database/queries.sql` | Các truy vấn SQL |
| `database/migrations/` | Các script migration |
| `database/migrations/verify_final_state.sql` | Kiểm tra trạng thái sau migration |

Tên database phát triển được sử dụng trong môi trường hiện tại là `hms_dev`.

**Trạng thái thực tế:**

- PostgreSQL đã được cài đặt và sử dụng trên môi trường thử nghiệm.
- Backend xác nhận tìm thấy bảng `room` và `room_type`.
- Database xác nhận tồn tại:
  - `public.room`
  - `public.room_type`
- API Rooms đã truy xuất và trả về 4 phòng.

**Lưu ý:**

- Không commit mật khẩu, thông tin kết nối nhạy cảm hoặc file backup Database.
- Không chạy lại migration hoặc rollback trên môi trường có dữ liệu cần bảo toàn nếu chưa xác định rõ tác động.
- Cấu trúc Database chính thức cần căn cứ vào schema và migration đã được nhóm thống nhất.

## 5. Phương án triển khai ba VM

### 5.1. Trạng thái hiện tại

Người phụ trách đã tự tạo ba VM bằng Oracle VirtualBox trên máy Windows cá nhân để thử nghiệm kiến trúc ba tầng.

**Ba VM này chưa phải hạ tầng chính thức của nhóm.**

Chúng được sử dụng để:

- Thử nghiệm cách phân chia Frontend, Backend và Database.
- Kiểm tra kết nối mạng giữa các thành phần.
- Đánh giá cấu hình tài nguyên.
- Chuẩn bị minh chứng kỹ thuật ban đầu.
- Làm cơ sở trao đổi với các thành viên về phương án VM dùng chung.

### 5.2. Thông tin ba VM thử nghiệm

| Máy ảo | Vai trò thử nghiệm | Host-only IP | CPU | RAM | Disk |
|---|---|---|---:|---:|---:|
| HMS-VM1-Frontend | Frontend | `192.168.56.103` | 1 vCPU | 1536 MB | 15 GB |
| HMS-VM2-Backend | Backend | `192.168.56.102` | 1 vCPU | 1536 MB | 15 GB |
| HMS-VM3-Database | Database | `192.168.56.101` | 1 vCPU | 1536 MB | 15 GB |
| **Tổng** | **3 VM** | | **3 vCPU** | **4608 MB** | **45 GB** |

Thông tin bổ sung:

- Công cụ ảo hóa: Oracle VirtualBox.
- Máy chủ vật lý: Windows cá nhân.
- Guest OS được cấu hình trong VirtualBox: Ubuntu 24.04 LTS 64-bit.
- Adapter 1: NAT.
- Adapter 2: Host-only.
- Định dạng ổ đĩa: VDI.
- Dung lượng `Capacity`: 15360 MB mỗi VM.

Lưu ý: Dung lượng 15 GB là dung lượng tối đa của ổ đĩa ảo, không phải dung lượng thực tế đang chiếm trên máy Windows. Phiên bản hệ điều hành thực tế bên trong từng guest chưa được xác minh độc lập.

### 5.3. Kiến trúc thử nghiệm

```text
             HOST WINDOWS
          Oracle VirtualBox
                  |
          Host-only Network
           192.168.56.0/24
                  |
                  v
       +----------------------+
       | VM1 - Frontend       |
       | 192.168.56.103       |
       | React / Vite         |
       +----------------------+
                  |
             HTTP :8000
                  |
                  v
       +----------------------+
       | VM2 - Backend        |
       | 192.168.56.102       |
       | FastAPI / Uvicorn    |
       +----------------------+
                  |
        PostgreSQL TCP :5432
                  |
                  v
       +----------------------+
       | VM3 - Database       |
       | 192.168.56.101       |
       | PostgreSQL           |
       +----------------------+
```

Đây là kiến trúc thử nghiệm đã được kiểm tra kết nối cơ bản, không phải sơ đồ triển khai chính thức được nhóm phê duyệt.

### 5.4. Kết quả kiểm tra kết nối

| Mã kiểm tra | Nội dung | Kết quả |
|---|---|---|
| VM-W1-01 | VM1 gọi `GET /api/health` trên VM2 | HTTP 200 |
| VM-W1-02 | VM1 gọi `GET /api/rooms` trên VM2 | HTTP 200, trả về 4 phòng |
| VM-W1-03 | PostgreSQL trên VM3 lắng nghe tại `192.168.56.101:5432` | LISTEN |
| VM-W1-04 | VM2 kiểm tra TCP tới VM3 bằng `nc -vz 192.168.56.101 5432` | succeeded |
| VM-W1-05 | Backend khởi động và tìm thấy bảng `room`, `room_type` | Đã xác nhận qua log |

**Giới hạn xác minh:**

- `nc succeeded` chỉ xác nhận kết nối TCP, không tự chứng minh đăng nhập PostgreSQL và truy vấn SQL từ VM2.
- Log Backend đã xác nhận kết nối PostgreSQL trong môi trường thử nghiệm, nhưng cần phân biệt với kiểm tra quyền truy cập từ các máy khác.
- Chưa kiểm tra quyền truy cập VM từ máy tính riêng của các thành viên.

### 5.5. Các nội dung cần nhóm thống nhất

Trước khi coi môi trường là hạ tầng chính thức, nhóm cần thống nhất:

1. Nhà cung cấp VM: máy cá nhân, máy chủ dùng chung hoặc dịch vụ cloud.
2. Số lượng VM và cách phân chia vai trò.
3. CPU, RAM và dung lượng lưu trữ.
4. Hệ điều hành và phiên bản phần mềm.
5. IP hoặc hostname và phương thức truy cập.
6. Quyền truy cập của từng thành viên.
7. Người chịu trách nhiệm quản lý và bảo trì.
8. Thời gian VM sẵn sàng để nhóm sử dụng.

**Trạng thái:** Pending – Chờ nhóm thống nhất.

Ba VM cá nhân hiện tại chỉ là môi trường thử nghiệm và minh chứng kỹ thuật ban đầu. Không tự động chuyển chúng thành môi trường chính thức nếu chưa có sự đồng ý của nhóm.

## 6. Yêu cầu kết nối mạng dự kiến

| Dịch vụ | Cổng | Phạm vi truy cập dự kiến |
|---|---:|---|
| HTTP | 80 | Trình duyệt truy cập Frontend nếu sử dụng HTTP |
| HTTPS | 443 | Trình duyệt truy cập Frontend nếu cấu hình TLS |
| FastAPI / Uvicorn | 8000 | Frontend kết nối Backend qua mạng nội bộ |
| PostgreSQL | 5432 | Backend kết nối Database qua mạng nội bộ |

Nguyên tắc:

- Không mặc định PostgreSQL phải mở trực tiếp ra Internet.
- Không mặc định Uvicorn phải công khai cổng 8000.
- Chỉ mở các cổng cần thiết theo kiến trúc được nhóm thống nhất.
- Giới hạn nguồn truy cập theo vai trò và yêu cầu bảo mật.
- Không đưa mật khẩu hoặc thông tin xác thực vào Git.
- Cấu hình firewall, TLS và quyền truy cập cần được người quản lý VM xác nhận.

Các cổng trên là cổng mặc định hoặc phương án kỹ thuật dự kiến; không phải toàn bộ cấu hình đã được phê duyệt cho môi trường dùng chung.

## 7. Kiểm tra dịch vụ

### 7.1. Frontend

Các nội dung đã kiểm tra:

- Frontend build thành công bằng `npm --prefix frontend run build`.
- Frontend kết nối API.
- Hiển thị 4 phòng.
- Kiểm tra lọc loại phòng.
- Kiểm tra sắp xếp giá tăng dần và giảm dần.
- Kiểm tra lọc sức chứa từ 3 người.
- Xóa bộ lọc và khôi phục danh sách 4 phòng.

Ngày filter chưa được xác nhận hoàn chỉnh.

### 7.2. Backend

Các nội dung đã kiểm tra:

- API Health trả HTTP 200.
- API Rooms trả HTTP 200.
- Kiểm thử 11/11 unittest thành công.
- Kiểm tra dependencies bằng `pip check` không có lỗi.

Các test bao gồm kiểm tra CORS, Health, Database failure, bộ lọc phòng, phân trang, dữ liệu rỗng và tính ổn định của kết quả.

### 7.3. Database

Các nội dung đã kiểm tra:

- PostgreSQL hoạt động.
- Hai bảng `room` và `room_type` tồn tại.
- PostgreSQL lắng nghe tại `192.168.56.101:5432`.
- Backend có thể kết nối TCP tới Database.
- Backend khởi động và log xác nhận tìm thấy các bảng cần thiết.

## 8. Cảnh báo và giới hạn môi trường

Trong quá trình kiểm tra các VM xuất hiện cảnh báo:

```text
watchdog: BUG: soft lockup - CPU#0 stuck for ...
```

Cảnh báo này cần được theo dõi khi đánh giá độ ổn định và tài nguyên VM. Chưa có đủ dữ liệu để xác định nguyên nhân cụ thể hoặc kết luận mức độ ảnh hưởng.

Các giới hạn khác:

- Ba VM hiện chạy trên cùng máy Windows cá nhân.
- Tài nguyên VM phụ thuộc vào máy chủ vật lý.
- Khi máy chủ vật lý tắt hoặc mất kết nối, các VM có thể không truy cập được.
- Host-only không tự động cho phép các thành viên khác truy cập từ máy riêng.
- Chưa có xác nhận về lịch sử dụng và quyền truy cập VM chung.

## 9. Trạng thái chuẩn bị môi trường

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Git | Đã kiểm tra | Máy Windows cá nhân |
| Node.js / npm | Đã kiểm tra | Máy Windows cá nhân |
| Python | Đã kiểm tra | Máy Windows cá nhân |
| PostgreSQL / psql | Đã kiểm tra | Máy Windows cá nhân |
| VS Code | Đã cài đặt | Máy phụ trách |
| pgAdmin 4 | Đã cài đặt | Máy phụ trách |
| Postman | Đã cài đặt | Máy phụ trách |
| Oracle VirtualBox | Đã cài đặt | Đã tạo 3 VM thử nghiệm |
| Frontend | Đã build và kiểm tra cơ bản | Build thành công, API hoạt động |
| Backend | Đã chạy và kiểm thử | 11/11 unittest thành công |
| Database | Đã kiểm tra cơ bản | PostgreSQL và bảng dữ liệu hoạt động |
| VM1 – Frontend | Đã kiểm tra | IP `192.168.56.103` |
| VM2 – Backend | Đã kiểm tra | IP `192.168.56.102` |
| VM3 – Database | Đã kiểm tra | IP `192.168.56.101` |
| Frontend → Backend | Đã kiểm tra | HTTP 200 |
| Backend → Database | Đã kiểm tra | TCP succeeded; Backend log xác nhận kết nối |
| VM chính thức của nhóm | Pending | Chờ nhóm thống nhất |
| Quyền truy cập VM từ máy thành viên | Pending | Chưa kiểm tra |
| Lịch sử dụng VM chung | Pending | Chờ nhóm thống nhất |
| Quyền GitHub của tất cả thành viên | Pending | Chưa xác minh đầy đủ |

## 10. Kết luận

Môi trường phát triển cá nhân của người phụ trách đã được chuẩn bị và kiểm tra các thành phần chính.

Frontend đã build thành công và truy cập được API. Backend đã khởi chạy, trả kết quả cho các request thử nghiệm và có 11/11 unittest thành công. PostgreSQL hoạt động, có các bảng dữ liệu cần thiết và đã kiểm tra được kết nối mạng từ Backend.

Ba VM trên Oracle VirtualBox cũng đã được tạo và kiểm tra kết nối cơ bản theo kiến trúc Frontend – Backend – Database.

Tuy nhiên, ba VM hiện tại là môi trường thử nghiệm cá nhân của Thanh Thư, **chưa phải hạ tầng chính thức hoặc môi trường dùng chung được nhóm thống nhất**.

Các nội dung cần tiếp tục xác nhận gồm:

- Nhà cung cấp và cấu hình VM chính thức.
- Vai trò và số lượng VM được nhóm lựa chọn.
- Quyền truy cập của các thành viên.
- Người quản lý và lịch sử dụng môi trường.
- Quyền GitHub của các thành viên.

Tài liệu sẽ được cập nhật khi nhóm có quyết định chính thức về môi trường triển khai.

**Kết luận trạng thái:** Đã chuẩn bị và kiểm tra môi trường thử nghiệm cá nhân; chưa xác nhận triển khai hạ tầng VM dùng chung của nhóm.