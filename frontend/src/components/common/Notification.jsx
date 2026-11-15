
import './Notification.css';

function Notification({
  type = 'info',
  message = '',
  onClose,
}) {
  if (!message) return null;

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  return (
    <div
      className={`notification notification--${type}`}
      role="alert"
    >
      <span className="notification__icon">
        {icons[type] || icons.info}
      </span>

      <span className="notification__message">
        {message}
      </span>

      {onClose && (
        <button
          type="button"
          className="notification__close"
          onClick={onClose}
          aria-label="Đóng thông báo"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default Notification;
