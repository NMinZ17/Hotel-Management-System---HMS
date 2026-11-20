-- ============================================================================
-- SEED TẦNG 4 (BENCHMARK): database/seeds/04_bench_seed.sql
-- Chạy trên hms_bench SAU KHI đã chạy V001__init_hms_schema.sql và 01_master_seed.sql
-- Quy mô sinh: 200 phòng, 20.000 khách, 100.000 đặt phòng, 70.400 lưu trú
-- ============================================================================

BEGIN;

-- 1. Sinh 200 phòng (10 tầng x 20 phòng/tầng)
INSERT INTO room (room_id, room_type_id, room_number, floor, housekeeping_status, maintenance_status, is_active)
SELECT
    g AS room_id,
    ((g - 1) % 3) + 1 AS room_type_id,
    LPAD((((g - 1) / 20) + 1)::text, 2, '0') || LPAD((((g - 1) % 20) + 1)::text, 2, '0') AS room_number,
    (((g - 1) / 20) + 1)::smallint AS floor,
    'CLEAN',
    'OK',
    TRUE
FROM generate_series(1, 200) AS g;

INSERT INTO room_amenity (room_id, amenity_id)
SELECT r.room_id, a.amenity_id
FROM room r
CROSS JOIN amenity a
WHERE a.amenity_id <= 3 OR r.room_type_id >= 2;

-- 2. Sinh 20 nhân viên & 20.000 khách hàng
INSERT INTO app_user (user_id, email, password_hash, is_active)
SELECT
    g,
    'staff' || g || '@hms-bench.example',
    'bench_hash',
    TRUE
FROM generate_series(1, 20) AS g;

INSERT INTO user_role (user_id, role_id)
SELECT g, ((g - 1) % 5) + 1
FROM generate_series(1, 20) AS g;

INSERT INTO employee (employee_id, user_id, full_name, job_title, is_active)
SELECT
    g,
    g,
    'Nhan vien Bench ' || g,
    CASE ((g - 1) % 4)
        WHEN 0 THEN 'Manager'
        WHEN 1 THEN 'Receptionist'
        WHEN 2 THEN 'Housekeeping Staff'
        ELSE 'Maintenance Tech'
    END,
    TRUE
FROM generate_series(1, 20) AS g;

INSERT INTO guest (guest_id, user_id, full_name, phone, email)
SELECT
    g,
    NULL,
    'Khach Bench ' || g,
    '09' || LPAD(g::text, 8, '0'),
    'guest' || g || '@bench.example'
FROM generate_series(1, 20000) AS g;

-- 3. Sinh 100.000 đơn đặt phòng không chồng lấn (200 phòng x 500 khung 3 ngày từ 2024-01-01)
-- Slot s in 0..350   (70.200 đơn): CHECKED_OUT (2024-01-01 -> 2026-11-19)
-- Slot s = 351       (200 đơn)   : CHECKED_IN  (2026-11-19 -> 2026-11-22)
-- Slot s in 352..499 (29.600 đơn): CONFIRMED   (2026-11-22 -> 2028-02-09)
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note)
SELECT
    (s * 200) + r AS reservation_id,
    (((s * 200) + r - 1) % 20000) + 1 AS booked_by_guest_id,
    CASE
        WHEN s <= 350 THEN 'CHECKED_OUT'
        WHEN s = 351  THEN 'CHECKED_IN'
        ELSE 'CONFIRMED'
    END AS status,
    ('2024-01-01'::date + (s * 3) - 7)::timestamptz AS created_at,
    NULL,
    NULL
FROM generate_series(0, 499) AS s
CROSS JOIN generate_series(1, 200) AS r;

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled)
SELECT
    (s * 200) + r AS reservation_room_id,
    (s * 200) + r AS reservation_id,
    r AS room_id,
    ('2024-01-01'::date + (s * 3)) AS check_in_date,
    ('2024-01-01'::date + ((s + 1) * 3)) AS check_out_date,
    2,
    0,
    CASE ((r - 1) % 3)
        WHEN 0 THEN 800000.00
        WHEN 1 THEN 1200000.00
        ELSE 2500000.00
    END AS nightly_price,
    FALSE
FROM generate_series(0, 499) AS s
CROSS JOIN generate_series(1, 200) AS r;

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary)
SELECT reservation_id, booked_by_guest_id, TRUE
FROM reservation;

-- 4. Sinh 70.400 lượt lưu trú (stay + stay_room + folio) cho slot 0..351
INSERT INTO stay (stay_id, reservation_id, checked_in_by, checked_out_by, actual_check_in, actual_check_out, status)
SELECT
    rr.reservation_room_id AS stay_id,
    rr.reservation_id,
    ((rr.room_id - 1) % 20) + 1 AS checked_in_by,
    CASE WHEN rr.reservation_room_id <= 70200 THEN ((rr.room_id - 1) % 20) + 1 ELSE NULL END AS checked_out_by,
    rr.check_in_date::timestamptz + INTERVAL '14 hours' AS actual_check_in,
    CASE WHEN rr.reservation_room_id <= 70200 THEN rr.check_out_date::timestamptz + INTERVAL '11 hours' ELSE NULL END AS actual_check_out,
    CASE WHEN rr.reservation_room_id <= 70200 THEN 'CHECKED_OUT' ELSE 'IN_HOUSE' END AS status
