# Đặc tả Công thức & Hợp đồng Dữ liệu 6 Báo cáo (R01 – R06)

Tài liệu này quy định chuẩn công thức nghiệp vụ, quy tắc lọc dữ liệu trên lược đồ 28 bảng của Hệ thống Quản lý Khách sạn (HMS), câu truy vấn PostgreSQL tham chiếu và cấu trúc JSON đầu ra để đội **Frontend** chủ động xây dựng giao diện/mock dữ liệu song song với đội **Backend**.

---

## 1. Quy ước chung & Tham số đầu vào

### 1.1. Bộ tham số lọc chuẩn (Query Parameters)
Tất cả 6 API báo cáo sử dụng chung quy ước tham số đầu vào qua HTTP `GET`:

| Tham số | Kiểu dữ liệu | Bắt buộc | Mô tả & Quy ước |
| :--- | :--- | :--- | :--- |
| `from_date` | `DATE` (`YYYY-MM-DD`) | Có | Ngày bắt đầu kỳ báo cáo, tính từ `00:00:00` theo múi giờ `hotel.timezone` (`Asia/Ho_Chi_Minh`). |
| `to_date` | `DATE` (`YYYY-MM-DD`) | Có | Ngày kết thúc kỳ báo cáo theo **khoảng nửa mở** $[ \text{from\_date},\; \text{to\_date} )$. Ví dụ: lấy trọn tháng 11/2026 truyền `from_date=2026-11-01&to_date=2026-12-01` (gồm $30$ ngày). |
| `room_type_id` | `BIGINT` | Không | Lọc theo hạng phòng cụ thể (áp dụng cho R01, R02, R04). Bỏ trống để lấy toàn khách sạn. |
| `granularity` | `ENUM` | Không | Chu kỳ gom nhóm biểu đồ chuỗi thời gian: `DAY` (mặc định), `WEEK`, hoặc `MONTH`. |

### 1.2. Quy tắc tính toán & Xử lý ngoại lệ
1. **Khoảng nửa mở (Half-Open Interval):**
   * Đối với dữ liệu ngày lưu trú (`reservation_room`), một đêm phòng được tính cho ngày $d$ nếu $d \in [\text{check\_in\_date},\; \text{check\_out\_date})$. Ngày khách trả phòng (`check_out_date`) không tính là một đêm lưu trú.
   * Đối với dữ liệu dấu thời gian (`issued_at`, `paid_at`, `ordered_at`, `completed_at`), bản ghi thuộc kỳ báo cáo khi $\text{timestamp} \ge \text{from\_date} \text{ 00:00:00}$ và $\text{timestamp} < \text{to\_date} \text{ 00:00:00}$.
2. **Bảo vệ chia cho $0$ (Division by Zero):**
   * Nếu mẫu số bằng $0$ (ví dụ: không có đêm phòng bán được trong kỳ hoặc chưa có đơn dịch vụ hoàn thành), API trả về `0.00` cho các chỉ số tỷ lệ/trung bình thay vì `NaN` hoặc `Infinity`.
3. **Quy ước làm tròn & Tiền tệ:**
   * Đơn vị tiền tệ mặc định: `VND` (`NUMERIC(14,2)`).
   * Tỷ lệ phần trăm (`%_pct`), chỉ số trung bình (`avg_*`, `mttr_hours`) làm tròn $2$ chữ số thập phân bằng `ROUND(val, 2)`.

---

## 2. Chi tiết 6 Báo cáo (R01 – R06)

### R01 — Báo cáo Công suất phòng (Occupancy Report)

* **Endpoint:** `GET /api/v1/reports/r01-occupancy`
* **Thành phần UI gợi ý:** 4 thẻ KPI tổng quan, biểu đồ đường tỷ lệ lấp đầy theo ngày/tháng, bảng phân rã theo hạng phòng.
* **Bảng nguồn:** `room`, `room_type`, `reservation`, `reservation_room`.
* **Quy tắc lọc dữ liệu:**
  * **Phòng khả dụng (Mẫu số):** Các phòng thỏa mãn `room.is_active = TRUE` và `room.maintenance_status <> 'OUT_OF_ORDER'`.
  * **Đêm phòng đã bán (Tử số):** Các dòng `reservation_room` thỏa mãn `is_cancelled = FALSE` và `reservation.status IN ('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT')`, có giao thoa ngày với kỳ báo cáo.

