-- ============================================================================
-- SEED TẦNG 2 (DEV): database/seeds/02_dev_fixture.sql
-- Chạy trên hms_dev SAU KHI đã chạy 01_master_seed.sql
-- ============================================================================

BEGIN;

-- 1. Phòng vật lý & Tiện nghi
INSERT INTO room (room_id, room_type_id, room_number, floor, housekeeping_status, maintenance_status, is_active) VALUES
(101, 1, '101', 1, 'CLEAN', 'OK', TRUE),
(102, 1, '102', 1, 'CLEAN', 'OK', TRUE),
(201, 2, '201', 2, 'CLEAN', 'OK', TRUE),
(202, 3, '202', 2, 'DIRTY', 'OK', TRUE),
(301, 2, '301', 3, 'CLEAN', 'MINOR_ISSUE', TRUE);

INSERT INTO room_amenity (room_id, amenity_id) VALUES
(101, 1), (101, 2), (101, 3),
(102, 1), (102, 2), (102, 3),
(201, 1), (201, 2), (201, 3), (201, 4),
(202, 1), (202, 2), (202, 3), (202, 4),
(301, 1), (301, 2), (301, 3), (301, 4);

-- 2. Tài khoản, Nhân viên & Khách hàng
INSERT INTO app_user (user_id, email, password_hash, is_active, created_at) VALUES
(1, 'admin@hms.example',      'demo_hash', TRUE, '2026-01-01 08:00:00+07'),
(2, 'letan@hms.example',      'demo_hash', TRUE, '2026-01-01 08:00:00+07'),
(3, 'khach1@hms.example',     'demo_hash', TRUE, '2026-01-01 08:00:00+07'),
(4, 'buongphong@hms.example', 'demo_hash', TRUE, '2026-01-01 08:00:00+07'),
(5, 'kythuat@hms.example',    'demo_hash', TRUE, '2026-01-01 08:00:00+07');

INSERT INTO user_role (user_id, role_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5);

INSERT INTO employee (employee_id, user_id, full_name, job_title, is_active) VALUES
(1, 1, 'Nguyen Van Quan', 'Manager',            TRUE),
(2, 2, 'Tran Thi Le',     'Receptionist',       TRUE),
(3, 4, 'Le Thi Hoa',      'Housekeeping Staff', TRUE),
(4, 5, 'Pham Van Ky',     'Maintenance Tech',   TRUE);

INSERT INTO guest (guest_id, user_id, full_name, phone, email) VALUES
(1, 3,    'Pham Thu Ha',     '0900000001', 'ha@example.com'),
(2, NULL, 'Nguyen Minh Anh', '0900000002', 'anh@example.com'),
(3, NULL, 'Tran Duc Long',   '0900000003', 'long@example.com');

