import { useState } from 'react';
import { Link } from 'react-router-dom';
import { roomApi, reservationApi } from '../lib/api';

export default function BookingPage() {
  // Bộ lọc tìm phòng
  const [searchParams, setSearchParams] = useState({
    check_in: '',
    check_out: '',
    room_type: '',
  });

  const [rooms, setRooms] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loadingRooms, setLoadingRooms] = useState(false);
  const [searchError, setSearchError] = useState('');

  // State đặt phòng
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [bookingForm, setBookingForm] = useState({
    guests_count: 1,
    guest_names: '',
    promo_code: '',
    special_requests: '',
  });

  const [submittingBooking, setSubmittingBooking] = useState(false);
  const [bookingError, setBookingError] = useState('');
  const [confirmationData, setConfirmationData] = useState(null);

  const validateDates = (checkIn, checkOut) => {
    if (!checkIn || !checkOut) {
      return 'Vui lòng chọn đầy đủ ngày nhận phòng và ngày trả phòng.';
    }
    const today = new Date().toISOString().split('T')[0];
    if (checkIn < today) {
      return 'Ngày nhận phòng không được nhỏ hơn ngày hiện tại.';
    }
    if (checkOut <= checkIn) {
      return 'Ngày trả phòng phải sau ngày nhận phòng ít nhất 1 đêm.';
    }
    return '';
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (loadingRooms) return;

    setSearchError('');
    setBookingError('');
    setConfirmationData(null);
    setSelectedRoom(null);

    const dateErr = validateDates(searchParams.check_in, searchParams.check_out);
    if (dateErr) {
      setSearchError(dateErr);
      return;
    }

    setLoadingRooms(true);
    try {
      const query = {
        check_in: searchParams.check_in,
        check_out: searchParams.check_out,
      };
      if (searchParams.room_type) {
        query.room_type = searchParams.room_type;
      }

      const res = await roomApi.searchAvailable(query);
      const list = Array.isArray(res.data) ? res.data : res.data?.items || [];
      setRooms(list);
      setHasSearched(true);
    } catch (err) {
      setSearchError(err.message || 'Không thể tải danh sách phòng trống.');
      setRooms([]);
    } finally {
      setLoadingRooms(false);
    }
  };

  const handleSelectRoom = (room) => {
    setSelectedRoom(room);
    setBookingError('');
    setConfirmationData(null);
    setBookingForm({
      guests_count: 1,
      guest_names: '',
      promo_code: '',
      special_requests: '',
    });
  };

  const handleCreateBooking = async (e) => {
    e.preventDefault();
    if (submittingBooking || !selectedRoom) return;

    setBookingError('');

    const dateErr = validateDates(searchParams.check_in, searchParams.check_out);
    if (dateErr) {
      setBookingError(dateErr);
      return;
    }

    if (Number(bookingForm.guests_count) < 1) {
      setBookingError('Số lượng khách phải từ 1 người trở lên.');
      return;
    }

    // Chuẩn bị payload hỗ trợ cả đặt 1 khách & nhiều khách/mã giảm giá theo hợp đồng
    const additionalGuests = bookingForm.guest_names
      .split('\n')
      .map((name) => name.trim())
      .filter(Boolean);

    const payload = {
      room_id: selectedRoom.id,
      check_in: searchParams.check_in,
      check_out: searchParams.check_out,
      guests_count: Number(bookingForm.guests_count),
      guest_names: additionalGuests,
      promo_code: bookingForm.promo_code.trim() || undefined,
      special_requests: bookingForm.special_requests.trim() || undefined,
    };

    setSubmittingBooking(true);
    try {
      const res = await reservationApi.create(payload);
      setConfirmationData(res.data);
      setSelectedRoom(null);
      // Loại bỏ phòng vừa đặt khỏi danh sách hiện tại để tránh đặt trùng
      setRooms((prev) => prev.filter((r) => r.id !== selectedRoom.id));
    } catch (err) {
      // Hiển thị rõ lỗi hết phòng (409), lỗi ngày sai (400/422) hoặc chưa đăng nhập (401)
      setBookingError(err.message || 'Đặt phòng thất bại. Vui lòng thử lại.');
    } finally {
      setSubmittingBooking(false);
    }
  };

  return (
    <div style={{ maxWidth: 960, margin: '24px auto', padding: '0 16px' }}>
      <h1>Tìm kiếm & Đặt phòng</h1>

      {/* 1. Form tìm phòng */}
      <form
        onSubmit={handleSearch}
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 12,
          padding: 16,
          backgroundColor: '#f8f9fa',
          border: '1px solid #ddd',
          borderRadius: 8,
          marginBottom: 20,
        }}
      >
        <div>
          <label htmlFor="check_in" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            Ngày nhận phòng <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="check_in"
            type="date"
            value={searchParams.check_in}
            onChange={(e) => setSearchParams((p) => ({ ...p, check_in: e.target.value }))}
            disabled={loadingRooms}
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </div>

        <div>
          <label htmlFor="check_out" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            Ngày trả phòng <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="check_out"
            type="date"
            value={searchParams.check_out}
            onChange={(e) => setSearchParams((p) => ({ ...p, check_out: e.target.value }))}
            disabled={loadingRooms}
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </div>

        <div>
          <label htmlFor="room_type" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            Loại phòng
          </label>
          <select
            id="room_type"
            value={searchParams.room_type}
            onChange={(e) => setSearchParams((p) => ({ ...p, room_type: e.target.value }))}
            disabled={loadingRooms}
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          >
            <option value="">Tất cả loại phòng</option>
            <option value="standard">Phòng Tiêu chuẩn (Standard)</option>
            <option value="deluxe">Phòng Cao cấp (Deluxe)</option>
            <option value="suite">Phòng Suite</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button
            type="submit"
            disabled={loadingRooms}
            style={{
              width: '100%',
              padding: 9,
              backgroundColor: loadingRooms ? '#90caf9' : '#1976d2',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              fontWeight: 600,
              cursor: loadingRooms ? 'not-allowed' : 'pointer',
            }}
          >
            {loadingRooms ? 'Đang tìm...' : 'Tìm phòng'}
          </button>
        </div>
      </form>

      {/* Thông báo lỗi tìm kiếm */}
      {searchError && (
        <div role="alert" style={{ padding: 12, marginBottom: 16, background: '#ffebee', color: '#c62828', borderRadius: 6 }}>
          <strong>Lỗi tìm kiếm:</strong> {searchError}
        </div>
      )}

      {/* Phiếu xác nhận đặt phòng từ API */}
      {confirmationData && (
        <div
          role="status"
          style={{
            padding: 16,
            marginBottom: 20,
            backgroundColor: '#e8f5e9',
            border: '1px solid #81c784',
            borderRadius: 8,
          }}
        >
          <h2 style={{ marginTop: 0, color: '#2e7d32' }}>Xác nhận đặt phòng thành công</h2>
          <p>
            <strong>Mã đơn đặt phòng:</strong> #{confirmationData.id || confirmationData.reservation_code}
          </p>
          <p>
            <strong>Phòng:</strong> {confirmationData.room_number || confirmationData.room?.room_number || confirmationData.room_id}
          </p>
          <p>
            <strong>Thời gian lưu trú:</strong> {confirmationData.check_in} đến {confirmationData.check_out}
          </p>
          <p>
            <strong>Trạng thái đơn:</strong> {confirmationData.status}
          </p>
          {confirmationData.total_amount !== undefined && (
            <p>
              <strong>Tổng tiền dự kiến:</strong> {Number(confirmationData.total_amount).toLocaleString('vi-VN')} VNĐ
            </p>
          )}
          <Link to="/my-reservations" style={{ fontWeight: 600, color: '#1976d2' }}>
            Xem danh sách đơn đặt phòng của tôi →
          </Link>
        </div>
      )}

      {/* 2. Kết quả tìm phòng */}
      {loadingRooms && <p>Đang tải danh sách phòng khả dụng...</p>}

      {!loadingRooms && hasSearched && rooms.length === 0 && !searchError && (
        <div style={{ padding: 20, textAlign: 'center', border: '1px dashed #ccc', borderRadius: 8 }}>
          Không có phòng trống phù hợp với ngày và loại phòng bạn đã chọn.
        </div>
      )}

      {!loadingRooms && rooms.length > 0 && (
        <div style={{ overflowX: 'auto', marginBottom: 24 }}>
          <h2>Danh sách phòng có thể đặt ({rooms.length})</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f3f5', borderBottom: '2px solid #dee2e6' }}>
                <th style={{ padding: 10 }}>Số phòng</th>
                <th style={{ padding: 10 }}>Loại phòng</th>
                <th style={{ padding: 10 }}>Sức chứa</th>
                <th style={{ padding: 10 }}>Giá / đêm</th>
                <th style={{ padding: 10 }}>Trạng thái nghiệp vụ</th>
                <th style={{ padding: 10 }}>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {rooms.map((room) => (
                <tr key={room.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                  <td style={{ padding: 10 }}><strong>{room.room_number || room.name || `#${room.id}`}</strong></td>
                  <td style={{ padding: 10 }}>{room.room_type}</td>
                  <td style={{ padding: 10 }}>{room.capacity ? `${room.capacity} khách` : '—'}</td>
                  <td style={{ padding: 10 }}>
                    {room.price_per_night !== undefined
                      ? `${Number(room.price_per_night).toLocaleString('vi-VN')} VNĐ`
                      : '—'}
                  </td>
                  <td style={{ padding: 10 }}>
                    {/* Hiển thị nguyên trạng dữ liệu từ API theo Mục 7 UI Conventions */}
                    <div>Vệ sinh: {room.housekeeping_status || '—'}</div>
                    <div>Bảo trì: {room.maintenance_status || '—'}</div>
                  </td>
                  <td style={{ padding: 10 }}>
                    <button
                      type="button"
                      onClick={() => handleSelectRoom(room)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: selectedRoom?.id === room.id ? '#2e7d32' : '#1976d2',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 4,
                        cursor: 'pointer',
                      }}
                    >
                      {selectedRoom?.id === room.id ? 'Đang chọn' : 'Chọn đặt phòng'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 3. Biểu mẫu đặt phòng */}
      {selectedRoom && (
        <div style={{ padding: 20, border: '1px solid #1976d2', borderRadius: 8, backgroundColor: '#f8fbff' }}>
          <h2 style={{ marginTop: 0 }}>
            Đặt phòng: {selectedRoom.room_number || `#${selectedRoom.id}`} ({searchParams.check_in} → {searchParams.check_out})
          </h2>

          {bookingError && (
            <div role="alert" style={{ padding: 12, marginBottom: 16, background: '#ffebee', color: '#c62828', borderRadius: 6 }}>
              <strong>Không thể đặt phòng:</strong> {bookingError}
            </div>
          )}

          <form onSubmit={handleCreateBooking}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 12 }}>
              <div>
                <label htmlFor="guests_count" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                  Số lượng khách <span style={{ color: 'red' }}>*</span>
                </label>
                <input
                  id="guests_count"
                  type="number"
                  min={1}
                  max={selectedRoom.capacity || 10}
                  value={bookingForm.guests_count}
                  onChange={(e) => setBookingForm((p) => ({ ...p, guests_count: e.target.value }))}
                  disabled={submittingBooking}
                  style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
                />
              </div>

              <div>
                <label htmlFor="promo_code" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                  Mã giảm giá (nếu có)
                </label>
                <input
                  id="promo_code"
                  type="text"
                  value={bookingForm.promo_code}
                  onChange={(e) => setBookingForm((p) => ({ ...p, promo_code: e.target.value }))}
                  disabled={submittingBooking}
                  placeholder="Nhập mã ưu đãi..."
                  style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: 12 }}>
              <label htmlFor="guest_names" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                Danh sách tên khách lưu trú (mỗi khách một dòng)
              </label>
              <textarea
                id="guest_names"
                rows={3}
                value={bookingForm.guest_names}
                onChange={(e) => setBookingForm((p) => ({ ...p, guest_names: e.target.value }))}
                disabled={submittingBooking}
                placeholder="Nguyễn Văn A&#10;Trần Thị B"
                style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ marginBottom: 16 }}>
              <label htmlFor="special_requests" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                Ghi chú / Yêu cầu thêm
              </label>
              <input
                id="special_requests"
                type="text"
                value={bookingForm.special_requests}
                onChange={(e) => setBookingForm((p) => ({ ...p, special_requests: e.target.value }))}
                disabled={submittingBooking}
                placeholder="Ví dụ: Nhận phòng muộn sau 20h"
                style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ display: 'flex', gap: 12 }}>
              <button
                type="submit"
                disabled={submittingBooking}
                style={{
                  padding: '10px 20px',
                  backgroundColor: submittingBooking ? '#90caf9' : '#2e7d32',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  fontWeight: 600,
                  cursor: submittingBooking ? 'not-allowed' : 'pointer',
                }}
              >
                {submittingBooking ? 'Đang gửi yêu cầu đặt phòng...' : 'Lưu & Xác nhận đặt phòng'}
              </button>

              <button
                type="button"
                disabled={submittingBooking}
                onClick={() => setSelectedRoom(null)}
                style={{
                  padding: '10px 16px',
                  backgroundColor: '#e0e0e0',
                  border: 'none',
                  borderRadius: 6,
                  cursor: submittingBooking ? 'not-allowed' : 'pointer',
                }}
              >
                Hủy bỏ
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}