#### Công thức toán học
* **Tổng số đêm phòng khả dụng ($\text{Total Room-Nights}$):**
  $$\text{Total Room-Nights} = N_{\text{active\_rooms}} \times (\text{to\_date} - \text{from\_date})$$
* **Số đêm phòng đã bán ($\text{Occupied Room-Nights}$)** (xử lý chính xác cả các đơn đặt phòng vắt qua ranh giới `from_date` hoặc `to_date`):
  $$\text{Occupied Room-Nights} = \sum_{i} \max\Big(0,\; \min(\text{check\_out\_date}_i,\; \text{to\_date}) - \max(\text{check\_in\_date}_i,\; \text{from\_date})\Big)$$
* **Số đêm phòng còn trống ($\text{Available Room-Nights}$):**
  $$\text{Available Room-Nights} = \max\Big(0,\; \text{Total Room-Nights} - \text{Occupied Room-Nights}\Big)$$
* **Tỷ lệ lấp đầy ($\text{Occupancy Rate}$):**
  $$\text{Occupancy Rate (\%)} = \text{ROUND}\left(\frac{\text{Occupied Room-Nights}}{\text{Total Room-Nights}} \times 100,\; 2\right)$$

#### Truy vấn SQL tham chiếu (PostgreSQL)
```sql
WITH active_rooms AS (
    SELECT r.room_id, r.room_type_id, rt.name AS room_type_name
    FROM room r
    JOIN room_type rt ON rt.room_type_id = r.room_type_id
    WHERE r.is_active = TRUE
      AND r.maintenance_status <> 'OUT_OF_ORDER'
      AND ($3::bigint IS NULL OR r.room_type_id = $3)
),
occupied AS (
    SELECT
        ar.room_type_id,
        COALESCE(SUM(
            GREATEST(0, LEAST(rr.check_out_date, $2::date) - GREATEST(rr.check_in_date, $1::date))
        ), 0) AS occupied_nights
    FROM active_rooms ar
    LEFT JOIN reservation_room rr
      ON rr.room_id = ar.room_id
     AND rr.is_cancelled = FALSE
     AND rr.check_in_date < $2::date
     AND rr.check_out_date > $1::date
    LEFT JOIN reservation res
      ON res.reservation_id = rr.reservation_id
     AND res.status IN ('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT')
    GROUP BY ar.room_type_id
)
SELECT
    rt.room_type_id,
    rt.name AS room_type_name,
    COUNT(ar.room_id) * ($2::date - $1::date) AS total_room_nights,
    COALESCE(o.occupied_nights, 0) AS occupied_room_nights,
    ROUND(
        COALESCE(o.occupied_nights, 0)::numeric * 100
        / NULLIF(COUNT(ar.room_id) * ($2::date - $1::date), 0),
        2
    ) AS occupancy_rate_pct
FROM active_rooms ar
JOIN room_type rt ON rt.room_type_id = ar.room_type_id
LEFT JOIN occupied o ON o.room_type_id = rt.room_type_id
GROUP BY rt.room_type_id, rt.name, o.occupied_nights
ORDER BY rt.room_type_id;
```

#### JSON Contract mẫu
```json
{
  "report_code": "R01",
  "period": { "from_date": "2026-12-01", "to_date": "2027-01-01" },
  "summary": {
    "active_rooms": 4,
    "total_room_nights": 124,
    "occupied_room_nights": 22,
    "available_room_nights": 102,
    "occupancy_rate_pct": 17.74
  },
  "breakdown_by_room_type": [
    {
      "room_type_id": 1,
      "room_type_name": "Standard",
      "total_room_nights": 62,
      "occupied_room_nights": 13,
      "occupancy_rate_pct": 20.97
    },
    {
      "room_type_id": 2,
      "room_type_name": "Deluxe",
      "total_room_nights": 31,
      "occupied_room_nights": 5,
      "occupancy_rate_pct": 16.13
    },
    {
      "room_type_id": 3,
      "room_type_name": "Suite",
      "total_room_nights": 31,
      "occupied_room_nights": 4,
      "occupancy_rate_pct": 12.90
    }
  ]
}
```

---

### R02 — Báo cáo Doanh thu, ADR & RevPAR (Revenue & Yield Report)

