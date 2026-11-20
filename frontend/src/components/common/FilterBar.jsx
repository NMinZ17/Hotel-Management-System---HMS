import './FilterBar.css';

function FilterBar({
  filters = [],
  values = {},
  onChange,
  onReset,
}) {
  return (
    <div className="filter-bar">
      <div className="filter-bar__fields">
        {filters.map((filter) => (
          <div className="filter-bar__field" key={filter.key}>
            <label
              htmlFor={`filter-${filter.key}`}
              className="filter-bar__label"
            >
              {filter.label}
            </label>

            {filter.type === 'select' ? (
              <select
                id={`filter-${filter.key}`}
                value={values[filter.key] ?? ''}
                onChange={(event) =>
                  onChange?.(filter.key, event.target.value)
                }
                className="filter-bar__control"
              >
                <option value="">
                  {filter.placeholder || 'Tất cả'}
                </option>

                {(filter.options || []).map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id={`filter-${filter.key}`}
                type={filter.type || 'text'}
                value={values[filter.key] ?? ''}
                onChange={(event) =>
                  onChange?.(filter.key, event.target.value)
                }
                placeholder={filter.placeholder || ''}
                className="filter-bar__control"
              />
            )}
          </div>
        ))}
      </div>

      <button
        type="button"
        className="filter-bar__reset"
        onClick={onReset}
      >
        Xóa bộ lọc
      </button>
    </div>
  );
}

export default FilterBar;