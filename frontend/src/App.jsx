import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import RoomsPage from './pages/RoomsPage';

// Layout cơ bản có thanh điều hướng
const Layout = ({ children }) => (
    <div>
        <nav style={{ padding: 10, background: '#eee' }}>
            <Link to="/rooms" style={{ marginRight: 10 }}>
                Phòng
            </Link>
        </nav>

        {children}
    </div>
);

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/rooms" element={<RoomsPage />} />
        <Route path="/" element={<Navigate to="/rooms" replace />} />
        <Route path="*" element={<Navigate to="/rooms" replace />} />
      </Routes>
    </Router>
  );
}

export default App;