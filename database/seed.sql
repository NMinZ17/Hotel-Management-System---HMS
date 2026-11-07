INSERT INTO hotel (hotel_id, name, address, phone, timezone) 
VALUES (1, 'HMS Demo Hotel', '1 Pho Demo, Ha Noi', '0240000000', 'Asia/Ho_Chi_Minh');

INSERT INTO room_type (room_type_id, name, max_guests, base_price, is_active) VALUES
(1, 'Standard', 2, 800000.00, TRUE),
(2, 'Deluxe',   3, 1200000.00, TRUE),
(3, 'Suite',    4, 2500000.00, TRUE);

INSERT INTO amenity (amenity_id, name) VALUES 
(1, 'WiFi'), 
(2, 'TV'), 
(3, 'Dieu hoa'), 
(4, 'Bon tam');

INSERT INTO room (room_id, room_type_id, room_number, floor, housekeeping_status, maintenance_status, is_active) VALUES
(101, 1, '101', 1, 'CLEAN', 'OK', TRUE),
(102, 1, '102', 1, 'CLEAN', 'OK', TRUE),
(201, 2, '201', 2, 'CLEAN', 'OK', TRUE),
(202, 3, '202', 2, 'CLEAN', 'OK', TRUE);


INSERT INTO room_amenity (room_id, amenity_id) VALUES
(101, 1), (101, 2), (101, 3),
(102, 1), (102, 2), (102, 3),
(201, 1), (201, 2), (201, 3), (201, 4),
(202, 1), (202, 2), (202, 3), (202, 4);


INSERT INTO role (role_id, code, name) VALUES
(1, 'ADMIN',     'Quan tri'), 
(2, 'RECEPTION', 'Le tan'), 
(3, 'GUEST',     'Khach');

INSERT INTO app_user (user_id, email, password_hash, is_active, created_at) VALUES
(1, 'admin@hms.example',  'demo_hash', TRUE, CURRENT_TIMESTAMP),
(2, 'letan@hms.example',  'demo_hash', TRUE, CURRENT_TIMESTAMP),
(3, 'khach1@hms.example', 'demo_hash', TRUE, CURRENT_TIMESTAMP);

INSERT INTO user_role (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 3);

INSERT INTO employee (employee_id, user_id, full_name, job_title, is_active) VALUES
(1, 1, 'Nguyen Van Quan', 'Manager', TRUE),
(2, 2, 'Tran Thi Le',     'Receptionist', TRUE);

INSERT INTO guest (guest_id, user_id, full_name, phone, email) VALUES
(1, 3,    'Pham Thu Ha',   '0900000001', 'ha@example.com'),
(2, NULL, 'Nguyen Minh Anh', '0900000002', 'anh@example.com'),
(3, NULL, 'Tran Duc Long',  '0900000003', 'long@example.com');

INSERT INTO discount (discount_id, code, discount_type, value, valid_from, valid_to, is_active) VALUES
(1, 'WELCOME10', 'PERCENT', 10.00, '2026-01-01', '2026-12-31', TRUE);

INSERT INTO service (service_id, name, category, unit_price, is_active) VALUES
(1, 'Giat ui',  'LAUNDRY',  50000.00, TRUE),
(2, 'An sang',  'FOOD',    120000.00, TRUE),
(3, 'Minibar',  'BEVERAGE', 80000.00, TRUE);

INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, note) VALUES 
(1, 1, 'CONFIRMED', CURRENT_TIMESTAMP, 'Thu Ha dat phong 102 tu 10/12 den 12/12/2026');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(1, 1, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES 
(1, 1, 102, '2026-12-10', '2026-12-12', 2, 0, 800000.00, FALSE);