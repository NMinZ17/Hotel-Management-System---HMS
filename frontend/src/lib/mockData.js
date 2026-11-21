export const MOCK_ROOM_TYPES = [
  { room_type_id: 1, name: 'Standard', max_guests: 2, base_price: 800000 },
  { room_type_id: 2, name: 'Deluxe', max_guests: 3, base_price: 1200000 },
  { room_type_id: 3, name: 'Suite', max_guests: 4, base_price: 2500000 },
];

export const MOCK_ROOMS = [
  {
    room_id: 101,
    room_number: '101',
    floor: 1,
    room_type_id: 1,
    room_type: 'Standard',
    max_guests: 2,
    base_price: 800000,
    housekeeping_status: 'CLEAN',
    maintenance_status: 'OK',
    amenities: ['WiFi', 'TV', 'Dieu hoa'],
    is_available: true,
  },
  {
    room_id: 102,
    room_number: '102',
    floor: 1,
    room_type_id: 1,
    room_type: 'Standard',
    max_guests: 2,
    base_price: 800000,
    housekeeping_status: 'CLEAN',
    maintenance_status: 'OK',
    amenities: ['WiFi', 'TV', 'Dieu hoa'],
    is_available: false, // Đã có người đặt trong DB mẫu
  },
  {
    room_id: 201,
    room_number: '201',
    floor: 2,
    room_type_id: 2,
    room_type: 'Deluxe',
    max_guests: 3,
    base_price: 1200000,
    housekeeping_status: 'CLEAN',
    maintenance_status: 'OK',
    amenities: ['WiFi', 'TV', 'Dieu hoa', 'Bon tam'],
    is_available: true,
  },
  {
    room_id: 202,
    room_number: '202',
    floor: 2,
    room_type_id: 3,
    room_type: 'Suite',
    max_guests: 4,
    base_price: 2500000,
    housekeeping_status: 'CLEAN',
    maintenance_status: 'OK',
    amenities: ['WiFi', 'TV', 'Dieu hoa', 'Bon tam'],
    is_available: true,
  },
];

export const MOCK_DISCOUNTS = [
  { code: 'WELCOME10', discount_type: 'PERCENT', value: 10 },
];