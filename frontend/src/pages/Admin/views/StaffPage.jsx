
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { count, optionsOf } from '../common/utils.js';

const STAFF_STATUS = {
  working: { label: 'Đang làm việc', tone: 'success' },
  leave: { label: 'Nghỉ phép', tone: 'warning' },
  stopped: { label: 'Ngừng làm việc', tone: 'neutral' },
};

const DEPARTMENTS = [
  'Lễ tân',
  'Buồng phòng',
  'Nhà hàng',
  'Bảo trì',
  'Kế toán',
  'Quản lý',
];

const SHIFTS = [
  'Sáng (06:00-14:00)',
  'Chiều (14:00-22:00)',
  'Đêm (22:00-06:00)',
  'Hành chính',
];

const initials = name => {
  const parts = name.trim().split(/\s+/);

  return (
    parts[0][0] +
    (parts.length > 1 ? parts[parts.length - 1][0] : '')
  ).toUpperCase();
};

const staffConfig = {
  title: 'Nhân viên',
  subtitle: 'Danh sách nhân viên, bộ phận và ca làm việc.',
  addLabel: 'Thêm nhân viên',
  noun: 'nhân viên',
  label: r => r.name,
  exportName: 'nhan-vien',
  searchKeys: ['name', 'code', 'role'],
  searchPlaceholder: 'Tìm theo tên, mã hoặc chức vụ',

  // Backend hiện chưa có API quản lý nhân viên.
  rows: [],

  
  stats: rows => {
    if (rows.length === 0) {
      return [
        { label: 'Tổng nhân viên', value: '--', note: 'Chưa có API nhân viên' },
        { label: 'Đang làm việc', value: '--', note: 'Chưa có dữ liệu' },
        { label: 'Nghỉ phép', value: '--', note: 'Chưa có dữ liệu' },
        { label: 'Bộ phận', value: '--', note: 'Chưa có dữ liệu' },
      ];
    }

    return [
      {
        label: 'Tổng nhân viên',
        value: rows.length,
        note: 'Trong hệ thống',
      },
      {
        label: 'Đang làm việc',
        value: count(rows, r => r.status === 'working'),
        note: 'Nhân viên hiện hữu',
      },
      {
        label: 'Nghỉ phép',
        value: count(rows, r => r.status === 'leave'),
        note: 'Đang nghỉ có phép',
      },
      {
        label: 'Bộ phận',
        value: new Set(rows.map(r => r.dept)).size,
        note: 'Đang hoạt động',
      },
    ];
  },


  tabs: [
    { id: 'all', label: 'Tất cả', match: () => true },
    {
      id: 'working',
      label: 'Đang làm việc',
      match: r => r.status === 'working',
    },
    {
      id: 'leave',
      label: 'Nghỉ phép',
      match: r => r.status === 'leave',
    },
  ],

  filters: [
    {
      id: 'dept',
      all: 'Tất cả bộ phận',
      options: DEPARTMENTS,
      get: r => r.dept,
    },
    {
      id: 'shift',
      all: 'Mọi ca làm',
      options: SHIFTS,
      get: r => r.shift,
    },
  ],

  columns: [
    {
      key: 'name',
      label: 'Nhân viên',
      render: r => (
        <div className="avatar-cell">
          <span className="avatar-sm" aria-hidden="true">
            {initials(r.name)}
          </span>
          <strong>{r.name}</strong>
        </div>
      ),
      text: r => r.name,
    },
    { key: 'code', label: 'Mã NV' },
    { key: 'role', label: 'Chức vụ' },
    { key: 'dept', label: 'Bộ phận' },
    { key: 'shift', label: 'Ca làm' },
    { key: 'phone', label: 'Điện thoại' },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => (
        <StatusTag map={STAFF_STATUS} value={r.status} />
      ),
      text: r => STAFF_STATUS[r.status]?.label,
    },
  ],

  // Chưa có API thêm, sửa hoặc xóa nhân viên.
  fields: [],
};

export default function StaffPage() {
  return <CrudPage config={staffConfig} />;
}