-- 3. Đơn đặt phòng #1: Tương lai (CONFIRMED - phòng 102 từ 10/12 đến 12/12/2026)
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(1, 1, 'CONFIRMED', '2026-11-15 10:00:00+07', NULL, 'Thu Ha dat phong 102 tu 10/12 den 12/12/2026');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(1, 1, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(1, 1, 102, '2026-12-10', '2026-12-12', 2, 0, 800000.00, FALSE);

-- 4. Đơn đặt phòng #2: Đã trả phòng hoàn tất (CHECKED_OUT - phòng 201 từ 01/11 đến 03/11/2026)
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(2, 2, 'CHECKED_OUT', '2026-10-25 14:00:00+07', NULL, 'Minh Anh luu tru 2 dem phong Deluxe 201');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(2, 2, TRUE), (2, 3, FALSE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(2, 2, 201, '2026-11-01', '2026-11-03', 2, 0, 1200000.00, FALSE);

INSERT INTO reservation_discount (reservation_id, discount_id, discount_amount) VALUES
(2, 1, 240000.00);

INSERT INTO stay (stay_id, reservation_id, checked_in_by, checked_out_by, actual_check_in, actual_check_out, status) VALUES
(1, 2, 2, 2, '2026-11-01 14:05:00+07', '2026-11-03 11:30:00+07', 'CHECKED_OUT');

INSERT INTO stay_room (stay_room_id, stay_id, reservation_room_id, room_id, assigned_from, assigned_to) VALUES
(1, 1, 2, 201, '2026-11-01 14:05:00+07', '2026-11-03 11:30:00+07');

INSERT INTO folio (folio_id, stay_id, status, opened_at, closed_at) VALUES
(1, 1, 'CLOSED', '2026-11-01 14:05:00+07', '2026-11-03 11:30:00+07');

INSERT INTO folio_item (folio_item_id, folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at) VALUES
(1, 1, 'CHARGE',   'Tien phong Deluxe 201 (2 dem)', 2.00, 1200000.00, 'ROOM:2:2026-11-01', '2026-11-01 14:05:00+07'),
(2, 1, 'CHARGE',   'An sang (2 suat)',              2.00,  120000.00, 'SOI:1',             '2026-11-02 08:15:00+07'),
(3, 1, 'DISCOUNT', 'Ma giam gia WELCOME10',         1.00, -240000.00, 'DISC:2:1',          '2026-11-03 11:20:00+07');

INSERT INTO service_order (service_order_id, stay_room_id, assigned_to, status, ordered_at, completed_at) VALUES
(1, 1, 3, 'COMPLETED', '2026-11-02 07:45:00+07', '2026-11-02 08:15:00+07');

INSERT INTO service_order_item (service_order_item_id, service_order_id, service_id, quantity, unit_price, folio_item_id) VALUES
(1, 1, 2, 2.00, 120000.00, 2);

INSERT INTO invoice (invoice_id, folio_id, invoice_number, subtotal, discount_total, tax_amount, issued_at, status) VALUES
(1, 1, 'INV-202611-0001', 2640000.00, 240000.00, 192000.00, '2026-11-03 11:25:00+07', 'PAID');

INSERT INTO payment (payment_id, invoice_id, recorded_by, amount, method, transaction_ref, paid_at) VALUES
(1, 1, 2, 2592000.00, 'CARD', 'POS-20261103-0001', '2026-11-03 11:28:00+07');

INSERT INTO guest_review (review_id, stay_id, guest_id, rating, comment, created_at) VALUES
(1, 1, 2, 5, 'Phong sach se, nhan vien ho tro nhanh.', '2026-11-03 18:00:00+07');

-- 5. Đơn đặt phòng #3: Khách đang lưu trú tại khách sạn (IN_HOUSE - phòng 202 từ 19/11 đến 22/11/2026)
INSERT INTO reservation (reservation_id, booked_by_guest_id, status, created_at, cancelled_at, note) VALUES
(3, 3, 'CHECKED_IN', '2026-11-18 09:00:00+07', NULL, 'Duc Long dang o phong Suite 202');

INSERT INTO reservation_guest (reservation_id, guest_id, is_primary) VALUES
(3, 3, TRUE);

INSERT INTO reservation_room (reservation_room_id, reservation_id, room_id, check_in_date, check_out_date, adults, children, nightly_price, is_cancelled) VALUES
(3, 3, 202, '2026-11-19', '2026-11-22', 2, 1, 2500000.00, FALSE);

INSERT INTO stay (stay_id, reservation_id, checked_in_by, checked_out_by, actual_check_in, actual_check_out, status) VALUES
(2, 3, 2, NULL, '2026-11-19 14:10:00+07', NULL, 'IN_HOUSE');

INSERT INTO stay_room (stay_room_id, stay_id, reservation_room_id, room_id, assigned_from, assigned_to) VALUES
(2, 2, 3, 202, '2026-11-19 14:10:00+07', NULL);

INSERT INTO folio (folio_id, stay_id, status, opened_at, closed_at) VALUES
(2, 2, 'OPEN', '2026-11-19 14:10:00+07', NULL);

INSERT INTO folio_item (folio_item_id, folio_id, entry_type, description, quantity, unit_price, source_key, occurred_at) VALUES
(4, 2, 'CHARGE', 'Tien phong Suite 202 (dem 19/11)', 1.00, 2500000.00, 'ROOM:3:2026-11-19', '2026-11-19 14:10:00+07');

INSERT INTO service_order (service_order_id, stay_room_id, assigned_to, status, ordered_at, completed_at) VALUES
(2, 2, 3, 'IN_PROGRESS', '2026-11-20 09:30:00+07', NULL);

INSERT INTO service_order_item (service_order_item_id, service_order_id, service_id, quantity, unit_price, folio_item_id) VALUES
(2, 2, 1, 3.00, 50000.00, NULL);

-- 6. Vận hành buồng phòng, bảo trì & nhật ký kiểm toán
INSERT INTO housekeeping_task (task_id, room_id, assigned_to, scheduled_at, completed_at, status) VALUES
(1, 201, 3, '2026-11-03 11:35:00+07', '2026-11-03 12:15:00+07', 'COMPLETED'),
(2, 202, 3, '2026-11-20 10:00:00+07', NULL, 'PENDING');

INSERT INTO maintenance_ticket (ticket_id, room_id, reported_by, assigned_to, description, status, reported_at, closed_at) VALUES
(1, 202, 3, 4, 'Kiem tra dieu khien dieu hoa dinh ky', 'CLOSED', '2026-11-05 09:00:00+07', '2026-11-05 10:00:00+07'),
(2, 301, 3, 4, 'Den ngu dau giuong nhap nhay', 'OPEN', '2026-11-20 08:30:00+07', NULL);

INSERT INTO audit_event (event_id, actor_user_id, reservation_id, service_order_id, action, details, occurred_at) VALUES
(1, 2, 2, NULL, 'STAY_CHECKED_OUT', '{"stay_id": 1, "invoice_number": "INV-202611-0001"}'::jsonb, '2026-11-03 11:30:00+07'),
(2, 2, 3, NULL, 'STAY_CHECKED_IN',  '{"stay_id": 2, "room_number": "202"}'::jsonb, '2026-11-19 14:10:00+07');

-- 7. Đồng bộ sequence
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
SELECT setval(pg_get_serial_sequence('housekeeping_task', 'task_id'), COALESCE(MAX(task_id), 1)) FROM housekeeping_task;
SELECT setval(pg_get_serial_sequence('maintenance_ticket', 'ticket_id'), COALESCE(MAX(ticket_id), 1)) FROM maintenance_ticket;
SELECT setval(pg_get_serial_sequence('service_order', 'service_order_id'), COALESCE(MAX(service_order_id), 1)) FROM service_order;
SELECT setval(pg_get_serial_sequence('service_order_item', 'service_order_item_id'), COALESCE(MAX(service_order_item_id), 1)) FROM service_order_item;
SELECT setval(pg_get_serial_sequence('guest_review', 'review_id'), COALESCE(MAX(review_id), 1)) FROM guest_review;
SELECT setval(pg_get_serial_sequence('audit_event', 'event_id'), COALESCE(MAX(event_id), 1)) FROM audit_event;

COMMIT;