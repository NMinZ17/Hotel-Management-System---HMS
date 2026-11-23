
import Reveal from '../../components/common/Reveal';
import './AdminDashboard.css';

const statistics = [
  {
    label: 'Tổng số phòng',
    value: '--',
    note: 'Tổng phòng trong khách sạn',
  },
  {
    label: 'Phòng đang sử dụng',
    value: '--',
    note: 'Đang có khách lưu trú',
  },
  {
    label: 'Phòng còn trống',
    value: '--',
    note: 'Sẵn sàng đón khách',
  },
  {
    label: 'Tổng doanh thu',
    value: '--',
    note: 'Doanh thu trong kỳ',
  },
];

export default function AdminDashboard() {
  return (
    <div className="admin-dashboard">
      <Reveal>
        <div className="dashboard-heading">
          <div>
            <h1>Tổng quan khách sạn</h1>
            <p>Chào mừng bạn đến với hệ thống quản trị HMS.</p>
          </div>

          <div className="dashboard-date">
            Bảng điều khiển quản trị
          </div>
        </div>
      </Reveal>

      <div className="dashboard-statistics">
        {statistics.map((item, index) => (
          <Reveal key={item.label} delay={index * 90}>
            <div className="dashboard-card">
              <div className="dashboard-card-label">
                {item.label}
              </div>
              <strong className="dashboard-card-value">
                {item.value}
              </strong>
              <span className="dashboard-card-note">
                {item.note}
              </span>
            </div>
          </Reveal>
        ))}
      </div>

      <div className="dashboard-middle">
        <Reveal>
          <section className="dashboard-panel revenue-panel">
            <div className="panel-heading">
              <div>
                <h2>Doanh thu</h2>
                <p>Theo dõi doanh thu khách sạn</p>
              </div>
              <span className="panel-tag">Chưa có dữ liệu</span>
            </div>

            <div className="revenue-empty">
              <div className="revenue-empty-icon">↗</div>
              <strong>Chưa có dữ liệu doanh thu</strong>
              <p>
                Biểu đồ sẽ được cập nhật khi có API thống kê doanh thu.
              </p>
            </div>
          </section>
        </Reveal>

        <Reveal delay={100}>
          <section className="dashboard-panel occupancy-panel">
            <div className="panel-heading">
              <div>
                <h2>Tình trạng phòng</h2>
                <p>Tỷ lệ sử dụng phòng</p>
              </div>
            </div>

            <div className="occupancy-empty">
              <div className="occupancy-circle">
                <span>--</span>
                <small>Đang cập nhật</small>
              </div>
              <div className="occupancy-legend">
                <span>● Đang sử dụng</span>
                <span>● Còn trống</span>
                <span>● Đang bảo trì</span>
              </div>
            </div>
          </section>
        </Reveal>
      </div>

      <div className="dashboard-bottom">
        <Reveal>
          <section className="dashboard-panel activity-panel">
            <div className="panel-heading">
              <div>
                <h2>Hoạt động gần đây</h2>
                <p>Các hoạt động mới nhất trong khách sạn</p>
              </div>
            </div>

            <div className="dashboard-table-wrapper">
              <table className="dashboard-table">
                <thead>
                  <tr>
                    <th>Thời gian</th>
                    <th>Hoạt động</th>
                    <th>Người thực hiện</th>
                    <th>Phòng</th>
                    <th>Trạng thái</th>
                  </tr>
                </thead>

                <tbody>
                  <tr>
                    <td colSpan={5} className="dashboard-empty-cell">
                      Chưa có dữ liệu hoạt động
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </Reveal>

        <Reveal delay={100}>
          <section className="dashboard-panel booking-panel">
            <div className="panel-heading">
              <div>
                <h2>Thống kê đặt phòng</h2>
                <p>Tình hình đặt phòng</p>
              </div>
            </div>

            <div className="booking-empty">
              <strong>--</strong>
              <span>Lượt đặt phòng</span>
              <p>Dữ liệu sẽ được cập nhật khi API sẵn sàng.</p>
            </div>
          </section>
        </Reveal>
      </div>
    </div>
  );
}
