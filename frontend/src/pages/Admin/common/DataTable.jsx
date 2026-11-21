
import { useEffect, useState } from 'react';
import Glyph from './Glyph.jsx';
import { SelectBox } from './ui.jsx';
import { count, fold } from './utils.js';

export default function DataTable({
  noun,
  columns,
  rows = [],
  tabs = [],
  filters = [],
  searchKeys = [],
  searchPlaceholder,
  onEdit,
  onDelete,
  onPatch,
  extraActions,
  pageSize = 10,
}) {
  const [tab, setTab] = useState(tabs[0]?.id ?? '');
  const [query, setQuery] = useState('');
  const [filterValues, setFilterValues] = useState({});
  const [page, setPage] = useState(1);
  const [menu, setMenu] = useState(null);

  // Đóng menu thao tác khi bấm ra ngoài / cuộn / đổi kích thước
  useEffect(() => {
    if (!menu) return undefined;

    const onPointerDown = e => {
      if (!e.target.closest('.row-menu, .row-menu-btn')) {
        setMenu(null);
      }
    };

    const close = () => setMenu(null);

    window.addEventListener('pointerdown', onPointerDown);
    window.addEventListener('resize', close);
    window.addEventListener('scroll', close, true);

    return () => {
      window.removeEventListener('pointerdown', onPointerDown);
      window.removeEventListener('resize', close);
      window.removeEventListener('scroll', close, true);
    };
  }, [menu]);

  // Tab đang được chọn
  const activeTab = tabs.find(t => t.id === tab) ?? tabs[0];
const q = fold(query.trim());

const filtered = rows.filter(row => {
  const tabMatch = activeTab?.match ?? activeTab?.get;

  if (tabMatch && !tabMatch(row)) return false;

  for (const f of filters) {
    const filterId = f.id ?? f.key;
    const value = filterValues[filterId];

    if (value && String(f.get(row)) !== value) return false;
  }

  if (q && !searchKeys.some(key => fold(row[key]).includes(q))) return false;

  return true;
});

  // Phân trang
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const current = Math.min(page, pages);
  const start = (current - 1) * pageSize;
  const visible = filtered.slice(start, start + pageSize);

  const from = filtered.length ? start + 1 : 0;
  const to = start + visible.length;

  const firstPage = Math.max(
    1,
    Math.min(current - 2, pages - 4)
  );

  const pageNumbers = Array.from(
    { length: Math.min(5, pages) },
    (_, i) => firstPage + i
  );

  const hasFilter =
    query || Object.values(filterValues).some(Boolean);

  const resetFilters = () => {
    setQuery('');
    setFilterValues({});
    setPage(1);
  };

  // Mở menu thao tác
  const openMenu = (e, row) => {
    if (menu?.id === row.id) {
      setMenu(null);
      return;
    }

    const rect = e.currentTarget.getBoundingClientRect();
    const below = window.innerHeight - rect.bottom > 190;

    setMenu({
      id: row.id,
      right: window.innerWidth - rect.right,
      top: below ? rect.bottom + 4 : undefined,
      bottom: below
        ? undefined
        : window.innerHeight - rect.top + 4,
    });
  };

  const menuRow = menu
    ? rows.find(row => row.id === menu.id)
    : null;

  // Chỉ hiển thị thao tác khi đã có hàm xử lý tương ứng
  const actions = menuRow
    ? [
        ...(extraActions && onPatch
          ? extraActions(menuRow).map(action => ({
              type: 'patch',
              ...action,
            }))
          : []),
        ...(onEdit
          ? [{ type: 'edit', label: 'Chỉnh sửa' }]
          : []),
        ...(onDelete
          ? [{ type: 'delete', label: 'Xóa' }]
          : []),
      ]
    : [];

  const handleAction = action => {
    if (!menuRow) return;

    if (action.type === 'patch' && onPatch) {
      onPatch(menuRow, action.patch);
    }

    if (action.type === 'edit' && onEdit) {
      onEdit(menuRow);
    }

    if (action.type === 'delete' && onDelete) {
      onDelete(menuRow);
    }

    setMenu(null);
  };

  return (
    <article className="dashboard-panel table-panel">
      <div className="table-tabs" role="tablist">
        {tabs.map(t => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={(activeTab?.id ?? '') === t.id}
            className={`table-tab ${
              (activeTab?.id ?? '') === t.id ? 'active' : ''
            }`}
            onClick={() => {
              setTab(t.id);
              setPage(1);
            }}
          >
            {t.label}
            <b>{count(rows, t.match ?? t.get)}</b>
          </button>
        ))}
      </div>

      <div className="table-toolbar">
        <label className="table-search">
          <Glyph name="search" />
          <input
            type="search"
            value={query}
            placeholder={searchPlaceholder}
            aria-label="Tìm kiếm"
            onChange={e => {
              setQuery(e.target.value);
              setPage(1);
            }}
          />
        </label>

        {filters.map(f => {
          const filterId = f.id ?? f.key;
          const filterLabel = f.all ?? f.label;

          return (
            <SelectBox
              key={filterId}
              label={filterLabel}
              allLabel={filterLabel}
              options={f.options ?? []}
              value={filterValues[filterId] ?? ''}
              onChange={e => {
                setFilterValues(values => ({
                  ...values,
                  [filterId]: e.target.value,
                }));
                setPage(1);
              }}
            />
          );
        })}

        <button
          type="button"
          className="icon-btn"
          onClick={resetFilters}
          disabled={!hasFilter}
          aria-label="Xóa bộ lọc"
          title="Xóa bộ lọc"
        >
          <Glyph name="sliders" />
        </button>
      </div>

      <div className="table-body table-scroll">
        <table className="activity-table data-table">
          <thead>
            <tr>
              {columns.map(column => (
                <th key={column.key} scope="col">
                  {column.label}
                </th>
              ))}
              <th scope="col" className="col-actions">
                Thao tác
              </th>
            </tr>
          </thead>

          <tbody>
            {visible.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length + 1}
                  className="table-empty"
                >
                  Không tìm thấy {noun} phù hợp.
                  {hasFilter && (
                    <button
                      type="button"
                      className="link-button"
                      onClick={resetFilters}
                    >
                      Xóa bộ lọc
                    </button>
                  )}
                </td>
              </tr>
            ) : (
              visible.map(row => (
                <tr key={row.id}>
                  {columns.map(column => (
                    <td
                      key={column.key}
                      className={
                        column.strong ? 'cell-strong' : undefined
                      }
                    >
                      {column.render
                        ? column.render(row)
                        : row[column.key]}
                    </td>
                  ))}

                  <td className="col-actions">
                    <button
                      type="button"
                      className="row-menu-btn"
                      aria-label="Mở menu thao tác"
                      aria-haspopup="menu"
                      aria-expanded={menu?.id === row.id}
                      onClick={e => openMenu(e, row)}
                      disabled={actions.length === 0}
                      title={
                        actions.length === 0
                          ? 'Chưa có thao tác API'
                          : 'Mở menu thao tác'
                      }
                    >
                      <Glyph name="dots" size={18} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <footer className="table-footer">
        <span>
          Hiển thị {from}–{to} / {filtered.length} {noun}
        </span>

        <nav className="pager" aria-label="Phân trang">
          <button
            type="button"
            disabled={current === 1}
            onClick={() => setPage(current - 1)}
            aria-label="Trang trước"
          >
            <Glyph name="left" size={14} />
          </button>

          {pageNumbers.map(number => (
            <button
              key={number}
              type="button"
              className={number === current ? 'active' : ''}
              aria-current={
                number === current ? 'page' : undefined
              }
              onClick={() => setPage(number)}
            >
              {number}
            </button>
          ))}

          <button
            type="button"
            disabled={current === pages}
            onClick={() => setPage(current + 1)}
            aria-label="Trang sau"
          >
            <Glyph name="right" size={14} />
          </button>
        </nav>
      </footer>

      {menu && menuRow && actions.length > 0 && (
        <ul
          className="row-menu"
          role="menu"
          style={{
            top: menu.top,
            bottom: menu.bottom,
            right: menu.right,
          }}
        >
          {actions.map((action, index) => (
            <li key={`${action.type}-${action.label}-${index}`} role="none">
              <button
                type="button"
                role="menuitem"
                className={
                  action.type === 'delete' ? 'danger' : undefined
                }
                onClick={() => handleAction(action)}
              >
                {action.label}
              </button>
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
