export default function StaffDataTable({
  columns = [],
  data = [],
  loading = false,
  error = '',
  emptyText = 'Không có dữ liệu.',
  rowKey = 'id',
}) {
  if (loading) return <p>Đang tải dữ liệu...</p>;
  if (error) return <p className="staff-error">{error}</p>;

  return (
    <div className="staff-table-wrapper">
      <table className="staff-data-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="staff-empty">
                {emptyText}
              </td>
            </tr>
          ) : (
            data.map((item, index) => (
              <tr key={item[rowKey] ?? item.room_id ?? index}>
                {columns.map((column) => (
                  <td key={column.key}>
                    {column.render
                      ? column.render(item)
                      : item[column.key] ?? '-'}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}