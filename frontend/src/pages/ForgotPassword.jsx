import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useToast } from '../context/ToastContext';
import { Sparkles, Mail, ArrowLeft, Send, CheckCircle2, KeyRound } from 'lucide-react';

export const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submittedToken, setSubmittedToken] = useState(null);
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      toast.warning('Please enter your registered email address.');
      return;
    }

    setLoading(true);
    try {
      const res = await authService.forgotPassword(email);
      if (res.success) {
        toast.success('Password reset link generated successfully!');
        if (res.data?.reset_token) {
          setSubmittedToken(res.data.reset_token);
        }
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.message || 'Failed to process password reset.');
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
            <KeyRound size={28} />
          </div>
          <h1 style={{ fontSize: '1.9rem', marginBottom: '0.4rem' }}>
            Password Recovery
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Reset your ResearchX account password
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          {!submittedToken ? (
            <>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.75rem', fontWeight: 700 }}>Forgot Password?</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                Enter the email address associated with your account, and we'll generate a secure, time-limited reset link.
              </p>

              <form onSubmit={handleSubmit}>
                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                  <label className="form-label" htmlFor="forgot-email">Registered Email Address</label>
                  <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                    <Mail size={18} />
                    <input
                      id="forgot-email"
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

                <button
                  type="submit"
                  className="btn btn-primary btn-block btn-lg"
                  disabled={loading}
                  id="forgot-submit-btn"
                >
                  {loading ? (
                    <span>Generating Reset Link...</span>
                  ) : (
                    <>
                      <span>Send Reset Link</span>
                      <Send size={16} />
                    </>
                  )}
                </button>
              </form>
            </>
          ) : (
            <div style={{ textAlign: 'center', padding: '0.5rem 0' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.15)',
                color: '#34d399',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem'
              }}>
                <CheckCircle2 size={26} />
              </div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Reset Link Generated!</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                A secure password reset token has been issued for <strong>{email}</strong>. It is valid for 15 minutes.
              </p>

              <div style={{
                padding: '1rem',
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: '8px',
                marginBottom: '1.5rem',
                textAlign: 'left'
              }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--accent)', marginBottom: 6 }}>
                  Direct Password Reset Link:
                </div>
                <Link
                  to={`/reset-password?token=${submittedToken}`}
                  style={{
                    display: 'block',
                    fontSize: '0.84rem',
                    color: '#ffffff',
                    wordBreak: 'break-all',
                    textDecoration: 'underline'
                  }}
                  id="direct-reset-link"
                >
                  Proceed to Reset Password →
                </Link>
              </div>

              <button
                type="button"
                className="btn btn-primary btn-block"
                onClick={() => navigate(`/reset-password?token=${submittedToken}`)}
                id="reset-password-now-btn"
              >
                Reset Password Now
              </button>
            </div>
          )}

          <div style={{ marginTop: '1.5rem', textAlign: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
            <Link to="/login" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: '0.88rem', fontWeight: 600 }}>
              <ArrowLeft size={15} />
              <span>Back to Sign In</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
