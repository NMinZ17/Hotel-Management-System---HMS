import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RoomsPage from './pages/RoomsPage';

// Component bảo vệ route đơn giản (kiểm tra token)
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
};

// Layout cơ bản có thanh điều hướng
const Layout = ({ children }) => (
  <div>
    <nav style={{ padding: 10, background: '#eee' }}>
      <Link to="/rooms" style={{ marginRight: 10 }}>Phòng</Link>
      <button onClick={() => { localStorage.removeItem('token'); window.location.href = '/login'; }}>
        Đăng xuất
      </button>
    </nav>
    {children}
  </div>
);

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/rooms"
          element={
            <PrivateRoute>
              <Layout>
                <RoomsPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/rooms" replace />} />
      </Routes>
    </Router>
  );
}

export default App;