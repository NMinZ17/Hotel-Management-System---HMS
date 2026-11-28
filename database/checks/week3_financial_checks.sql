-- ============================================================================
-- KIỂM TRA TÀI CHÍNH TUẦN 2: database/checks/week2_financial_checks.sql
-- Phan Thị Mai Trang – HMS-W2-TRANG
-- Issue: https://github.com/NMinZ17/Hotel-Management-System---HMS/issues/7
--
-- Chạy SAU: 01_master_seed.sql + 02_dev_fixture.sql + 06_financial_fixture.sql
-- Môi trường: hms_dev
--
-- File này gồm 4 phần:
--   P1 – Kiểm tra cấu trúc và tính toàn vẹn dữ liệu
--   P2 – Đối chiếu số tiền fixture #20 (không nhân bản SUM)
--   P3 – SQL R01–R06 với kỳ cố định và kết quả kỳ vọng
--   P4 – Chứng minh lỗi nhân bản SUM khi JOIN sai cách
--
-- Chạy từng khối SELECT riêng lẻ trong psql hoặc DBeaver.
-- Mỗi truy vấn có dòng -- KỲ VỌNG: ... ghi rõ kết quả đúng.
-- ============================================================================


-- ============================================================================
-- PHẦN 1: KIỂM TRA CẤU TRÚC VÀ TÍNH TOÀN VẸN
-- ============================================================================

-- ─────────────────────────────────────────────────
-- P1-A: Đếm đúng 28 bảng nghiệp vụ trong schema
-- KỲ VỌNG: 28
-- ─────────────────────────────────────────────────
SELECT COUNT(*) AS so_bang
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type   = 'BASE TABLE';

-- ─────────────────────────────────────────────────
-- P1-B: reservation_room không có reservation tương ứng (mồ côi)
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT rr.reservation_room_id, rr.reservation_id
FROM reservation_room rr
LEFT JOIN reservation r ON r.reservation_id = rr.reservation_id
WHERE r.reservation_id IS NULL;

-- ─────────────────────────────────────────────────
-- P1-C: folio_item không có folio tương ứng (mồ côi)
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT fi.folio_item_id, fi.folio_id
FROM folio_item fi
LEFT JOIN folio f ON f.folio_id = fi.folio_id
WHERE f.folio_id IS NULL;

-- ─────────────────────────────────────────────────
-- P1-D: folio OPEN khi stay đã CHECKED_OUT (không nhất quán)
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT f.folio_id, f.status AS folio_status, s.status AS stay_status
FROM folio f
JOIN stay s ON s.stay_id = f.stay_id
WHERE s.status = 'CHECKED_OUT'
  AND f.status = 'OPEN';

-- ─────────────────────────────────────────────────
-- P1-E: invoice PAID mà tổng payment < gross (tổng phải thu)
-- gross = subtotal - discount_total + tax_amount
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT
    i.invoice_id,
    i.invoice_number,
    (i.subtotal - i.discount_total + i.tax_amount)   AS gross,
    COALESCE(SUM(p.amount), 0)                        AS tong_da_thu,
    (i.subtotal - i.discount_total + i.tax_amount)
      - COALESCE(SUM(p.amount), 0)                    AS con_thieu
FROM invoice i
LEFT JOIN payment p ON p.invoice_id = i.invoice_id
WHERE i.status = 'PAID'
GROUP BY i.invoice_id, i.invoice_number, i.subtotal, i.discount_total, i.tax_amount
HAVING COALESCE(SUM(p.amount), 0) < (i.subtotal - i.discount_total + i.tax_amount);

-- ─────────────────────────────────────────────────
-- P1-F: service_order_item ghi cùng folio_item_id hai lần
-- (vi phạm uq_service_order_item_folio_item)
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT folio_item_id, COUNT(*) AS lan_ghi
FROM service_order_item
WHERE folio_item_id IS NOT NULL
GROUP BY folio_item_id
HAVING COUNT(*) > 1;

-- ─────────────────────────────────────────────────
-- P1-G: Chống chồng lịch – phòng bị giữ 2 lần trong cùng khoảng ngày
-- (ràng buộc EXCLUDE đã xử lý ở DB, kiểm tra để xác nhận)
-- KỲ VỌNG: 0 dòng
-- ─────────────────────────────────────────────────
SELECT a.reservation_room_id AS id_a, b.reservation_room_id AS id_b,
       a.room_id, a.check_in_date, a.check_out_date
FROM reservation_room a
JOIN reservation_room b
  ON a.room_id = b.room_id
 AND a.reservation_room_id < b.reservation_room_id
 AND a.is_cancelled = FALSE
 AND b.is_cancelled = FALSE
 AND daterange(a.check_in_date, a.check_out_date, '[)')
  && daterange(b.check_in_date, b.check_out_date, '[)');


