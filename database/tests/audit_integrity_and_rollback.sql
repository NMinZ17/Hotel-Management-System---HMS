-- ============================================================================
-- AUDIT SCRIPT: database/tests/audit_integrity_and_rollback.sql
-- 1. Xác nhận 0 lịch chồng lấn
-- 2. Xác nhận 0 bản ghi mồ côi (tham chiếu & nghiệp vụ)
-- 3. Đối chiếu số dòng 28 bảng trước / trong / sau ROLLBACK
-- ============================================================================

-- ----------------------------------------------------------------------------
-- PHẦN 1: KIỂM CHỨNG KHÔNG CÓ LỊCH CHỒNG LẤN (KỲ VỌNG: TẤT CẢ = 0)
-- ----------------------------------------------------------------------------
SELECT 'OVERLAP_RESERVATION_ROOM' AS check_name, COUNT(*) AS violation_count
FROM reservation_room a
JOIN reservation_room b
  ON a.room_id = b.room_id
 AND a.reservation_room_id < b.reservation_room_id
WHERE a.is_cancelled = FALSE
  AND b.is_cancelled = FALSE
  AND daterange(a.check_in_date, a.check_out_date, '[)')
      && daterange(b.check_in_date, b.check_out_date, '[)')

UNION ALL

SELECT 'OVERLAP_STAY_ROOM' AS check_name, COUNT(*) AS violation_count
FROM stay_room a
JOIN stay_room b
  ON a.room_id = b.room_id
 AND a.stay_room_id < b.stay_room_id
WHERE tstzrange(a.assigned_from, COALESCE(a.assigned_to, 'infinity'::timestamptz), '[)')
      && tstzrange(b.assigned_from, COALESCE(b.assigned_to, 'infinity'::timestamptz), '[)')

UNION ALL

SELECT 'STALE_ACTIVE_ROOM_ON_CANCELLED_RES' AS check_name, COUNT(*) AS violation_count
FROM reservation r
JOIN reservation_room rr ON rr.reservation_id = r.reservation_id
WHERE r.status IN ('CANCELLED', 'NO_SHOW')
  AND rr.is_cancelled = FALSE;

-- ----------------------------------------------------------------------------
-- PHẦN 2: KIỂM CHỨNG KHÔNG CÓ BẢN GHI MỒ CÔI (KỲ VỌNG: TẤT CẢ = 0)
-- ----------------------------------------------------------------------------
SELECT 'ORPHAN_ROOM_WITHOUT_TYPE' AS check_name, COUNT(*) AS orphan_count
FROM room r LEFT JOIN room_type rt ON rt.room_type_id = r.room_type_id
WHERE rt.room_type_id IS NULL

UNION ALL
SELECT 'ORPHAN_RESERVATION_WITHOUT_GUEST', COUNT(*)
FROM reservation r LEFT JOIN guest g ON g.guest_id = r.booked_by_guest_id
WHERE g.guest_id IS NULL

UNION ALL
SELECT 'ORPHAN_RESERVATION_WITHOUT_ROOM', COUNT(*)
FROM reservation r
LEFT JOIN reservation_room rr ON rr.reservation_id = r.reservation_id
WHERE rr.reservation_room_id IS NULL

UNION ALL
SELECT 'ORPHAN_RESERVATION_WITHOUT_PRIMARY_GUEST', COUNT(*)
FROM reservation r
LEFT JOIN reservation_guest rg
  ON rg.reservation_id = r.reservation_id AND rg.is_primary = TRUE
WHERE rg.reservation_id IS NULL

UNION ALL
SELECT 'ORPHAN_STAY_WITHOUT_FOLIO', COUNT(*)
FROM stay s LEFT JOIN folio f ON f.stay_id = s.stay_id
WHERE f.folio_id IS NULL

UNION ALL
SELECT 'ORPHAN_STAY_WITHOUT_STAY_ROOM', COUNT(*)
FROM stay s LEFT JOIN stay_room sr ON sr.stay_id = s.stay_id
WHERE sr.stay_room_id IS NULL

UNION ALL
SELECT 'ORPHAN_SERVICE_ORDER_WITHOUT_ITEMS', COUNT(*)
FROM service_order so LEFT JOIN service_order_item soi ON soi.service_order_id = so.service_order_id
WHERE soi.service_order_item_id IS NULL

UNION ALL
SELECT 'ORPHAN_INVOICE_WITHOUT_FOLIO', COUNT(*)
FROM invoice i LEFT JOIN folio f ON f.folio_id = i.folio_id
WHERE f.folio_id IS NULL

