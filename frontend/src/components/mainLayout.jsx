import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function MainLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div style={{ fontFamily: 'sans-serif', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header / Navbar */}
      <header style={{ backgroundColor: '#1e293b', color: 'white', padding: '15px 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold', fontSize: '18px' }}>
            🏨 HMS Demo Hotel
          </Link>
          <Link to="/rooms" style={{ color: '#cbd5e1', textDecoration: 'none' }}>Tìm phòng</Link>
        </div>

        <div>
          {isAuthenticated ? (
            <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
              <span>Xin chào, <strong>{user?.email || user?.full_name}</strong> ({user?.role || 'USER'})</span>
              <button onClick={handleLogout} style={{ padding: '6px 12px', cursor: 'pointer', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '4px' }}>
                Đăng xuất
              </button>
            </div>
          ) : (
            <Link to="/login" style={{ padding: '8px 16px', backgroundColor: '#3b82f6', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
              Đăng nhập
            </Link>
          )}
        </div>
      </header>

      {/* Nội dung các trang con sẽ render ở đây */}
      <main style={{ flex: 1, padding: '20px 30px', maxWidth: '1200px', width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>
        <Outlet />
      </main>
    </div>
  );
}