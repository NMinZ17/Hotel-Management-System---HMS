BEGIN;

DROP TABLE booking_events;

ALTER TABLE reservation_room DROP CONSTRAINT ck_reservation_room_dates;
ALTER TABLE reservation_room ALTER COLUMN reservation_room_id DROP IDENTITY;
ALTER TABLE reservation      ALTER COLUMN reservation_id DROP IDENTITY;

DELETE FROM schema_migrations WHERE version = '001';

COMMIT;