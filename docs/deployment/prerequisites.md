# Deployment Prerequisites – HMS

**Mã công việc:** HMS-W1-THU  
**Issue:** #5 – Thiết kế layout chung, request thử và kiểm tra VM  
**Người phụ trách:** Đỗ Thị Thanh Thư  
**Reviewer:** maingoclinh1681  
**Tuần thực hiện:** Week 1 (09/11/2026 – 15/11/2026)  
**Trạng thái:** Draft – Đang chuẩn bị môi trường, chưa xác nhận triển khai VM  
**Ngày cập nhật:** 13/11/2026

---

## 1. Mục đích

Tài liệu ghi nhận các yêu cầu chuẩn bị môi trường phát triển và thông tin cần thu thập để kiểm tra khả năng sẵn sàng của môi trường triển khai hệ thống Hotel Management System (HMS) trong tuần 1.

Nội dung tập trung vào:

- Kiểm tra các công cụ phát triển đã cài đặt trên máy của người phụ trách.
- Ghi nhận các công nghệ và thành phần cần thiết cho frontend, backend và database.
- Thu thập thông tin và xác định trạng thái truy cập của ba máy ảo (VM).
- Đề xuất phương án kết nối giữa frontend, backend và PostgreSQL để nhóm xem xét.
- Xác định các bước kiểm tra dịch vụ và điều kiện cần thiết trước khi thực hiện kiểm thử tích hợp.

Tài liệu này thuộc phạm vi chuẩn bị môi trường của tuần 1, không phải hướng dẫn triển khai hoàn chỉnh. Những thông tin chưa được nhóm hoặc người quản lý VM xác nhận sẽ được đánh dấu là **Pending** hoặc **Dự kiến**.

## 2. Công nghệ và công cụ sử dụng

Các công nghệ và công cụ được ghi nhận theo định hướng dự án và môi trường làm việc hiện tại:

| Thành phần | Công nghệ / Công cụ | Mục đích |
|---|---|---|
| Frontend | React + Vite | Xây dựng giao diện quản trị và vận hành |
| Backend | Python + FastAPI | Xây dựng REST API |
| Database | PostgreSQL | Lưu trữ dữ liệu hệ thống |
| API Testing | Postman | Gửi request và kiểm thử API |
| Web Server / Reverse Proxy | NGINX (dự kiến) | Phục vụ frontend và chuyển tiếp request API nếu được nhóm lựa chọn |
| Code Editor | Visual Studio Code | Phát triển và chỉnh sửa mã nguồn |
| Version Control | Git + GitHub | Quản lý mã nguồn và phối hợp nhóm |

**Lưu ý:**

- React, Vite, Python, FastAPI và PostgreSQL cần được đối chiếu với cấu hình thực tế của repository.
- NGINX hiện được ghi nhận là phương án dự kiến, chưa khẳng định đã được nhóm thống nhất triển khai.
- Phiên bản chính thức của công cụ và thư viện cần căn cứ vào các file cấu hình của repository và sự thống nhất của nhóm.

## 3. Yêu cầu môi trường phát triển trên máy thành viên

### 3.1. Công cụ cần cài đặt

| Công cụ | Mục đích | Lệnh kiểm tra |
|---|---|---|
| Git | Quản lý mã nguồn | `git --version` |
| Node.js | Chạy môi trường frontend | `node --version` |
| npm | Quản lý package frontend | `npm --version` |
| Python | Chạy backend FastAPI | `python --version` |
| PostgreSQL | Quản lý database | `psql --version` |
| pgAdmin 4 | Quản trị database bằng giao diện | Mở pgAdmin 4 |
| Postman | Kiểm thử API | Mở Postman |
| Visual Studio Code | Chỉnh sửa mã nguồn | Mở VS Code |

### 3.2. Phiên bản đã kiểm tra trên máy phụ trách

Các phiên bản dưới đây là thông tin đã kiểm tra trên máy của người phụ trách, không đại diện cho toàn bộ máy thành viên hoặc máy ảo.

| Công cụ | Phiên bản đã kiểm tra |
|---|---|
| Git | 2.55.0.windows.5 |
| Node.js | v26.13.0 |
| npm | 11.20.0 |
| Python | 3.13.15 |
| PostgreSQL / psql | 18.6 |

Các thành viên cần tự kiểm tra và ghi nhận phiên bản trên máy của mình.