UNION ALL
SELECT 'ORPHAN_PAYMENT_WITHOUT_INVOICE', COUNT(*)
FROM payment p LEFT JOIN invoice i ON i.invoice_id = p.invoice_id
WHERE i.invoice_id IS NULL;

-- ----------------------------------------------------------------------------
-- PHẦN 3: CHỤP SỐ DÒNG 28 BẢNG TRƯỚC / TRONG / SAU ROLLBACK
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    v_tbl TEXT;
    v_cnt BIGINT;
    v_before JSONB := '{}'::jsonb;
    v_inside JSONB := '{}'::jsonb;
    v_after  JSONB := '{}'::jsonb;
    v_b BIGINT;
    v_i BIGINT;
    v_a BIGINT;
    v_diff_tables INT := 0;
    v_tables TEXT[] := ARRAY[
        'amenity', 'app_user', 'audit_event', 'discount', 'employee',
        'folio', 'folio_item', 'guest', 'guest_review', 'hotel',
        'housekeeping_task', 'invoice', 'maintenance_ticket', 'payment', 'reservation',
        'reservation_discount', 'reservation_guest', 'reservation_room', 'role', 'room',
        'room_amenity', 'room_type', 'service', 'service_order', 'service_order_item',
        'stay', 'stay_room', 'user_role'
    ];
BEGIN
    -- 1. Chụp số dòng 28 bảng TRƯỚC giao dịch
    FOREACH v_tbl IN ARRAY v_tables LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', v_tbl) INTO v_cnt;
        v_before := jsonb_set(v_before, ARRAY[v_tbl], to_jsonb(v_cnt));
    END LOOP;

    -- 2. Chèn dữ liệu thử nghiệm trong subtransaction rồi chủ động ROLLBACK
    BEGIN
        INSERT INTO guest (guest_id, full_name, phone, email)
        VALUES (999901, 'Khach Tam Rollback', '0999999999', 'temp_rb@example.com');

        INSERT INTO reservation (reservation_id, booked_by_guest_id, status, note)
        VALUES (999901, 999901, 'CONFIRMED', 'Giao dich se bi rollback');

        INSERT INTO reservation_guest (reservation_id, guest_id, is_primary)
        VALUES (999901, 999901, TRUE);

        INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, nightly_price)
        VALUES (999901, 999901, 101, '2027-01-10', '2027-01-12', 2, 800000.00);

        INSERT INTO audit_event (event_id, actor_user_id, reservation_id, action, details)
        VALUES (999901, 2, 999901, 'TEMP_TEST_ACTION', '{"rollback": true}'::jsonb);

        -- Chụp số dòng TRONG lúc giao dịch đang mở
        FOREACH v_tbl IN ARRAY v_tables LOOP
            EXECUTE format('SELECT COUNT(*) FROM %I', v_tbl) INTO v_cnt;
            v_inside := jsonb_set(v_inside, ARRAY[v_tbl], to_jsonb(v_cnt));
        END LOOP;

        -- Kích hoạt rollback toàn bộ dữ liệu vừa chèn
        RAISE EXCEPTION 'FORCE_SUBTX_ROLLBACK' USING ERRCODE = 'P9999';
    EXCEPTION
        WHEN SQLSTATE 'P9999' THEN
            NULL;
    END;

    -- 3. Đếm lại số dòng 28 bảng SAU ROLLBACK và in kết quả đối chiếu
    FOREACH v_tbl IN ARRAY v_tables LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', v_tbl) INTO v_cnt;
        v_after := jsonb_set(v_after, ARRAY[v_tbl], to_jsonb(v_cnt));

        v_b := (v_before ->> v_tbl)::bigint;
        v_i := (v_inside ->> v_tbl)::bigint;
        v_a := (v_after  ->> v_tbl)::bigint;

        IF v_b <> v_a THEN
            v_diff_tables := v_diff_tables + 1;
        END IF;

        RAISE NOTICE '% | before=% | inside_tx=% | after_rollback=% | diff=%',
            RPAD(v_tbl, 22), v_b, v_i, v_a, (v_a - v_b);
    END LOOP;

    IF v_diff_tables > 0 THEN
        RAISE EXCEPTION 'FAIL ROLLBACK AUDIT: Co % bang bi lech so dong sau ROLLBACK!', v_diff_tables;
    ELSE
        RAISE NOTICE '-----------------------------------------------------------------------';
        RAISE NOTICE '[PASS] ROLLBACK AUDIT: 28/28 bang giu nguyen chinh xac so dong truoc va sau ROLLBACK.';
    END IF;
END $$;