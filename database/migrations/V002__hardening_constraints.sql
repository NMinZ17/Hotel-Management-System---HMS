-- ============================================================================
-- MIGRATION: database/migrations/V002__hardening_constraints.sql
-- Gia cố đồng bộ hủy đặt phòng, khóa xóa folio_item đã liên kết và dấu giảm giá
-- ============================================================================

BEGIN;

-- 1. Ngăn xóa folio_item nếu đang được tham chiếu bởi service_order_item
ALTER TABLE service_order_item
    DROP CONSTRAINT IF EXISTS fk_service_order_item_folio_item,
    ADD CONSTRAINT fk_service_order_item_folio_item
        FOREIGN KEY (folio_item_id) REFERENCES folio_item(folio_item_id)
        ON DELETE RESTRICT;

-- 2. Ràng buộc dấu tiền trên folio_item: DISCOUNT phải có unit_price <= 0
ALTER TABLE folio_item
    DROP CONSTRAINT IF EXISTS ck_folio_item_unit_price,
    ADD CONSTRAINT ck_folio_item_unit_price CHECK (
        (entry_type IN ('CHARGE', 'TAX') AND unit_price >= 0)
        OR (entry_type = 'DISCOUNT' AND unit_price <= 0)
        OR (entry_type = 'ADJUSTMENT')
    );

-- 3. Trigger tự động giải phóng phòng khi reservation chuyển sang CANCELLED / NO_SHOW
CREATE OR REPLACE FUNCTION fn_sync_reservation_room_cancel()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.status IN ('CANCELLED', 'NO_SHOW')
       AND OLD.status IS DISTINCT FROM NEW.status THEN
        UPDATE reservation_room
        SET is_cancelled = TRUE
        WHERE reservation_id = NEW.reservation_id
          AND is_cancelled = FALSE;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_sync_reservation_room_cancel ON reservation;
CREATE TRIGGER trg_sync_reservation_room_cancel
    AFTER UPDATE OF status ON reservation
    FOR EACH ROW
    EXECUTE FUNCTION fn_sync_reservation_room_cancel();

COMMIT;