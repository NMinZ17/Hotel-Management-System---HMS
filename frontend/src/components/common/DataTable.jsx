
import './DataTable.css';

function DataTable({
  columns = [],
  data = [],
  loading = false,
  error = null,
}) {
  // Trường hợp đang tải dữ liệu
  if (loading) {
    return (
      <div className="data-table-message">
        Đang tải dữ liệu...
      </div>
    );
  }

  // Trường hợp xảy ra lỗi
  if (error) {
    return (
      <div className="data-table-message data-table-error">
        {error}
      </div>
    );
  }

  // Trường hợp không có dữ liệu
  if (data.length === 0) {
    return (
      <div className="data-table-message">
        Không có dữ liệu
      </div>
    );
  }

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>
                {column.label}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, index) => (
            <tr key={row.id ?? index}>
              {columns.map((column) => (
                <td key={column.key}>
                  {column.render
                    ? column.render(row[column.key], row)
                    : row[column.key] ?? '—'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
