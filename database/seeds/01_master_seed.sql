-- ============================================================================
-- SEED TẦNG 1: database/seeds/01_master_seed.sql
-- Dữ liệu danh mục chuẩn dùng chung cho cả 3 môi trường (dev, test, bench)
-- ============================================================================

BEGIN;

INSERT INTO hotel (hotel_id, name, address, phone, timezone) VALUES
(1, 'HMS Demo Hotel', '1 Pho Demo, Ha Noi', '0240000000', 'Asia/Ho_Chi_Minh')
ON CONFLICT (hotel_id) DO NOTHING;

INSERT INTO room_type (room_type_id, name, max_guests, base_price, is_active) VALUES
(1, 'Standard', 2,  800000.00, TRUE),
(2, 'Deluxe',   3, 1200000.00, TRUE),
(3, 'Suite',    4, 2500000.00, TRUE)
ON CONFLICT (room_type_id) DO NOTHING;

INSERT INTO amenity (amenity_id, name) VALUES
(1, 'WiFi'),
(2, 'TV'),
(3, 'Dieu hoa'),
(4, 'Bon tam')
ON CONFLICT (amenity_id) DO NOTHING;

INSERT INTO role (role_id, code, name) VALUES
(1, 'ADMIN',        'Quan tri'),
(2, 'RECEPTION',    'Le tan'),
(3, 'GUEST',        'Khach'),
(4, 'HOUSEKEEPING', 'Buong phong'),
(5, 'MAINTENANCE',  'Ky thuat'),
(6, 'ACCOUNTANT',   'Ke toan')
ON CONFLICT (role_id) DO NOTHING;

INSERT INTO service (service_id, name, category, unit_price, is_active) VALUES
(1, 'Giat ui',  'LAUNDRY',   50000.00, TRUE),
(2, 'An sang',  'FOOD',     120000.00, TRUE),
(3, 'Minibar',  'BEVERAGE',  80000.00, TRUE)
ON CONFLICT (service_id) DO NOTHING;

INSERT INTO discount (discount_id, code, discount_type, value, valid_from, valid_to, is_active) VALUES
(1, 'WELCOME10', 'PERCENT', 10.00, '2026-01-01', '2026-12-31', TRUE)
ON CONFLICT (discount_id) DO NOTHING;

-- Đồng bộ sequence cho các bảng danh mục
SELECT setval(pg_get_serial_sequence('hotel', 'hotel_id'), COALESCE(MAX(hotel_id), 1)) FROM hotel;
SELECT setval(pg_get_serial_sequence('room_type', 'room_type_id'), COALESCE(MAX(room_type_id), 1)) FROM room_type;
SELECT setval(pg_get_serial_sequence('amenity', 'amenity_id'), COALESCE(MAX(amenity_id), 1)) FROM amenity;
SELECT setval(pg_get_serial_sequence('role', 'role_id'), COALESCE(MAX(role_id), 1)) FROM role;
SELECT setval(pg_get_serial_sequence('service', 'service_id'), COALESCE(MAX(service_id), 1)) FROM service;
SELECT setval(pg_get_serial_sequence('discount', 'discount_id'), COALESCE(MAX(discount_id), 1)) FROM discount;

COMMIT;