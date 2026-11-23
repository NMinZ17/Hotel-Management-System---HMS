
import CrudPage from '../common/CrudPage.jsx';
import { StatusTag } from '../common/ui.jsx';
import { count, money, optionsOf } from '../common/utils.js';

const AMENITY_GROUP = {
  room: { label: 'Trong phòng', tone: 'gold' },
  common: { label: 'Khu vực chung', tone: 'info' },
  service: { label: 'Dịch vụ', tone: 'neutral' },
};

const ACTIVE_STATUS = {
  active: { label: 'Hoạt động', tone: 'success' },
  inactive: { label: 'Tạm ngưng', tone: 'neutral' },
};

const amenitiesConfig = {
  title: 'Tiện nghi',
  subtitle: 'Danh mục tiện nghi và dịch vụ đi kèm của khách sạn.',
  addLabel: 'Thêm tiện nghi',
  noun: 'tiện nghi',
  label: r => r.name,
  exportName: 'tien-nghi',
  searchKeys: ['name'],
  searchPlaceholder: 'Tìm theo tên tiện nghi',

  // Backend chưa có API tiện nghi.
  rows: [],

  stats: rows => [
    {
      label: 'Tổng tiện nghi',
      value: rows.length,
      note: 'Trong danh mục',
    },
    {
      label: 'Đang hoạt động',
      value: count(rows, r => r.status === 'active'),
      note: `${count(rows, r => r.status === 'inactive')} tạm ngưng`,
    },
    {
      label: 'Miễn phí',
      value: rows.length
        ? count(rows, r => Number(r.fee) === 0)
        : '--',
      note: 'Khách không phải trả thêm',
    },
    {
      label: 'Có phí',
      value: rows.length
        ? count(rows, r => Number(r.fee) > 0)
        : '--',
      note: 'Tính thêm vào hóa đơn',
    },
  ],

  tabs: [
    { id: 'all', label: 'Tất cả', match: () => true },
    { id: 'room', label: 'Trong phòng', match: r => r.group === 'room' },
    { id: 'common', label: 'Khu vực chung', match: r => r.group === 'common' },
    { id: 'service', label: 'Dịch vụ', match: r => r.group === 'service' },
  ],

  filters: [
    {
      id: 'fee',
      all: 'Mọi mức phí',
      options: [
        { value: 'free', label: 'Miễn phí' },
        { value: 'paid', label: 'Có phí' },
      ],
      get: r => Number(r.fee) === 0 ? 'free' : 'paid',
    },
    {
      id: 'status',
      all: 'Tất cả trạng thái',
      options: optionsOf(ACTIVE_STATUS),
      get: r => r.status,
    },
  ],

  columns: [
    { key: 'name', label: 'Tiện nghi', strong: true },
    {
      key: 'group',
      label: 'Nhóm',
      render: r => (
        <StatusTag map={AMENITY_GROUP} value={r.group} />
      ),
      text: r => AMENITY_GROUP[r.group]?.label ?? '',
    },
    {
      key: 'fee',
      label: 'Phí sử dụng',
      render: r => r.fee == null
        ? 'Chưa xác định'
        : Number(r.fee) === 0
          ? 'Miễn phí'
          : money(r.fee),
      text: r => r.fee ?? '',
    },
    {
      key: 'status',
      label: 'Trạng thái',
      render: r => (
        <StatusTag map={ACTIVE_STATUS} value={r.status} />
      ),
      text: r => ACTIVE_STATUS[r.status]?.label ?? '',
    },
  ],

  // Chưa có API thêm/sửa tiện nghi.
  fields: [],
};

export default function AmenitiesPage() {
  return <CrudPage config={amenitiesConfig} />;
}

