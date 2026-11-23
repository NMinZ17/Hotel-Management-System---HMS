import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './StaffLayout.css';

const menuItems = [
  { path: '/staff', label: 'Tổng quan', end: true, icon: '⌂' },
  { path: '/staff/rooms', label: 'Danh sách phòng', icon: '▣' },
  { path: '/staff/guests', label: 'Khách hàng', icon: '♙' },
  { path: '/staff/bookings', label: 'Đặt phòng', icon: '▦' },
  { path: '/staff/housekeeping', label: 'Tình trạng phòng', icon: '✧' },
];

export default function StaffLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="staff-layout">
      <aside className="staff-sidebar">
        <div className="staff-brand">
          <strong>HMS</strong>
          <span>HOTEL MANAGEMENT</span>
        </div>

        <div className="staff-menu-title">NHÂN VIÊN</div>

        <nav className="staff-nav">
          {menuItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              className={({ isActive }) =>
                `staff-nav-link ${isActive ? 'active' : ''}`
              }
            >
              <span className="staff-nav-icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="staff-sidebar-footer">
          <span>Staff Portal</span>
          <small>Hotel Management System</small>
        </div>
      </aside>

      <div className="staff-main">
        <header className="staff-topbar">
          <div>
            <strong>Hệ thống nhân viên</strong>
            <span>Quản lý và tra cứu thông tin khách sạn</span>
          </div>

          <div className="staff-account">
            <div className="staff-avatar">NV</div>
            <div>
              <strong>
                {user?.full_name || user?.email || 'Nhân viên'}
              </strong>
              <small>Staff</small>
            </div>

            {isAuthenticated && (
              <button onClick={handleLogout} className="staff-logout">
                Đăng xuất
              </button>
            )}
          </div>
        </header>

        <main className="staff-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}