import React, { useState, useEffect } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import { useToast } from '../context/ToastContext';
import { PasswordInput } from '../components/PasswordInput';
import { Sparkles, KeyRound, ArrowLeft, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const checkToken = async () => {
      if (!token) {
        setTokenError('No password reset token was provided.');
        setVerifying(false);
        return;
      }

      try {
        const res = await authService.verifyResetToken(token);
        if (res.success && res.data?.valid) {
          setTokenValid(true);
          setUserEmail(res.data.email || '');
        } else {
          setTokenError(res.message || 'Invalid or expired password reset token.');
        }
      } catch (err) {
        setTokenError(err.response?.data?.detail || err.response?.data?.message || 'Password reset token is invalid or has expired.');
      } finally {
        setVerifying(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newPassword) {
      toast.warning('Please enter a new password.');
      return;
    }
    if (newPassword.length < 6) {
      toast.warning('Password must be at least 6 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.warning('Passwords do not match.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await authService.resetPassword(token, newPassword);
      if (res.success) {
        toast.success('Your password has been reset successfully! You may now sign in.');
        navigate('/login');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.message || 'Failed to reset password.');
    } finally {
      setSubmitting(false);
    }
  };

  if (verifying) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1.5rem',
        background: 'radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 60%)'
      }}>
        <div className="glass-panel" style={{ padding: '2.5rem', textAlign: 'center', maxWidth: '420px', width: '100%' }}>
          <div style={{ color: 'var(--accent)', marginBottom: '1rem' }}>
            <KeyRound size={32} className="animate-spin" />
          </div>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Verifying Security Token...</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Please wait while we validate your password reset request.</p>
        </div>
      </div>
    );
  }

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
            <ShieldCheck size={28} />
          </div>
          <h1 style={{ fontSize: '1.9rem', marginBottom: '0.4rem' }}>
            Create New Password
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Set a secure new password for your account
          </p>
        </div>

        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          {tokenValid ? (
            <>
              <div style={{ marginBottom: '1.25rem' }}>
                <h2 style={{ fontSize: '1.25rem', marginBottom: '0.35rem', fontWeight: 700 }}>Reset Password</h2>
                {userEmail && (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Updating password for: <strong style={{ color: 'var(--text-main)' }}>{userEmail}</strong>
                  </p>
                )}
              </div>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label" htmlFor="new-password">New Password</label>
                  <PasswordInput
                    id="new-password"
                    placeholder="Enter at least 6 characters"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                  <label className="form-label" htmlFor="confirm-new-password">Confirm New Password</label>
                  <PasswordInput
                    id="confirm-new-password"
                    placeholder="Re-enter your new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary btn-block btn-lg"
                  disabled={submitting}
                  id="reset-submit-btn"
                >
                  {submitting ? (
                    <span>Updating Password...</span>
                  ) : (
                    <>
                      <span>Update Password</span>
                      <CheckCircle2 size={16} />
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
                background: 'rgba(239, 68, 68, 0.15)',
                color: '#f87171',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem'
              }}>
                <AlertTriangle size={24} />
              </div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>Invalid or Expired Link</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: '1.5rem' }}>
                {tokenError || 'This password reset link is invalid, has already been used, or has expired.'}
              </p>

              <Link to="/forgot-password" className="btn btn-primary btn-block" id="request-new-link-btn">
                Request a New Reset Link
              </Link>
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
