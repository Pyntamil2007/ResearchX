import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { userService } from '../services/userService';
import { PasswordInput } from '../components/PasswordInput';
import { Modal } from '../components/Modal';
import {
  User,
  Mail,
  Lock,
  Shield,
  Calendar,
  Save,
  Trash2,
  AlertTriangle,
  KeyRound,
  ShieldAlert,
  CheckCircle2,
  Layers,
  Settings as SettingsIcon,
  ShieldCheck
} from 'lucide-react';

export const Profile = () => {
  const { user, updateUserProfile, logout, isAdmin } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('profile'); // 'profile', 'account', 'security', 'delete'

  // Account Settings Form State
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [savingProfile, setSavingProfile] = useState(false);

  // Security (Change Password) Form State
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);

  // Delete Account Modal State
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deletingAccount, setDeletingAccount] = useState(false);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!name || !email) {
      toast.warning('Please enter both name and email.');
      return;
    }

    setSavingProfile(true);
    try {
      const res = await userService.updateProfile(user.id, { name, email });
      if (res.success && res.data) {
        updateUserProfile(res.data);
        toast.success('Account information updated successfully!');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.message || 'Failed to update account.');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e) => {
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

    setSavingPassword(true);
    try {
      const res = await userService.changePassword(user.id, newPassword);
      if (res.success) {
        toast.success('Password changed successfully!');
        setNewPassword('');
        setConfirmPassword('');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.message || 'Failed to change password.');
    } finally {
      setSavingPassword(false);
    }
  };

  const handleDeleteAccountConfirm = async (e) => {
    e.preventDefault();
    if (!deletePassword) {
      toast.warning('Please enter your password to confirm account deletion.');
      return;
    }

    setDeletingAccount(true);
    try {
      const res = await userService.deleteMyAccount(deletePassword);
      if (res.success) {
        toast.success('Your account has been deleted successfully.');
        setIsDeleteModalOpen(false);
        logout();
        navigate('/login', { replace: true });
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.message || 'Failed to delete account.');
    } finally {
      setDeletingAccount(false);
    }
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', paddingBottom: '3rem' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.9rem', marginBottom: '0.35rem' }}>Profile & Settings</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
          Manage your personal research profile, account settings, security preferences, and data privacy.
        </p>
      </div>

      {/* Settings Navigation Tabs */}
      <div style={{
        display: 'flex',
        gap: 8,
        borderBottom: '1px solid var(--border-color)',
        marginBottom: '2rem',
        overflowX: 'auto',
        paddingBottom: 4
      }}>
        <button
          className={`btn btn-sm ${activeTab === 'profile' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('profile')}
          id="tab-profile"
        >
          <User size={15} />
          <span>Profile</span>
        </button>

        <button
          className={`btn btn-sm ${activeTab === 'account' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('account')}
          id="tab-account"
        >
          <SettingsIcon size={15} />
          <span>Account Settings</span>
        </button>

        <button
          className={`btn btn-sm ${activeTab === 'security' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('security')}
          id="tab-security"
        >
          <Lock size={15} />
          <span>Security</span>
        </button>

        <button
          className={`btn btn-sm ${activeTab === 'delete' ? 'btn-danger' : 'btn-secondary'}`}
          onClick={() => setActiveTab('delete')}
          id="tab-delete-account"
          style={activeTab === 'delete' ? { background: '#ef4444', color: '#ffffff' } : { color: '#f87171' }}
        >
          <Trash2 size={15} />
          <span>Delete Account</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: PROFILE OVERVIEW                                                   */}
      {/* ========================================================================= */}
      {activeTab === 'profile' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* User ID Card */}
          <div className="glass-panel" style={{ padding: '2.25rem 2rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{
              width: '84px',
              height: '84px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontSize: '2.2rem',
              fontWeight: 800,
              marginBottom: '1rem',
              boxShadow: '0 8px 24px var(--primary-glow)'
            }}>
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>

            <h3 style={{ fontSize: '1.35rem', marginBottom: '4px' }}>{user?.name}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>{user?.email}</p>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 12,
              width: '100%',
              borderTop: '1px solid var(--border-color)',
              paddingTop: '1.5rem',
              textAlign: 'left',
              fontSize: '0.9rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-dim)' }}>Assigned Role:</span>
                <span className={user?.role === 'ADMIN' ? 'badge badge-admin' : 'badge badge-user'}>
                  {user?.role === 'ADMIN' ? '🛡️ Administrator' : '🎓 Researcher'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-dim)' }}>Account Status:</span>
                <span className="badge badge-analyzed" style={{ textTransform: 'capitalize' }}>
                  {user?.status}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-dim)' }}>Auth Provider:</span>
                <span style={{ color: 'var(--text-main)', fontWeight: 600, textTransform: 'capitalize' }}>
                  {user?.auth_provider || 'Local'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-dim)' }}>Member Since:</span>
                <span style={{ color: 'var(--text-muted)' }}>
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Actions Panel */}
          <div className="glass-panel" style={{ padding: '2.25rem 2rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.75rem' }}>Profile Summary</h3>
              <p className="academic-paragraph" style={{ marginBottom: '1.25rem' }}>
                Your ResearchX account enables zero-hallucination NLP paper analysis, multi-format OCR uploads, structured academic reporting, and history management.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ padding: '12px 16px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: 10 }}>
                  <CheckCircle2 size={18} color="var(--success)" />
                  <span style={{ fontSize: '0.9rem' }}>Secure JWT-encrypted Session</span>
                </div>
                <div style={{ padding: '12px 16px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: 10 }}>
                  <ShieldCheck size={18} color="var(--accent)" />
                  <span style={{ fontSize: '0.9rem' }}>Bcrypt-12 Password Hashing</span>
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, marginTop: '1.5rem' }}>
              <button className="btn btn-secondary btn-block" onClick={() => setActiveTab('account')}>
                Edit Account Info
              </button>
              <button className="btn btn-secondary btn-block" onClick={() => setActiveTab('security')}>
                Change Password
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: ACCOUNT SETTINGS                                                   */}
      {/* ========================================================================= */}
      {activeTab === 'account' && (
        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: 4 }}>Account Settings</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
              Update your full name and registered contact email address.
            </p>
          </div>

          <form onSubmit={handleUpdateProfile} style={{ maxWidth: '520px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="account-name">Full Name</label>
              <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                <User size={18} />
                <input
                  id="account-name"
                  type="text"
                  className="form-input"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '1.75rem' }}>
              <label className="form-label" htmlFor="account-email">Email Address</label>
              <div className="search-input-wrapper" style={{ minWidth: 'auto' }}>
                <Mail size={18} />
                <input
                  id="account-email"
                  type="email"
                  className="form-input"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={savingProfile}
              id="save-account-btn"
            >
              <Save size={18} />
              <span>{savingProfile ? 'Saving Changes...' : 'Save Account Settings'}</span>
            </button>
          </form>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: SECURITY (CHANGE PASSWORD)                                         */}
      {/* ========================================================================= */}
      {activeTab === 'security' && (
        <div className="glass-panel" style={{ padding: '2.25rem 2rem' }}>
          <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.25rem', marginBottom: 4 }}>Security & Password</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
              Change your login password. Passwords must be at least 6 characters long and are encrypted with bcrypt.
            </p>
          </div>

          <form onSubmit={handleChangePassword} style={{ maxWidth: '520px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="new-profile-password">New Password</label>
              <PasswordInput
                id="new-profile-password"
                placeholder="Enter at least 6 characters"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <div className="form-group" style={{ marginBottom: '1.75rem' }}>
              <label className="form-label" htmlFor="confirm-profile-password">Confirm New Password</label>
              <PasswordInput
                id="confirm-profile-password"
                placeholder="Repeat your new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={savingPassword}
              id="change-password-btn"
            >
              <KeyRound size={18} />
              <span>{savingPassword ? 'Updating Password...' : 'Update Password'}</span>
            </button>
          </form>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: DELETE ACCOUNT (DANGER ZONE)                                       */}
      {/* ========================================================================= */}
      {activeTab === 'delete' && (
        <div className="glass-panel" style={{ padding: '2.25rem 2rem', borderColor: 'rgba(239, 68, 68, 0.4)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1.25rem' }}>
            <div style={{ padding: 10, background: 'rgba(239, 68, 68, 0.15)', color: '#f87171', borderRadius: '10px' }}>
              <AlertTriangle size={24} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.3rem', color: '#f87171', margin: '0 0 4px 0' }}>Danger Zone: Delete Account</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
                Permanently remove your account and all associated research documents, extracted data, and history.
              </p>
            </div>
          </div>

          <div style={{ maxWidth: '640px' }}>
            <div style={{
              padding: '1.25rem',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: '10px',
              marginBottom: '1.75rem'
            }}>
              <h4 style={{ fontSize: '1rem', color: '#fca5a5', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                <ShieldAlert size={18} />
                <span>Irreversible Permanent Action</span>
              </h4>
              <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>
                Once you delete your account, there is no going back. All your uploaded research papers, PDF files, AI structured reports, empirical result benchmarks, and audit histories will be immediately and permanently erased from the database and disk storage.
              </p>
            </div>

            {isAdmin ? (
              <div style={{
                padding: '1rem 1.25rem',
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                borderRadius: '8px',
                color: '#a5b4fc',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: 10
              }}>
                <ShieldCheck size={20} />
                <span>
                  <strong>Administrator Account Protection:</strong> Administrator accounts cannot be deleted through self-service settings to ensure system continuity.
                </span>
              </div>
            ) : (
              <button
                type="button"
                className="btn btn-danger btn-lg"
                onClick={() => {
                  setDeletePassword('');
                  setIsDeleteModalOpen(true);
                }}
                id="open-delete-account-modal-btn"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
              >
                <Trash2 size={18} />
                <span>Delete Account</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* DELETE ACCOUNT CONFIRMATION MODAL                                         */}
      {/* ========================================================================= */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => !deletingAccount && setIsDeleteModalOpen(false)}
        title="Delete Account Confirmation"
      >
        <div style={{ padding: '0.5rem 0' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: '1.25rem',
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            color: '#f87171'
          }}>
            <AlertTriangle size={24} style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '0.9rem', fontWeight: 600, lineHeight: 1.4 }}>
              Are you sure you want to delete your account?<br />
              <span style={{ fontSize: '0.82rem', fontWeight: 400, color: '#cbd5e1' }}>
                This action will permanently delete your account and associated data.
              </span>
            </div>
          </div>

          <form onSubmit={handleDeleteAccountConfirm}>
            <div className="form-group" style={{ marginBottom: '1.75rem' }}>
              <label className="form-label" htmlFor="delete-account-password">
                Enter your password to confirm identity:
              </label>
              <PasswordInput
                id="delete-account-password"
                placeholder="Enter your current password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                required
                autoComplete="current-password"
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10 }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsDeleteModalOpen(false)}
                disabled={deletingAccount}
                id="cancel-delete-account-btn"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-danger"
                disabled={deletingAccount || !deletePassword}
                id="confirm-delete-account-btn"
                style={{ background: '#ef4444', borderColor: '#ef4444', color: '#ffffff' }}
              >
                {deletingAccount ? 'Deleting Account...' : 'Delete Account'}
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </div>
  );
};
