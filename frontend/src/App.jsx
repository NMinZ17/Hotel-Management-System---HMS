import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import RoomsPage from './pages/RoomsPage';
import LoginPage from './pages/LoginPage';
import BookingPage from './pages/BookingPage';
import MyReservationsPage from './pages/MyReservationsPage';

// Layout cơ bản có thanh điều hướng
const Layout = ({ children }) => (
    <div>
        <nav style={{ padding: 10, background: '#eee' }}>
            <Link to="/rooms" style={{ marginRight: 10 }}>
                Phòng
            </Link>
            <Link to="/login" style={{ marginRight: 10 }}>
                Đăng nhập
            </Link>
            <Link to="/booking" style={{ marginRight: 10 }}>
                Đặt phòng
            </Link>
            <Link to="/my-reservations" style={{ marginRight: 10 }}>
                Lịch sử đặt phòng
            </Link>
        </nav>

        {children}
    </div>
);

function App() {
  return (
    <Router>
        <Layout>
            <Routes>
                <Route path="/rooms" element={<RoomsPage />} />
                <Route path="/booking" element={<BookingPage />} />
                <Route path="/my-reservations" element={<MyReservationsPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/" element={<Navigate to="/rooms" replace />} />
                <Route path="*" element={<Navigate to="/rooms" replace />} />
            </Routes>
        </Layout>
    </Router>
  );
}

export default App;