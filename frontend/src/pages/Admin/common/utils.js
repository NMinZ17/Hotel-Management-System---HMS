export const pad = n => String(n).padStart(2, '0');

export function isoOffset(days) {
  const d = new Date();
  d.setHours(12, 0, 0, 0);
  d.setDate(d.getDate() + days);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export const fmtDate = iso => (iso ? iso.split('-').reverse().join('/') : '');
export const money = v => `${Number(v).toLocaleString('vi-VN')} ₫`;

export const count = (rows, fn) => {
  if (!Array.isArray(rows)) return 0;
  if (typeof fn !== 'function') return rows.length;
  return rows.filter(fn).length;
};

export const percent = (a, b) =>
  (b ? (a / b) * 100 : 0).toLocaleString('vi-VN', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  });

/* Bỏ dấu tiếng Việt để tìm kiếm dễ hơn */
export const fold = s =>
  String(s ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd');

export const opt = o => (typeof o === 'string' ? { value: o, label: o } : o);
export const optionsOf = map =>
  Object.entries(map).map(([value, { label }]) => ({ value, label }));

export function exportCsv(name, columns, rows) {
  const cols = columns.filter(c => c.label);
  const esc = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const lines = [
    cols.map(c => esc(c.label)).join(','),
    ...rows.map(r => cols.map(c => esc(c.text ? c.text(r) : r[c.key])).join(',')),
  ];
  const blob = new Blob([`\ufeff${lines.join('\n')}`], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${name}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
