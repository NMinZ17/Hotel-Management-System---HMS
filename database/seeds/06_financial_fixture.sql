-- ============================================================================
-- SEED TẦNG 6 (FINANCIAL): database/seeds/06_financial_fixture.sql
-- Fixture tài chính phức tạp – tính tay được – để kiểm tra R01-R06
--
-- Chạy SAU:  01_master_seed.sql  +  02_dev_fixture.sql
-- Môi trường: hms_dev (hoặc hms_test nếu dùng 03_test_fixture thay 02_dev)
-- IDs bắt đầu từ 20 để không xung đột với 02_dev (IDs 1-3) và 05_edge_case (10-18)
--
-- KỊCH BẢN:  Đơn #20 – Nhiều phòng + nhiều dịch vụ + mã WELCOME10 + 2 lần thanh toán
--   Khách chính : Pham Thu Ha      (guest_id=1,  có tài khoản)
--   Khách đi cùng: Nguyen Minh Anh (guest_id=2,  vãng lai)
--   Phòng A : 101 Standard  – 3 đêm 05-08/12/2026 – 800.000 VND/đêm
--   Phòng B : 201 Deluxe    – 3 đêm 05-08/12/2026 – 1.200.000 VND/đêm
--   Mã giảm : WELCOME10 (discount_id=1) – 10% trên tổng CHARGE
--   Dịch vụ : Giặt đồ ×2 (hoàn thành, ghi folio)
--             Minibar  ×3 (hoàn thành, ghi folio)
--             Ăn sáng  ×4 (đang xử lý, chưa ghi folio – folio đã CLOSED)
--
-- ─────────────────────────────────────────────────────────────────────────────
-- BẢNG ĐÁP ÁN TÍNH TAY (kỳ vọng để đối chiếu):
--
--  folio_item_id | entry_type | qty | unit_price      | dòng phí
--  ─────────────────────────────────────────────────────────────
--       20       | CHARGE     | 3   |  800.000,00     | 2.400.000,00  tiền phòng 101
--       21       | CHARGE     | 3   | 1.200.000,00    | 3.600.000,00  tiền phòng 201
--       22       | CHARGE     | 2   |   50.000,00     |   100.000,00  giặt đồ
--       23       | CHARGE     | 3   |   80.000,00     |   240.000,00  minibar
--       24       | DISCOUNT   | 1   |  -634.000,00    |  -634.000,00  WELCOME10
--  ─────────────────────────────────────────────────────────────
--  Tổng CHARGE trước giảm  :  2.400.000 + 3.600.000 + 100.000 + 240.000 = 6.340.000
--  Giảm giá WELCOME10 10%  :  10% × 6.340.000  = 634.000
--  invoice.subtotal         :  6.340.000
--  invoice.discount_total   :    634.000
--  Doanh thu thuần (net)    :  6.340.000 - 634.000           = 5.706.000
--  Thuế 8% (VAT trên net)   :  5.706.000 × 8%               = 456.480
--  invoice.tax_amount       :    456.480
--  Tổng phải thu (gross)    :  5.706.000 + 456.480           = 6.162.480
--  ─────────────────────────────────────────────────────────────
--  payment_id=20 : 3.000.000 CASH   (trả trước khi checkout)
--  payment_id=21 : 3.162.480 TRANSFER TRF-20261208-0001 (phần còn lại)
--  Tổng thu      : 3.000.000 + 3.162.480 = 6.162.480  ✓ = gross
-- ─────────────────────────────────────────────────────────────────────────────

BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 1: ĐẶT PHÒNG (reservation → reservation_guest → reservation_room → discount)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note)
VALUES (20, 1, 'CHECKED_OUT', '2026-11-20 10:00:00+07', NULL,
        'Thu Ha + Minh Anh dat 2 phong 05-08/12; WELCOME10; 2 payment');

-- Hai khách trong đơn
INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(20, 1, TRUE),   -- Pham Thu Ha – người đặt chính
(20, 2, FALSE);  -- Nguyen Minh Anh – đi cùng

-- Hai phòng trong đơn
-- [2026-12-05, 2026-12-08) = 3 đêm, không xung đột với phòng 101/201 trong kỳ Dec 05-08
INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id,
                              check_in_date, check_out_date,
                              adults, children, nightly_price, is_cancelled)
VALUES
(20, 20, 101, '2026-12-05', '2026-12-08', 2, 0,  800000.00, FALSE),  -- Standard 101
(21, 20, 201, '2026-12-05', '2026-12-08', 2, 1, 1200000.00, FALSE);  -- Deluxe  201

-- Mã giảm giá: 10% × 6.340.000 = 634.000
INSERT INTO reservation_discount (reservation_id, discount_id, discount_amount)
VALUES (20, 1, 634000.00);

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 2: LƯU TRÚ (stay → stay_room)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO stay (stay_id, reservation_id, checked_in_by, checked_out_by,
                  actual_check_in, actual_check_out, status)
VALUES (20, 20, 2, 2,
        '2026-12-05 14:00:00+07',
        '2026-12-08 11:00:00+07',
        'CHECKED_OUT');