Các phiên bản trên mới phản ánh trạng thái cài đặt và kiểm tra phiên bản. Khả năng tương thích với cấu hình chính thức của dự án cần được đối chiếu thêm với repository và nhóm.

### 3.3. Kiểm tra sau khi cài đặt

Mở PowerShell hoặc Terminal và chạy:

```powershell
git --version
node --version
npm --version
python --version
psql --version
```

Nếu lệnh không được nhận diện, cần kiểm tra lại việc cài đặt và cấu hình biến môi trường PATH.

Việc kiểm tra phiên bản không đồng nghĩa với việc frontend, backend hoặc database của dự án đã chạy thành công.

## 4. Yêu cầu môi trường chạy hệ thống

### 4.1. Frontend

- Sử dụng React và Vite theo cấu hình frontend của nhóm.
- Cài đặt dependency theo các file cấu hình package được cung cấp trong repository.
- Chạy frontend theo hướng dẫn trong README.
- Trong môi trường phát triển, frontend có thể chạy bằng Vite development server.
- Khi triển khai, frontend có thể được build thành các tệp tĩnh để web server phục vụ. Việc sử dụng NGINX cần được nhóm xác nhận.

Frontend hiện đang chờ PR khởi tạo của thành viên phụ trách được merge trước khi tiếp tục kiểm tra trên nhánh tích hợp.

Các lệnh dự kiến sau khi mã nguồn frontend đã sẵn sàng và cấu trúc repository được xác nhận:

Cài đặt dependency:

```powershell
cd frontend
npm ci
```

Chạy môi trường phát triển:

```powershell
npm run dev
```

Build frontend:

```powershell
npm run build
```

Chỉ thực hiện các lệnh trên khi thư mục frontend và các file cấu hình tương ứng đã có trong repository.

### 4.2. Backend

Backend được định hướng xây dựng bằng Python và FastAPI. Qua kiểm tra nhánh `origin/trang/checkpoint_1`, ghi nhận nhánh này đã có một số file mã nguồn Backend. Tuy nhiên, chưa xác nhận ứng dụng đã khởi chạy và hoạt động hoàn chỉnh.

**Các công nghệ và thư viện được khai báo:**

- FastAPI: xây dựng REST API.
- Uvicorn: máy chủ ASGI để chạy ứng dụng.
- SQLAlchemy: hỗ trợ truy vấn và thao tác với cơ sở dữ liệu.
- Psycopg: thư viện kết nối PostgreSQL.
- python-dotenv: hỗ trợ đọc cấu hình môi trường.
- requests: hỗ trợ gửi HTTP request.

File khai báo dependencies: `backend/requirements.txt`.

File mã nguồn API hiện có: `backend/app/main.py`. Ứng dụng khai báo tên `HMS Hotel API`, phiên bản `0.4.0` và có endpoint `POST /api/bookings` phục vụ chức năng tạo đặt phòng.

**Các API theo định hướng tích hợp:**

Theo tài liệu `docs/api-contract.md`, hai endpoint được đề xuất cho tuần 1 gồm:

- `GET /api/health`: kiểm tra trạng thái hoạt động của Backend.
- `GET /api/rooms`: lấy danh sách phòng phục vụ tích hợp Frontend – Backend – Database.

Các endpoint trên hiện được mô tả trong hợp đồng API ở trạng thái đề xuất, chưa xác nhận đã được triển khai trong mã nguồn `backend/app/main.py`. Vì vậy, cần thành viên phụ trách Backend xác nhận và cập nhật hợp đồng API trước khi Frontend tích hợp chính thức.

**Lệnh cài đặt và khởi chạy dự kiến:**

