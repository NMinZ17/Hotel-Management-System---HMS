import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../lib/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [currentUser, setCurrentUser] = useState(null);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
    confirm_password: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (!formData.email.trim()) return 'Vui lòng nhập email.';
    if (!formData.password) return 'Vui lòng nhập mật khẩu.';
    if (mode === 'register') {
      if (!formData.full_name.trim()) return 'Vui lòng nhập họ và tên.';
      if (formData.password.length < 6) return 'Mật khẩu cần tối thiểu 6 ký tự.';
      if (formData.password !== formData.confirm_password) {
        return 'Mật khẩu xác nhận không khớp.';
      }
    }
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return; // Chặn gửi lặp

    setErrorMsg('');
    setSuccessMsg('');

    const validationError = validateForm();
    if (validationError) {
      setErrorMsg(validationError);
      return;
    }

    setSubmitting(true);
    try {
      if (mode === 'login') {
        const res = await authApi.login({
          email: formData.email.trim(),
          password: formData.password,
        });
        const { access_token, token, user } = res.data;
        const authToken = access_token || token;

        if (authToken) localStorage.setItem('token', authToken);
        const userInfo = user || { email: formData.email.trim() };
        localStorage.setItem('user', JSON.stringify(userInfo));
        setCurrentUser(userInfo);

        setSuccessMsg('Đăng nhập thành công. Đang chuyển hướng...');
        setTimeout(() => navigate('/booking'), 800);
      } else {
        await authApi.register({
          full_name: formData.full_name.trim(),
          email: formData.email.trim(),
          phone: formData.phone.trim(),
          password: formData.password,
        });
        setSuccessMsg('Đăng ký tài khoản thành công. Vui lòng đăng nhập.');
        setMode('login');
        setFormData((prev) => ({ ...prev, password: '', confirm_password: '' }));
      }
    } catch (err) {
      setErrorMsg(err.message || 'Không thể xác thực tài khoản.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setCurrentUser(null);
    setSuccessMsg('Đã đăng xuất khỏi hệ thống.');
    setErrorMsg('');
  };

  return (
    <div style={{ maxWidth: 460, margin: '32px auto', padding: 24, border: '1px solid #ddd', borderRadius: 8 }}>
      <h1 style={{ marginTop: 0 }}>
        {mode === 'login' ? 'Đăng nhập hệ thống' : 'Đăng ký tài khoản khách'}
      </h1>

      {/* Hiển thị trạng thái đăng nhập hiện tại */}
      {currentUser && (
        <div
          style={{
            padding: 12,
            marginBottom: 16,
            backgroundColor: '#e8f5e9',
            border: '1px solid #a5d6a7',
            borderRadius: 6,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>
            Đang đăng nhập: <strong>{currentUser.full_name || currentUser.email}</strong>
          </span>
          <button type="button" onClick={handleLogout} style={{ padding: '4px 10px', cursor: 'pointer' }}>
            Đăng xuất
          </button>
        </div>
      )}

      {/* Notification lỗi / thành công */}
      {errorMsg && (
        <div role="alert" style={{ padding: 12, marginBottom: 16, background: '#ffebee', color: '#c62828', borderRadius: 6 }}>
          <strong>Lỗi:</strong> {errorMsg}
        </div>
      )}
      {successMsg && (
        <div role="status" style={{ padding: 12, marginBottom: 16, background: '#e8f5e9', color: '#2e7d32', borderRadius: 6 }}>
          <strong>Thành công:</strong> {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        {mode === 'register' && (
          <>
            <div style={{ marginBottom: 12 }}>
              <label htmlFor="full_name" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                Họ và tên <span style={{ color: 'red' }}>*</span>
              </label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                value={formData.full_name}
                onChange={handleChange}
                disabled={submitting}
                placeholder="Nguyễn Văn A"
                style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
              />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label htmlFor="phone" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
                Số điện thoại
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
                disabled={submitting}
                placeholder="0912345678"
                style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
              />
            </div>
          </>
        )}

        <div style={{ marginBottom: 12 }}>
          <label htmlFor="email" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            Email <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            disabled={submitting}
            placeholder="khachhang@example.com"
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label htmlFor="password" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
            Mật khẩu <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleChange}
            disabled={submitting}
            style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
          />
        </div>

        {mode === 'register' && (
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="confirm_password" style={{ display: 'block', marginBottom: 4, fontWeight: 600 }}>
              Xác nhận mật khẩu <span style={{ color: 'red' }}>*</span>
            </label>
            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              disabled={submitting}
              style={{ width: '100%', padding: 8, boxSizing: 'border-box' }}
            />
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          style={{
            width: '100%',
            padding: 10,
            backgroundColor: submitting ? '#90caf9' : '#1976d2',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            fontWeight: 600,
            cursor: submitting ? 'not-allowed' : 'pointer',
          }}
        >
          {submitting
            ? 'Đang xử lý...'
            : mode === 'login'
            ? 'Đăng nhập'
            : 'Đăng ký'}
        </button>
      </form>

      <div style={{ marginTop: 16, textAlign: 'center' }}>
        {mode === 'login' ? (
          <span>
            Chưa có tài khoản?{' '}
            <button
              type="button"
              disabled={submitting}
              onClick={() => {
                setMode('register');
                setErrorMsg('');
                setSuccessMsg('');
              }}
              style={{ background: 'none', border: 'none', color: '#1976d2', cursor: 'pointer', textDecoration: 'underline' }}
            >
              Đăng ký ngay
            </button>
          </span>
        ) : (
          <span>
            Đã có tài khoản?{' '}
            <button
              type="button"
              disabled={submitting}
              onClick={() => {
                setMode('login');
                setErrorMsg('');
                setSuccessMsg('');
              }}
              style={{ background: 'none', border: 'none', color: '#1976d2', cursor: 'pointer', textDecoration: 'underline' }}
            >
              Quay lại đăng nhập
            </button>
          </span>
        )}
      </div>
    </div>
  );
}