import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { roomApi } from '../lib/api';

const ROOM_IMAGES = [
  'https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80',
];

const ITEMS_PER_PAGE = 6;

export default function RoomsPage() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Bộ lọc trên Header & Thanh tìm kiếm
  const [searchText, setSearchText] = useState('');
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [capacityInput, setCapacityInput] = useState('');
  const [appliedFilter, setAppliedFilter] = useState({ capacity: 0 });
  const [sortBy, setSortBy] = useState('default');
  const [selectedRoomType, setSelectedRoomType] = useState('ALL');

  // Phân trang & Modal
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        const response = await roomApi.getAll();
        const list = Array.isArray(response) ? response : response?.data || [];
        setRooms(list);
      } catch (err) {
        setError('Không thể tải danh sách phòng. Vui lòng kiểm tra kết nối backend.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRooms();
  }, []);

  // Danh sách loại phòng duy nhất cho dropdown Bộ lọc/sắp xếp
  const roomTypes = useMemo(() => {
    const map = new Map();
    rooms.forEach((r) => {
      if (r.room_type?.name) {
        map.set(r.room_type.room_type_id, r.room_type.name);
      }
    });
    return Array.from(map.entries());
  }, [rooms]);

  // Lọc và sắp xếp danh sách phòng
  const filteredRooms = useMemo(() => {
    let result = [...rooms];

    if (searchText.trim()) {
      const kw = searchText.toLowerCase();
      result = result.filter(
        (r) =>
          (r.room_number || '').toLowerCase().includes(kw) ||
          (r.room_type?.name || '').toLowerCase().includes(kw)
      );
    }

    if (appliedFilter.capacity > 0) {
      result = result.filter(
        (r) => (r.room_type?.max_guests || 0) >= appliedFilter.capacity
      );
    }

    if (selectedRoomType !== 'ALL') {
      result = result.filter(
        (r) => String(r.room_type_id) === String(selectedRoomType)
      );
    }

    if (sortBy === 'price_asc') {
      result.sort(
        (a, b) => Number(a.room_type?.base_price || 0) - Number(b.room_type?.base_price || 0)
      );
    } else if (sortBy === 'price_desc') {
      result.sort(
        (a, b) => Number(b.room_type?.base_price || 0) - Number(a.room_type?.base_price || 0)
      );
    }

    return result;
  }, [rooms, searchText, appliedFilter, selectedRoomType, sortBy]);

  const totalPages = Math.max(1, Math.ceil(filteredRooms.length / ITEMS_PER_PAGE));
  const paginatedRooms = filteredRooms.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const handleApplySearch = () => {
    setAppliedFilter({ capacity: Number(capacityInput) || 0 });
    setCurrentPage(1);
  };

  const handleToggleLike = (roomId) => {
    setLikedIds((prev) =>
      prev.includes(roomId) ? prev.filter((id) => id !== roomId) : [...prev, roomId]
    );
  };

  const handleConfirmBooking = (bookingData) => {
    const existing = JSON.parse(localStorage.getItem('hms_bookings') || '[]');
    localStorage.setItem('hms_bookings', JSON.stringify([bookingData, ...existing]));
    setBookingRoom(null);
    alert(
      `Đặt phòng ${bookingData.room_number} thành công!\nKhách hàng: ${bookingData.full_name} (${bookingData.phone})\nThời gian: ${bookingData.check_in} → ${bookingData.check_out}`
    );
  };

  return (
    <div>
      {/* HEADER TRANG CHỦ */}
      <header className="home-header">
        <div className="brand-group" onClick={() => navigate('/rooms')}>
          <div className="brand-logo">Logo</div>
          <span className="brand-name">HMS Demo Hotel</span>
        </div>

        <div className="header-actions">
          <input
            type="text"
            className="header-search-input"
            placeholder="Tìm kiếm số phòng, loại phòng..."
            value={searchText}
            onChange={(e) => {
              setSearchText(e.target.value);
              setCurrentPage(1);
            }}
          />
          <button
            type="button"
            className="header-login-btn"
            onClick={() => setShowLogin(true)}
          >
            Login
          </button>
        </div>
      </header>

      {/* NỘI DUNG CHÍNH */}
      <main className="main-container">
        {/* THANH TÌM KIẾM & BỘ LỌC */}
        <section className="filter-toolbar">
          <div className="filter-left-group">
            <div className="filter-box">
              <span>Ngày đặt:</span>
              <input
                type="date"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
              />
            </div>

            <div className="filter-box">
              <span>Ngày trả:</span>
              <input
                type="date"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
              />
            </div>

            <div className="filter-box">
              <span>Sức chứa:</span>
              <input
                type="number"
                min={1}
                max={10}
                placeholder="Số người"
                style={{ width: 85 }}
                value={capacityInput}
                onChange={(e) => setCapacityInput(e.target.value)}
              />
            </div>

            <button type="button" className="btn-search" onClick={handleApplySearch}>
              Tìm
            </button>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <select
              className="sort-select"
              value={selectedRoomType}
              onChange={(e) => {
                setSelectedRoomType(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="ALL">Loại phòng: Tất cả</option>
              {roomTypes.map(([id, name]) => (
                <option key={id} value={id}>
                  {name}
                </option>
              ))}
            </select>

            <select
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="default">Bộ lọc/sắp xếp</option>
              <option value="price_asc">Giá: Thấp → Cao</option>
              <option value="price_desc">Giá: Cao → Thấp</option>
            </select>
          </div>
        </section>

        {/* TRẠNG THÁI LOADING / LỖI / LƯỚI PHÒNG */}
        {loading && <p>Đang tải danh sách phòng...</p>}
        {error && <p style={{ color: '#dc2626', fontWeight: 600 }}>{error}</p>}

        {!loading && !error && paginatedRooms.length === 0 && (
          <p>Không tìm thấy phòng phù hợp với điều kiện lọc.</p>
        )}

        {!loading && !error && paginatedRooms.length > 0 && (
          <section className="rooms-grid">
            {paginatedRooms.map((room, idx) => {
              const imgSrc = ROOM_IMAGES[(room.room_id || idx) % ROOM_IMAGES.length];
              return (
                <article key={room.room_id} className="room-card">
                  <div className="room-card-image-wrap">
                    <img src={imgSrc} alt={`Phòng ${room.room_number}`} />
                    <span className="room-badge-top">
                      Phòng {room.room_number} • Tầng {room.floor}
                    </span>
                  </div>

                  <div className="room-card-body">
                    <div className="room-card-title">
                      {room.room_type?.name || 'Phòng tiêu chuẩn'}
                    </div>
                    <div className="room-card-meta">
                      Sức chứa tối đa: {room.room_type?.max_guests ?? 2} khách
                    </div>
                    <div className="room-card-price">
                      {Number(room.room_type?.base_price || 0).toLocaleString('vi-VN')} VNĐ / đêm
                    </div>

                    <button
                      type="button"
                      className="btn-room-detail"
                      onClick={() => setDetailRoom({ ...room, imageUrl: imgSrc })}
                    >
                      Chi tiết phòng
                    </button>
                  </div>
                </article>
              );
            })}
          </section>
        )}

        {/* PHÂN TRANG: 1 2 > */}
        {!loading && !error && filteredRooms.length > 0 && (
          <nav className="pagination-bar" aria-label="Phân trang">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                type="button"
                className={`page-btn ${currentPage === page ? 'active' : ''}`}
                onClick={() => setCurrentPage(page)}
              >
                {page}
              </button>
            ))}
            <button
              type="button"
              className="page-btn"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              title="Trang sau"
            >
              ▶
            </button>
          </nav>
        )}
      </main>

      {/* FOOTER */}
      <footer className="home-footer">
        <span>
          <strong>HMS Demo Hotel</strong> — Hệ thống đặt phòng khách sạn trực tuyến
        </span>
        <span>Hotline: 20066688 • Địa chỉ: Thanh Xuân, Hà Nội, Việt Nam</span>
      </footer>
    </div>
  );
}