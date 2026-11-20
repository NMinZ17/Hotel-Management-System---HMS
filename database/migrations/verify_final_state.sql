-- 1) Phải trả về 0 dòng
SELECT a.room_id, a.reservation_room_id AS rr1, b.reservation_room_id AS rr2
FROM reservation_room AS a
JOIN reservation_room AS b
  ON a.room_id = b.room_id
 AND a.reservation_room_id < b.reservation_room_id
 AND a.is_cancelled IS NOT TRUE AND b.is_cancelled IS NOT TRUE
 AND a.check_in_date < b.check_out_date
 AND a.check_out_date > b.check_in_date;

-- 2) Phải ra dat_phong = 1, su_kien = 1
SELECT
  (SELECT COUNT(*) FROM reservation_room
    WHERE room_id = 101 AND check_in_date = '2026-12-20') AS dat_phong,
  (SELECT COUNT(*) FROM booking_events
    WHERE room_id = 101 AND dataset = 'demo' AND event_type = 'CREATED') AS su_kien;

-- 3) Xem chi tiet ai là người đặt thành công
SELECT rr.reservation_room_id, rr.reservation_id, g.full_name,
       rr.check_in_date, rr.check_out_date
FROM reservation_room AS rr
JOIN reservation_guest AS rg ON rg.reservation_id = rr.reservation_id AND rg.is_primary
JOIN guest AS g ON g.guest_id = rg.guest_id
WHERE rr.room_id = 101;