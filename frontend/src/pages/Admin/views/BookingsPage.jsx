
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { fmtDate, money, optionsOf } from '../common/utils.js';

const BOOKING_STATUS = {
  pending: { label: 'Chờ xác nhận', tone: 'warning' },
  confirmed: { label: 'Đã xác nhận', tone: 'success' },
  checkedin: { label: 'Đang lưu trú', tone: 'info' },
  checkedout: { label: 'Đã trả phòng', tone: 'neutral' },
  cancelled: { label: 'Đã hủy', tone: 'danger' },
};

const BOOKING_SOURCES = ['Website', 'Booking.com', 'Agoda', 'Trực tiếp'];

const bookingsConfig = {
  title: 'Đặt phòng',
  subtitle: 'Theo dõi đặt phòng, nhận phòng và trả phòng.',
  addLabel: 'Tạo đặt phòng',
  noun: 'đặt phòng',
  label: r => r.code,
  exportName: 'dat-phong',
  searchKeys: ['code', 'guest', 'room'],
  searchPlaceholder: 'Tìm theo mã, tên khách hoặc số phòng',

  // Backend hiện chưa có API đặt phòng.
  rows: [],

  stats: rows => [
    {
      label: 'Nhận phòng hôm nay',
      value: '--',
      note: 'Chưa có API đặt phòng',
    },
    {
      label: 'Đang lưu trú',
      value: '--',
      note: 'Chưa có API đặt phòng',
    },
    {
      label: 'Chờ xác nhận',
      value: '--',
      note: 'Chưa có API đặt phòng',
    },
    {
      label: 'Đã hủy',
      value: '--',
      note: 'Chưa có API đặt phòng',
    },
  ],

  tabs: [
    { id: 'all', label: 'Tất cả', match: () => true },
    { id: 'pending', label: 'Chờ xác nhận', match: r => r.status === 'pending' },
    { id: 'confirmed', label: 'Đã xác nhận', match: r => r.status === 'confirmed' },
    { id: 'checkedin', label: 'Đang lưu trú', match: r => r.status === 'checkedin' },
    { id: 'cancelled', label: 'Đã hủy', match: r => r.status === 'cancelled' },
  ],

  filters: [
    {
      id: 'source',
      all: 'Tất cả nguồn',
      options: BOOKING_SOURCES,
      get: r => r.source,
    },
    {
      id: 'status',
      all: 'Tất cả trạng thái',
      options: optionsOf(BOOKING_STATUS),
      get: r => r.status,
    },
  ],

  columns: [
    { key: 'code', label: 'Mã đặt phòng', strong: true },
    { key: 'guest', label: 'Khách' },
    { key: 'room', label: 'Phòng' },
    {
      key: 'checkIn',
      label: 'Nhận phòng',
      render: r => fmtDate(r.checkIn),
      text: r => fmtDate(r.checkIn),
    },
    {
      key: 'checkOut',
      label: 'Trả phòng',
      render: r => fmtDate(r.checkOut),
      text: r => fmtDate(r.checkOut),
    },
    { key: 'source', label: 'Nguồn' },
    {
      key: 'total',
      label: 'Tổng tiền',
      render: r => money(r.total),
      text: r => r.total,
    },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => (
        <StatusTag map={BOOKING_STATUS} value={r.status} />
      ),
      text: r => BOOKING_STATUS[r.status]?.label ?? '',
    },
  ],

  // Chưa có API tạo, sửa hoặc cập nhật trạng thái đặt phòng.
  fields: [],
};

export default function BookingsPage() {
  return <CrudPage config={bookingsConfig} />;
}

