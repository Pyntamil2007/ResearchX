import React, { useState, useEffect } from 'react';
import { adminService } from '../services/adminService';
import { useToast } from '../context/ToastContext';
import { useAuth } from '../context/AuthContext';
import { Pagination } from '../components/Pagination';
import { SearchBar } from '../components/SearchBar';
import { Modal } from '../components/Modal';
import { PasswordInput } from '../components/PasswordInput';
import {
  Users as UsersIcon,
  UserPlus,
  Search,
  Trash2,
  Edit,
  Shield,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  User,
  KeyRound
} from 'lucide-react';

export const Users = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [meta, setMeta] = useState({ page: 1, limit: 10, total: 0, total_pages: 1 });
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isResetPasswordOpen, setIsResetPasswordOpen] = useState(false);
  const [userToEdit, setUserToEdit] = useState(null);
  const [userToDelete, setUserToDelete] = useState(null);
  const [userToReset, setUserToReset] = useState(null);
  const [resetPasswordVal, setResetPasswordVal] = useState('');
  const [resetPasswordConfirmVal, setResetPasswordConfirmVal] = useState('');
  const [saving, setSaving] = useState(false);

  // Create form state
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('USER');

  // Edit form state
  const [editName, setEditName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editRole, setEditRole] = useState('USER');
  const [editStatus, setEditStatus] = useState('active');
  const [editPassword, setEditPassword] = useState('');

  const toast = useToast();

  const USER_SORT_OPTIONS = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'name', label: 'Name (A-Z)' },
    { value: 'email', label: 'Email (A-Z)' },
    { value: 'role', label: 'Role (Admin First)' }
  ];

  const fetchUsers = async (pageNumber = 1, currentLimit = limit) => {
    try {
      setLoading(true);
      const res = await adminService.getUsers({
        search: search.trim() || undefined,
        role: roleFilter !== 'all' ? roleFilter : undefined,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        sort_by: sortBy,
        page: pageNumber,
        limit: currentLimit
      });
      if (res.success && res.data) {
        setUsers(res.data.items);
        setMeta(res.data.meta);
      }
    } catch (err) {
      toast.error('Failed to load user accounts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers(1, limit);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, roleFilter, statusFilter, sortBy, limit]);

  const handleResetFilters = () => {
    setSearch('');
    setRoleFilter('all');
    setStatusFilter('all');
    setSortBy('newest');
    setLimit(10);
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    fetchUsers(1, newLimit);
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    if (!newName || !newEmail || !newPassword) {
      toast.warning('Please provide name, email, and password.');
      return;
    }
    setSaving(true);
    try {
      const res = await adminService.createUser({
        name: newName.trim(),
        email: newEmail.trim(),
        password: newPassword,
        role: newRole,
        status: 'active'
      });
      if (res.success) {
        toast.success(`User '${newName}' created successfully.`);
        setIsCreateOpen(false);
        setNewName('');
        setNewEmail('');
        setNewPassword('');
        fetchUsers(meta.page);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create user.');
    } finally {
      setSaving(false);
    }
  };

  const openEditModal = (user) => {
    setUserToEdit(user);
    setEditName(user.name);
    setEditEmail(user.email);
    setEditRole(user.role);
    setEditStatus(user.status);
    setEditPassword('');
    setIsEditOpen(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!userToEdit) return;
    setSaving(true);
    try {
      const payload = {
        name: editName.trim(),
        email: editEmail.trim(),
        role: editRole,
        status: editStatus
      };
      if (editPassword.trim()) payload.password = editPassword.trim();

      const res = await adminService.updateUser(userToEdit.id, payload);
      if (res.success) {
        toast.success(`User '${editName}' updated successfully.`);
        setIsEditOpen(false);
        fetchUsers(meta.page);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update user.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleStatus = async (user) => {
    const nextStatus = user.status === 'active' ? 'inactive' : 'active';
    try {
      await adminService.updateUserStatus(user.id, nextStatus);
      toast.success(`User ${user.name} marked as ${nextStatus}.`);
      fetchUsers(meta.page);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update status.');
    }
  };

  const handleToggleRole = async (user) => {
    const nextRole = user.role === 'ADMIN' ? 'USER' : 'ADMIN';
    try {
      await adminService.updateUserRole(user.id, nextRole);
      toast.success(`User ${user.name} role changed to ${nextRole}.`);
      fetchUsers(meta.page);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to update role.');
    }
  };

  const openResetPasswordModal = (user) => {
    setUserToReset(user);
    setResetPasswordVal('');
    setResetPasswordConfirmVal('');
    setIsResetPasswordOpen(true);
  };

  const handleResetPasswordSubmit = async (e) => {
    e.preventDefault();
    if (!userToReset) return;
    if (resetPasswordVal.length < 6) {
      toast.warning('Password must be at least 6 characters.');
      return;
    }
    if (resetPasswordVal !== resetPasswordConfirmVal) {
      toast.warning('Passwords do not match.');
      return;
    }
    setSaving(true);
    try {
      const res = await adminService.resetUserPassword(userToReset.id, resetPasswordVal);
      if (res.success) {
        toast.success(`Password for ${userToReset.name} has been securely reset.`);
        setIsResetPasswordOpen(false);
        setResetPasswordVal('');
        setResetPasswordConfirmVal('');
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to reset password.');
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!userToDelete) return;
    setSaving(true);
    try {
      await adminService.deleteUser(userToDelete.id);
      toast.success(`User '${userToDelete.name}' deleted.`);
      setUserToDelete(null);
      fetchUsers(meta.page);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to delete user.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>User Management</h1>
          <p>Create, update, activate/deactivate, and manage system users and authorization roles.</p>
        </div>
        <div className="dashboard-actions">
          <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)} id="admin-create-user-btn">
            <UserPlus size={16} />
            <span>Create New User</span>
          </button>
        </div>
      </div>

      {/* Universal Search + Filter + Sort Bar */}
      <SearchBar
        search={search}
        onSearchChange={setSearch}
        role={roleFilter}
        onRoleChange={setRoleFilter}
        status={statusFilter}
        onStatusChange={setStatusFilter}
        statusesList={[
          { value: 'active', label: 'Active' },
          { value: 'inactive', label: 'Inactive' }
        ]}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOptions={USER_SORT_OPTIONS}
        onReset={handleResetFilters}
        placeholder="Search users by name or email..."
      />

      {/* Users Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
          <p>Loading user accounts...</p>
        </div>
      ) : users.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <UsersIcon size={32} />
          </div>
          <h4>No matching users found</h4>
          <p>Try clearing your filters or create a new user account.</p>
          <button className="btn btn-secondary btn-sm" onClick={handleResetFilters}>
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Status</th>
                <th>Registered</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{u.name}</div>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{u.email}</div>
                  </td>
                  <td>
                    <span className={u.role === 'ADMIN' ? 'badge badge-admin' : 'badge badge-user'}>
                      {u.role}
                    </span>
                  </td>
                  <td>
                    <span className={u.status === 'active' ? 'badge badge-analyzed' : 'badge badge-failed'}>
                      {u.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      {/* Reset Password */}
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openResetPasswordModal(u)}
                        title="Reset User Password"
                        id={`reset-pwd-btn-${u.id}`}
                      >
                        <KeyRound size={14} />
                      </button>

                      {/* Toggle Status */}
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleToggleStatus(u)}
                        disabled={u.id === currentUser?.id}
                        title={u.status === 'active' ? 'Deactivate account' : 'Activate account'}
                        id={`toggle-status-btn-${u.id}`}
                      >
                        {u.status === 'active' ? (
                          <CheckCircle2 size={14} color="var(--success)" />
                        ) : (
                          <XCircle size={14} color="var(--danger)" />
                        )}
                      </button>

                      {/* Edit */}
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openEditModal(u)}
                        title="Edit user details"
                        id={`edit-user-btn-${u.id}`}
                      >
                        <Edit size={14} />
                      </button>

                      {/* Delete */}
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => setUserToDelete(u)}
                        disabled={u.id === currentUser?.id}
                        title="Delete user"
                        id={`delete-user-btn-${u.id}`}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      <Pagination
        currentPage={meta.page}
        totalPages={meta.total_pages}
        totalItems={meta.total}
        limit={meta.limit}
        onPageChange={(p) => fetchUsers(p, limit)}
        onLimitChange={handleLimitChange}
      />

      {/* Create User Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create New User"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsCreateOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleCreateSubmit} disabled={saving} id="confirm-create-user-btn">
              {saving ? 'Creating...' : 'Create User'}
            </button>
          </>
        }
      >
        <form onSubmit={handleCreateSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g. Marie Curie"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="e.g. marie.curie@research.org"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <PasswordInput
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min 6 characters"
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Authorization Role</label>
            <select
              className="form-select"
              value={newRole}
              onChange={(e) => setNewRole(e.target.value)}
            >
              <option value="USER">User / Researcher</option>
              <option value="ADMIN">System Administrator</option>
            </select>
          </div>
        </form>
      </Modal>

      {/* Edit User Modal */}
      <Modal
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        title={`Edit User: ${userToEdit?.name}`}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsEditOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleEditSubmit} disabled={saving} id="confirm-edit-user-btn">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </>
        }
      >
        <form onSubmit={handleEditSubmit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input
              type="text"
              className="form-input"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              value={editEmail}
              onChange={(e) => setEditEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Change Password (Optional)</label>
            <PasswordInput
              placeholder="Leave blank to keep existing password"
              value={editPassword}
              onChange={(e) => setEditPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Role</label>
            <select
              className="form-select"
              value={editRole}
              onChange={(e) => setEditRole(e.target.value)}
              disabled={userToEdit?.id === currentUser?.id}
            >
              <option value="USER">User / Researcher</option>
              <option value="ADMIN">System Administrator</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Status</label>
            <select
              className="form-select"
              value={editStatus}
              onChange={(e) => setEditStatus(e.target.value)}
              disabled={userToEdit?.id === currentUser?.id}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </form>
      </Modal>

      {/* Delete User Modal */}
      <Modal
        isOpen={!!userToDelete}
        onClose={() => setUserToDelete(null)}
        title="Confirm User Deletion"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setUserToDelete(null)} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={confirmDelete} disabled={saving} id="confirm-delete-user-btn">
              {saving ? 'Deleting...' : 'Delete User'}
            </button>
          </>
        }
      >
        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            background: 'var(--danger-bg)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--danger)',
            flexShrink: 0
          }}>
            <AlertTriangle size={20} />
          </div>
          <div>
            <p style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: 6 }}>
              Are you sure you want to delete user account '{userToDelete?.name}'?
            </p>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              {userToDelete?.email}
            </p>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: 8 }}>
              This action is permanent and will cascade delete all uploaded papers and analysis history owned by this user.
            </p>
          </div>
        </div>
      </Modal>

      {/* Reset Password Modal */}
      <Modal
        isOpen={isResetPasswordOpen}
        onClose={() => setIsResetPasswordOpen(false)}
        title={`Reset Password for: ${userToReset?.name}`}
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setIsResetPasswordOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleResetPasswordSubmit} disabled={saving} id="confirm-reset-pwd-btn">
              {saving ? 'Resetting...' : 'Set New Password'}
            </button>
          </>
        }
      >
        <form onSubmit={handleResetPasswordSubmit}>
          <div style={{ marginBottom: '1.25rem', padding: '10px 14px', background: 'rgba(245, 158, 11, 0.08)', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.25)', fontSize: '0.85rem', color: '#fbbf24' }}>
            Enter a new password for <strong>{userToReset?.email}</strong>. For security, existing passwords are never retrievable or displayed.
          </div>

          <div className="form-group">
            <label className="form-label">New Password</label>
            <PasswordInput
              value={resetPasswordVal}
              onChange={(e) => setResetPasswordVal(e.target.value)}
              placeholder="Min 6 characters"
              required
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirm New Password</label>
            <PasswordInput
              value={resetPasswordConfirmVal}
              onChange={(e) => setResetPasswordConfirmVal(e.target.value)}
              placeholder="Repeat new password"
              required
              autoComplete="new-password"
            />
          </div>
        </form>
      </Modal>
    </div>
  );
};
