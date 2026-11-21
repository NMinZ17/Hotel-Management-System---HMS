
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { roomApi } from '../../../lib/api';
import StaffStatusTag from '../common/StaffStatusTag.jsx';

const shortcuts = [
  {
    icon: '▦',
    title: 'Danh sách phòng',
    description: 'Tra cứu phòng, tầng và trạng thái hiện tại.',
    path: '/staff/rooms',
    color: 'blue',
  },
  {
    icon: '♙',
    title: 'Khách hàng',
    description: 'Tra cứu thông tin khách lưu trú.',
    path: '/staff/guests',
    color: 'purple',
  },
  {
    icon: '▣',
    title: 'Đặt phòng',
    description: 'Theo dõi thông tin đặt phòng.',
    path: '/staff/bookings',
    color: 'orange',
  },
  {
    icon: '✧',
    title: 'Tình trạng phòng',
    description: 'Theo dõi thông tin dọn dẹp và bảo trì.',
    path: '/staff/housekeeping',
    color: 'green',
  },
];

export default function StaffDashboard() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    async function loadRooms() {
      try {
        setLoading(true);
        setError('');

        const response = await roomApi.getAll();
        const data = response.data;
        const list = Array.isArray(data)
          ? data
          : data?.items ?? data?.rooms ?? [];

        if (mounted) setRooms(list);
      } catch (err) {
        if (mounted) {
          setError(err.message || 'Không thể tải danh sách phòng.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadRooms();

    return () => {
      mounted = false;
    };
  }, []);

  const roomStats = useMemo(() => {
    const getStatus = (room) =>
      String(room.status || '').toLowerCase();

    return {
      total: rooms.length,
      available: rooms.filter((room) =>
        ['available', 'vacant'].includes(getStatus(room))
      ).length,
      occupied: rooms.filter((room) =>
        ['occupied', 'booked'].includes(getStatus(room))
      ).length,
      maintenance: rooms.filter((room) =>
        ['maintenance', 'repair'].includes(getStatus(room))
      ).length,
    };
  }, [rooms]);

  const statusItems = [
    { label: 'Còn trống', value: roomStats.available, color: 'available' },
    { label: 'Đang sử dụng', value: roomStats.occupied, color: 'occupied' },
    { label: 'Bảo trì', value: roomStats.maintenance, color: 'maintenance' },
  ];

  return (
    <div className="staff-dashboard">
      
    <section className="staff-welcome">
    <div>
        <span className="staff-welcome-label">
        HOTEL MANAGEMENT SYSTEM
        </span>
        <h1>Tổng quan nhân viên</h1>
        <p>
        Chào mừng bạn đến với hệ thống quản lý khách sạn.
        Theo dõi thông tin và tình hình hoạt động tại đây.
        </p>
        <Link to="/staff/rooms" className="staff-welcome-button">
        Xem danh sách phòng <span>→</span>
        </Link>
    </div>
    </section>


      <div className="staff-section-heading">
        <div>
          <h2>Tổng quan hoạt động</h2>
          <p>Các thông tin hiện có trong hệ thống</p>
        </div>
        <span className="staff-live-label">
          <span /> Dữ liệu phòng
        </span>
      </div>

      <section className="staff-stat-grid">
        <article className="staff-stat-card">
          <div className="staff-stat-icon blue">▦</div>
          <div className="staff-stat-label">Tổng số phòng</div>
          <div className="staff-stat-value">
            {loading ? '...' : roomStats.total}
          </div>
          <Link to="/staff/rooms">Xem danh sách <span>→</span></Link>
        </article>

        <article className="staff-stat-card">
          <div className="staff-stat-icon green">✓</div>
          <div className="staff-stat-label">Phòng còn trống</div>
          <div className="staff-stat-value">
            {loading ? '...' : roomStats.available}
          </div>
          <Link to="/staff/rooms">Tra cứu phòng <span>→</span></Link>
        </article>

        <article className="staff-stat-card">
          <div className="staff-stat-icon orange">♙</div>
          <div className="staff-stat-label">Phòng đang sử dụng</div>
          <div className="staff-stat-value">
            {loading ? '...' : roomStats.occupied}
          </div>
          <Link to="/staff/rooms">Xem chi tiết <span>→</span></Link>
        </article>

        <article className="staff-stat-card">
          <div className="staff-stat-icon purple">⚙</div>
          <div className="staff-stat-label">Phòng bảo trì</div>
          <div className="staff-stat-value">
            {loading ? '...' : roomStats.maintenance}
          </div>
          <Link to="/staff/housekeeping">Theo dõi <span>→</span></Link>
        </article>
      </section>

      {error && (
        <div className="staff-dashboard-error">
          {error}
          <button onClick={() => window.location.reload()}>
            Thử lại
          </button>
        </div>
      )}

      <section className="staff-dashboard-content">
        <div className="staff-dashboard-panel">
          <div className="staff-panel-heading">
            <div>
              <h2>Trạng thái phòng</h2>
              <p>Tổng hợp theo dữ liệu phòng hiện có</p>
            </div>
            <Link to="/staff/rooms">Chi tiết →</Link>
          </div>

          {loading ? (
            <p className="staff-muted">Đang tải dữ liệu...</p>
          ) : (
            <>
              <div className="staff-status-total">
                <strong>{roomStats.total}</strong>
                <span>Tổng số phòng</span>
              </div>

              <div className="staff-status-list">
                {statusItems.map((item) => (
                  <div className="staff-status-row" key={item.label}>
                    <div className="staff-status-row-label">
                      <span className={`staff-dot ${item.color}`} />
                      {item.label}
                    </div>
                    <strong>{item.value}</strong>
                  </div>
                ))}
              </div>

              {rooms.length === 0 && (
                <p className="staff-muted">Chưa có dữ liệu phòng.</p>
              )}
            </>
          )}
        </div>

        <div className="staff-dashboard-panel">
          <div className="staff-panel-heading">
            <div>
              <h2>Truy cập nhanh</h2>
              <p>Các chức năng dành cho nhân viên</p>
            </div>
          </div>

          <div className="staff-shortcut-list">
            {shortcuts.map((item) => (
              <Link
                to={item.path}
                className="staff-shortcut"
                key={item.path}
              >
                <div className={`staff-shortcut-icon ${item.color}`}>
                  {item.icon}
                </div>
                <div className="staff-shortcut-info">
                  <strong>{item.title}</strong>
                  <span>{item.description}</span>
                </div>
                <span className="staff-shortcut-arrow">→</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="staff-dashboard-note">
        <div className="staff-note-icon">i</div>
        <div>
          <strong>Lưu ý về dữ liệu hệ thống</strong>
          <p>
            Thông tin phòng được tải từ API hiện có. Các chức năng
            khách hàng, đặt phòng và dọn dẹp/bảo trì sẽ hiển thị dữ liệu
            khi backend cung cấp endpoint tương ứng.
          </p>
        </div>
      </section>
    </div>
  );
}
