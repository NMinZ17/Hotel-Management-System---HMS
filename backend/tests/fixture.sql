-- Test-only fixture, executed in a fresh, randomly named PostgreSQL schema.
CREATE TABLE room_type (
    room_type_id BIGINT PRIMARY KEY,
    name VARCHAR(80),
    max_guests SMALLINT,
    base_price NUMERIC(14, 2),
    is_active BOOLEAN
);

CREATE TABLE room (
    room_id BIGINT PRIMARY KEY,
    room_type_id BIGINT REFERENCES room_type(room_type_id),
    room_number VARCHAR(15),
    floor SMALLINT,
    housekeeping_status VARCHAR(15),
    maintenance_status VARCHAR(15),
    is_active BOOLEAN
);

INSERT INTO room_type
    (room_type_id, name, max_guests, base_price, is_active)
VALUES
    (1, 'Standard', 2, 800000.00, TRUE),
    (2, 'Deluxe', 3, 1200000.50, TRUE),
    (3, 'Archived type', 4, 2500000.00, FALSE);

INSERT INTO room
    (room_id, room_type_id, room_number, floor,
     housekeeping_status, maintenance_status, is_active)
VALUES
    (101, 1, '101', 1, 'CLEAN', 'OK', TRUE),
    (105, 1, '101', 1, 'DIRTY', 'OK', TRUE),
    (102, 1, '102', 1, 'CLEAN', 'OK', TRUE),
    (201, 2, '201', 2, 'CLEAN', 'BLOCKED', TRUE),
    (202, 2, '202', 2, 'CLEAN', 'OK', FALSE),
    (301, 3, '301', 3, 'CLEAN', 'OK', TRUE);
