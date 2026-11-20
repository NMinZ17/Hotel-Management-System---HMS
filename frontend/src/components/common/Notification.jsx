import { useEffect } from 'react';
import './Notification.css';

function Notification({
  type = 'info',
  message = '',
  onClose,
  duration = 2500,
  autoClose = true,
}) {
  useEffect(() => {
    if (!message || !autoClose || !onClose) return;

    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [message, autoClose, onClose, duration]);

  if (!message) return null;

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };

  const safeType = icons[type] ? type : 'info';

  return (
    <div
      className={`notification notification--${safeType}`}
      role={safeType === 'error' ? 'alert' : 'status'}
    >
      <span className="notification__icon">
        {icons[safeType]}
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