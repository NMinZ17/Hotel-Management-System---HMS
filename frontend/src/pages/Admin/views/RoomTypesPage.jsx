
import { useEffect, useState } from 'react';
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { money } from '../common/utils.js';
import apiClient from '../../../lib/api.js';

const TYPE_STATUS = {
  unknown: { label: 'Chưa xác định', tone: 'neutral' },
};

const roomTypesConfig = {
  title: 'Loại phòng',
  subtitle: 'Thông tin loại phòng được lấy từ dữ liệu phòng trong hệ thống.',
  addLabel: 'Thêm loại phòng',
  noun: 'loại phòng',
  label: r => r.name,
  exportName: 'loai-phong',
  searchKeys: ['name'],
  searchPlaceholder: 'Tìm theo tên loại phòng',

  stats: rows => {
    const prices = rows
      .map(r => Number(r.price))
      .filter(Number.isFinite);

    return [
      {
        label: 'Số loại phòng',
        value: rows.length,
        note: 'Lấy từ dữ liệu phòng',
      },
      {
        label: 'Giá thấp nhất',
        value: prices.length ? money(Math.min(...prices)) : '--',
        note: 'Mỗi đêm',
      },
      {
        label: 'Giá cao nhất',
        value: prices.length ? money(Math.max(...prices)) : '--',
        note: 'Mỗi đêm',
      },
      {
        label: 'Tổng số phòng',
        value: rows.reduce((sum, r) => sum + r.rooms, 0),
        note: 'Thuộc mọi loại phòng',
      },
    ];
  },

  tabs: [
    { id: 'all', label: 'Tất cả', match: () => true },
  ],

  filters: [
    {
      id: 'capacity',
      all: 'Mọi sức chứa',
      options: [1, 2, 3, 4, 5, 6].map(n => ({
        value: String(n),
        label: `${n} khách`,
      })),
      get: r => String(r.capacity ?? ''),
    },
  ],

  columns: [
    { key: 'name', label: 'Loại phòng', strong: true },
    {
      key: 'capacity',
      label: 'Sức chứa',
      render: r => r.capacity != null ? `${r.capacity} khách` : '—',
      text: r => r.capacity ?? '',
    },
    {
      key: 'area',
      label: 'Diện tích',
      render: () => '—',
      text: () => '',
    },
    {
      key: 'price',
      label: 'Giá / đêm',
      render: r => r.price != null ? money(r.price) : '—',
      text: r => r.price ?? '',
    },
    { key: 'rooms', label: 'Số phòng' },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => (
        <StatusTag map={TYPE_STATUS} value={r.status} />
      ),
      text: r => TYPE_STATUS[r.status]?.label ?? '',
    },
  ],

  // Chưa có API thêm/sửa loại phòng.
  fields: [],
};

export default function RoomTypesPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadRoomTypes = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await apiClient.get('/api/rooms');

      if (!Array.isArray(response.data)) {
        throw new Error('Dữ liệu phòng từ API không hợp lệ.');
      }

      const rooms = response.data;

      // Gom các phòng theo room_type_id.
      const roomTypes = new Map();

      rooms.forEach(room => {
        const type = room.room_type;

        if (!type || type.room_type_id == null) return;

        const id = type.room_type_id;

        if (!roomTypes.has(id)) {
          roomTypes.set(id, {
            id,
            name: type.name ?? '',
            capacity: type.max_guests ?? null,
            area: null,
            price: type.base_price ?? null,
            rooms: 0,
            status: 'unknown',
          });
        }

        roomTypes.get(id).rooms += 1;
      });

      setRows(Array.from(roomTypes.values()));
    } catch (err) {
      console.error('Lỗi tải danh sách loại phòng:', err);

      setError(
        err.response?.data?.detail ||
        err.message ||
        'Không thể tải danh sách loại phòng từ API.'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRoomTypes();
  }, []);

  if (loading) {
    return (
      <div className="admin-dashboard">
        <p>Đang tải danh sách loại phòng...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <h2>Loại phòng</h2>
        <p role="alert">{error}</p>
        <button
          type="button"
          onClick={loadRoomTypes}
        >
          Thử tải lại
        </button>
      </div>
    );
  }

  return (
    <CrudPage
      config={{
        ...roomTypesConfig,
        rows,
      }}
    />
  );
}