FROM reservation_room rr
WHERE rr.reservation_room_id <= 70400;

INSERT INTO stay_room (stay_room_id, stay_id, reservation_room_id, room_id, assigned_from, assigned_to)
SELECT
    s.stay_id,
    s.stay_id,
    s.stay_id,
    rr.room_id,
    s.actual_check_in,
    s.actual_check_out
FROM stay s
JOIN reservation_room rr ON rr.reservation_room_id = s.stay_id;

INSERT INTO folio (folio_id, stay_id, status, opened_at, closed_at)
SELECT
    s.stay_id,
    s.stay_id,
    CASE WHEN s.status = 'CHECKED_OUT' THEN 'CLOSED' ELSE 'OPEN' END,
    s.actual_check_in,
    s.actual_check_out
FROM stay s;

-- 5. Sinh 140.600 bút toán folio_item (tiền phòng + thuế) và 70.200 hóa đơn/thanh toán
INSERT INTO folio_item (folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at)
SELECT
    f.folio_id,
    'CHARGE',
    'Tien phong 3 dem',
    3.00,
    rr.nightly_price,
    'ROOM:' || rr.reservation_room_id,
    f.opened_at
FROM folio f
JOIN reservation_room rr ON rr.reservation_room_id = f.stay_id;

INSERT INTO folio_item (folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at)
SELECT
    f.folio_id,
    'TAX',
    'Thue VAT 8%',
    1.00,
    ROUND(rr.nightly_price * 3 * 0.08, 2),
    'TAX:' || rr.reservation_room_id,
    f.closed_at
FROM folio f
JOIN reservation_room rr ON rr.reservation_room_id = f.stay_id
WHERE f.status = 'CLOSED';

INSERT INTO invoice (invoice_id, folio_id, invoice_number, subtotal, discount_total, tax_amount, issued_at, status)
SELECT
    f.folio_id,
    f.folio_id,
    'INV-BENCH-' || LPAD(f.folio_id::text, 7, '0'),
    rr.nightly_price * 3,
    0.00,
    ROUND(rr.nightly_price * 3 * 0.08, 2),
    f.closed_at,
    'PAID'
FROM folio f
JOIN reservation_room rr ON rr.reservation_room_id = f.stay_id
WHERE f.status = 'CLOSED';

INSERT INTO payment (payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at)
SELECT
    i.invoice_id,
    i.invoice_id,
    ((i.invoice_id - 1) % 20) + 1,
    i.subtotal + i.tax_amount,
    CASE (i.invoice_id % 4)
        WHEN 0 THEN 'CASH'
        WHEN 1 THEN 'CARD'
        WHEN 2 THEN 'TRANSFER'
        ELSE 'EWALLET'
    END,
    'BENCH-TXN-' || LPAD(i.invoice_id::text, 8, '0'),
    i.issued_at
FROM invoice i;

-- 6. Đồng bộ sequence
SELECT setval(pg_get_serial_sequence('room', 'room_id'), COALESCE(MAX(room_id), 1)) FROM room;
SELECT setval(pg_get_serial_sequence('app_user', 'user_id'), COALESCE(MAX(user_id), 1)) FROM app_user;
SELECT setval(pg_get_serial_sequence('guest', 'guest_id'), COALESCE(MAX(guest_id), 1)) FROM guest;
SELECT setval(pg_get_serial_sequence('employee', 'employee_id'), COALESCE(MAX(employee_id), 1)) FROM employee;
SELECT setval(pg_get_serial_sequence('reservation', 'reservation_id'), COALESCE(MAX(reservation_id), 1)) FROM reservation;
SELECT setval(pg_get_serial_sequence('reservation_room', 'reservation_room_id'), COALESCE(MAX(reservation_room_id), 1)) FROM reservation_room;
SELECT setval(pg_get_serial_sequence('stay', 'stay_id'), COALESCE(MAX(stay_id), 1)) FROM stay;
SELECT setval(pg_get_serial_sequence('stay_room', 'stay_room_id'), COALESCE(MAX(stay_room_id), 1)) FROM stay_room;
SELECT setval(pg_get_serial_sequence('folio', 'folio_id'), COALESCE(MAX(folio_id), 1)) FROM folio;
SELECT setval(pg_get_serial_sequence('folio_item', 'folio_item_id'), COALESCE(MAX(folio_item_id), 1)) FROM folio_item;
SELECT setval(pg_get_serial_sequence('invoice', 'invoice_id'), COALESCE(MAX(invoice_id), 1)) FROM invoice;
SELECT setval(pg_get_serial_sequence('payment', 'payment_id'), COALESCE(MAX(payment_id), 1)) FROM payment;

COMMIT;

-- Cập nhật thống kê planner ngoài transaction
VACUUM ANALYZE;