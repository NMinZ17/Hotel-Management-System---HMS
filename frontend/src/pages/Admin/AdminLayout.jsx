import { useState } from 'react';
import './AdminLayout.css';

/* Menu + icons */
const menuItems = [
  { id: 'dashboard', label: 'Tổng quan', icon: 'grid' },
  { id: 'rooms', label: 'Quản lý phòng', icon: 'bed' },
  { id: 'room-types', label: 'Loại phòng', icon: 'layers' },
  { id: 'amenities', label: 'Tiện nghi', icon: 'star' },
  { id: 'bookings', label: 'Đặt phòng', icon: 'calendar' },
  { id: 'guests', label: 'Khách hàng', icon: 'users' },
  { id: 'housekeeping', label: 'Buồng phòng', icon: 'brush' },
  { id: 'staff', label: 'Nhân viên', icon: 'user' },
  { id: 'reports', label: 'Báo cáo', icon: 'chart' },
  { id: 'settings', label: 'Cài đặt', icon: 'settings' },
];

const iconPaths = {
  grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  bed: <><path d="M3 18V6"/><path d="M3 14h18v4"/><path d="M5 14V9h6a3 3 0 0 1 3 3v2"/><path d="M14 11h5a2 2 0 0 1 2 2v1"/></>,
  layers: <><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5"/><path d="m3 16 9 5 9-5"/></>,
  star: <><path d="m12 3 2.7 5.5 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1-4.4-4.3 6.1-.9L12 3Z"/></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M20 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></>,
  brush: <><path d="m14 6 4 4"/><path d="m5 21 9-9 4 4-9 9H5z"/><path d="m14 6 3-3 4 4-3 3"/></>,
  user: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
  chart: <><path d="M3 3v18h18"/><path d="m8 15 4-4 4 3 5-7"/></>,
  settings: <><circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.4 1.1-1.4 2.4-1.7-.7a8 8 0 0 1-1.7 1l-.3 1.8h-2.8l-.3-1.8a8 8 0 0 1-1.7-1l-1.7.7-1.4-2.4 1.4-1.1a8 8 0 0 1 0-2l-1.4-1.1 1.4-2.4 1.7.7a8 8 0 0 1 1.7-1l.3-1.8h2.8l.3 1.8a8 8 0 0 1 1.7 1l1.7-.7 1.4 2.4-1.4 1.1a8 8 0 0 1 0 2Z"/></>,
  panel: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></>,
  bell: <><path d="M6 9a6 6 0 0 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9Z"/><path d="M10 20a2 2 0 0 0 4 0"/></>,
  chevron: <><path d="m6 9 6 6 6-6"/></>,
  help: <><circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7"/><path d="M12 17h.01"/></>,
  download: <><path d="M12 4v11"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/></>,
  arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
  check: <><path d="m5 12 5 5 9-10"/></>,
};

function Icon({ name, size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {iconPaths[name]}
    </svg>
  );
}

/* Nút liên kết nhỏ có mũi tên – dùng chung cho thẻ và tiêu đề khối */
function PageLink({ children, onClick }) {
  return (
    <button type="button" className="link-button" onClick={onClick} disabled={!onClick}>
      {children}
      <Icon name="arrow" size={14} />
    </button>
  );
}

function StatCard({ icon, tone, label, note, linkLabel, onLink }) {
  return (
    <article className="dashboard-card stat-card stat-card--link">
      <span className={`stat-icon stat-icon--${tone}`} aria-hidden="true">
        <Icon name={icon} size={20} />
      </span>
      <span className="stat-label">{label}</span>
      <strong className="stat-value">--</strong>
      <div className="stat-foot">
        <span>{note}</span>
      </div>
      <PageLink onClick={onLink}>{linkLabel}</PageLink>
    </article>
  );
}

/* Biểu đồ doanh thu: trạng thái chưa có dữ liệu */
function RevenueChart() {
  return (
    <div className="revenue-empty">
      <strong>Chưa có dữ liệu doanh thu</strong>
      <p>Biểu đồ sẽ được cập nhật khi có API thống kê doanh thu.</p>
    </div>
  );
}

