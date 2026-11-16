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
  as = 'input',
  options = [],
  disabled = false,
}) {
  const fieldId = id || name;

  const commonProps = {
    id: fieldId,
    name,
    value,
    onChange: (event) => onChange?.(event.target.value),
    required,
    disabled,
    'aria-invalid': Boolean(error),
    'aria-describedby': error ? `${fieldId}-error` : undefined,
    className: `form-field__input ${
      error ? 'form-field__input--error' : ''
    }`,
  };

  return (
    <div className="form-field">
      <label htmlFor={fieldId} className="form-field__label">
        {label}
        {required && <span className="form-field__required"> *</span>}
      </label>

      {as === 'select' ? (
        <select {...commonProps}>
          <option value="">
            {placeholder || 'Vui lòng chọn'}
          </option>

          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : (
        <input
          {...commonProps}
          type={type}
          placeholder={placeholder}
        />
      )}

      {error && (
        <p
          id={`${fieldId}-error`}
          className="form-field__error"
        >
          {error}
        </p>
      )}
    </div>
  );
}

export default FormField;