-- ============================================================================
-- PHẦN 2: ĐỐI CHIẾU SỐ TIỀN FIXTURE #20
-- ============================================================================

-- ─────────────────────────────────────────────────
-- P2-A: Tổng từng loại folio_item của folio_id=20
-- KỲ VỌNG:
--   CHARGE   = 6.340.000  (2.400k + 3.600k + 100k + 240k)
--   DISCOUNT =  -634.000
--   Net dòng = 5.706.000
-- ─────────────────────────────────────────────────
SELECT
    entry_type,
    COUNT(*)                                     AS so_dong,
    SUM(quantity * unit_price)                   AS tong_thanh_tien
FROM folio_item
WHERE folio_id = 20
GROUP BY entry_type
ORDER BY entry_type;

-- ─────────────────────────────────────────────────
-- P2-B: So sánh tổng folio_item CHARGE với invoice.subtotal
-- KỲ VỌNG: sai_lech = 0
-- ─────────────────────────────────────────────────
WITH charge_sum AS (
    SELECT
        f.folio_id,
        SUM(fi.quantity * fi.unit_price) AS tong_charge
    FROM folio f
    JOIN folio_item fi ON fi.folio_id = f.folio_id
    WHERE fi.entry_type = 'CHARGE'
      AND f.folio_id = 20
    GROUP BY f.folio_id
)
SELECT
    cs.folio_id,
    cs.tong_charge                                AS tinh_tu_folio_item,
    i.subtotal                                    AS invoice_subtotal,
    cs.tong_charge - i.subtotal                   AS sai_lech
FROM charge_sum cs
JOIN invoice i ON i.folio_id = cs.folio_id;

-- ─────────────────────────────────────────────────
-- P2-C: Kiểm tra gross = subtotal - discount_total + tax_amount
-- và tổng payment = gross
-- KỲ VỌNG:
--   gross           = 6.162.480
--   tong_payment    = 6.162.480
--   sai_lech_tien   = 0,00
-- ─────────────────────────────────────────────────
SELECT
    i.invoice_id,
    i.invoice_number,
    i.subtotal,
    i.discount_total,
    i.tax_amount,
    (i.subtotal - i.discount_total + i.tax_amount)   AS gross,
    SUM(p.amount)                                     AS tong_payment,
    (i.subtotal - i.discount_total + i.tax_amount)
      - SUM(p.amount)                                 AS sai_lech_tien
FROM invoice i
JOIN payment p ON p.invoice_id = i.invoice_id
WHERE i.invoice_id = 20
GROUP BY i.invoice_id, i.invoice_number, i.subtotal, i.discount_total, i.tax_amount;

-- ─────────────────────────────────────────────────
-- P2-D: Chi tiết từng payment của invoice #20
-- KỲ VỌNG: 2 dòng – 3.000.000 CASH + 3.162.480 TRANSFER
-- ─────────────────────────────────────────────────
SELECT payment_id, amount, method, transaction_ref,
       paid_at AT TIME ZONE 'Asia/Ho_Chi_Minh' AS paid_at_vn
FROM payment
WHERE invoice_id = 20
ORDER BY paid_at;

