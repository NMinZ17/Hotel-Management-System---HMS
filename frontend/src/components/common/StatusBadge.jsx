
import './StatusBadge.css';

const statusConfig = {
  CONFIRMED: {
    label: 'Đã xác nhận',
    type: 'success',
  },
  PENDING: {
    label: 'Đang xử lý',
    type: 'warning',
  },
  CANCELLED: {
    label: 'Đã hủy',
    type: 'danger',
  },
  CLEAN: {
    label: 'Sạch',
    type: 'success',
  },
  DIRTY: {
    label: 'Chưa dọn',
    type: 'warning',
  },
  CLEANING: {
    label: 'Đang dọn',
    type: 'info',
  },
  AVAILABLE: {
    label: 'Có thể sử dụng',
    type: 'success',
  },
  BLOCKED: {
    label: 'Đang bảo trì',
    type: 'danger',
  },
};

function StatusBadge({ status }) {
  const config = statusConfig[status] || {
    label: status || 'Không xác định',
    type: 'neutral',
  };

  return (
    <span className={`status-badge status-badge--${config.type}`}>
      {config.label}
    </span>
  );
}

export default StatusBadge;
