import { Routes, Route, Navigate } from 'react-router-dom';

import StaffLayout from './StaffLayout.jsx';

import StaffDashboard from './views/StaffDashboard.jsx';
import StaffRoomsPage from './views/StaffRoomsPage.jsx';
import StaffGuestsPage from './views/StaffGuestsPage.jsx';
import StaffBookingsPage from './views/StaffBookingsPage.jsx';
import StaffHousekeepingPage from './views/StaffHousekeepingPage.jsx';
import './StaffPages.css';

export const STAFF_PAGES = {
  dashboard: StaffDashboard,
  rooms: StaffRoomsPage,
  guests: StaffGuestsPage,
  bookings: StaffBookingsPage,
  housekeeping: StaffHousekeepingPage,
};

export default function StaffPages() {
  return (
    <Routes>
      <Route element={<StaffLayout />}>
        <Route index element={<StaffDashboard />} />
        <Route path="rooms" element={<StaffRoomsPage />} />
        <Route path="guests" element={<StaffGuestsPage />} />
        <Route path="bookings" element={<StaffBookingsPage />} />
        <Route path="housekeeping" element={<StaffHousekeepingPage />} />
        <Route path="*" element={<Navigate to="/staff" replace />} />
      </Route>
    </Routes>
  );
}