* **Endpoint:** `GET /api/v1/reports/r02-revenue`
* **Thành phần UI gợi ý:** Thẻ KPI doanh thu thuần/tổng, ADR, RevPAR; biểu đồ cột chồng phân tách Doanh thu phòng vs Doanh thu dịch vụ.
* **Bảng nguồn:** `invoice`, `folio`, `folio_item`, `room`, `reservation_room`.
* **Quy tắc lọc dữ liệu:**
  * Chỉ tính các hóa đơn hợp lệ `invoice.status IN ('ISSUED', 'PARTIAL', 'PAID')` (loại bỏ `'DRAFT'` và `'VOID'`) có `invoice.issued_at` nằm trong kỳ $[ \text{from\_date},\; \text{to\_date} )$.
  * Phân loại nguồn doanh thu trên `folio_item` (`entry_type = 'CHARGE'`): tiền phòng có `source_key LIKE 'ROOM:%'`, tiền dịch vụ có `source_key LIKE 'SO%'` (`SO:` hoặc `SOI:`).

#### Công thức toán học
* **Doanh thu tiền phòng ($\text{Room Revenue}$):**
  $$\text{Room Revenue} = \sum_{\substack{\text{entry\_type} = \text{'CHARGE'} \\ \text{source\_key LIKE 'ROOM:\%'}}} (\text{quantity} \times \text{unit\_price})$$
* **Doanh thu dịch vụ ($\text{Service Revenue}$):**
  $$\text{Service Revenue} = \sum_{\substack{\text{entry\_type} = \text{'CHARGE'} \\ \text{source\_key LIKE 'SO\%'}}} (\text{quantity} \times \text{unit\_price})$$
* **Doanh thu thuần ($\text{Net Revenue}$ - sau giảm giá, trước thuế):**
  $$\text{Net Revenue} = \sum (\text{invoice.subtotal} - \text{invoice.discount\_total})$$
* **Tổng doanh thu có thuế ($\text{Gross Revenue}$):**
  $$\text{Gross Revenue} = \text{Net Revenue} + \sum \text{invoice.tax\_amount}$$
* **Giá phòng bình quân ngày ($\text{ADR - Average Daily Rate}$):**
  $$\text{ADR} = \text{ROUND}\left(\frac{\text{Room Revenue}}{\text{Occupied Room-Nights}},\; 2\right)$$
* **Doanh thu trên mỗi phòng khả dụng ($\text{RevPAR - Revenue Per Available Room}$):**
  $$\text{RevPAR} = \text{ROUND}\left(\frac{\text{Room Revenue}}{\text{Total Room-Nights}},\; 2\right)$$

#### JSON Contract mẫu
```json
{
  "report_code": "R02",
  "period": { "from_date": "2026-11-01", "to_date": "2026-12-01" },
  "currency": "VND",
  "summary": {
    "invoice_count": 1,
    "room_revenue": 2400000.00,
    "service_revenue": 240000.00,
    "other_charge_revenue": 0.00,
    "subtotal": 2640000.00,
    "discount_total": 240000.00,
    "net_revenue": 2400000.00,
    "tax_amount": 192000.00,
    "gross_revenue": 2592000.00,
    "adr": 1200000.00,
    "revpar": 20000.00
  },
  "series": [
    {
      "bucket": "2026-11-03",
      "room_revenue": 2400000.00,
      "service_revenue": 240000.00,
      "net_revenue": 2400000.00,
      "gross_revenue": 2592000.00
    }
  ]
}
```

---

### R03 — Báo cáo Công nợ & Dòng tiền thực thu (Billing & Cashflow Report)

* **Endpoint:** `GET /api/v1/reports/r03-billing-cashflow`
* **Thành phần UI gợi ý:** Biểu đồ tròn tỷ trọng phương thức thanh toán (`CASH`, `CARD`, `TRANSFER`, `EWALLET`), bảng danh sách hóa đơn chưa thanh toán hết (`ISSUED`, `PARTIAL`) và sổ cái khách đang ở (`OPEN`).
* **Bảng nguồn:** `invoice`, `payment`, `folio`, `folio_item`, `stay`, `reservation`, `guest`.
* **Quy tắc lọc dữ liệu:**
  * Tiền thực thu tính theo ngày ghi nhận giao dịch `payment.paid_at` trong kỳ $[ \text{from\_date},\; \text{to\_date} )$.
  * Công nợ phải thu (`Outstanding A/R`) tính trên các hóa đơn có `invoice.status IN ('ISSUED', 'PARTIAL')`.
  * Chi phí tạm tính khách đang ở (`Unbilled Open Folio`) tính trên các sổ cái `folio.status = 'OPEN'`, lưu ý `folio_item` loại `DISCOUNT` đã mang giá trị `unit_price <= 0`.

