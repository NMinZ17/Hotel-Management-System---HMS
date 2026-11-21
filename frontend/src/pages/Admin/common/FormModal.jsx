
import { useEffect, useState } from 'react';
import Glyph from './Glyph.jsx';
import { opt } from './utils.js';

export default function FormModal({ title, fields, initial, submitLabel, onSubmit, onClose }) {
  const [values, setValues] = useState(() =>
    Object.fromEntries(
      fields.map(f => [
        f.name,
        initial?.[f.name] ??
          f.default ??
          (f.type === 'select' ? opt(f.options[0]).value : ''),
      ])
    )
  );

  useEffect(() => {
    const onKey = e => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const submit = e => {
    e.preventDefault();
    const result = { ...values };
    fields.forEach(f => {
      if (f.type === 'number') result[f.name] = Number(values[f.name]);
    });
    onSubmit(result);
  };

  return (
    <div
      className="modal-backdrop"
      onMouseDown={e => e.target === e.currentTarget && onClose()}
    >
      <form className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" onSubmit={submit}>
        <header className="modal-head">
          <h2 id="modal-title">{title}</h2>
          <button type="button" className="icon-btn plain" onClick={onClose} aria-label="Đóng">
            <Glyph name="close" />
          </button>
        </header>

        <div className="form-grid">
          {fields.map((f, i) => (
            <label key={f.name} className={`field ${f.full ? 'full' : ''}`}>
              <span>{f.label}</span>
              {f.type === 'select' ? (
                <select
                  value={values[f.name]}
                  onChange={e => setValues(v => ({ ...v, [f.name]: e.target.value }))}
                >
                  {f.options.map(o => {
                    const { value, label } = opt(o);
                    return <option key={value} value={value}>{label}</option>;
                  })}
                </select>
              ) : (
                <input
                  type={f.type ?? 'text'}
                  value={values[f.name]}
                  min={f.min}
                  required={f.required}
                  placeholder={f.placeholder}
                  autoFocus={i === 0}
                  onChange={e => setValues(v => ({ ...v, [f.name]: e.target.value }))}
                />
              )}
            </label>
          ))}
        </div>

        <footer className="modal-foot">
          <button type="button" className="dashboard-button" onClick={onClose}>Hủy</button>
          <button type="submit" className="btn-primary">{submitLabel}</button>
        </footer>
      </form>
    </div>
  );
}
