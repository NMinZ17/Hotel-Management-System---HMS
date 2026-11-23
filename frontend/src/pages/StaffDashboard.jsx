import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomApi } from '../lib/api';

export default function StaffDashboard() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 5 bộ lọc tương ứng thiết kế Staff/Lễ tân: Tầng, Loại phòng, Số phòng, Giá tiền, Tình trạng
  const [floorFilter, setFloorFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [roomNumberQuery, setRoomNumberQuery] = useState('');
  const [priceSort, setPriceSort] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const response = await roomApi.getAll();
        const list = Array.isArray(response) ? response : response?.data || [];
        setRooms(list);
      } catch (err) {
        setError('Không thể tải dữ liệu phòng cho Staff dashboard.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRooms();
  }, []);

  const floors = useMemo(() => {
    return Array.from(new Set(rooms.map((r) => r.floor).filter((f) => f !== null))).sort(
      (a, b) => a - b
    );
  }, [rooms]);

  const roomTypes = useMemo(() => {
    return Array.from(new Set(rooms.map((r) => r.room_type?.name).filter(Boolean)));
  }, [rooms]);

  const filteredRooms = useMemo(() => {
    let list = [...rooms];

    if (floorFilter !== 'ALL') {
      list = list.filter((r) => String(r.floor) === String(floorFilter));
    }

    if (typeFilter !== 'ALL') {
      list = list.filter((r) => r.room_type?.name === typeFilter);
    }

    if (roomNumberQuery.trim()) {
      const q = roomNumberQuery.toLowerCase();
      list = list.filter((r) => (r.room_number || '').toLowerCase().includes(q));
    }

    if (statusFilter !== 'ALL') {
      list = list.filter(
        (r) =>
          (r.housekeeping_status || '').toLowerCase() === statusFilter.toLowerCase() ||
          (r.maintenance_status || '').toLowerCase() === statusFilter.toLowerCase()
      );
    }

    if (priceSort === 'ASC') {
      list.sort(
        (a, b) => Number(a.room_type?.base_price || 0) - Number(b.room_type?.base_price || 0)
      );
    } else if (priceSort === 'DESC') {
      list.sort(
        (a, b) => Number(b.room_type?.base_price || 0) - Number(a.room_type?.base_price || 0)
      );
    }

    return list;
  }, [rooms, floorFilter, typeFilter, roomNumberQuery, priceSort, statusFilter]);

  const handleLogout = () => {
    localStorage.removeItem('hms_staff_user');
    navigate('/rooms');
  };

  return (
    <div>
      {/* HEADER STAFF DASHBOARD */}
      <header className="staff-header">
        <h1>Staff dashboard</h1>
        <button type="button" className="header-login-btn" onClick={handleLogout}>
          Log out
        </button>
      </header>

      <main className="main-container">
        {/* 5 BỘ LỌC THEO CỘT CỦA FIGMA */}
        <section className="staff-filters-bar">
          <div className="staff-filter-item">
            <span>Tầng</span>
            <select value={floorFilter} onChange={(e) => setFloorFilter(e.target.value)}>
              <option value="ALL">Tất cả tầng</option>
              {floors.map((fl) => (
                <option key={fl} value={fl}>
                  Tầng {fl}
                </option>
              ))}
            </select>
          </div>

          <div className="staff-filter-item">
            <span>Loại phòng</span>
            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
              <option value="ALL">Tất cả loại phòng</option>
              {roomTypes.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          <div className="staff-filter-item">
            <span>Số phòng</span>
            <input
              type="text"
              placeholder="VD: 101..."
              value={roomNumberQuery}
              onChange={(e) => setRoomNumberQuery(e.target.value)}
            />
          </div>

          <div className="staff-filter-item">
            <span>Giá tiền</span>
            <select value={priceSort} onChange={(e) => setPriceSort(e.target.value)}>
              <option value="ALL">Mặc định</option>
              <option value="ASC">Thấp → Cao</option>
              <option value="DESC">Cao → Thấp</option>
            </select>
          </div>

          <div className="staff-filter-item">
            <span>Tình trạng</span>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="ALL">Tất cả trạng thái</option>
              <option value="CLEAN">CLEAN (Sạch)</option>
              <option value="DIRTY">DIRTY (Cần dọn)</option>
              <option value="OK">OK (Hoạt động tốt)</option>
              <option value="MAINTENANCE">MAINTENANCE (Bảo trì)</option>
            </select>
          </div>
        </section>

        {/* BẢNG DANH SÁCH PHÒNG */}
        {loading && <p>Đang tải dữ liệu phòng...</p>}
        {error && <p style={{ color: '#dc2626' }}>{error}</p>}

        {!loading && !error && (
          <div className="staff-table-wrapper">
            <table className="staff-table">
              <thead>
                <tr>
                  <th>Tầng</th>
                  <th>Loại phòng</th>
                  <th>Số phòng</th>
                  <th>Giá tiền</th>
                  <th>Tình trạng (Dọn dẹp / Bảo trì)</th>
                </tr>
              </thead>
              <tbody>
                {filteredRooms.length === 0 ? (
                  <tr>
                    <td colSpan={5} style={{ textAlign: 'center', padding: 24 }}>
                      Không có phòng nào phù hợp bộ lọc.
                    </td>
                  </tr>
                ) : (
                  filteredRooms.map((room) => {
                    const hk = (room.housekeeping_status || 'N/A').toUpperCase();
                    const mt = (room.maintenance_status || 'N/A').toUpperCase();
                    return (
                      <tr key={room.room_id}>
                        <td>Tầng {room.floor ?? '-'}</td>
                        <td>
                          <strong>{room.room_type?.name || 'N/A'}</strong>
                          <div style={{ fontSize: 12, color: '#4b5563' }}>
                            Tối đa {room.room_type?.max_guests ?? 2} khách
                          </div>
                        </td>
                        <td>
                          <strong>{room.room_number}</strong>
                        </td>
                        <td>
                          {Number(room.room_type?.base_price || 0).toLocaleString('vi-VN')} VNĐ
                        </td>
                        <td>
                          <span
                            className={`status-badge ${
                              hk === 'CLEAN' ? 'status-clean' : 'status-dirty'
                            }`}
                          >
                            {hk}
                          </span>
                          <span
                            className={`status-badge ${
                              mt === 'OK' || mt === 'NONE' ? 'status-ok' : 'status-warn'
                            }`}
                          >
                            {mt}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}