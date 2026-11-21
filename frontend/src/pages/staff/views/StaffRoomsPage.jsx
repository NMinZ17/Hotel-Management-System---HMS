import { useEffect, useMemo, useState } from 'react';
import { roomApi } from '../../../lib/api';
import StaffPageHead from '../common/StaffPageHead';
import StaffDataTable from '../common/StaffDataTable';

export default function StaffRoomsPage() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [keyword, setKeyword] = useState('');
  const [floor, setFloor] = useState('ALL');

  useEffect(() => {
    let active = true;

    roomApi.getAll()
      .then((res) => {
        const data = res?.data ?? res;
        const list = Array.isArray(data) ? data : data?.items ?? [];
        if (active) setRooms(list);
      })
      .catch((err) => {
        if (active) setError(err.message || 'Không tải được danh sách phòng.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, []);

  const floors = [...new Set(rooms.map((room) => room.floor).filter((v) => v != null))];

  const filteredRooms = useMemo(() => rooms.filter((room) => {
    const matchesKeyword = String(room.room_number || '')
      .toLowerCase().includes(keyword.trim().toLowerCase());
    const matchesFloor = floor === 'ALL' || String(room.floor) === floor;
    return matchesKeyword && matchesFloor;
  }), [rooms, keyword, floor]);

  const columns = [
    { key: 'room_number', label: 'Số phòng' },
    { key: 'floor', label: 'Tầng' },
    {
      key: 'room_type',
      label: 'Loại phòng',
      render: (room) => room.room_type?.name || 'Chưa có thông tin',
    },
    {
      key: 'max_guests',
      label: 'Sức chứa',
      render: (room) => room.room_type?.max_guests ?? '-',
    },
    {
      key: 'base_price',
      label: 'Giá cơ bản',
      render: (room) => room.room_type?.base_price != null
        ? `${Number(room.room_type.base_price).toLocaleString('vi-VN')} VNĐ`
        : '-',
    },
    {
      key: 'status',
      label: 'Trạng thái',
      render: (room) => room.status || 'Chưa có dữ liệu',
    },
  ];

  return (
    <div className="staff-page">
      <StaffPageHead
        title="Danh sách phòng"
        description="Tra cứu thông tin phòng và loại phòng."
      />

      <div className="staff-toolbar">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Tìm số phòng..."
        />

        <select value={floor} onChange={(e) => setFloor(e.target.value)}>
          <option value="ALL">Tất cả tầng</option>
          {floors.map((value) => (
            <option key={value} value={value}>Tầng {value}</option>
          ))}
        </select>
      </div>

      <StaffDataTable
        columns={columns}
        data={filteredRooms}
        loading={loading}
        error={error}
        rowKey="room_id"
        emptyText="Không tìm thấy phòng phù hợp."
      />
    </div>
  );
}