#### Công thức toán học
* **Giá trị phải thu của một hóa đơn ($\text{Invoice Total}$):**
  $$\text{Invoice Total} = \text{subtotal} - \text{discount\_total} + \text{tax\_amount} \quad (\text{status} \ne \text{'VOID'})$$
* **Tổng tiền thực thu trong kỳ ($\text{Collected Total}$):**
  $$\text{Collected Total} = \sum_{\text{paid\_at} \in [\text{from\_date},\; \text{to\_date})} \text{payment.amount}$$
* **Dư nợ phải thu chưa tất toán ($\text{Outstanding A/R Balance}$):**
  $$\text{Outstanding A/R Balance} = \sum_{\text{status} \in \{\text{'ISSUED'},\; \text{'PARTIAL'}\}} \left(\text{Invoice Total} - \sum \text{payment.amount}\right)$$
* **Giá trị phát sinh tạm tính trên các phòng đang ở ($\text{Unbilled Open Folio Total}$):**
  $$\text{Unbilled Open Folio Total} = \sum_{\text{folio.status} = \text{'OPEN'}} (\text{folio\_item.quantity} \times \text{folio\_item.unit\_price})$$

#### JSON Contract mẫu
```json
{
  "report_code": "R03",
  "period": { "from_date": "2026-11-01", "to_date": "2026-12-01" },
  "currency": "VND",
  "summary": {
    "billed_gross_total": 2592000.00,
    "collected_total": 2592000.00,
    "outstanding_ar_balance": 0.00,
    "unbilled_open_folio_total": 2500000.00
  },
  "collections_by_method": [
    { "method": "CASH",     "tx_count": 0, "amount": 0.00 },
    { "method": "CARD",     "tx_count": 1, "amount": 2592000.00 },
    { "method": "TRANSFER", "tx_count": 0, "amount": 0.00 },
    { "method": "EWALLET",  "tx_count": 0, "amount": 0.00 }
  ],
  "open_folios": [
    {
      "folio_id": 2,
      "stay_id": 2,
      "guest_name": "Tran Duc Long",
      "room_number": "202",
      "accrued_amount": 2500000.00
    }
  ]
}
```

---

### R04 — Báo cáo Đặt phòng, Hủy phòng & Hiệu quả Khuyến mãi (Booking Funnel & Promos)

* **Endpoint:** `GET /api/v1/reports/r04-booking-funnel`
* **Thành phần UI gợi ý:** Biểu đồ phễu trạng thái đặt phòng, chỉ số thời gian đặt trước (Lead Time) & số đêm ở trung bình (ALOS), bảng hiệu quả từng mã giảm giá.
* **Bảng nguồn:** `reservation`, `reservation_room`, `reservation_discount`, `discount`.
* **Quy tắc lọc dữ liệu:** Lọc theo ngày tạo đơn `reservation.created_at` nằm trong kỳ $[ \text{from\_date},\; \text{to\_date} )$.

#### Công thức toán học
* **Tỷ lệ hủy đơn ($\text{Cancellation Rate}$):**
  $$\text{Cancellation Rate (\%)} = \text{ROUND}\left(\frac{N_{\text{status} = \text{'CANCELLED'}}}{N_{\text{total\_reservations}}} \times 100,\; 2\right)$$
* **Tỷ lệ khách không đến ($\text{No-Show Rate}$):**
  $$\text{No-Show Rate (\%)} = \text{ROUND}\left(\frac{N_{\text{status} = \text{'NO\_SHOW'}}}{N_{\text{total\_reservations}}} \times 100,\; 2\right)$$
* **Thời gian đặt phòng trước trung bình ($\text{Avg Lead Time - Days}$):**
  $$\text{Avg Lead Time} = \text{ROUND}\left(\frac{1}{N} \sum_{i=1}^{N} \Big(\text{check\_in\_date}_i - \text{DATE}(\text{created\_at}_i)\Big),\; 2\right)$$
* **Số đêm lưu trú trung bình trên mỗi phòng đặt ($\text{ALOS - Average Length of Stay}$):**
  $$\text{ALOS} = \text{ROUND}\left(\frac{\sum_{\text{is\_cancelled} = \text{FALSE}} (\text{check\_out\_date} - \text{check\_in\_date})}{N_{\text{reservation\_room} \mid \text{is\_cancelled} = \text{FALSE}}},\; 2\right)$$

