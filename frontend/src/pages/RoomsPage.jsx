import { useEffect, useState } from 'react';
import { roomApi } from '../lib/api';

const RoomsPage = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const response = await roomApi.getAll();
        setRooms(response.data);
      } catch (err) {
        setError('Không thể tải danh sách phòng. Vui lòng thử lại sau.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRooms();
  }, []);

  if (loading) return <div style={{ padding: 20 }}>Đang tải dữ liệu phòng...</div>;
  if (error) return <div style={{ padding: 20, color: 'red' }}>{error}</div>;
  if (rooms.length === 0) return <div style={{ padding: 20 }}>Không có phòng nào.</div>;

  return (
    <div style={{ padding: 20 }}>
      <h2>Danh sách phòng</h2>
      <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Số phòng</th>
            <th>Tầng</th>
            <th>Loại phòng</th>
            <th>Giá cơ bản</th>
            <th>Trạng thái dọn dẹp</th>
            <th>Trạng thái bảo trì</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((room) => (
            <tr key={room.room_id}>
              <td>{room.room_id}</td>
              <td>{room.room_number}</td>
              <td>{room.floor}</td>
              <td>{room.room_type?.name || 'N/A'}</td>
              <td>{Number(room.room_type?.base_price || 0).toLocaleString('vi-VN')} VNĐ</td>
              <td>{room.housekeeping_status}</td>
              <td>{room.maintenance_status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RoomsPage;