-- ─────────────────────────────────────────────────
-- P2-E: Dịch vụ ĂN SÁNG (service_order #22) chưa ghi folio
-- KỲ VỌNG: folio_item_id IS NULL, status=IN_PROGRESS
--           → 480.000 VND KHÔNG được tính vào R02/R03
-- ─────────────────────────────────────────────────
SELECT
    so.service_order_id,
    s.name       AS service_name,
    soi.quantity,
    soi.unit_price,
    soi.quantity * soi.unit_price AS gia_tri_chua_ghi,
    soi.folio_item_id,
    so.status
FROM service_order_item soi
JOIN service_order so ON so.service_order_id = soi.service_order_id
JOIN service s ON s.service_id = soi.service_id
WHERE so.service_order_id = 22;


-- ============================================================================
-- PHẦN 3: SQL R01–R06
--
-- Giả định: 01_master + 02_dev + 06_financial_fixture đã được nạp.
-- KHÔNG giả định 05_edge_case_fixture (để kết quả xác định).
--
-- Kỳ báo cáo cho R01, R02, R03, R05, R06: [2026-12-05, 2026-12-09)  ← 4 ngày
--   Chỉ đơn #20 (phòng 101+201) và service_order #20,21,22 rơi vào kỳ này.
-- Kỳ báo cáo cho R04: [2026-11-01, 2026-12-09)  ← để bắt được đơn #20 theo created_at
-- ============================================================================

-- ─────────────────────────────────────────────────
-- R01 – Công suất phòng
-- Kỳ: 2026-12-05 đến 2026-12-09 (4 ngày)
--
-- Active rooms (maintenance_status <> 'OUT_OF_ORDER', is_active=TRUE):
--   101 (OK), 102 (OK), 201 (OK), 202 (OK), 301 (MINOR_ISSUE) → 5 phòng
-- total_room_nights    = 5 × 4 = 20
-- Occupied nights trong kỳ:
--   RR #20: phòng 101, [2026-12-05, 2026-12-08) ∩ [2026-12-05, 2026-12-09) = 3 đêm
--   RR #21: phòng 201, [2026-12-05, 2026-12-08) ∩ [2026-12-05, 2026-12-09) = 3 đêm
-- occupied_room_nights = 6
-- occupancy_rate_pct   = ROUND(6/20×100, 2) = 30.00%
--
-- KỲ VỌNG (tổng): total=20, occupied=6, available=14, rate=30.00%
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-12-05'::date AS from_date,
           '2026-12-09'::date AS to_date,
           NULL::bigint        AS filter_room_type_id
),
active_rooms AS (
    SELECT r.room_id, r.room_type_id, rt.name AS room_type_name
    FROM room r
    JOIN room_type rt ON rt.room_type_id = r.room_type_id
    CROSS JOIN params
    WHERE r.is_active = TRUE
      AND r.maintenance_status <> 'OUT_OF_ORDER'
      AND (params.filter_room_type_id IS NULL
           OR r.room_type_id = params.filter_room_type_id)
),
occupied AS (
    SELECT
        ar.room_type_id,
        COALESCE(SUM(
            GREATEST(0,
                LEAST(rr.check_out_date, p.to_date)
                - GREATEST(rr.check_in_date, p.from_date)
            )
        ), 0) AS occupied_nights
    FROM active_rooms ar
    CROSS JOIN params p
    LEFT JOIN reservation_room rr
        ON rr.room_id = ar.room_id
       AND rr.is_cancelled = FALSE
       AND rr.check_in_date  < p.to_date
       AND rr.check_out_date > p.from_date
    LEFT JOIN reservation res
        ON res.reservation_id = rr.reservation_id
       AND res.status IN ('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT')
    GROUP BY ar.room_type_id
)
SELECT
    rt.room_type_id,
    rt.name                                                                     AS room_type_name,
    COUNT(ar.room_id) * (p.to_date - p.from_date)                              AS total_room_nights,
    COALESCE(o.occupied_nights, 0)                                              AS occupied_room_nights,
    GREATEST(0, COUNT(ar.room_id) * (p.to_date - p.from_date)
               - COALESCE(o.occupied_nights, 0))                                AS available_room_nights,
    ROUND(
        COALESCE(o.occupied_nights, 0)::numeric * 100
        / NULLIF(COUNT(ar.room_id) * (p.to_date - p.from_date), 0),
        2
    )                                                                           AS occupancy_rate_pct
FROM active_rooms ar
CROSS JOIN params p
JOIN room_type rt ON rt.room_type_id = ar.room_type_id
LEFT JOIN occupied o ON o.room_type_id = rt.room_type_id
GROUP BY rt.room_type_id, rt.name, o.occupied_nights, p.to_date, p.from_date
ORDER BY rt.room_type_id;


