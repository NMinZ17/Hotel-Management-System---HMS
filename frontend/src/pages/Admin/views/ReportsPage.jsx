
import { PageHead, Stat } from '../common/ui.jsx';

export default function ReportsPage() {
  return (
    <div className="admin-dashboard">
      <PageHead
        title="Báo cáo"
        subtitle="Tổng hợp doanh thu, công suất phòng và nguồn đặt phòng."
      >
        <button
          type="button"
          className="dashboard-button"
          disabled
          title="Chưa có dữ liệu báo cáo để xuất"
        >
          Xuất báo cáo
        </button>
      </PageHead>

      <section className="dashboard-statistics" aria-label="Chỉ số chính">
        <Stat
          label="Tổng doanh thu"
          value="--"
          note="Chưa có dữ liệu"
        />
        <Stat
          label="Công suất trung bình"
          value="--"
          note="Chưa có dữ liệu"
        />
        <Stat
          label="Giá phòng trung bình"
          value="--"
          note="Chưa có dữ liệu"
        />
        <Stat
          label="RevPAR"
          value="--"
          note="Chưa có dữ liệu"
        />
      </section>

      <section className="dashboard-middle">
        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Doanh thu theo tháng</h2>
              <p className="panel-subtitle">
                Chưa có dữ liệu doanh thu
              </p>
            </div>
            <span className="chart-legend">Doanh thu</span>
          </header>

          <div className="report-empty">
            <strong>Chưa có dữ liệu doanh thu</strong>
            <p>
              Biểu đồ sẽ được cập nhật khi có API thống kê doanh thu.
            </p>
          </div>
        </article>

        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Doanh thu theo loại phòng</h2>
              <p className="panel-subtitle">
                Tỷ trọng trong tổng doanh thu
              </p>
            </div>
          </header>

          <div className="report-empty">
            <strong>Chưa có dữ liệu</strong>
            <p>
              Chưa có dữ liệu doanh thu theo loại phòng.
            </p>
          </div>
        </article>
      </section>

      <section className="dashboard-bottom">
        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Doanh thu theo quý</h2>
              <p className="panel-subtitle">
                So sánh với quý liền trước
              </p>
            </div>
          </header>

          <div className="table-scroll">
            <table className="activity-table">
              <thead>
                <tr>
                  <th scope="col">Quý</th>
                  <th scope="col">Doanh thu</th>
                  <th scope="col">So với quý trước</th>
                </tr>
              </thead>

              <tbody>
                <tr>
                  <td colSpan={3} className="cell-muted">
                    Chưa có dữ liệu báo cáo
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article className="dashboard-panel">
          <header className="panel-header">
            <div>
              <h2 className="panel-title">Nguồn đặt phòng</h2>
              <p className="panel-subtitle">
                Tỷ lệ theo kênh bán
              </p>
            </div>
          </header>

          <div className="report-empty">
            <strong>Chưa có dữ liệu</strong>
            <p>
              Chưa có dữ liệu thống kê theo nguồn đặt phòng.
            </p>
          </div>
        </article>
      </section>
    </div>
  );
}