#### JSON Contract mẫu
```json
{
  "report_code": "R04",
  "period": { "from_date": "2026-10-01", "to_date": "2026-12-01" },
  "summary": {
    "total_reservations": 7,
    "status_breakdown": {
      "PENDING": 0,
      "CONFIRMED": 5,
      "CHECKED_IN": 1,
      "CHECKED_OUT": 1,
      "CANCELLED": 0,
      "NO_SHOW": 0
    },
    "cancellation_rate_pct": 0.00,
    "no_show_rate_pct": 0.00,
    "avg_lead_time_days": 23.40,
    "avg_length_of_stay_nights": 2.25
  },
  "promo_performance": [
    {
      "discount_id": 1,
      "code": "WELCOME10",
      "discount_type": "PERCENT",
      "usage_count": 1,
      "total_discount_amount": 240000.00
    },
    {
      "discount_id": 2,
      "code": "FIXED500K",
      "discount_type": "FIXED",
      "usage_count": 1,
      "total_discount_amount": 500000.00
    }
  ]
}
```

---

### R05 — Báo cáo Doanh thu & SLA Dịch vụ bổ sung (Services & SLA Report)

* **Endpoint:** `GET /api/v1/reports/r05-services`
* **Thành phần UI gợi ý:** Biểu đồ cột doanh thu theo nhóm dịch vụ (`FOOD`, `BEVERAGE`, `LAUNDRY`, `SPA`, `TRANSPORT`, `OTHER`), thẻ thời gian xử lý đơn trung bình (SLA) và tỷ lệ gắn kết dịch vụ (Attach Rate).
* **Bảng nguồn:** `service`, `service_order`, `service_order_item`, `stay_room`, `stay`.
* **Quy tắc lọc dữ liệu:** Lọc theo `service_order.ordered_at` trong kỳ $[ \text{from\_date},\; \text{to\_date} )$. Doanh thu và thời gian xử lý SLA chỉ tính trên các đơn có `service_order.status = 'COMPLETED'`.

#### Công thức toán học
* **Doanh thu dịch vụ hoàn thành ($\text{Total Service Sales}$):**
  $$\text{Total Service Sales} = \sum_{\text{status} = \text{'COMPLETED'}} (\text{service\_order\_item.quantity} \times \text{service\_order\_item.unit\_price})$$
* **Thời gian hoàn tất đơn dịch vụ trung bình ($\text{Avg Fulfillment Minutes}$):**
  $$\text{Avg Fulfillment Minutes} = \text{ROUND}\left(\frac{1}{N_{\text{completed}}} \sum \frac{\text{EXTRACT(EPOCH FROM (completed\_at - ordered\_at))}}{60},\; 2\right)$$
* **Tỷ lệ lượt lưu trú có sử dụng dịch vụ ($\text{Service Attach Rate}$):**
  $$\text{Service Attach Rate (\%)} = \text{ROUND}\left(\frac{\text{Count(DISTINCT stay\_id có đơn COMPLETED)}}{\text{Total Stays trong kỳ}} \times 100,\; 2\right)$$

#### JSON Contract mẫu
```json
{
  "report_code": "R05",
  "period": { "from_date": "2026-11-01", "to_date": "2026-12-01" },
  "currency": "VND",
  "summary": {
    "total_orders": 2,
    "completed_orders": 1,
    "in_progress_orders": 1,
    "cancelled_orders": 0,
    "total_service_sales": 240000.00,
    "avg_fulfillment_minutes": 30.00,
    "service_attach_rate_pct": 50.00
  },
  "breakdown_by_category": [
    { "category": "FOOD",      "order_items": 1, "quantity": 2.00, "revenue": 240000.00 },
    { "category": "LAUNDRY",   "order_items": 0, "quantity": 0.00, "revenue": 0.00 },
    { "category": "BEVERAGE",  "order_items": 0, "quantity": 0.00, "revenue": 0.00 },
    { "category": "SPA",       "order_items": 0, "quantity": 0.00, "revenue": 0.00 },
    { "category": "TRANSPORT", "order_items": 0, "quantity": 0.00, "revenue": 0.00 },
    { "category": "OTHER",     "order_items": 0, "quantity": 0.00, "revenue": 0.00 }
  ]
}
```

---

### R06 — Báo cáo Buồng phòng, Bảo trì & Chất lượng Đánh giá (Operations & CSAT)

