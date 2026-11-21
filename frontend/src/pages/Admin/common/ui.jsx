import Glyph from './Glyph.jsx';
import { opt } from './utils.js';


export function Tag({ tone = 'neutral', children }) {
  return <span className={`tag tag--${tone}`}>{children}</span>;
}

export function StatusTag({ map, value }) {
  const s = map[value];
  return <Tag tone={s?.tone}>{s?.label ?? value}</Tag>;
}

export function Stat({ label, value, note, trend, tone }) {
  return (
    <article className="dashboard-card stat-card">
      <span className="stat-accent" aria-hidden="true" />
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <div className="stat-foot">
        <span>{note}</span>
        {trend ? <span className={`stat-trend ${tone ?? ''}`}>{trend}</span> : null}
      </div>
    </article>
  );
}

export function PageHead({ title, subtitle, children }) {
  return (
    <section className="dashboard-head">
      <div>
        <h1 className="dashboard-title">{title}</h1>
        <p className="dashboard-subtitle">{subtitle}</p>
      </div>
      <div className="dashboard-actions">{children}</div>
    </section>
  );
}

export function SelectBox({ label, value, onChange, allLabel, options }) {
  return (
    <label className="select-wrap">
      <select value={value} onChange={onChange} aria-label={label}>
        {allLabel !== undefined && <option value="">{allLabel}</option>}
        {options.map(o => {
          const { value: v, label: l } = opt(o);
          return <option key={v} value={v}>{l}</option>;
        })}
      </select>
      <Glyph name="chevron" size={14} />
    </label>
  );
}



