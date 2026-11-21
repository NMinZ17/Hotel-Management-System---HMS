
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { optionsOf } from '../common/utils.js';

const HK_STATUS = {
  pending: { label: 'Chờ xử lý', tone: 'warning' },
  progress: { label: 'Đang xử lý', tone: 'info' },
  done: { label: 'Hoàn thành', tone: 'success' },
};

const HK_PRIORITY = {
  high: { label: 'Cao', tone: 'danger' },
  medium: { label: 'Trung bình', tone: 'warning' },
  low: { label: 'Thấp', tone: 'neutral' },
};

const housekeepingConfig = {
  title: 'Buồng phòng',
  subtitle: 'Phân công và theo dõi công việc dọn phòng trong ngày.',
  addLabel: 'Thêm công việc',
  noun: 'công việc',
  label: r => `${r.task} – phòng ${r.room}`,
  exportName: 'buong-phong',
  searchKeys: ['room', 'task', 'staff'],
  searchPlaceholder: 'Tìm theo phòng, công việc hoặc nhân viên',

  // Backend hiện chưa có API quản lý công việc buồng phòng.
  rows: [],

  stats: () => [
    {
      label: 'Chờ xử lý',
      value: '--',
      note: 'Chưa có API buồng phòng',
    },
    {
      label: 'Đang xử lý',
      value: '--',
      note: 'Chưa có API buồng phòng',
    },
    {
      label: 'Hoàn thành',
      value: '--',
      note: 'Chưa có API buồng phòng',
    },
    {
      label: 'Ưu tiên cao',
      value: '--',
      note: 'Chưa có API buồng phòng',
    },
  ],

  tabs: [
    { id: 'all', label: 'Tất cả', match: () => true },
    { id: 'pending', label: 'Chờ xử lý', match: r => r.status === 'pending' },
    { id: 'progress', label: 'Đang xử lý', match: r => r.status === 'progress' },
    { id: 'done', label: 'Hoàn thành', match: r => r.status === 'done' },
  ],

  filters: [
    {
      id: 'staff',
      all: 'Tất cả nhân viên',
      options: [],
      get: r => r.staff,
    },
    {
      id: 'priority',
      all: 'Mọi mức ưu tiên',
      options: optionsOf(HK_PRIORITY),
      get: r => r.priority,
    },
  ],

  columns: [
    { key: 'room', label: 'Phòng', strong: true },
    { key: 'task', label: 'Công việc' },
    { key: 'staff', label: 'Nhân viên phụ trách' },
    {
      key: 'priority',
      label: 'Ưu tiên',
      render: r => (
        <StatusTag map={HK_PRIORITY} value={r.priority} />
      ),
      text: r => HK_PRIORITY[r.priority]?.label ?? '',
    },
    { key: 'time', label: 'Giờ' },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => (
        <StatusTag map={HK_STATUS} value={r.status} />
      ),
      text: r => HK_STATUS[r.status]?.label ?? '',
    },
  ],

  // Chưa có API thêm, sửa hoặc cập nhật công việc.
  fields: [],
};

export default function HousekeepingPage() {
  return <CrudPage config={housekeepingConfig} />;
}