-- ─────────────────────────────────────────────────
-- R02 – Doanh thu, ADR và RevPAR
-- Kỳ: 2026-12-05 đến 2026-12-09
-- Chỉ invoice PAID/ISSUED/PARTIAL có issued_at trong kỳ
--
-- invoice #20: issued_at = 2026-12-08 11:05 ✓ trong kỳ
--   room_revenue    = 2.400.000 + 3.600.000  = 6.000.000  (source_key LIKE 'ROOM:%')
--   service_revenue = 100.000  + 240.000     =   340.000  (source_key LIKE 'SOI:%')
--   subtotal        = 6.340.000
--   discount_total  =   634.000
--   net_revenue     = 5.706.000
--   tax_amount      =   456.480
--   gross_revenue   = 6.162.480
--   ADR             = 6.000.000 / 6 = 1.000.000,00
--   RevPAR          = 6.000.000 / 20 = 300.000,00   (total_room_nights=20 từ R01)
--
-- KỲ VỌNG: invoice_count=1, room_rev=6.000.000, svc_rev=340.000,
--          net=5.706.000, gross=6.162.480, ADR=1.000.000, RevPAR=300.000
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-12-05'::date AS from_date,
           '2026-12-09'::date AS to_date
),
valid_invoices AS (
    SELECT i.invoice_id, i.folio_id, i.subtotal, i.discount_total, i.tax_amount
    FROM invoice i
    CROSS JOIN params p
    WHERE i.status IN ('PAID', 'ISSUED', 'PARTIAL')
      AND i.issued_at >= p.from_date
      AND i.issued_at <  p.to_date + INTERVAL '1 day'  -- to_date ngày cuối tính đến 00:00 hôm sau
),
-- Tổng hợp folio_item TRƯỚC khi join với invoice để tránh nhân bản
folio_revenue AS (
    SELECT
        fi.folio_id,
        SUM(CASE WHEN fi.entry_type = 'CHARGE'
                  AND fi.source_key LIKE 'ROOM:%'
                 THEN fi.quantity * fi.unit_price ELSE 0 END) AS room_revenue,
        SUM(CASE WHEN fi.entry_type = 'CHARGE'
                  AND fi.source_key LIKE 'SOI:%'
                 THEN fi.quantity * fi.unit_price ELSE 0 END) AS service_revenue,
        SUM(CASE WHEN fi.entry_type = 'CHARGE'
                  AND fi.source_key NOT LIKE 'ROOM:%'
                  AND fi.source_key NOT LIKE 'SOI:%'
                 THEN fi.quantity * fi.unit_price ELSE 0 END) AS other_revenue
    FROM folio_item fi
    WHERE fi.entry_type = 'CHARGE'
    GROUP BY fi.folio_id
),
-- Đếm occupied nights độc lập (tái dùng logic R01)
occupied_nights_total AS (
    SELECT COALESCE(SUM(
        GREATEST(0,
            LEAST(rr.check_out_date, p.to_date)
            - GREATEST(rr.check_in_date, p.from_date)
        )
    ), 0) AS total_occ
    FROM reservation_room rr
    JOIN reservation res ON res.reservation_id = rr.reservation_id
    CROSS JOIN params p
    WHERE rr.is_cancelled = FALSE
      AND res.status IN ('CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT')
      AND rr.check_in_date  < p.to_date
      AND rr.check_out_date > p.from_date
),
active_room_count AS (
    SELECT COUNT(*) AS n FROM room
    WHERE is_active = TRUE AND maintenance_status <> 'OUT_OF_ORDER'
),
total_room_nights AS (
    SELECT arc.n * (p.to_date - p.from_date) AS trn
    FROM active_room_count arc CROSS JOIN params p
)
SELECT
    COUNT(vi.invoice_id)                                AS invoice_count,
    ROUND(SUM(fr.room_revenue),    2)                   AS room_revenue,
    ROUND(SUM(fr.service_revenue), 2)                   AS service_revenue,
    ROUND(SUM(vi.subtotal),        2)                   AS subtotal,
    ROUND(SUM(vi.discount_total),  2)                   AS discount_total,
    ROUND(SUM(vi.subtotal - vi.discount_total), 2)      AS net_revenue,
    ROUND(SUM(vi.tax_amount),      2)                   AS tax_amount,
    ROUND(SUM(vi.subtotal - vi.discount_total
              + vi.tax_amount),    2)                   AS gross_revenue,
    -- ont và trn là scalar (1 dòng) → dùng MAX() để dùng được với aggregate
    ROUND(SUM(fr.room_revenue)
          / NULLIF(MAX(ont.total_occ), 0), 2)           AS adr,
    ROUND(SUM(fr.room_revenue)
          / NULLIF(MAX(trn.trn), 0),    2)              AS revpar
FROM valid_invoices vi
LEFT JOIN folio_revenue fr ON fr.folio_id = vi.folio_id
CROSS JOIN occupied_nights_total ont
CROSS JOIN total_room_nights trn;


