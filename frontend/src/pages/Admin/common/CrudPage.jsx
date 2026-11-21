
import { useState } from 'react';
import DataTable from './DataTable.jsx';
import FormModal from './FormModal.jsx';
import Glyph from './Glyph.jsx';
import { PageHead, Stat } from './ui.jsx';
import { exportCsv } from './utils.js';

export default function CrudPage({ config }) {
  // Chỉ sử dụng dữ liệu được truyền từ API hoặc nguồn dữ liệu thật.
  // Không tự tạo dữ liệu mẫu.
  const rows = config.rows ?? [];

  const [modal, setModal] = useState(null);

  const save = values => {
    if (!config.onSave || !modal) return;

    config.onSave(values, modal);
    setModal(null);
  };

  const remove = row => {
    if (!config.onDelete) return;

    const label = config.label
      ? config.label(row)
      : row.id;

    if (window.confirm(`Xóa ${config.noun} "${label}"?`)) {
      config.onDelete(row);
    }
  };

  const patch = (row, changes) => {
    if (!config.onPatch) return;

    config.onPatch(row, changes);
  };

  const stats = config.stats
    ? config.stats(rows)
    : [];

  return (
    <div className="admin-dashboard">
      <PageHead
        title={config.title}
        subtitle={config.subtitle}
      >
        <button
          type="button"
          className="dashboard-button"
          onClick={() =>
            exportCsv(config.exportName, config.columns, rows)
          }
        >
          <Glyph name="download" size={15} />
          Xuất báo cáo
        </button>

        <button
          type="button"
          className="btn-primary"
          disabled={!config.onSave}
          onClick={() => setModal({ mode: 'add' })}
        >
          <Glyph name="plus" size={15} />
          {config.addLabel}
        </button>
      </PageHead>

      <section
        className="dashboard-statistics"
        aria-label="Thống kê nhanh"
      >
        {stats.map(stat => (
          <Stat key={stat.label} {...stat} />
        ))}
      </section>

      <DataTable
        noun={config.noun}
        columns={config.columns}
        rows={rows}
        tabs={config.tabs}
        filters={config.filters}
        searchKeys={config.searchKeys}
        searchPlaceholder={config.searchPlaceholder}
        extraActions={config.onPatch ? config.extraActions : undefined}
        onEdit={
          config.onSave
            ? row => setModal({ mode: 'edit', row })
            : undefined
        }
        onDelete={config.onDelete ? remove : undefined}
        onPatch={config.onPatch ? patch : undefined}
      />

      {modal && (
        <FormModal
          title={
            modal.mode === 'edit'
              ? `Chỉnh sửa ${config.noun}`
              : config.addLabel
          }
          fields={config.fields}
          initial={modal.row}
          submitLabel={
            modal.mode === 'edit'
              ? 'Lưu thay đổi'
              : config.addLabel
          }
          onSubmit={save}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}