-- Hai phòng vật lý gắn với lượt ở
INSERT INTO stay_room (stay_room_id, stay_id, reservation_room_id, room_id,
                       assigned_from, assigned_to)
VALUES
(20, 20, 20, 101, '2026-12-05 14:00:00+07', '2026-12-08 11:00:00+07'),
(21, 20, 21, 201, '2026-12-05 14:00:00+07', '2026-12-08 11:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 3: FOLIO VÀ DÒNG PHÍ
-- folio_item unique index: (folio_id, source_key) WHERE source_key IS NOT NULL
-- source_key format: ROOM:<reservation_room_id>:<check_in_date>  |  SOI:<soi_id>  |  DISC:<res_id>:<discount_id>
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO folio (folio_id, stay_id, status, opened_at, closed_at)
VALUES (20, 20, 'CLOSED', '2026-12-05 14:00:00+07', '2026-12-08 11:00:00+07');

INSERT INTO folio_item (folio_item_id, folio_id, entry_type, description,
                        quantity, unit_price, source_key, occurred_at)
VALUES
-- Tiền phòng: snapshot nightly_price × số đêm (qty)
(20, 20, 'CHARGE', 'Tien phong Standard 101 (3 dem: 05-07/12/2026)',
         3.00, 800000.00, 'ROOM:20:2026-12-05', '2026-12-05 14:00:00+07'),

(21, 20, 'CHARGE', 'Tien phong Deluxe 201 (3 dem: 05-07/12/2026)',
         3.00, 1200000.00, 'ROOM:21:2026-12-05', '2026-12-05 14:00:00+07'),

-- Dịch vụ đã hoàn thành (ghi folio sau khi service_order COMPLETED)
(22, 20, 'CHARGE', 'Giat do (2 mon) – SOI:20',
         2.00, 50000.00, 'SOI:20', '2026-12-06 09:30:00+07'),

(23, 20, 'CHARGE', 'Minibar (3 chai) – SOI:21',
         3.00, 80000.00, 'SOI:21', '2026-12-07 20:15:00+07'),

-- Giảm giá: unit_price <= 0 bắt buộc (ck_folio_item_unit_price trong V002)
-- 10% × (3×800k + 3×1200k + 2×50k + 3×80k) = 10% × 6.340.000 = 634.000
(24, 20, 'DISCOUNT', 'Ma giam WELCOME10 (-10% tren tong CHARGE)',
         1.00, -634000.00, 'DISC:20:1', '2026-12-08 11:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 4: DỊCH VỤ (service_order → service_order_item)
-- service_order #20: giặt đồ – COMPLETED → ghi folio_item_id=22
-- service_order #21: minibar  – COMPLETED → ghi folio_item_id=23
-- service_order #22: ăn sáng  – IN_PROGRESS → folio_item_id=NULL (folio đã CLOSED)
--                     Mục đích: kiểm tra không được tính vào R02/R03
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO service_order (service_order_id, stay_room_id, assigned_to,
                           status, ordered_at, completed_at)
VALUES
(20, 20, 3, 'COMPLETED',   '2026-12-06 09:00:00+07', '2026-12-06 09:30:00+07'),  -- giặt   (30 phút)
(21, 20, 3, 'COMPLETED',   '2026-12-07 20:00:00+07', '2026-12-07 20:15:00+07'),  -- minibar (15 phút)
(22, 21, 3, 'IN_PROGRESS', '2026-12-08 07:30:00+07', NULL);                       -- ăn sáng (chưa xong)

-- uq_service_order_item_folio_item: folio_item_id phải UNIQUE khi IS NOT NULL
INSERT INTO service_order_item (service_order_item_id, service_order_id, service_id,
                                quantity, unit_price, folio_item_id)
VALUES
(20, 20, 1, 2.00,  50000.00, 22),   -- giặt → đã ghi folio_item #22
(21, 21, 3, 3.00,  80000.00, 23),   -- minibar → đã ghi folio_item #23
(22, 22, 2, 4.00, 120000.00, NULL); -- ăn sáng → chưa ghi folio (480.000 chưa tính vào doanh thu)

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 5: HÓA ĐƠN VÀ THANH TOÁN (invoice → payment)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO invoice (invoice_id, folio_id, invoice_number,
                     subtotal, discount_total, tax_amount,
                     issued_at, status)
VALUES (20, 20, 'INV-202612-0020',
        6340000.00,   -- subtotal  = tổng CHARGE = 2.400k+3.600k+100k+240k
        634000.00,    -- discount  = 10% × subtotal
        456480.00,    -- tax       = 8% × (subtotal - discount) = 8% × 5.706.000
        '2026-12-08 11:05:00+07', 'PAID');

-- Hai lần thanh toán; tổng = 3.000.000 + 3.162.480 = 6.162.480 = gross ✓
-- payment #20: CASH, không có transaction_ref
-- payment #21: TRANSFER, có transaction_ref duy nhất (uq_payment_transaction_ref)
INSERT INTO payment (payment_id, invoice_id, recorded_by,
                     amount, method, transaction_ref, paid_at)
VALUES
(20, 20, 2, 3000000.00, 'CASH',     NULL,                 '2026-12-08 10:00:00+07'),
(21, 20, 2, 3162480.00, 'TRANSFER', 'TRF-20261208-0001',  '2026-12-08 11:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 6: VẬN HÀNH (housekeeping_task + maintenance_ticket)
-- ─────────────────────────────────────────────────────────────────────────────

-- Dọn phòng sau checkout:
-- Task #20 phòng 101 đã hoàn thành (40 phút)
-- Task #21 phòng 201 chưa làm (PENDING) → để kiểm tra completion_rate R06 = 50%
INSERT INTO housekeeping_task (task_id, room_id, assigned_to,
                               scheduled_at, completed_at, status)
VALUES
(20, 101, 3, '2026-12-08 12:00:00+07', '2026-12-08 12:40:00+07', 'COMPLETED'),
(21, 201, 3, '2026-12-08 12:00:00+07', NULL,                      'PENDING');

-- Phiếu bảo trì phòng 101: báo cáo trong kỳ Dec, đóng sau 2 giờ
-- (MTTR R06 = 2.00 giờ)
INSERT INTO maintenance_ticket (ticket_id, room_id, reported_by, assigned_to,
                                description, status, reported_at, closed_at)
VALUES (20, 101, 2, 4,
        'Voi nuoc phong tam bi rot – thay gioang',
        'CLOSED',
        '2026-12-06 08:00:00+07',
        '2026-12-06 10:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 7: ĐÁNH GIÁ
-- ─────────────────────────────────────────────────────────────────────────────

-- uq_guest_review_stay_guest: (stay_id, guest_id) phải UNIQUE
INSERT INTO guest_review (review_id, stay_id, guest_id, rating, comment, created_at)
VALUES (20, 20, 1, 4, 'Phong sach, dich vu nhanh. Giat do hoi cham mot chut.',
        '2026-12-08 15:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 8: AUDIT LOG
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO audit_event (event_id, actor_user_id, reservation_id, service_order_id,
                         action, details, occurred_at)
VALUES
(20, 2, 20, NULL, 'STAY_CHECKED_IN',
 '{"stay_id": 20, "rooms": ["101", "201"], "reservation_id": 20}'::jsonb,
 '2026-12-05 14:00:00+07'),
(21, 2, 20, NULL, 'STAY_CHECKED_OUT',
 '{"stay_id": 20, "invoice_number": "INV-202612-0020", "gross": 6162480}'::jsonb,
 '2026-12-08 11:00:00+07');

-- ─────────────────────────────────────────────────────────────────────────────
-- BƯỚC 9: ĐỒNG BỘ SEQUENCE
-- ─────────────────────────────────────────────────────────────────────────────

SELECT setval(pg_get_serial_sequence('reservation',          'reservation_id'),          COALESCE(MAX(reservation_id),          1)) FROM reservation;
SELECT setval(pg_get_serial_sequence('reservation_room',     'reservation_room_id'),     COALESCE(MAX(reservation_room_id),     1)) FROM reservation_room;
SELECT setval(pg_get_serial_sequence('stay',                 'stay_id'),                 COALESCE(MAX(stay_id),                 1)) FROM stay;
SELECT setval(pg_get_serial_sequence('stay_room',            'stay_room_id'),            COALESCE(MAX(stay_room_id),            1)) FROM stay_room;
SELECT setval(pg_get_serial_sequence('folio',                'folio_id'),                COALESCE(MAX(folio_id),                1)) FROM folio;
SELECT setval(pg_get_serial_sequence('folio_item',           'folio_item_id'),           COALESCE(MAX(folio_item_id),           1)) FROM folio_item;
SELECT setval(pg_get_serial_sequence('invoice',              'invoice_id'),              COALESCE(MAX(invoice_id),              1)) FROM invoice;
SELECT setval(pg_get_serial_sequence('payment',              'payment_id'),              COALESCE(MAX(payment_id),              1)) FROM payment;
SELECT setval(pg_get_serial_sequence('service_order',        'service_order_id'),        COALESCE(MAX(service_order_id),        1)) FROM service_order;
SELECT setval(pg_get_serial_sequence('service_order_item',   'service_order_item_id'),   COALESCE(MAX(service_order_item_id),   1)) FROM service_order_item;
SELECT setval(pg_get_serial_sequence('housekeeping_task',    'task_id'),                 COALESCE(MAX(task_id),                 1)) FROM housekeeping_task;
SELECT setval(pg_get_serial_sequence('maintenance_ticket',   'ticket_id'),               COALESCE(MAX(ticket_id),              1)) FROM maintenance_ticket;
SELECT setval(pg_get_serial_sequence('guest_review',         'review_id'),               COALESCE(MAX(review_id),              1)) FROM guest_review;
SELECT setval(pg_get_serial_sequence('audit_event',          'event_id'),                COALESCE(MAX(event_id),                1)) FROM audit_event;

COMMIT;
