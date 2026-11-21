const STATUS_LABELS = {
  available: 'Còn trống',
  occupied: 'Đang có khách',
  cleaning: 'Đang dọn',
  maintenance: 'Đang bảo trì',
  clean: 'Đã dọn',
  dirty: 'Chưa dọn',
  pending: 'Đang chờ',
  confirmed: 'Đã xác nhận',
  cancelled: 'Đã hủy',
};

export default function StaffStatusTag({ status }) {
  const value = String(status || '').toLowerCase();
  const label = STATUS_LABELS[value] || status || 'Chưa có dữ liệu';

  return (
    <span className={`staff-status staff-status-${value || 'unknown'}`}>
      {label}
    </span>
  );
}