Theo cấu trúc hiện tại và hướng dẫn trong `docs/getting-started.md`, có thể tham khảo các lệnh sau từ thư mục `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Đây là các lệnh dự kiến, chưa được xác nhận chạy thành công trên môi trường triển khai của nhóm.

**Lưu ý về trạng thái triển khai:**

- Mã nguồn `backend/app/main.py` hiện tham chiếu `app.database.engine`, nhưng nhánh được kiểm tra chưa có file `backend/app/database.py`.
- Chưa xác nhận đầy đủ cấu hình kết nối PostgreSQL và các biến môi trường cần thiết.
- Chưa xác nhận hai endpoint `GET /api/health` và `GET /api/rooms` đã được triển khai.
- Chưa có bằng chứng xác nhận Backend khởi động và hoạt động thành công.

Do đó, Backend hiện được ghi nhận ở trạng thái đã có một số mã nguồn và dependencies, nhưng chưa đủ cơ sở kết luận đã triển khai hoàn chỉnh. Các lệnh cài đặt, khởi chạy và API tích hợp cần được thành viên phụ trách xác nhận trước khi sử dụng làm quy trình triển khai chính thức.

### 4.3. Database

Dự án sử dụng PostgreSQL làm hệ quản trị cơ sở dữ liệu.

**Các file SQL hiện có:**

| File | Chức năng |
|---|---|
| `database/schema.sql` | Khởi tạo cấu trúc 28 bảng dữ liệu |
| `database/seed.sql` | Thêm dữ liệu mẫu phục vụ thử nghiệm |
| `database/queries.sql` | Chứa các truy vấn SQL |
| `database/migrations/add_booking_events.sql` | Bổ sung cấu trúc và chức năng ghi nhận sự kiện đặt phòng |
| `database/migrations/add_booking_events_rollback.sql` | Hỗ trợ hoàn tác migration |
| `database/migrations/verify_final_state.sql` | Kiểm tra trạng thái sau migration |

**Quy trình khởi tạo dự kiến:**

1. Tạo database PostgreSQL dành cho môi trường phát triển.
2. Thực thi `database/schema.sql` để tạo cấu trúc bảng.
3. Thực thi `database/seed.sql` để thêm dữ liệu giả.
4. Thực thi migration theo đúng thứ tự và hướng dẫn của thành viên phụ trách CSDL.
5. Kiểm tra cấu trúc bảng, dữ liệu mẫu và kết quả migration.

Tên database `hms_dev` được đề cập trong tài liệu `docs/getting-started.md`, hiện được ghi nhận là tên đề xuất cho môi trường phát triển và cần được nhóm xác nhận.

**Lưu ý:**

- Schema ban đầu định nghĩa 28 bảng. Migration `add_booking_events.sql` bổ sung bảng `schema_migrations`, bảng `booking_events`, đồng thời điều chỉnh cơ chế sinh ID cho một số bảng và bổ sung ràng buộc kiểm tra ngày đặt phòng.
- Chỉ sử dụng dữ liệu giả trong quá trình thử nghiệm.
- Không commit mật khẩu, thông tin kết nối nhạy cảm hoặc file backup chứa dữ liệu cá nhân.
- Cần xác nhận thứ tự thực thi SQL và khả năng hoàn tác trước khi áp dụng trên môi trường dùng chung.
- Chưa xác nhận Database đã được khởi tạo và kiểm thử thành công trên các máy thành viên.

## 5. Phương án triển khai ba VM

### 5.1. Kiến trúc ba VM dự kiến – Chờ nhóm xác nhận

Đề xuất phân chia ba máy ảo theo vai trò để nhóm xem xét:

```text
                 Người dùng / Trình duyệt
                           |
                           v
                 VM1 – Frontend / NGINX
                    (Dự kiến)
                           |
                    HTTP API nội bộ
                           |
                           v
                     VM2 – Backend
                    (Dự kiến)
                     FastAPI
                           |
                Kết nối PostgreSQL nội bộ
                           |
                           v
                    VM3 – Database
                    (Dự kiến)
                    PostgreSQL
