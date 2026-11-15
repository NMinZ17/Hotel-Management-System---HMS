
import './FormField.css';

function FormField({
  id,
  label,
  name,
  type = 'text',
  value = '',
  onChange,
  placeholder = '',
  required = false,
  error = '',
}) {
  const fieldId = id || name;

  return (
    <div className="form-field">
      <label htmlFor={fieldId} className="form-field__label">
        {label}
        {required && <span className="form-field__required"> *</span>}
      </label>

      <input
        id={fieldId}
        name={name}
        type={type}
        value={value}
        onChange={(event) => onChange?.(event.target.value)}
        placeholder={placeholder}
        required={required}
        aria-invalid={Boolean(error)}
        className={`form-field__input ${error ? 'form-field__input--error' : ''}`}
      />

      {error && <p className="form-field__error">{error}</p>}
    </div>
  );
}

export default FormField;
