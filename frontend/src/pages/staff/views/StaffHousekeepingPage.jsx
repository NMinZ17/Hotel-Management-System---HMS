import { useEffect, useState } from 'react';
import { roomApi } from '../../../lib/api';
import StaffPageHead from '../common/StaffPageHead';
import StaffDataTable from '../common/StaffDataTable';
import StaffStatusTag from '../common/StaffStatusTag';

export default function StaffHousekeepingPage() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    roomApi.getAll()
      .then((res) => {
        const data = res?.data ?? res;
        const list = Array.isArray(data) ? data : data?.items ?? [];
        if (active) setRooms(list);
      })
      .catch((err) => {
        if (active) setError(err.message || 'Không tải được dữ liệu phòng.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, []);

  const columns = [
    { key: 'room_number', label: 'Số phòng' },
    {
      key: 'housekeeping_status',
      label: 'Tình trạng dọn dẹp',
      render: (room) => (
        <StaffStatusTag status={room.housekeeping_status} />
      ),
    },
    {
      key: 'maintenance_status',
      label: 'Tình trạng bảo trì',
      render: (room) => (
        <StaffStatusTag status={room.maintenance_status} />
      ),
    },
  ];

  return (
    <div className="staff-page">
      <StaffPageHead
        title="Tình trạng phòng"
        description="Theo dõi tình trạng dọn dẹp và bảo trì phòng."
      />

      <StaffDataTable
        columns={columns}
        data={rooms}
        loading={loading}
        error={error}
        rowKey="room_id"
        emptyText="Chưa có dữ liệu phòng."
      />

      {!loading && !error && rooms.length > 0 && (
        <p className="staff-muted">
          Nếu API chưa trả về trạng thái dọn dẹp hoặc bảo trì,
          hệ thống sẽ hiển thị “Chưa có dữ liệu”.
        </p>
      )}
    </div>
  );
}