-- ─────────────────────────────────────────────────
-- R03 – Công nợ và dòng tiền thực thu
-- Kỳ: 2026-12-05 đến 2026-12-09 (lọc payment.paid_at)
--
-- Thực thu trong kỳ:
--   payment #20: 3.000.000 CASH   paid_at 2026-12-08 ✓
--   payment #21: 3.162.480 TRANSFER paid_at 2026-12-08 ✓
--   collected_total = 6.162.480
-- Outstanding A/R (invoice ISSUED/PARTIAL):
--   invoice #20 → PAID → 0
--   → outstanding_ar_balance = 0
-- Open folio (from 02_dev_fixture):
--   folio #2 (stay #2 IN_HOUSE): folio_item #4 qty=1 unit_price=2.500.000
--   unbilled_open_folio_total = 2.500.000
--
-- KỲ VỌNG:
--   collected_total = 6.162.480
--   outstanding_ar_balance = 0
--   unbilled_open_folio_total = 2.500.000
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-12-05'::date AS from_date,
           '2026-12-09'::date AS to_date
),
collected AS (
    SELECT
        p.method,
        COUNT(*)        AS tx_count,
        SUM(p.amount)   AS amount
    FROM payment p
    CROSS JOIN params pr
    WHERE p.paid_at >= pr.from_date
      AND p.paid_at <  pr.to_date + INTERVAL '1 day'
    GROUP BY p.method
),
outstanding AS (
    SELECT
        COALESCE(SUM(
            (i.subtotal - i.discount_total + i.tax_amount)
            - COALESCE(paid.paid_sum, 0)
        ), 0) AS ar_balance
    FROM invoice i
    LEFT JOIN (
        SELECT invoice_id, SUM(amount) AS paid_sum
        FROM payment GROUP BY invoice_id
    ) paid ON paid.invoice_id = i.invoice_id
    WHERE i.status IN ('ISSUED', 'PARTIAL')
),
open_folios AS (
    SELECT
        f.folio_id,
        f.stay_id,
        SUM(fi.quantity * fi.unit_price) AS accrued_amount
    FROM folio f
    JOIN folio_item fi ON fi.folio_id = f.folio_id
    WHERE f.status = 'OPEN'
    GROUP BY f.folio_id, f.stay_id
)
SELECT
    COALESCE(SUM(c.amount), 0)              AS collected_total,
    (SELECT ar_balance FROM outstanding)    AS outstanding_ar_balance,
    COALESCE(SUM(of2.accrued_amount), 0)    AS unbilled_open_folio_total
FROM collected c
FULL OUTER JOIN open_folios of2 ON FALSE;  -- cross product sẽ sai; dùng subquery

-- Phiên bản rõ hơn:
SELECT
    (SELECT COALESCE(SUM(p.amount), 0)
     FROM payment p
     WHERE p.paid_at >= '2026-12-05'
       AND p.paid_at <  '2026-12-09'::date + INTERVAL '1 day')       AS collected_total,

    (SELECT COALESCE(SUM(
         (i.subtotal - i.discount_total + i.tax_amount)
         - COALESCE(ps.paid_sum, 0)
     ), 0)
     FROM invoice i
     LEFT JOIN (SELECT invoice_id, SUM(amount) AS paid_sum
                FROM payment GROUP BY invoice_id) ps
            ON ps.invoice_id = i.invoice_id
     WHERE i.status IN ('ISSUED', 'PARTIAL'))                          AS outstanding_ar_balance,

    (SELECT COALESCE(SUM(fi.quantity * fi.unit_price), 0)
     FROM folio f
     JOIN folio_item fi ON fi.folio_id = f.folio_id
     WHERE f.status = 'OPEN')                                          AS unbilled_open_folio_total;

-- Thanh toán phân theo phương thức trong kỳ:
SELECT
    p.method,
    COUNT(*)        AS tx_count,
    SUM(p.amount)   AS amount
FROM payment p
WHERE p.paid_at >= '2026-12-05'
  AND p.paid_at <  '2026-12-09'::date + INTERVAL '1 day'
GROUP BY p.method
ORDER BY p.method;


-- ─────────────────────────────────────────────────
-- R04 – Đặt phòng, hủy và khuyến mãi
-- Kỳ: 2026-11-01 đến 2026-12-09 (lọc reservation.created_at)
--
-- Đơn tạo trong kỳ (từ 02_dev + 06_financial):
--   #1  CONFIRMED  tạo 2026-11-15  ✓
--   #2  CHECKED_OUT tạo 2026-10-25 ✗ (ngoài kỳ)
--   #3  CHECKED_IN  tạo 2026-11-18  ✓
--   #20 CHECKED_OUT tạo 2026-11-20  ✓
-- total_reservations = 3  (1,3,20)
-- cancellation_rate  = 0.00%
-- avg_lead_time      = tính tay bên dưới
--
-- RR #1  : check_in 2026-12-10, created 2026-11-15 → lead = 25 ngày
-- RR #3  : check_in 2026-11-19, created 2026-11-18 → lead =  1 ngày
-- RR #20a: check_in 2026-12-05, created 2026-11-20 → lead = 15 ngày
-- RR #20b: check_in 2026-12-05, created 2026-11-20 → lead = 15 ngày
-- avg_lead = (25 + 1 + 15 + 15) / 4 = 56/4 = 14.00 ngày
-- ALOS (is_cancelled=FALSE):
--   RR #1: 2 đêm, RR #3: 3 đêm, RR #20a: 3 đêm, RR #20b: 3 đêm → ALOS = 11/4 = 2.75
--
-- KỲ VỌNG: total=3, cancel_rate=0, avg_lead=14.00, ALOS=2.75
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-11-01'::date AS from_date,
           '2026-12-09'::date AS to_date
),
res_in_period AS (
    SELECT r.*
    FROM reservation r
    CROSS JOIN params p
    WHERE r.created_at >= p.from_date
      AND r.created_at <  p.to_date + INTERVAL '1 day'
),
booking_stats AS (
    SELECT
        COUNT(*)                                                            AS total_reservations,
        COUNT(*) FILTER (WHERE status = 'CANCELLED')                       AS cancelled_count,
        COUNT(*) FILTER (WHERE status = 'NO_SHOW')                         AS no_show_count,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'CANCELLED')::numeric * 100
            / NULLIF(COUNT(*), 0), 2
        )                                                                   AS cancellation_rate_pct,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'NO_SHOW')::numeric * 100
            / NULLIF(COUNT(*), 0), 2
        )                                                                   AS no_show_rate_pct
    FROM res_in_period
),
lead_alos AS (
    SELECT
        ROUND(AVG(rr.check_in_date - r.created_at::date), 2)               AS avg_lead_time_days,
        ROUND(AVG(rr.check_out_date - rr.check_in_date), 2)                AS avg_length_of_stay
    FROM res_in_period r
    JOIN reservation_room rr ON rr.reservation_id = r.reservation_id
    WHERE rr.is_cancelled = FALSE
)
SELECT bs.*, la.avg_lead_time_days, la.avg_length_of_stay
FROM booking_stats bs CROSS JOIN lead_alos la;

