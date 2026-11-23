import { useEffect, useState } from 'react';
import AdminLayout, { AdminDashboard } from './AdminLayout.jsx';
import './AdminPages.css';

import RoomsPage from './views/RoomsPage.jsx';
import RoomTypesPage from './views/RoomTypesPage.jsx';
import AmenitiesPage from './views/AmenitiesPage.jsx';
import BookingsPage from './views/BookingsPage.jsx';
import GuestsPage from './views/GuestsPage.jsx';
import HousekeepingPage from './views/HousekeepingPage.jsx';
import StaffPage from './views/StaffPage.jsx';
import ReportsPage from './views/ReportsPage.jsx';
import SettingsPage from './views/SettingsPage.jsx';

/* id trùng với menuItems trong AdminLayout.jsx */
export const ADMIN_PAGES = {
  dashboard: AdminDashboard,
  rooms: RoomsPage,
  'room-types': RoomTypesPage,
  amenities: AmenitiesPage,
  bookings: BookingsPage,
  guests: GuestsPage,
  housekeeping: HousekeepingPage,
  staff: StaffPage,
  reports: ReportsPage,
  settings: SettingsPage,
};

export default function AdminApp() {
  const [page, setPage] = useState('dashboard');
  const Page = ADMIN_PAGES[page] ?? AdminDashboard;

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [page]);

  return (
    <AdminLayout activePage={page} onNavigate={setPage}>
      <Page onNavigate={setPage} />
    </AdminLayout>
  );
}