/* Biểu đồ tình trạng phòng: trạng thái chưa có dữ liệu */
function RoomDonut() {
  return (
    <div className="occupancy-body">
      <div className="occupancy-circle">
        <span>--</span>
        <small>Chưa có dữ liệu</small>
      </div>
      <ul className="occupancy-legend">
        <li>Chưa có dữ liệu tình trạng phòng</li>
      </ul>
    </div>
  );
}

/* Dashboard
   onNavigate(id): chuyển sang trang có id trùng với menuItems */
export function AdminDashboard({ onNavigate, onExport, onViewAllActivities }) {
  const go = id => (onNavigate ? () => onNavigate(id) : undefined);

  return (
    <div className="admin-dashboard">
      <section className="dashboard-head">
        <div>
          <h1 className="dashboard-title">Tổng quan khách sạn</h1>
          <p className="dashboard-subtitle">
            Tình hình hoạt động của khách sạn.
          </p>
        </div>

        <div className="dashboard-actions">
          <button
            type="button"
            className="dashboard-button"
            onClick={onExport}
            disabled={!onExport}
          >
            <Icon name="download" size={15} />
            Xuất báo cáo
          </button>
        </div>
      </section>

      <section className="dashboard-statistics" aria-label="Thống kê nhanh">
        <StatCard
          icon="bed"
          tone="teal"
          label="Tổng số phòng"
          note="Chưa có dữ liệu"
          linkLabel="Xem danh sách phòng"
          onLink={go('rooms')}
        />
        <StatCard
          icon="users"
          tone="amber"
          label="Phòng có khách"
          note="Chưa có dữ liệu công suất"
          linkLabel="Xem đặt phòng"
          onLink={go('bookings')}
        />
        <StatCard
          icon="check"
          tone="green"
          label="Phòng trống"
          note="Chưa có dữ liệu"
          linkLabel="Tra cứu phòng"
          onLink={go('rooms')}
        />
        <StatCard
          icon="chart"
          tone="violet"
          label="Tổng doanh thu"
          note="Chưa có dữ liệu doanh thu"
          linkLabel="Xem báo cáo"
          onLink={go('reports')}
        />
      </section>

      <section className="dashboard-middle">
        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Doanh thu theo thời gian</h2>
              <p className="panel-subtitle">Chưa có dữ liệu doanh thu</p>
            </div>
            <div className="panel-links">
              <span className="chart-legend">Doanh thu</span>
              <PageLink onClick={go('reports')}>Xem báo cáo</PageLink>
            </div>
          </header>
          <RevenueChart />
        </article>

        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Tình trạng phòng</h2>
              <p className="panel-subtitle">Chưa có dữ liệu phòng</p>
            </div>
            <PageLink onClick={go('rooms')}>Quản lý phòng</PageLink>
          </header>
          <RoomDonut />
        </article>
      </section>

      <section className="dashboard-bottom">
        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Hoạt động gần đây</h2>
              <p className="panel-subtitle">Các hoạt động mới nhất trong khách sạn</p>
            </div>
            <PageLink onClick={onViewAllActivities ?? go('housekeeping')}>
              Xem tất cả
            </PageLink>
          </header>

          <div className="table-scroll">
            <table className="activity-table">
              <thead>
                <tr>
                  <th scope="col">Giờ</th>
                  <th scope="col">Hoạt động</th>
                  <th scope="col">Khách / nhân viên</th>
                  <th scope="col">Phòng</th>
                  <th scope="col">Trạng thái</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan={5} className="cell-muted">
                    Chưa có dữ liệu hoạt động
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Thống kê đặt phòng</h2>
              <p className="panel-subtitle">Tình hình đặt phòng</p>
            </div>
            <PageLink onClick={go('bookings')}>Xem đặt phòng</PageLink>
          </header>

          <div className="booking-hero">
            <strong>--</strong>
            <span>Lượt đặt phòng</span>
          </div>
          <p className="booking-trend">Chưa có dữ liệu đặt phòng</p>

          <dl className="booking-grid">
            <div>
              <dt>Đã nhận phòng</dt>
              <dd>--</dd>
            </div>
            <div>
              <dt>Dự kiến đến</dt>
              <dd>--</dd>
            </div>
            <div>
              <dt>Trả phòng</dt>
              <dd>--</dd>
            </div>
            <div>
              <dt>Đã hủy</dt>
              <dd>--</dd>
            </div>
          </dl>
        </article>
      </section>
    </div>
  );
}