-- Hiệu quả khuyến mãi trong kỳ:
SELECT
    d.discount_id, d.code, d.discount_type,
    COUNT(rd.reservation_id)   AS usage_count,
    SUM(rd.discount_amount)    AS total_discount_amount
FROM reservation_discount rd
JOIN discount d ON d.discount_id = rd.discount_id
JOIN reservation r ON r.reservation_id = rd.reservation_id
WHERE r.created_at >= '2026-11-01'
  AND r.created_at <  '2026-12-09'::date + INTERVAL '1 day'
GROUP BY d.discount_id, d.code, d.discount_type
ORDER BY d.discount_id;


-- ─────────────────────────────────────────────────
-- R05 – Doanh thu và SLA dịch vụ bổ sung
-- Kỳ: 2026-12-05 đến 2026-12-09 (lọc service_order.ordered_at)
--
-- SO #20 (giặt,   COMPLETED, ordered 2026-12-06 09:00 → done 09:30) = 30 phút
-- SO #21 (minibar, COMPLETED, ordered 2026-12-07 20:00 → done 20:15) = 15 phút
-- SO #22 (ăn sáng, IN_PROGRESS, ordered 2026-12-08 07:30) → chưa tính SLA/doanh thu
--
-- total_orders = 3, completed = 2, in_progress = 1
-- total_service_sales = 2×50.000 + 3×80.000 = 340.000
-- avg_fulfillment_minutes = (30 + 15) / 2 = 22.50 phút
-- service_attach_rate: distinct stay có COMPLETED trong kỳ = 1 (stay #20)
--                      total stays check_in trong kỳ = 1 (stay #20)
--                      → 100.00%
--
-- KỲ VỌNG: total=3, completed=2, sales=340.000, avg_fulfil=22.50, attach=100.00%
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-12-05'::date AS from_date,
           '2026-12-09'::date AS to_date
),
orders_in_period AS (
    SELECT so.*
    FROM service_order so
    CROSS JOIN params p
    WHERE so.ordered_at >= p.from_date
      AND so.ordered_at <  p.to_date + INTERVAL '1 day'
),
sales AS (
    SELECT
        s.category,
        COUNT(soi.service_order_item_id)            AS order_items,
        SUM(soi.quantity)                           AS total_qty,
        SUM(soi.quantity * soi.unit_price)          AS revenue
    FROM orders_in_period op
    JOIN service_order_item soi ON soi.service_order_id = op.service_order_id
    JOIN service s ON s.service_id = soi.service_id
    WHERE op.status = 'COMPLETED'
    GROUP BY s.category
),
sla AS (
    SELECT
        ROUND(AVG(
            EXTRACT(EPOCH FROM (op.completed_at - op.ordered_at)) / 60
        ), 2) AS avg_fulfillment_minutes
    FROM orders_in_period op
    WHERE op.status = 'COMPLETED'
),
attach AS (
    -- Tỷ lệ lượt lưu trú trong kỳ có ít nhất 1 đơn dịch vụ COMPLETED
    SELECT
        COUNT(DISTINCT sr.stay_id) FILTER (
            WHERE op_c.service_order_id IS NOT NULL
        )::numeric
        / NULLIF(COUNT(DISTINCT sr.stay_id), 0) * 100  AS attach_rate_pct
    FROM stay_room sr
    JOIN stay st ON st.stay_id = sr.stay_id
    CROSS JOIN params p
    LEFT JOIN orders_in_period op_c
        ON op_c.stay_room_id = sr.stay_room_id
       AND op_c.status = 'COMPLETED'
    WHERE st.actual_check_in >= p.from_date
      AND st.actual_check_in <  p.to_date + INTERVAL '1 day'
)
SELECT
    (SELECT COUNT(*)                                 FROM orders_in_period)         AS total_orders,
    (SELECT COUNT(*) FILTER (WHERE status='COMPLETED') FROM orders_in_period)       AS completed_orders,
    (SELECT COUNT(*) FILTER (WHERE status='IN_PROGRESS') FROM orders_in_period)     AS in_progress_orders,
    (SELECT COALESCE(SUM(revenue),0) FROM sales)                                    AS total_service_sales,
    (SELECT avg_fulfillment_minutes  FROM sla)                                      AS avg_fulfillment_minutes,
    ROUND((SELECT attach_rate_pct FROM attach), 2)                                  AS service_attach_rate_pct;

-- Phân tích theo danh mục (viết thành câu truy vấn độc lập vì CTE sales chỉ có phạm vi trong câu trên):
SELECT
    s.category,
    COUNT(soi.service_order_item_id)   AS order_items,
    SUM(soi.quantity)                  AS total_qty,
    SUM(soi.quantity * soi.unit_price) AS revenue
FROM service_order so
JOIN service_order_item soi ON soi.service_order_id = so.service_order_id
JOIN service s              ON s.service_id         = soi.service_id
WHERE so.ordered_at >= '2026-12-05'::date
  AND so.ordered_at <  '2026-12-09'::date + INTERVAL '1 day'
  AND so.status = 'COMPLETED'
GROUP BY s.category
ORDER BY revenue DESC;


-- ─────────────────────────────────────────────────
-- R06 – Vận hành buồng phòng, bảo trì và đánh giá
-- Kỳ: 2026-12-05 đến 2026-12-09
--
-- Housekeeping (scheduled_at trong kỳ):
--   task #20: COMPLETED (101, dọn 40 phút)
--   task #21: PENDING   (201)
--   total_active = 2, completed = 1 → completion_rate = 50.00%
--   avg_turnaround = 40.00 phút
--
-- Maintenance (reported_at trong kỳ):
--   ticket #20: CLOSED (101, 2 giờ)
--   MTTR = 2.00 giờ
--
-- Guest reviews (created_at trong kỳ):
--   review #20: stay_id=20, guest=1, rating=4
--   avg_rating = 4.00, five_star_share = 0.00%
--
-- KỲ VỌNG: hk_total=2, hk_done=1, rate=50%, avg_turnaround=40 phút,
--           tickets=1, resolved=1, mttr=2.00 giờ, review=1, avg=4.00
-- ─────────────────────────────────────────────────
WITH params AS (
    SELECT '2026-12-05'::date AS from_date,
           '2026-12-09'::date AS to_date
),
hk AS (
    SELECT
        COUNT(*) FILTER (WHERE status <> 'CANCELLED')           AS total_active_tasks,
        COUNT(*) FILTER (WHERE status = 'COMPLETED')            AS completed_tasks,
        COUNT(*) FILTER (WHERE status IN ('PENDING','IN_PROGRESS')) AS pending_tasks,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'COMPLETED')::numeric * 100
            / NULLIF(COUNT(*) FILTER (WHERE status <> 'CANCELLED'), 0),
            2
        )                                                       AS completion_rate_pct,
        ROUND(AVG(
            EXTRACT(EPOCH FROM (completed_at - scheduled_at)) / 60
        ) FILTER (WHERE status = 'COMPLETED'), 2)               AS avg_turnaround_minutes
    FROM housekeeping_task ht
    CROSS JOIN params p
    WHERE ht.scheduled_at >= p.from_date
      AND ht.scheduled_at <  p.to_date + INTERVAL '1 day'
),
maint AS (
    SELECT
        COUNT(*)                                                AS total_tickets,
        COUNT(*) FILTER (WHERE status IN ('OPEN','IN_PROGRESS')) AS open_or_in_progress,
        COUNT(*) FILTER (WHERE status IN ('RESOLVED','CLOSED')) AS resolved_tickets,
        ROUND(AVG(
            EXTRACT(EPOCH FROM (closed_at - reported_at)) / 3600
        ) FILTER (WHERE closed_at IS NOT NULL), 2)             AS mttr_hours,
        (SELECT COUNT(*) FROM room WHERE maintenance_status = 'OUT_OF_ORDER') AS out_of_order_now
    FROM maintenance_ticket mt
    CROSS JOIN params p
    WHERE mt.reported_at >= p.from_date
      AND mt.reported_at <  p.to_date + INTERVAL '1 day'
),
csat AS (
    SELECT
        COUNT(*)                                                AS review_count,
        ROUND(AVG(rating), 2)                                  AS avg_rating,
        ROUND(
            COUNT(*) FILTER (WHERE rating = 5)::numeric * 100
            / NULLIF(COUNT(*), 0),
            2
        )                                                       AS five_star_share_pct
    FROM guest_review gr
    CROSS JOIN params p
    WHERE gr.created_at >= p.from_date
      AND gr.created_at <  p.to_date + INTERVAL '1 day'
)
SELECT
    hk.total_active_tasks, hk.completed_tasks, hk.pending_tasks,
    hk.completion_rate_pct, hk.avg_turnaround_minutes,
    maint.total_tickets, maint.open_or_in_progress, maint.resolved_tickets,
    maint.mttr_hours, maint.out_of_order_now,
    csat.review_count, csat.avg_rating, csat.five_star_share_pct
