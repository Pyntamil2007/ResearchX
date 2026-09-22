import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { PasswordInput } from '../components/PasswordInput';
import { Sparkles, User as UserIcon, Mail, UserPlus } from 'lucide-react';

export const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { user, token, register } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

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
    if (!name || !email || !password) {
      toast.warning('Please fill in all required fields.');
      return;
    }
    if (password.length < 6) {
      toast.warning('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      toast.warning('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const data = await register(name.trim(), email.trim().toLowerCase(), password);
      toast.success('Registration successful! Welcome to ResearchX.');
      if (data?.user?.role === 'ADMIN') {
        navigate('/admin/dashboard', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    } catch (err) {
      toast.error(err.response?.data?.message || err.message || 'Registration failed.');
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
      <div style={{ width: '100%', maxWidth: '460px' }}>
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
            Join our AI-powered research analysis platform
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          <h2 style={{ fontSize: '1.35rem', marginBottom: '1.25rem', fontWeight: 700 }}>Create Account</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="register-name">Full Name</label>
              <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                <UserIcon size={18} />
                <input
                  id="register-name"
                  type="text"
                  className="form-input"
                  placeholder="Dr. Alan Turing"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="register-email">Email Address</label>
              <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                <Mail size={18} />
                <input
                  id="register-email"
                  type="email"
                  className="form-input"
                  placeholder="alan.turing@cambridge.ac.uk"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="register-password">Password</label>
              <PasswordInput
                id="register-password"
                placeholder="Min. 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <div className="form-group" style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" htmlFor="register-confirm-password">Confirm Password</label>
              <PasswordInput
                id="register-confirm-password"
                placeholder="Repeat password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block btn-lg"
              disabled={loading}
              id="register-submit-btn"
            >
              {loading ? (
                <span>Creating Account...</span>
              ) : (
                <>
                  <span>Create Account</span>
                  <UserPlus size={18} />
                </>
              )}
            </button>
          </form>

          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: 'var(--accent)', fontWeight: 600 }}>
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
