
import { useEffect, useState } from 'react';
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { count, money, optionsOf, percent } from '../common/utils.js';
import apiClient from '../../../lib/api.js';

const ROOM_STATUS = {
  available: { label: 'Trống', tone: 'success' },
  cleaning: { label: 'Đang dọn', tone: 'warning' },
  occupied: { label: 'Có khách', tone: 'info' },
  out: { label: 'Ngừng sử dụng', tone: 'danger' },
};

const FLOOR_OPTIONS = [1, 2, 3, 4, 5, 6].map(n => ({
  value: String(n),
  label: `Tầng ${n}`,
}));

// Chuyển dữ liệu phòng từ API sang định dạng hiển thị
const mapRoom = room => {
  const housekeepingStatus = String(
    room.housekeeping_status ?? ''
  ).toUpperCase();

  const maintenanceStatus = String(
    room.maintenance_status ?? ''
  ).toUpperCase();

  let status = null;

  if (maintenanceStatus && maintenanceStatus !== 'OK') {
    status = 'out';
  } else if (
    housekeepingStatus === 'CLEANING' ||
    housekeepingStatus === 'DIRTY'
  ) {
    status = 'cleaning';
  }

  return {
    id: room.room_id,
    number: room.room_number ?? '',
    type: room.room_type?.name ?? '',
    floor: room.floor ?? '',
    price: Number(room.room_type?.base_price ?? 0),
    status,
  };
};

const roomsConfig = {
  title: 'Quản lý phòng',
  description: 'Theo dõi thông tin và trạng thái phòng khách sạn',


stats: rows => {
  const hasOccupancyData = rows.some(
    r => r.status === 'available' || r.status === 'occupied'
  );

  return [
    {
      label: 'Tổng số phòng',
      value: rows.length,
    },
    {
      label: 'Có khách',
      value: hasOccupancyData
        ? rows.filter(r => r.status === 'occupied').length
        : '--',
    },
    {
      label: 'Phòng trống',
      value: hasOccupancyData
        ? rows.filter(r => r.status === 'available').length
        : '--',
    },
    {
      label: 'Không khả dụng',
      value: rows.filter(r => r.status === 'out').length,
    },
  ];
},


  tabs: [
    { id: 'all', label: 'Tất cả', get: () => true },
    {
      id: 'available',
      label: 'Phòng trống',
      get: r => r.status === 'available',
    },
    {
      id: 'occupied',
      label: 'Có khách',
      get: r => r.status === 'occupied',
    },
    {
      id: 'unavailable',
      label: 'Không khả dụng',
      get: r => r.status === 'out',
    },
  ],

  filters: [
    {
      key: 'type',
      label: 'Loại phòng',
      options: [],
      get: r => r.type,
    },
    {
      key: 'floor',
      label: 'Tầng',
      options: FLOOR_OPTIONS,
      get: r => String(r.floor),
    },
    {
      key: 'status',
      label: 'Trạng thái',
      options: optionsOf(ROOM_STATUS),
      get: r => r.status,
    },
  ],

  columns: [
    {
      key: 'number',
      label: 'Số phòng',
    },
    {
      key: 'type',
      label: 'Loại phòng',
    },
    {
      key: 'floor',
      label: 'Tầng',
      render: r => r.floor ? `Tầng ${r.floor}` : '—',
    },
    {
      key: 'price',
      label: 'Giá phòng',
      render: r => money(r.price),
    },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => r.status
        ? <StatusTag map={ROOM_STATUS} value={r.status} />
        : 'Chưa xác định',
      text: r => ROOM_STATUS[r.status]?.label ?? 'Chưa xác định',
    },
  ],

  fields: [],
};

export default function RoomsPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchRooms = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await apiClient.get('/api/rooms');

      if (!Array.isArray(response.data)) {
        throw new Error('Dữ liệu phòng trả về không hợp lệ.');
      }

      const mappedRooms = response.data.map(mapRoom);
      setRows(mappedRooms);

      const roomTypes = [
        ...new Set(mappedRooms.map(room => room.type).filter(Boolean)),
      ];

      roomsConfig.filters[0].options = roomTypes.map(type => ({
        value: type,
        label: type,
      }));
    } catch (err) {
      console.error('Lỗi tải danh sách phòng:', err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Không thể tải danh sách phòng.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
  }, []);

  if (loading) {
    return <div className="page-loading">Đang tải danh sách phòng...</div>;
  }

  if (error) {
    return (
      <div className="page-error">
        <p>{error}</p>
        <button type="button" onClick={fetchRooms}>
          Thử lại
        </button>
      </div>
    );
  }

  return (
    <CrudPage
      config={{
        ...roomsConfig,
        rows,
      }}
    />
  );
}