FROM hk CROSS JOIN maint CROSS JOIN csat;


-- ============================================================================
-- PHẦN 4: CHỨNG MINH LỖI NHÂN BẢN SUM KHI JOIN SAI
-- ============================================================================

-- ─────────────────────────────────────────────────
-- P4-A: CÁCH SAI – JOIN invoice trực tiếp với folio_item rồi SUM
-- folio #20 có 5 folio_item → invoice bị nhân lên 5 lần trước khi SUM
-- KỲ VỌNG (sai): subtotal_sai >> 6.340.000
-- ─────────────────────────────────────────────────
SELECT
    'SAI (JOIN invoice-folio_item rồi SUM)'                 AS phuong_phap,
    SUM(fi.quantity * fi.unit_price)                        AS tong_charge_sai,
    SUM(i.subtotal)                                         AS subtotal_nhanboi_5_lan
FROM invoice i
JOIN folio_item fi ON fi.folio_id = i.folio_id
WHERE i.invoice_id = 20
  AND fi.entry_type = 'CHARGE';

-- ─────────────────────────────────────────────────
-- P4-B: CÁCH ĐÚNG – Aggregate folio_item TRƯỚC, rồi JOIN với invoice
-- KỲ VỌNG: 6.340.000 (khớp đáp án tính tay)
-- ─────────────────────────────────────────────────
WITH folio_agg AS (
    SELECT folio_id, SUM(quantity * unit_price) AS tong_charge
    FROM folio_item
    WHERE entry_type = 'CHARGE'
    GROUP BY folio_id
)
SELECT
    'ĐÚNG (aggregate folio_item trước, rồi JOIN)'           AS phuong_phap,
    fa.tong_charge,
    i.subtotal                                               AS invoice_subtotal,
    fa.tong_charge - i.subtotal                              AS sai_lech
