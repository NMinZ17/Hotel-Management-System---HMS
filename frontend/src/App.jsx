
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';

import MainLayout from './components/mainLayout';

import RoomsPage from './pages/RoomsPage';
import LoginPage from './pages/LoginPage';
import BookingPage from './pages/BookingPage';
import MyReservationsPage from './pages/MyReservationsPage';

import AdminApp from './pages/Admin/AdminPages';
import StaffPages from './pages/staff/StaffPages';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Trang khách hàng */}
          <Route element={<MainLayout />}>
            <Route path="/rooms" element={<RoomsPage />} />
            <Route path="/booking" element={<BookingPage />} />
            <Route
              path="/my-reservations"
              element={<MyReservationsPage />}
            />
          </Route>

          {/* Đăng nhập */}
          <Route path="/login" element={<LoginPage />} />

          {/* Quản trị */}
          <Route path="/admin/*" element={<AdminApp />} />

          {/* Nhân viên */}
          <Route path="/staff/*" element={<StaffPages />} />

          {/* Điều hướng mặc định */}
          <Route path="/" element={<Navigate to="/rooms" replace />} />
          <Route path="*" element={<Navigate to="/rooms" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
