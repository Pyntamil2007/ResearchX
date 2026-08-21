import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PasswordInput } from '../components/PasswordInput';
import { Sparkles, Mail, LogIn } from 'lucide-react';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { user, token, login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  React.useEffect(() => {
    if (token && user) {
      if (user.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [token, user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.warning('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      const data = await login(email.trim().toLowerCase(), password);
      toast.success('Welcome back to ResearchX!');
      if (data?.user?.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } catch (err) {
      toast.error(err.response?.data?.message || err.message || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem 1.5rem',
      background: 'radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 60%)'
    }}>
      <div style={{ width: '100%', maxWidth: '440px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            boxShadow: '0 8px 24px var(--primary-glow)',
            marginBottom: '1rem'
          }}>
            <Sparkles size={28} />
          </div>
          <h1 style={{ fontSize: '1.9rem', marginBottom: '0.4rem' }}>
            Research<span className="brand-accent">X</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Web Research Analyzer & Interactive Understanding Layer
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          <h2 style={{ fontSize: '1.35rem', marginBottom: '1.25rem', fontWeight: 700 }}>Sign In</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="login-email">Email Address</label>
              <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                <Mail size={18} />
                <input
                  id="login-email"
                  type="email"
                  className="form-input"
                  placeholder="name@organization.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <label className="form-label" htmlFor="login-password" style={{ marginBottom: 0 }}>Password</label>
                <Link
                  to="/forgot-password"
                  style={{ fontSize: '0.82rem', color: 'var(--accent)', fontWeight: 500 }}
                  id="forgot-password-link"
                >
                  Forgot Password?
                </Link>
              </div>
              <PasswordInput
                id="login-password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block btn-lg"
              disabled={loading}
              style={{ marginTop: '1.25rem' }}
              id="login-submit-btn"
            >
              {loading ? (
                <span>Signing In...</span>
              ) : (
                <>
                  <span>Sign In</span>
                  <LogIn size={18} />
                </>
              )}
            </button>
          </form>

          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Don't have an account yet?{' '}
            <Link to="/register" style={{ color: 'var(--accent)', fontWeight: 600 }}>
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