/* Layout
   - Sidebar mặc định thu gọn; bấm icon là chuyển trang ngay.
   - Chỉ nút "Thu gọn / Mở rộng menu" mới đổi trạng thái sidebar. */
export default function AdminLayout({
  activePage = 'dashboard',
  onNavigate,
  children,
}) {
  const [expanded, setExpanded] = useState(false);

  const activeItem = menuItems.find(item => item.id === activePage);

  return (
    <div className={`admin-layout ${expanded ? 'sidebar-open' : ''}`}>
      <aside
        className={`admin-sidebar ${expanded ? 'expanded' : ''}`}
        aria-label="Thanh điều hướng"
      >
        <div className="admin-brand">
          <div className="admin-brand-logo">HMS</div>
          <span className="admin-brand-subtitle">HOTEL MANAGEMENT</span>
        </div>

        <button
          type="button"
          className="admin-menu-toggle"
          onClick={() => setExpanded(!expanded)}
          aria-label={expanded ? 'Thu gọn menu' : 'Mở rộng menu'}
          aria-expanded={expanded}
        >
          <span className="admin-nav-icon">
            <Icon name="panel" size={20} />
          </span>
          <span className="admin-nav-label">Thu gọn menu</span>
        </button>

        <div className="admin-menu-label">QUẢN LÝ KHÁCH SẠN</div>

        <nav className="admin-nav" aria-label="Menu chính">
          {menuItems.map(item => (
            <button
              type="button"
              key={item.id}
              className={`admin-nav-item ${activePage === item.id ? 'active' : ''}`}
              aria-current={activePage === item.id ? 'page' : undefined}
              onClick={() => onNavigate?.(item.id)}
              title={!expanded ? item.label : undefined}
            >
              <span className="admin-nav-icon">
                <Icon name={item.icon} />
              </span>
              <span className="admin-nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="admin-sidebar-footer">
          <button
            type="button"
            className="admin-nav-item"
            title={!expanded ? 'Trợ giúp' : undefined}
          >
            <span className="admin-nav-icon">
              <Icon name="help" />
            </span>
            <span className="admin-nav-label">Trợ giúp &amp; hỗ trợ</span>
          </button>

          {!expanded ? (
            <div className="admin-hotel-short">HMS</div>
          ) : (
            <div className="admin-hotel-card">
              <strong>Khách sạn</strong>
              <span>Thông tin chưa được cấu hình</span>
            </div>
          )}
        </div>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <div className="admin-breadcrumb">
            {activeItem?.label || 'Quản trị'}
          </div>

          <div className="admin-topbar-right">
            <label className="admin-search">
              <Icon name="search" size={16} />
              <input
                type="search"
                placeholder="Tìm phòng, khách, đặt phòng..."
                aria-label="Tìm kiếm"
              />
            </label>

            <button
              type="button"
              className="admin-icon-button"
              aria-label="Thông báo"
            >
              <Icon name="bell" size={19} />
            </button>

            <span className="admin-hotel-name">HMS</span>

            <div className="admin-user">
              <div className="admin-avatar">--</div>
              <div className="admin-user-text">
                <strong>Tài khoản</strong>
                <small>Chưa có thông tin</small>
              </div>
              <Icon name="chevron" size={14} />
            </div>
          </div>
        </header>

        <main className="admin-content">
          {children ??
            (activePage === 'dashboard' ? (
              <AdminDashboard onNavigate={onNavigate} />
            ) : null)}
        </main>
      </div>
    </div>
  );
}