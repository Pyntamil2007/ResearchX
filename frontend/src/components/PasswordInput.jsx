import React, { useState } from 'react';
import { Lock, Eye, EyeOff } from 'lucide-react';

export const PasswordInput = ({
  id,
  name,
  value,
  onChange,
  placeholder = '••••••••',
  required = false,
  autoComplete,
  disabled = false,
  className = 'form-input',
  showLeftIcon = true,
  ...rest
}) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="password-input-wrapper">
      {showLeftIcon && (
        <span className="password-left-icon" aria-hidden="true">
          <Lock size={18} />
        </span>
      )}
      <input
        id={id}
        name={name}
        type={showPassword ? 'text' : 'password'}
        className={className}
        style={{
          paddingLeft: showLeftIcon ? '42px' : '14px',
          paddingRight: '42px'
        }}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        required={required}
        autoComplete={autoComplete}
        disabled={disabled}
        {...rest}
      />
      <button
        type="button"
        className="password-toggle-btn"
        onClick={() => setShowPassword(!showPassword)}
        aria-label={showPassword ? 'Hide password' : 'Show password'}
        title={showPassword ? 'Hide password' : 'Show password'}
        tabIndex={0}
      >
        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
      </button>
    </div>
  );
};