```

Vai trò đề xuất:

**VM1 – Frontend / NGINX**

- Phục vụ frontend React đã build.
- Nhận request từ trình duyệt.
- Có thể reverse proxy các request `/api` đến VM2 nếu nhóm lựa chọn NGINX.

**VM2 – Backend**

- Chạy ứng dụng FastAPI.
- Xử lý nghiệp vụ.
- Truy vấn và cập nhật dữ liệu thông qua PostgreSQL.

**VM3 – Database**

- Chạy PostgreSQL.
- Lưu trữ database HMS.
- Chỉ cho phép kết nối từ các nguồn được cấp quyền.

Đây là sơ đồ đề xuất để chuẩn bị kiểm tra môi trường, không phải phân công VM chính thức. Vai trò thực tế của từng VM cần được nhóm xác nhận trước khi triển khai.

### 5.2. Thông tin cần thu thập cho từng VM

| Thông tin | VM1 | VM2 | VM3 |
|---|---|---|---|
| Vai trò | Frontend / NGINX (dự kiến) | FastAPI (dự kiến) | PostgreSQL (dự kiến) |
| Nhà cung cấp | Pending | Pending | Pending |
| Hệ điều hành | Pending | Pending | Pending |
| CPU / RAM | Pending | Pending | Pending |
| Dung lượng ổ đĩa | Pending | Pending | Pending |
| IP hoặc hostname | Pending | Pending | Pending |
| Thời gian được cấp quyền | Pending | Pending | Pending |
| Người quản lý | Pending | Pending | Pending |
| Trạng thái truy cập | Chưa xác nhận | Chưa xác nhận | Chưa xác nhận |

Không tự điền IP, thông tin đăng nhập hoặc cấu hình tài nguyên khi chưa được người quản lý VM cung cấp.

### 5.3. Thông tin cần nhóm xác nhận

- Vai trò chính thức của từng VM.
- Nhà cung cấp VM và cách truy cập.
- Hệ điều hành của từng VM.
- CPU, RAM và dung lượng lưu trữ.
- IP hoặc hostname nội bộ.
- Quyền truy cập và thời gian được cấp.
- Quy tắc kết nối giữa ba VM.
- Người chịu trách nhiệm quản lý từng VM.

Người cung cấp thông tin VM: **Pending – Chờ nhóm xác nhận.**

## 6. Yêu cầu kết nối mạng dự kiến

Các cổng dưới đây là cổng mặc định hoặc phương án kỹ thuật dự kiến, chưa phải cấu hình đã được xác nhận trên VM.

| Dịch vụ | Cổng mặc định | Phạm vi truy cập dự kiến |
|---|---:|---|
| HTTP | 80 | Người dùng truy cập VM1 nếu sử dụng HTTP |
| HTTPS | 443 | Người dùng truy cập VM1 nếu cấu hình TLS |
| FastAPI / Uvicorn | 8000 | VM1 kết nối VM2 qua mạng nội bộ nếu sử dụng cổng mặc định |
| PostgreSQL | 5432 | VM2 kết nối VM3 qua mạng nội bộ nếu sử dụng cổng mặc định |

Nguyên tắc:

- Không mặc định PostgreSQL phải mở trực tiếp ra Internet.
- Không mặc định Uvicorn phải công khai cổng 8000.
- Chỉ mở các cổng cần thiết theo kiến trúc được nhóm thống nhất.
- Giới hạn nguồn truy cập theo vai trò và yêu cầu của nhóm.
- Không đưa mật khẩu hoặc thông tin xác thực vào Git.
- Cấu hình firewall, TLS và quyền truy cập cần được người quản lý VM xác nhận.

**Lưu ý:** Cấu hình mạng thực tế phải căn cứ vào sơ đồ triển khai được nhóm thống nhất và quyền quản trị VM được cấp.

### 7. Kiểm tra từng VM và dịch vụ sau khi được cấp quyền

Các bước dưới đây là checklist kiểm tra dự kiến, chỉ thực hiện sau khi nhóm được cấp VM, thông tin kết nối và cấu hình triển khai chính thức. Kết quả cần được ghi nhận để phục vụ kiểm tra và nghiệm thu môi trường.

#### 7.1. Kiểm tra VM Frontend

- Kiểm tra hệ điều hành và tài nguyên VM (CPU, RAM, dung lượng ổ đĩa).
- Kiểm tra phiên bản Node.js và npm bằng các lệnh `node --version` và `npm --version`.
- Kiểm tra mã nguồn Frontend đã được clone hoặc triển khai đầy đủ.
- Kiểm tra dependencies đã được cài đặt theo `package.json` và `package-lock.json`.
- Thực hiện lệnh khởi chạy Frontend theo README và cấu hình nhóm đã thống nhất.
- Kiểm tra khả năng truy cập giao diện từ trình duyệt.
- Ghi nhận địa chỉ truy cập, phiên bản công cụ và kết quả kiểm tra.

#### 7.2. Kiểm tra VM Backend

- Kiểm tra hệ điều hành, Python và môi trường ảo.
- Cài đặt dependencies theo `backend/requirements.txt`.
- Kiểm tra cấu hình kết nối database và các biến môi trường cần thiết.
- Kiểm tra sự tồn tại và khả năng sử dụng module kết nối database được Backend tham chiếu.
- Kiểm tra khả năng khởi động FastAPI.
- Đối chiếu các endpoint thực tế với `docs/api-contract.md`.
- Ghi nhận kết quả khởi động, lỗi phát sinh và thông tin phiên bản.

Lưu ý: Mã nguồn Backend hiện tham chiếu `app.database.engine`, nhưng nhánh được kiểm tra chưa có file `backend/app/database.py`. Ngoài ra, hợp đồng API hiện mô tả một số endpoint ở trạng thái đề xuất, chưa xác nhận toàn bộ đã được triển khai. Cần thành viên phụ trách Backend xác nhận trước khi sử dụng làm căn cứ nghiệm thu.

#### 7.3. Kiểm tra VM Database

- Kiểm tra PostgreSQL đã được cài đặt và đang hoạt động.
- Kiểm tra quyền truy cập database bằng tài khoản được cấp.
- Xác nhận database phát triển đã được tạo theo tên và cấu hình nhóm thống nhất.
- Kiểm tra cấu trúc bảng sau khi thực thi `database/schema.sql`.
- Kiểm tra dữ liệu mẫu sau khi thực thi `database/seed.sql`.
- Kiểm tra các migration, script rollback và script xác minh trong thư mục `database/migrations/`.
- Ghi nhận phiên bản PostgreSQL, trạng thái database và kết quả kiểm tra.

Lưu ý: Cần thống nhất thứ tự thực thi schema, seed và migration với thành viên phụ trách Database. Không tự ý chạy lại migration hoặc rollback trên môi trường có dữ liệu cần bảo toàn.

### 8. Kiểm tra tích hợp ba tầng

Mục tiêu là xác nhận luồng hoạt động giữa Frontend, Backend và Database, đồng thời kiểm tra khả năng trao đổi dữ liệu và xử lý lỗi giữa các thành phần.

#### 8.1. Kiểm tra kết nối Backend – Database

- Xác nhận Backend đọc được cấu hình kết nối database.
- Xác nhận Backend kết nối thành công với PostgreSQL.
- Kiểm tra Backend có thể thực hiện truy vấn dữ liệu phòng từ database.
- Đối chiếu dữ liệu trả về với dữ liệu đã được lưu trong PostgreSQL.
- Kiểm tra và ghi nhận lỗi kết nối, lỗi truy vấn hoặc lỗi cấu hình nếu có.

#### 8.2. Kiểm tra kết nối Frontend – Backend

Đối chiếu với hợp đồng API tại `docs/api-contract.md` và mã nguồn Backend thực tế.

Các endpoint cần quan tâm trong tuần 1:

- `POST /api/bookings`: endpoint tạo đặt phòng đã xuất hiện trong `backend/app/main.py`.
- `GET /api/health`: endpoint kiểm tra trạng thái API, được đề xuất trong hợp đồng tích hợp.
- `GET /api/rooms`: endpoint lấy danh sách phòng, được đề xuất trong hợp đồng tích hợp.

Lưu ý: Việc endpoint xuất hiện trong tài liệu hoặc mã nguồn chưa đồng nghĩa với việc endpoint đã hoạt động thành công. Chỉ thực hiện kiểm thử sau khi Backend được xác nhận đã triển khai và khởi chạy.

Khi kiểm thử, cần ghi nhận:
- HTTP status code.
- Nội dung response.
- Kết quả xử lý trên giao diện.
- Lỗi phát sinh (nếu có).
- Công cụ và các bước thực hiện kiểm thử.

#### 8.3. Kiểm tra luồng tích hợp hoàn chỉnh

Luồng mục tiêu đối với chức năng hiển thị danh sách phòng:

1. Frontend gửi yêu cầu lấy danh sách phòng đến Backend.
2. Backend tiếp nhận và xử lý yêu cầu.
3. Backend truy vấn dữ liệu phòng từ PostgreSQL.
4. Backend trả kết quả cho Frontend theo cấu trúc response đã thống nhất.
5. Frontend nhận dữ liệu và hiển thị danh sách phòng.

Tiêu chí kiểm tra:

- Frontend kết nối được với Backend.
- Backend truy vấn được dữ liệu từ PostgreSQL.
- Dữ liệu hiển thị trên giao diện khớp với dữ liệu trong database.
- Hệ thống xử lý phù hợp khi Backend hoặc Database không khả dụng.
- Frontend xử lý được trường hợp API trả về lỗi hoặc dữ liệu không hợp lệ.
- Có bằng chứng kiểm thử như ảnh chụp giao diện, response Postman hoặc log chạy ứng dụng.

**Trạng thái:** Các bước trên là kế hoạch kiểm tra tích hợp dự kiến. Chưa ghi nhận là đã kiểm thử thành công cho đến khi có kết quả thực tế và bằng chứng tương ứng.

## 9. Trạng thái chuẩn bị môi trường

Bảng dưới đây tổng hợp trạng thái cài đặt công cụ trên máy phụ trách, tình trạng chuẩn bị mã nguồn và mức độ sẵn sàng của môi trường triển khai tại thời điểm cập nhật tài liệu.

| Hạng mục | Trạng thái | Ghi chú |
| :--- | :--- | :--- |
| VS Code | Đã cài đặt | Trên máy phụ trách |
| Git | Đã cài và kiểm tra phiên bản | Phiên bản 2.55.0.windows.5 |
| Node.js / npm | Đã cài và kiểm tra phiên bản | Node.js v26.13.0, npm 11.20.0 |
| Python | Đã cài và kiểm tra phiên bản | Python 3.13.15 |
| PostgreSQL / psql | Đã cài và kiểm tra phiên bản | PostgreSQL / psql 18.6 |
| pgAdmin 4 | Đã cài đặt | Trên máy phụ trách |
| Postman | Đã cài đặt | Trên máy phụ trách |
| Frontend React | Đang chờ | Chờ PR khởi tạo được merge để kiểm tra và chạy theo cấu hình nhóm |
| Backend FastAPI | Chưa xác nhận | Repository đã có một số mã nguồn và dependencies; chưa xác nhận khởi chạy thành công |
| Database HMS | Chưa xác nhận | Chưa xác nhận database phát triển đã được tạo, schema và seed đã thực thi thành công |
| Thông tin VM1 | Chưa xác nhận | Chưa có thông tin và quyền truy cập |
| Thông tin VM2 | Chưa xác nhận | Chưa có thông tin và quyền truy cập |
| Thông tin VM3 | Chưa xác nhận | Chưa có thông tin và quyền truy cập |
| Truy cập các VM | Chưa thực hiện | Chờ được cấp quyền |
| Kiểm tra dịch vụ trên VM | Chưa thực hiện | Chờ môi trường sẵn sàng |
| Tích hợp ba tầng | Chưa thực hiện | Chưa có kết quả kiểm thử thực tế |

**Ghi chú:** Các phiên bản công cụ nêu trên được kiểm tra trên máy cá nhân của người phụ trách, không đại diện cho phiên bản đã cài đặt trên các VM. Các trạng thái triển khai và tích hợp sẽ được cập nhật khi có kết quả kiểm tra thực tế.

## 10. Kết luận

Trong tuần 1, người phụ trách đã chuẩn bị các công cụ phát triển cơ bản trên máy cá nhân và kiểm tra phiên bản của Git, Node.js, npm, Python và PostgreSQL.

Tài liệu đã tổng hợp các công nghệ chính của dự án, yêu cầu môi trường cho Frontend, Backend và Database, đồng thời đề xuất phương án phân chia ba VM và các yêu cầu kết nối để nhóm xem xét, thống nhất.

Tuy nhiên, kiến trúc triển khai chính thức, vai trò của từng VM, thông tin truy cập, cấu hình mạng và trạng thái triển khai các dịch vụ vẫn cần được nhóm xác nhận. Frontend đang chờ PR khởi tạo được merge; Backend và Database cũng chưa có đủ bằng chứng để xác nhận đã triển khai và hoạt động hoàn chỉnh.

Tại thời điểm cập nhật tài liệu, trạng thái công việc được tổng hợp như sau:

- **Công cụ phát triển trên máy phụ trách:** Đã cài đặt và kiểm tra theo từng hạng mục nêu trên.
- **Mã nguồn Frontend:** Đang chờ PR khởi tạo được merge để tiếp tục kiểm tra.
- **Backend và Database:** Đã có một số file mã nguồn và cấu hình trong repository, nhưng chưa xác nhận hoạt động hoàn chỉnh.
- **Thông tin và quyền truy cập VM:** Chưa xác nhận.
- **Kiểm tra dịch vụ trên VM:** Chưa thực hiện.
- **Kiểm tra tích hợp Frontend – Backend – Database:** Chưa thực hiện.

Không ghi nhận hệ thống đã triển khai hoặc tích hợp thành công khi chưa có kết quả kiểm tra thực tế.

Tài liệu sẽ tiếp tục được cập nhật khi nhóm thống nhất kiến trúc VM, cung cấp thông tin môi trường và hoàn thành các bước kiểm tra tương ứng.