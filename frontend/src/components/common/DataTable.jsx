import { useEffect, useState } from 'react';
import './DataTable.css';

function DataTable({
  columns = [],
  data = [],
  loading = false,
  error = null,
  pageSize = 5,
  loadingText = 'Đang tải dữ liệu...',
  emptyMessage = 'Không tìm thấy dữ liệu phù hợp với yêu cầu',
  hasActiveFilters = false,
  onClearFilters,
}) {
  const [currentPage, setCurrentPage] = useState(1);

  const safeData = Array.isArray(data) ? data : [];
  const safePageSize = Math.max(1, pageSize);
  const totalPages = Math.max(1, Math.ceil(safeData.length / safePageSize));

  useEffect(() => {
    setCurrentPage(1);
  }, [data, pageSize]);

  const pageData = safeData.slice(
    (currentPage - 1) * safePageSize,
    currentPage * safePageSize
  );

  if (loading) {
    return (
      <div className="data-table-message" role="status">
        {loadingText}
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-table-message data-table-error" role="alert">
        <strong>Có lỗi xảy ra</strong>
        <p>{error}</p>
      </div>
    );
  }

  if (safeData.length === 0) {
    return (
      <div className="data-table-message">
        <p>{emptyMessage}</p>

        {hasActiveFilters && onClearFilters && (
          <button
            type="button"
            className="data-table-clear"
            onClick={onClearFilters}
          >
            Xóa bộ lọc
          </button>
        )}
      </div>
    );
  }

  return (
    <div>
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
            {pageData.map((row, index) => (
              <tr key={row.id ?? row.room_id ?? row.booking_id ?? index}>
                {columns.map((column) => {
                  const value = row[column.key];

                  const isNumber =
                    column.align === 'right' ||
                    (column.align !== 'left' &&
                      typeof value === 'number');

                  return (
                    <td
                      key={column.key}
                      className={isNumber ? 'data-table__number' : ''}
                    >
                      {column.render
                        ? column.render(value, row)
                        : value ?? '—'}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {safeData.length > safePageSize && (
        <div className="data-table-pagination">
          <button
            type="button"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((page) => page - 1)}
          >
            Trang trước
          </button>

          <span>
            Trang {currentPage} / {totalPages}
          </span>

          <button
            type="button"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((page) => page + 1)}
          >
            Trang sau
          </button>
        </div>
      )}
    </div>
  );
}

export default DataTable;