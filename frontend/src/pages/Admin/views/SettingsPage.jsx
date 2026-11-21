
import { createContext, useContext, useState } from 'react';
import { PageHead } from '../common/ui.jsx';
import { opt } from '../common/utils.js';

const SETTING_TABS = [
  { id: 'hotel', label: 'Thông tin khách sạn' },
  { id: 'operation', label: 'Vận hành' },
  { id: 'notify', label: 'Thông báo' },
];

const NOTIFY_OPTIONS = [
  ['notifyBooking', 'Đặt phòng mới', 'Báo khi có đặt phòng mới từ mọi kênh'],
  ['notifyCheckin', 'Khách nhận phòng', 'Báo khi lễ tân hoàn tất nhận phòng'],
  ['notifyMaintenance', 'Yêu cầu bảo trì', 'Báo khi bộ phận buồng phòng gửi yêu cầu'],
  ['notifyDaily', 'Báo cáo hằng ngày qua email', 'Gửi tổng kết doanh thu vào cuối ngày'],
];

const EMPTY_FORM = {
  name: '',
  stars: '',
  address: '',
  phone: '',
  email: '',
  checkIn: '',
  checkOut: '',
  currency: '',
  vat: '',
  service: '',
  cancelPolicy: '',
  notifyBooking: false,
  notifyCheckin: false,
  notifyMaintenance: false,
  notifyDaily: false,
};

const SettingsContext = createContext(null);

function SettingField({
  name,
  label,
  type = 'text',
  full,
  placeholder,
  options,
  min,
  max,
  step,
}) {
  const { form, set } = useContext(SettingsContext);

  return (
    <label className={`field ${full ? 'full' : ''}`}>
      <span>{label}</span>

      {options ? (
        <select
          value={form[name]}
          onChange={e => set(name, e.target.value)}
        >
          <option value="">Chưa thiết lập</option>
          {options.map(o => {
            const { value, label: l } = opt(o);
            return (
              <option key={value} value={value}>
                {l}
              </option>
            );
          })}
        </select>
      ) : (
        <input
          type={type}
          value={form[name]}
          placeholder={placeholder}
          min={min}
          max={max}
          step={step}
          onChange={e =>
            set(
              name,
              type === 'number'
                ? (e.target.value === '' ? '' : Number(e.target.value))
                : e.target.value
            )
          }
        />
      )}
    </label>
  );
}

export default function SettingsPage() {
  const [tab, setTab] = useState('hotel');
  const [form, setForm] = useState(EMPTY_FORM);

  const set = (key, value) => {
    setForm(current => ({
      ...current,
      [key]: value,
    }));
  };

  const save = e => {
    e.preventDefault();
  };

  return (
    <SettingsContext.Provider value={{ form, set }}>
      <div className="admin-dashboard">
        <PageHead
          title="Cài đặt"
          subtitle="Thiết lập thông tin, quy tắc vận hành và thông báo của khách sạn."
        />

        <form className="dashboard-panel table-panel" onSubmit={save}>
          <div className="table-tabs" role="tablist">
            {SETTING_TABS.map(t => (
              <button
                key={t.id}
                type="button"
                role="tab"
                aria-selected={tab === t.id}
                className={`table-tab ${tab === t.id ? 'active' : ''}`}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="settings-body">
            {tab === 'hotel' && (
              <div className="form-grid">
                <SettingField name="name" label="Tên khách sạn" full />
                <SettingField
                  name="stars"
                  label="Hạng sao"
                  options={[1, 2, 3, 4, 5].map(n => ({
                    value: String(n),
                    label: `${n} sao`,
                  }))}
                />
                <SettingField
                  name="phone"
                  label="Điện thoại"
                  placeholder="Số điện thoại liên hệ"
                />
                <SettingField name="address" label="Địa chỉ" full />
                <SettingField
                  name="email"
                  label="Email"
                  type="email"
                  placeholder="Email liên hệ"
                  full
                />
              </div>
            )}

            {tab === 'operation' && (
              <div className="form-grid">
                <SettingField
                  name="checkIn"
                  label="Giờ nhận phòng"
                  type="time"
                />
                <SettingField
                  name="checkOut"
                  label="Giờ trả phòng"
                  type="time"
                />
                <SettingField
                  name="currency"
                  label="Tiền tệ"
                  options={[
                    { value: 'VND', label: 'Việt Nam Đồng (₫)' },
                    { value: 'USD', label: 'Đô la Mỹ ($)' },
                  ]}
                />
                <SettingField
                  name="cancelPolicy"
                  label="Chính sách hủy phòng"
                  options={[
                    { value: '24', label: 'Miễn phí trước 24 giờ' },
                    { value: '48', label: 'Miễn phí trước 48 giờ' },
                    { value: 'none', label: 'Không hoàn tiền' },
                  ]}
                />
                <SettingField
                  name="vat"
                  label="Thuế VAT (%)"
                  type="number"
                  min={0}
                  max={100}
                  step={0.5}
                />
                <SettingField
                  name="service"
                  label="Phí dịch vụ (%)"
                  type="number"
                  min={0}
                  max={100}
                  step={0.5}
                />
              </div>
            )}

            {tab === 'notify' && (
              <div>
                {NOTIFY_OPTIONS.map(([key, title, hint]) => (
                  <label key={key} className="switch-row">
                    <span>
                      <strong>{title}</strong>
                      <small>{hint}</small>
                    </span>
                    <input
                      type="checkbox"
                      role="switch"
                      checked={form[key]}
                      onChange={e => set(key, e.target.checked)}
                    />
                  </label>
                ))}
              </div>
            )}
          </div>

          <footer className="settings-foot">
            <span className="save-note" role="status">
              Chức năng lưu chưa được kết nối API.
            </span>
            <button type="submit" className="btn-primary" disabled>
              Lưu thay đổi
            </button>
          </footer>
        </form>
      </div>
    </SettingsContext.Provider>
  );
}

