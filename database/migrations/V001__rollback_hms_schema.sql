-- ============================================================================
-- MIGRATION ROLLBACK: database/migrations/V001__rollback_hms_schema.sql
-- Hoàn tác toàn bộ 28 bảng về trạng thái cơ sở dữ liệu trống
-- ============================================================================

BEGIN;

DROP TABLE IF EXISTS audit_event CASCADE;
DROP TABLE IF EXISTS guest_review CASCADE;
DROP TABLE IF EXISTS service_order_item CASCADE;
DROP TABLE IF EXISTS service_order CASCADE;
DROP TABLE IF EXISTS maintenance_ticket CASCADE;
DROP TABLE IF EXISTS housekeeping_task CASCADE;
DROP TABLE IF EXISTS service CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS invoice CASCADE;
DROP TABLE IF EXISTS folio_item CASCADE;
DROP TABLE IF EXISTS folio CASCADE;
DROP TABLE IF EXISTS stay_room CASCADE;
DROP TABLE IF EXISTS stay CASCADE;
DROP TABLE IF EXISTS reservation_discount CASCADE;
DROP TABLE IF EXISTS reservation_guest CASCADE;
DROP TABLE IF EXISTS reservation_room CASCADE;
DROP TABLE IF EXISTS reservation CASCADE;
DROP TABLE IF EXISTS discount CASCADE;
DROP TABLE IF EXISTS employee CASCADE;
DROP TABLE IF EXISTS guest CASCADE;
DROP TABLE IF EXISTS user_role CASCADE;
DROP TABLE IF EXISTS app_user CASCADE;
DROP TABLE IF EXISTS role CASCADE;
DROP TABLE IF EXISTS room_amenity CASCADE;
DROP TABLE IF EXISTS room CASCADE;
DROP TABLE IF EXISTS amenity CASCADE;
DROP TABLE IF EXISTS room_type CASCADE;
DROP TABLE IF EXISTS hotel CASCADE;

DROP EXTENSION IF EXISTS btree_gist;

COMMIT;