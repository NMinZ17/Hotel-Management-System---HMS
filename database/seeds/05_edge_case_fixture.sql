-- ============================================================================
-- SEED TÌNH HUỐNG BIÊN: database/seeds/05_edge_case_fixture.sql
-- Chạy sau 01_master_seed.sql và 03_test_fixture.sql
-- Bao phủ: Ngày liền kề, Phòng cuối cùng, Đơn nhiều phòng, Giảm giá FIXED/PERCENT
-- ============================================================================

BEGIN;

-- Bổ sung thêm khách hàng & chương trình giảm giá (FIXED + hết hạn)
INSERT INTO guest (guest_id, user_id, full_name, phone, email) VALUES
(4, NULL, 'Le Hoang Nam',   '0900000004', 'nam@example.com'),
(5, NULL, 'Vu Mai Phuong',  '0900000005', 'phuong@example.com'),
(6, NULL, 'Doan Quoc Bao',  '0900000006', 'bao@example.com')
ON CONFLICT (guest_id) DO NOTHING;

INSERT INTO discount (discount_id, code, discount_type, value, valid_from, valid_to, is_active) VALUES
(2, 'FIXED500K',   'FIXED',   500000.00, '2026-01-01', '2026-12-31', TRUE),
(3, 'EXPIRED2025', 'PERCENT',     15.00, '2025-01-01', '2025-12-31', FALSE)
ON CONFLICT (discount_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- KỊCH BẢN A: NGÀY LIỀN KỀ TRÊN PHÒNG 102 (Kẹp sát Đơn #1: 10/12 -> 12/12/2026)
-- ----------------------------------------------------------------------------
-- Đơn #10: [2026-12-08, 2026-12-10) -> check_out trùng ngày check_in của Đơn #1
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(10, 4, 'CONFIRMED', '2026-11-18 09:00:00+07', NULL, 'Lien ke truoc don #1 tren phong 102');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(10, 4, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(10, 10, 102, '2026-12-08', '2026-12-10', 2, 0, 800000.00, FALSE);

-- Đơn #11: [2026-12-12, 2026-12-14) -> check_in trùng ngày check_out của Đơn #1
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(11, 5, 'CONFIRMED', '2026-11-18 09:30:00+07', NULL, 'Lien ke sau don #1 tren phong 102');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(11, 5, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(11, 11, 102, '2026-12-12', '2026-12-14', 1, 0, 800000.00, FALSE);

-- ----------------------------------------------------------------------------
-- KỊCH BẢN B: PHÒNG CUỐI CÙNG (Giai đoạn 2026-12-10 -> 2026-12-12)
-- Hiện phòng 102 đã bị giữ bởi Đơn #1. Đặt tiếp 101 & 201 -> chỉ còn 202 là phòng cuối.
-- Sau đó Đơn #13 đặt nốt phòng 202 (Sold Out 100% toàn khách sạn).
-- ----------------------------------------------------------------------------
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(12, 4, 'CONFIRMED', '2026-11-19 10:00:00+07', NULL, 'Giu 101 va 201 -> de lai 202 la phong cuoi cung');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(12, 4, TRUE),
(12, 5, FALSE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(12, 12, 101, '2026-12-10', '2026-12-12', 2, 0,  800000.00, FALSE),
(13, 12, 201, '2026-12-10', '2026-12-12', 2, 1, 1200000.00, FALSE);

-- Đơn #13: Đặt phòng cuối cùng (Suite 202) -> Sold out 4/4 phòng
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(13, 6, 'CONFIRMED', '2026-11-19 11:00:00+07', NULL, 'Chot phong cuoi cung 202 - Sold out');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(13, 6, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(14, 13, 202, '2026-12-10', '2026-12-12', 2, 2, 2500000.00, FALSE);

-- ----------------------------------------------------------------------------
-- KỊCH BẢN C: ĐƠN NHIỀU PHÒNG & HỦY LẺ 1 PHÒNG (2026-12-20 -> 2026-12-23)
-- 1 reservation gồm 3 phòng (101, 102, 201), 3 khách, hủy riêng phòng 102
-- ----------------------------------------------------------------------------
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(14, 1, 'CONFIRMED', '2026-11-20 08:00:00+07', NULL, 'Doan gia dinh dat 3 phong (101, 102, 201), huy le 102');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(14, 1, TRUE),
(14, 2, FALSE),
(14, 3, FALSE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(15, 14, 101, '2026-12-20', '2026-12-23', 2, 0,  800000.00, FALSE),
(16, 14, 102, '2026-12-20', '2026-12-23', 2, 0,  800000.00, TRUE),  -- Hủy lẻ phòng này
(17, 14, 201, '2026-12-20', '2026-12-23', 2, 1, 1200000.00, FALSE);

-- ----------------------------------------------------------------------------
-- KỊCH BẢN D: GIẢM GIÁ CỐ ĐỊNH (FIXED500K) TRÊN ĐƠN ĐẶT PHÒNG SUITE 202
-- ----------------------------------------------------------------------------
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(15, 6, 'CONFIRMED', '2026-11-20 10:00:00+07', NULL, 'Dat Suite 202 ap dung ma giam FIXED500K');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(15, 6, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(18, 15, 202, '2026-12-20', '2026-12-22', 2, 0, 2500000.00, FALSE);

INSERT INTO reservation_discount (reservation_id, discount_id, discount_amount) VALUES
(15, 2, 500000.00);

-- Đồng bộ lại toàn bộ sequence
SELECT setval(pg_get_serial_sequence('guest', 'guest_id'), COALESCE(MAX(guest_id), 1)) FROM guest;
SELECT setval(pg_get_serial_sequence('discount', 'discount_id'), COALESCE(MAX(discount_id), 1)) FROM discount;
SELECT setval(pg_get_serial_sequence('reservation', 'reservation_id'), COALESCE(MAX(reservation_id), 1)) FROM reservation;
SELECT setval(pg_get_serial_sequence('reservation_room', 'reservation_room_id'), COALESCE(MAX(reservation_room_id), 1)) FROM reservation_room;

COMMIT;