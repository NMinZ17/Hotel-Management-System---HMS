-- ============================================================================
-- TEST SUITE: database/tests/verify_rules.sql
-- Kiểm thử 12 quy tắc toàn vẹn bằng Transaction (tự động ROLLBACK sau khi chạy)
-- Chạy trên hms_test sau khi đã chạy V001__init_hms_schema.sql,
-- 01_master_seed.sql và 03_test_fixture.sql
-- ============================================================================

BEGIN;

-- R01: Chặn đặt trùng phòng 102 trong khoảng [2026-12-11, 2026-12-13)
DO $$
DECLARE
    v_res_id BIGINT;
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (2, 'CONFIRMED')
    RETURNING reservation_id INTO v_res_id;

    INSERT INTO reservation_room (reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
    VALUES (v_res_id, 102, '2026-12-11', '2026-12-13', 2, 800000.00);

    RAISE EXCEPTION 'FAIL R01: He thong cho phep dat trung phong 102!';
EXCEPTION
    WHEN exclusion_violation THEN
        RAISE NOTICE '[PASS] R01: Da chan dat trung phong 102 (23P01 exclusion_violation).';
END $$;

-- R02: Cho phép đặt liền kề ngày trả phòng [2026-12-12, 2026-12-14) trên phòng 102
SAVEPOINT sp_r02;
DO $$
DECLARE
    v_res_id BIGINT;
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (2, 'CONFIRMED')
    RETURNING reservation_id INTO v_res_id;

    INSERT INTO reservation_room (reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
    VALUES (v_res_id, 102, '2026-12-12', '2026-12-14', 2, 800000.00);

    RAISE NOTICE '[PASS] R02: Cho phep check-in dung ngay khach truoc check-out [12/12, 14/12).';
END $$;
ROLLBACK TO SAVEPOINT sp_r02;

-- R03: Hủy phòng (is_cancelled = TRUE) giải phóng lịch cho đơn đặt mới
SAVEPOINT sp_r03;
DO $$
DECLARE
    v_res_id BIGINT;
BEGIN
    UPDATE reservation_room SET is_cancelled = TRUE WHERE reservation_room_id = 1;

    INSERT INTO reservation (booked_by_guest_id, status) VALUES (3, 'CONFIRMED')
    RETURNING reservation_id INTO v_res_id;

    INSERT INTO reservation_room (reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
    VALUES (v_res_id, 102, '2026-12-10', '2026-12-12', 1, 800000.00);

    RAISE NOTICE '[PASS] R03: Huy phong giai phong lich thanh cong.';
END $$;
ROLLBACK TO SAVEPOINT sp_r03;

-- R04: Chặn xếp trùng phòng vật lý trên stay_room
DO $$
DECLARE
    v_res1 BIGINT;
    v_res2 BIGINT;
    v_stay1 BIGINT;
    v_stay2 BIGINT;
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (2, 'CHECKED_IN') RETURNING reservation_id INTO v_res1;
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (3, 'CHECKED_IN') RETURNING reservation_id INTO v_res2;

    INSERT INTO stay (reservation_id, checked_in_by, actual_check_in, status)
    VALUES (v_res1, 2, '2026-12-20 14:00:00+07', 'IN_HOUSE') RETURNING stay_id INTO v_stay1;

    INSERT INTO stay (reservation_id, checked_in_by, actual_check_in, status)
    VALUES (v_res2, 2, '2026-12-20 15:00:00+07', 'IN_HOUSE') RETURNING stay_id INTO v_stay2;

    INSERT INTO stay_room (stay_id, room_id, assigned_from, assigned_to)
    VALUES (v_stay1, 101, '2026-12-20 14:00:00+07', NULL);

    INSERT INTO stay_room (stay_id, room_id, assigned_from, assigned_to)
    VALUES (v_stay2, 101, '2026-12-20 15:00:00+07', NULL);

    RAISE EXCEPTION 'FAIL R04: He thong cho phep xep trung phong vat ly!';
EXCEPTION
    WHEN exclusion_violation THEN
        RAISE NOTICE '[PASS] R04: Da chan xep trung phong vat ly tren stay_room (23P01).';
END $$;

-- R05: Chặn đặt phòng có check_out_date <= check_in_date
DO $$
DECLARE
    v_res_id BIGINT;
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (2, 'PENDING') RETURNING reservation_id INTO v_res_id;
    INSERT INTO reservation_room (reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
    VALUES (v_res_id, 101, '2026-12-25', '2026-12-25', 1, 800000.00);

    RAISE EXCEPTION 'FAIL R05: Cho phep dat phong 0 dem!';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE '[PASS] R05: Da chan check_out_date <= check_in_date (23514).';
END $$;

-- R06: Chặn trạng thái CANCELLED nhưng thiếu cancelled_at
DO $$
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status, cancelled_at)
    VALUES (2, 'CANCELLED', NULL);

    RAISE EXCEPTION 'FAIL R06: Cho phep CANCELLED ma khong co cancelled_at!';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE '[PASS] R06: Da chan CANCELLED thieu cancelled_at (23514).';
END $$;

-- R07: Chặn mã giảm giá PERCENT > 100%
DO $$
BEGIN
    INSERT INTO discount (code, discount_type, value, valid_from, valid_to)
    VALUES ('BAD150', 'PERCENT', 150.00, '2026-01-01', '2026-12-31');

    RAISE EXCEPTION 'FAIL R07: Cho phep giam gia > 100%%!';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE '[PASS] R07: Da chan ma giam gia vuot 100%% (23514).';
END $$;

-- R08: Chặn rating ngoài khoảng 1..5
DO $$
BEGIN
    INSERT INTO guest_review (stay_id, guest_id, rating, comment)
    VALUES (1, 3, 6, 'Diem khong hop le');

    RAISE EXCEPTION 'FAIL R08: Cho phep rating = 6!';
EXCEPTION
    WHEN check_violation THEN
        RAISE NOTICE '[PASS] R08: Da chan rating ngoai khoang 1..5 (23514).';
END $$;

-- R09: Chặn trùng số phòng (room_number)
DO $$
BEGIN
    INSERT INTO room (room_type_id, room_number, floor) VALUES (1, '101', 1);
    RAISE EXCEPTION 'FAIL R09: Cho phep trung so phong 101!';
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE '[PASS] R09: Da chan trung so phong (23505 unique_violation).';
END $$;

-- R10: Chặn ghi trùng bút toán folio (source_key)
DO $$
BEGIN
    INSERT INTO folio_item (folio_id, entry_type, description, quantity, unit_price, source_key)
    VALUES (1, 'CHARGE', 'Ghi trung', 1, 100000.00, 'ROOM:2:2026-11-01');

    RAISE EXCEPTION 'FAIL R10: Cho phep ghi trung source_key trong cung folio!';
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE '[PASS] R10: Da chan ghi trung but toan folio theo source_key (23505).';
END $$;

-- R11: Chặn khóa ngoại khách hàng không tồn tại
DO $$
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (999999, 'PENDING');
    RAISE EXCEPTION 'FAIL R11: Cho phep dat phong voi guest_id khong ton tai!';
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE NOTICE '[PASS] R11: Da chan khoa ngoai guest_id khong ton tai (23503).';
END $$;

-- R12: Kiểm thử trọn luồng nghiệp vụ Check-in -> Dịch vụ -> Folio -> Hóa đơn -> Thanh toán
SAVEPOINT sp_r12;
DO $$
DECLARE
    v_res_id BIGINT;
    v_rr_id BIGINT;
    v_stay_id BIGINT;
    v_sr_id BIGINT;
    v_folio_id BIGINT;
    v_fi_svc_id BIGINT;
    v_so_id BIGINT;
    v_inv_id BIGINT;
BEGIN
    INSERT INTO reservation (booked_by_guest_id, status) VALUES (3, 'CONFIRMED') RETURNING reservation_id INTO v_res_id;
    INSERT INTO reservation_room (reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
    VALUES (v_res_id, 202, '2026-12-20', '2026-12-21', 2, 2500000.00) RETURNING reservation_room_id INTO v_rr_id;

    UPDATE reservation SET status = 'CHECKED_IN' WHERE reservation_id = v_res_id;
    INSERT INTO stay (reservation_id, checked_in_by, actual_check_in, status)
    VALUES (v_res_id, 2, '2026-12-20 14:00:00+07', 'IN_HOUSE') RETURNING stay_id INTO v_stay_id;

    INSERT INTO stay_room (stay_id, reservation_room_id, room_id, assigned_from)
    VALUES (v_stay_id, v_rr_id, 202, '2026-12-20 14:00:00+07') RETURNING stay_room_id INTO v_sr_id;

    INSERT INTO folio (stay_id, status) VALUES (v_stay_id, 'OPEN') RETURNING folio_id INTO v_folio_id;

    INSERT INTO folio_item (folio_id, entry_type, description, quantity, unit_price, source_key)
    VALUES (v_folio_id, 'CHARGE', 'Tien phong Suite 202 (1 dem)', 1, 2500000.00, 'ROOM:' || v_rr_id || ':2026-12-20');

    INSERT INTO service_order (stay_room_id, assigned_to, status, completed_at)
    VALUES (v_sr_id, 3, 'COMPLETED', CURRENT_TIMESTAMP) RETURNING service_order_id INTO v_so_id;

    INSERT INTO folio_item (folio_id, entry_type, description, quantity, unit_price, source_key)
    VALUES (v_folio_id, 'CHARGE', 'Giat ui (2 kg)', 2, 50000.00, 'SO:' || v_so_id) RETURNING folio_item_id INTO v_fi_svc_id;

    INSERT INTO service_order_item (service_order_id, service_id, quantity, unit_price, folio_item_id)
    VALUES (v_so_id, 1, 2, 50000.00, v_fi_svc_id);

    INSERT INTO invoice (folio_id, invoice_number, subtotal, discount_total, tax_amount, status)
    VALUES (v_folio_id, 'INV-TEST-202612-9999', 2600000.00, 0, 208000.00, 'PAID') RETURNING invoice_id INTO v_inv_id;

    INSERT INTO payment (invoice_id, recorded_by, amount, method, transaction_ref)
    VALUES (v_inv_id, 2, 2808000.00, 'TRANSFER', 'TXN-TEST-9999');

    RAISE NOTICE '[PASS] R12: Luong nghiep vu da bang tu Check-in den Thanh toan thanh cong!';
END $$;
ROLLBACK TO SAVEPOINT sp_r12;

ROLLBACK;