FROM invoice i
JOIN folio_agg fa ON fa.folio_id = i.folio_id
WHERE i.invoice_id = 20;

-- ─────────────────────────────────────────────────
-- P4-C: Tương tự với payment – JOIN sai sẽ nhân bản nếu invoice có nhiều payment
-- KỲ VỌNG (sai): SUM(payment) nhân theo số folio_item
-- ─────────────────────────────────────────────────
-- Cách sai:
SELECT 'SAI – payment nhân bản do JOIN folio_item' AS phuong_phap,
       SUM(p.amount) AS tong_payment_sai
FROM invoice i
JOIN folio_item fi ON fi.folio_id = i.folio_id
JOIN payment    p  ON p.invoice_id = i.invoice_id
WHERE i.invoice_id = 20;

-- Cách đúng: aggregate payment riêng trước
SELECT 'ĐÚNG – aggregate payment riêng' AS phuong_phap,
       SUM(amount) AS tong_payment_dung
FROM payment WHERE invoice_id = 20;

-- ─────────────────────────────────────────────────
-- P4-D: Quy tắc chung để nhớ
-- ─────────────────────────────────────────────────
-- Khi tính doanh thu từ nhiều bảng có quan hệ 1-nhiều:
--   KHÔNG: SELECT SUM(fi.qty * fi.price) FROM invoice JOIN folio_item JOIN payment
--   ĐÚNG:  Aggregate từng bảng riêng bằng CTE/subquery, rồi JOIN kết quả
--
--   Ví dụ:
--     WITH fi_agg AS (SELECT folio_id, SUM(...) FROM folio_item GROUP BY folio_id),
--          pay_agg AS (SELECT invoice_id, SUM(amount) FROM payment GROUP BY invoice_id)
--     SELECT ... FROM invoice JOIN fi_agg ON ... JOIN pay_agg ON ...;
-- ============================================================================
