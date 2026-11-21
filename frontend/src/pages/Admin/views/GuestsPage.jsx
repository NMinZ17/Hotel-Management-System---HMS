
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag, } from '../common/ui.jsx';
import { optionsOf } from '../common/utils.js';

const GUEST_TIER = {
  standard: { label: 'Thường', tone: 'neutral' },
  member: { label: 'Thành viên', tone: 'info' },
  vip: { label: 'VIP', tone: 'gold' },
};

const GUEST_STATUS = {
  in: { label: 'Đang lưu trú', tone: 'success' },
  out: { label: 'Không lưu trú', tone: 'neutral' },
};

const NATIONALITIES = [
  'Việt Nam',
  'Hàn Quốc',
  'Nhật Bản',
  'Hoa Kỳ',
  'Pháp',
  'Úc',
];

const guestsConfig = {
  title: 'Khách hàng',
  subtitle: 'Hồ sơ khách, hạng thành viên và lịch sử lưu trú.',
  addLabel: 'Thêm khách',
  noun: 'khách',
  label: r => r.name,
  exportName: 'khach-hang',
  searchKeys: ['name', 'phone', 'email'],
  searchPlaceholder: 'Tìm theo tên, số điện thoại hoặc email',

  // Backend hiện chưa có API quản lý khách hàng.
  rows: [],

  stats: () => [
    {
      label: 'Tổng số khách',
      value: '--',
      note: 'Chưa có API khách hàng',
    },
    {
      label: 'Khách VIP',
      value: '--',
      note: 'Chưa có API khách hàng',
    },
    {
      label: 'Đang lưu trú',
      value: '--',
      note: 'Chưa có API khách hàng',
    },
    {
      label: 'Thành viên',
      value: '--',
      note: 'Chưa có API khách hàng',
    },
  ],

  tabs: [
    { id: 'all', label: 'Tất cả khách', match: () => true },
    { id: 'vip', label: 'VIP', match: r => r.tier === 'vip' },
    { id: 'in', label: 'Đang lưu trú', match: r => r.status === 'in' },
  ],

  filters: [
    {
      id: 'nationality',
      all: 'Mọi quốc tịch',
      options: NATIONALITIES,
      get: r => r.nationality,
    },
    {
      id: 'tier',
      all: 'Mọi hạng',
      options: optionsOf(GUEST_TIER),
      get: r => r.tier,
    },
  ],

  columns: [
    {
      key: 'name',
      label: 'Khách',
      render: r => (
        <div className="cell-stack">
          <strong>{r.name}</strong>
          <small>{r.email}</small>
        </div>
      ),
      text: r => r.name,
    },
    { key: 'phone', label: 'Điện thoại' },
    { key: 'nationality', label: 'Quốc tịch' },
    { key: 'stays', label: 'Số lần lưu trú' },
    {
      key: 'tier',
      label: 'Hạng',
      render: r => (
        <StatusTag map={GUEST_TIER} value={r.tier} />
      ),
      text: r => GUEST_TIER[r.tier]?.label ?? '',
    },
    {
      key: 'status',
      label: 'Tình trạng',
      render: r => (
        <StatusTag map={GUEST_STATUS} value={r.status} />
      ),
      text: r => GUEST_STATUS[r.status]?.label ?? '',
    },
  ],

  // Chưa có API thêm, sửa hoặc xóa khách hàng.
  fields: [],
};

export default function GuestsPage() {
  return <CrudPage config={guestsConfig} />;
}

