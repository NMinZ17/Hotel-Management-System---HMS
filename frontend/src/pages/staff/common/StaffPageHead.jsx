export default function StaffPageHead({ title, description, children }) {
  return (
    <div className="staff-page-head">
      <div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children && <div className="staff-page-actions">{children}</div>}
    </div>
  );
}