* **Endpoint:** `GET /api/v1/reports/r06-operations-csat`
* **Thành phần UI gợi ý:** 3 khối chỉ số vận hành song song: Hiệu suất Buồng phòng (Housekeeping), Thời gian sửa chữa Bảo trì (MTTR) và Điểm hài lòng khách hàng (CSAT $1$ – $5$ sao).
* **Bảng nguồn:** `housekeeping_task`, `maintenance_ticket`, `guest_review`, `room`.
* **Quy tắc lọc dữ liệu:**
  * Buồng phòng lọc theo `scheduled_at` trong kỳ; loại trừ các tác vụ `'CANCELLED'` khỏi mẫu số tỷ lệ hoàn thành.
  * Bảo trì lọc theo `reported_at` trong kỳ; MTTR tính trên các phiếu đã đóng (`closed_at IS NOT NULL`).
  * Đánh giá khách hàng lọc theo `guest_review.created_at` trong kỳ.

#### Công thức toán học
* **Tỷ lệ hoàn thành dọn phòng ($\text{HK Completion Rate}$):**
  $$\text{HK Completion Rate (\%)} = \text{ROUND}\left(\frac{N_{\text{hk\_status} = \text{'COMPLETED'}}}{N_{\text{hk\_status} \ne \text{'CANCELLED'}}} \times 100,\; 2\right)$$
* **Thời gian dọn phòng trung bình ($\text{Avg HK Turnaround Minutes}$):**
  $$\text{Avg HK Turnaround Minutes} = \text{ROUND}\left(\frac{1}{N_{\text{hk\_completed}}} \sum \frac{\text{EXTRACT(EPOCH FROM (completed\_at - scheduled\_at))}}{60},\; 2\right)$$
* **Thời gian khắc phục sự cố trung bình ($\text{MTTR - Mean Time To Repair in Hours}$):**
  $$\text{MTTR (Hours)} = \text{ROUND}\left(\frac{1}{N_{\text{closed\_tickets}}} \sum \frac{\text{EXTRACT(EPOCH FROM (closed\_at - reported\_at))}}{3600},\; 2\right)$$
* **Điểm hài lòng khách hàng trung bình ($\text{Avg Guest Rating - CSAT}$):**
  $$\text{Avg Guest Rating} = \text{ROUND}\left(\frac{1}{N_{\text{reviews}}} \sum_{i=1}^{N_{\text{reviews}}} \text{rating}_i,\; 2\right)$$

#### JSON Contract mẫu
```json
{
  "report_code": "R06",
  "period": { "from_date": "2026-11-01", "to_date": "2026-12-01" },
  "housekeeping": {
    "total_active_tasks": 2,
    "completed_tasks": 1,
    "pending_or_in_progress": 1,
    "completion_rate_pct": 50.00,
    "avg_turnaround_minutes": 40.00
  },
  "maintenance": {
    "total_tickets": 2,
    "open_or_in_progress": 1,
    "resolved_or_closed": 1,
    "mttr_hours": 1.00,
    "out_of_order_rooms_now": 0
  },
  "guest_satisfaction": {
    "review_count": 1,
    "avg_rating": 5.00,
    "five_star_share_pct": 100.00,
    "rating_distribution": {
      "5": 1,
      "4": 0,
      "3": 0,
      "2": 0,
      "1": 0
    }
  }
}
```

---

## 3. Ma trận chuẩn hóa định dạng hiển thị cho Frontend

| Hậu tố trường JSON | Kiểu dữ liệu | Định dạng hiển thị gợi ý trên UI | Ví dụ hiển thị |
| :--- | :--- | :--- | :--- |
| `*_revenue`, `*_amount`, `*_total`, `*_balance`, `adr`, `revpar` | `number` | Định dạng tiền tệ `vi-VN`, làm tròn hàng đơn vị hoặc $2$ số lẻ | `2.592.000 ₫` |
| `*_pct` | `number` | Kèm ký hiệu `%` với $2$ chữ số thập phân | `17,74%` |
| `*_nights`, `*_count`, `*_tasks`, `*_tickets` | `integer` | Số nguyên phân cách hàng nghìn | `124` |
| `*_days`, `*_minutes`, `*_hours`, `avg_rating`, `quantity` | `number` | Số thập phân tối đa $2$ chữ số lẻ kèm đơn vị | `40,00 phút` / `5,00 / 5` |