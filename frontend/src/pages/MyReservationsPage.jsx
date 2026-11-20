import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { reservationApi } from '../lib/api';

export default function MyReservationsPage() {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState('');
  const [actionNotice, setActionNotice] = useState({ type: '', text: '' });

  // Chi tiết đơn đang xem
  const [selectedDetail, setSelectedDetail] = useState(null);
  const [loadingDetailId, setLoadingDetailId] = useState(null);

  // Hộp thoại xác nhận hủy đơn (ConfirmDialog theo Mục 8 UI Conventions)
  const [cancelingTarget, setCancelingTarget] = useState(null);
  const [cancelReason, setCancelReason] = useState('');
  const [submittingCancel, setSubmittingCancel] = useState(false);

  const isAuthenticated = Boolean(localStorage.getItem('token'));

  const fetchMyReservations = useCallback(async () => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setPageError('');
    try {
      const res = await reservationApi.getMyReservations();
      const list = Array.isArray(res.data) ? res.data : res.data?.items || [];
      setReservations(list);
    } catch (err) {
      setPageError(err.message || 'Không thể tải danh sách đơn đặt phòng.');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchMyReservations();
  }, [fetchMyReservations]);

  // Xem chi tiết đơn (xác minh quyền sở hữu dữ liệu từ backend)
  const handleViewDetail = async (reservationId) => {
    if (loadingDetailId) return;
    setActionNotice({ type: '', text: '' });
    setLoadingDetailId(reservationId);
    try {
      const res = await reservationApi.getById(reservationId);
      setSelectedDetail(res.data);
    } catch (err) {
      setSelectedDetail(null);
      setActionNotice({
        type: 'error',
        text: err.message || 'Không thể xem chi tiết đơn đặt phòng này.',
      });
    } finally {
      setLoadingDetailId(null);
    }
  };

  // Xác nhận hủy đặt phòng
  const handleConfirmCancel = async (e) => {
    e.preventDefault();
    if (submittingCancel || !cancelingTarget) return;

    setSubmittingCancel(true);
    setActionNotice({ type: '', text: '' });

    try {
      const res = await reservationApi.cancel(cancelingTarget.id, cancelReason.trim());
      const updatedOrder = res.data;

      setReservations((prev) =>
        prev.map((item) =>
          item.id === cancelingTarget.id
            ? { ...item, status: updatedOrder?.status || 'cancelled' }
            : item
        )
      );

      if (selectedDetail?.id === cancelingTarget.id) {
        setSelectedDetail((prev) => ({
          ...prev,
          status: updatedOrder?.status || 'cancelled',
        }));
      }

      setActionNotice({
        type: 'success',
        text: `Đã hủy đơn đặt phòng #${cancelingTarget.id} thành công.`,
      });
      setCancelingTarget(null);
      setCancelReason('');
    } catch (err) {
      setActionNotice({
        type: 'error',
        text: err.message || 'Không thể hủy đơn đặt phòng này.',
      });
    } finally {
      setSubmittingCancel(false);
    }
  };

  const canCancelStatus = (status) => {
    if (!status) return true;
    const normalized = String(status).toLowerCase();
    return !['cancelled', 'checked_out', 'completed'].includes(normalized);
  };

  if (!isAuthenticated) {
    return (
      <div style={{ maxWidth: 640, margin: '32px auto', padding: 20, border: '1px solid #ddd', borderRadius: 8 }}>
        <h1>Đơn đặt phòng của tôi</h1>
        <p>Bạn cần đăng nhập để xem và quản lý các đơn đặt phòng cá nhân.</p>
        <Link to="/login" style={{ color: '#1976d2', fontWeight: 600 }}>
          Đi đến trang Đăng nhập →
        </Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 960, margin: '24px auto', padding: '0 16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>Đơn đặt phòng của tôi</h1>
        <button
          type="button"
          onClick={fetchMyReservations}
          disabled={loading}
          style={{ padding: '8px 14px', cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          {loading ? 'Đang tải...' : 'Làm mới danh sách'}
        </button>
      </div>

      {/* Thông báo kết quả thao tác */}
      {actionNotice.text && (
        <div
          role={actionNotice.type === 'error' ? 'alert' : 'status'}
          style={{
            padding: 12,
            marginBottom: 16,
            borderRadius: 6,
            backgroundColor: actionNotice.type === 'error' ? '#ffebee' : '#e8f5e9',
            color: actionNotice.type === 'error' ? '#c62828' : '#2e7d32',
          }}
        >
          <strong>{actionNotice.type === 'error' ? 'Lỗi: ' : 'Thành công: '}</strong>
          {actionNotice.text}
        </div>
      )}

      {/* Trạng thái Loading / Error / Empty */}
      {loading && <p>Đang tải danh sách đơn đặt phòng...</p>}

      {!loading && pageError && (
        <div role="alert" style={{ padding: 16, background: '#ffebee', color: '#c62828', borderRadius: 6 }}>
          <strong>Lỗi tải dữ liệu:</strong> {pageError}
        </div>
      )}

      {!loading && !pageError && reservations.length === 0 && (
        <div style={{ padding: 24, textAlign: 'center', border: '1px dashed #ccc', borderRadius: 8 }}>
          <p>Bạn chưa có đơn đặt phòng nào.</p>
          <Link to="/booking" style={{ color: '#1976d2', fontWeight: 600 }}>
            Đặt phòng ngay →
          </Link>
        </div>
      )}

      {/* Bảng danh sách đơn đặt phòng */}
      {!loading && !pageError && reservations.length > 0 && (
        <div style={{ overflowX: 'auto', marginBottom: 24 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f3f5', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: 10 }}>Mã đơn</th>
                <th style={{ padding: 10 }}>Phòng</th>
                <th style={{ padding: 10 }}>Nhận phòng</th>
                <th style={{ padding: 10 }}>Trả phòng</th>
                <th style={{ padding: 10 }}>Trạng thái</th>
                <th style={{ padding: 10 }}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {reservations.map((item) => (
                <tr key={item.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: 10 }}><strong>#{item.id}</strong></td>
                  <td style={{ padding: 10 }}>{item.room_number || item.room?.room_number || item.room_id}</td>
                  <td style={{ padding: 10 }}>{item.check_in}</td>
                  <td style={{ padding: 10 }}>{item.check_out}</td>
                  <td style={{ padding: 10 }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: 4,
                        fontSize: 13,
                        fontWeight: 600,
                        backgroundColor:
                          String(item.status).toLowerCase() === 'cancelled' ? '#ffebee' : '#e3f2fd',
                        color:
                          String(item.status).toLowerCase() === 'cancelled' ? '#c62828' : '#1565c0',
                      }}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td style={{ padding: 10, display: 'flex', gap: 8 }}>
                    <button
                      type="button"
                      disabled={loadingDetailId === item.id}
                      onClick={() => handleViewDetail(item.id)}
                      style={{ padding: '6px 10px', cursor: 'pointer' }}
                    >
                      {loadingDetailId === item.id ? 'Đang mở...' : 'Xem chi tiết'}
                    </button>

                    {canCancelStatus(item.status) && (
                      <button
                        type="button"
                        onClick={() => {
                          setCancelingTarget(item);
                          setCancelReason('');
                        }}
                        style={{
                          padding: '6px 10px',
                          backgroundColor: '#d32f2f',
                          color: '#fff',
                          border: 'none',
                          borderRadius: 4,
                          cursor: 'pointer',
                        }}
                      >
                        Hủy đơn
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Khung xác nhận hủy đơn (ConfirmDialog) */}
      {cancelingTarget && (
        <div
          style={{
            padding: 16,
            marginBottom: 20,
            border: '1px solid #d32f2f',
            backgroundColor: '#fff8f8',
            borderRadius: 8,
          }}
        >
          <h3 style={{ marginTop: 0, color: '#c62828' }}>
            Xác nhận hủy đơn đặt phòng #{cancelingTarget.id}
          </h3>
          <form onSubmit={handleConfirmCancel}>
            <div style={{ marginBottom: 12 }}>
              <label htmlFor="cancel_reason" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                Lý do hủy phòng (tùy chọn)
              </label>
              <input
                id="cancel_reason"
                type="text"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                disabled={submittingCancel}
                placeholder="Nhập lý do hủy đặt phòng..."
                style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
              />
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                type="submit"
                disabled={submittingCancel}
                style={{
                  padding: '8px 16px',
                  backgroundColor: submittingCancel ? '#ef9a9a' : '#d32f2f',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 4,
                  fontWeight: 600,
                  cursor: submittingCancel ? 'not-allowed' : 'pointer',
                }}
              >
                {submittingCancel ? 'Đang hủy...' : 'Xác nhận hủy'}
              </button>
              <button
                type="button"
                disabled={submittingCancel}
                onClick={() => setCancelingTarget(null)}
                style={{ padding: '8px 14px', cursor: 'pointer' }}
              >
                Đóng
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Khung hiển thị chi tiết đơn */}
      {selectedDetail && (
        <div style={{ padding: 20, border: '1px solid #ccc', borderRadius: 8, backgroundColor: '#fafafa' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ marginTop: 0 }}>Chi tiết đơn đặt phòng #{selectedDetail.id}</h2>
            <button type="button" onClick={() => setSelectedDetail(null)} style={{ padding: '4px 10px' }}>
              Đóng
            </button>
          </div>
          <p><strong>Phòng:</strong> {selectedDetail.room_number || selectedDetail.room?.room_number || selectedDetail.room_id}</p>
          <p><strong>Nhận phòng:</strong> {selectedDetail.check_in}</p>
          <p><strong>Trả phòng:</strong> {selectedDetail.check_out}</p>
          <p><strong>Số lượng khách:</strong> {selectedDetail.guests_count || 1}</p>
          {Array.isArray(selectedDetail.guest_names) && selectedDetail.guest_names.length > 0 && (
            <p><strong>Danh sách khách:</strong> {selectedDetail.guest_names.join(', ')}</p>
          )}
          {selectedDetail.promo_code && (
            <p><strong>Mã giảm giá áp dụng:</strong> {selectedDetail.promo_code}</p>
          )}
          {selectedDetail.total_amount !== undefined && (
            <p><strong>Tổng thanh toán:</strong> {Number(selectedDetail.total_amount).toLocaleString('vi-VN')} VNĐ</p>
          )}
          <p><strong>Trạng thái hiện tại:</strong> {selectedDetail.status}</p>
          {selectedDetail.special_requests && (
            <p><strong>Ghi chú:</strong> {selectedDetail.special_requests}</p>
          )}
        </div>
      )}
    </div>
  );
}