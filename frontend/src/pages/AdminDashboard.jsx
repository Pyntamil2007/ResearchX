import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../services/adminService';
import { useToast } from '../context/ToastContext';
import {
  Users,
  ShieldCheck,
  FileStack,
  Sparkles,
  HardDrive,
  Activity,
  ArrowRight,
  UserPlus,
  Server,
  Layers,
  History,
  CheckCircle2,
  AlertTriangle,
  FolderKanban
} from 'lucide-react';

export const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  const fetchAdminStats = async () => {
    try {
      setLoading(true);
      const res = await adminService.getAdminDashboard();
      if (res.success && res.data) {
        setStats(res.data);
      }
    } catch (err) {
      toast.error('Failed to load administrator metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminStats();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <p>Loading administrator analytics & system health...</p>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-page" style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Header */}
      <div className="dashboard-header" style={{ marginBottom: 0 }}>
        <div className="dashboard-title-area">
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--primary)', fontWeight: 700, fontSize: '0.88rem', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
            <ShieldCheck size={16} />
            <span>Administrator Control Center</span>
          </div>
          <h1>System Administration Dashboard</h1>
          <p>Global system oversight, user access management, research repository metrics, and application audit history.</p>
        </div>
        <div className="dashboard-actions">
          <Link to="/admin/users" className="btn btn-primary" id="admin-manage-users-btn">
            <Users size={18} />
            <span>Manage Users</span>
          </Link>
          <Link to="/admin/papers" className="btn btn-secondary" id="admin-manage-papers-btn">
            <FileStack size={18} />
            <span>Manage Research Papers</span>
          </Link>
        </div>
      </div>

      {/* Global Stat Metrics (6 Cards) */}
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        {/* Total Users */}
        <div className="glass-panel stat-card" style={{ '--stat-color': '#a78bfa', '--stat-glow': 'rgba(139, 92, 246, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <Users size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Registered Users</span>
            <span className="stat-value">{stats?.total_users ?? 0}</span>
            <span className="stat-subtext">{stats?.active_users ?? 0} active accounts</span>
          </div>
        </div>

        {/* Active Accounts */}
        <div className="glass-panel stat-card" style={{ '--stat-color': '#38bdf8', '--stat-glow': 'rgba(56, 189, 248, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <CheckCircle2 size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Active Users</span>
            <span className="stat-value">{stats?.active_users ?? 0}</span>
            <span className="stat-subtext">{stats?.inactive_users ?? 0} deactivated</span>
          </div>
        </div>

        {/* Total Papers */}
        <div className="glass-panel stat-card" style={{ '--stat-color': 'var(--primary)', '--stat-glow': 'rgba(99, 102, 241, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <FileStack size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Research Papers</span>
            <span className="stat-value">{stats?.total_papers ?? 0}</span>
            <span className="stat-subtext">Across all user accounts</span>
          </div>
        </div>

        {/* Total Analyses */}
        <div className="glass-panel stat-card" style={{ '--stat-color': 'var(--accent)', '--stat-glow': 'rgba(6, 182, 212, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <Sparkles size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Analyses</span>
            <span className="stat-value">{stats?.total_analyses ?? 0}</span>
            <span className="stat-subtext">AI extraction runs</span>
          </div>
        </div>

        {/* Successful Analyses */}
        <div className="glass-panel stat-card" style={{ '--stat-color': '#10b981', '--stat-glow': 'rgba(16, 185, 129, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <ShieldCheck size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Completed Analyses</span>
            <span className="stat-value">{stats?.completed_analyses ?? (stats?.total_analyzed ?? 0)}</span>
            <span className="stat-subtext">Successfully processed</span>
          </div>
        </div>

        {/* System Storage */}
        <div className="glass-panel stat-card" style={{ '--stat-color': '#fbbf24', '--stat-glow': 'rgba(251, 191, 36, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <HardDrive size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Repository Storage</span>
            <span className="stat-value">{stats?.storage_used_formatted || '0.00 MB'}</span>
            <span className="stat-subtext">{stats?.total_papers ?? 0} stored PDF/image files</span>
          </div>
        </div>
      </div>

      {/* Quick Navigation Panels (3 Action Blocks) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div style={{ padding: 8, background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa', borderRadius: '8px' }}>
                <Users size={20} />
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: 0 }}>User Management</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
              View all user accounts, elevate roles to Administrator, and activate or deactivate user logins.
            </p>
          </div>
          <Link to="/admin/users" className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-start' }}>
            <span>Manage {stats?.total_users ?? 0} Users</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div style={{ padding: 8, background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)', borderRadius: '8px' }}>
                <FileStack size={20} />
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Paper Management</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
              Search, filter, and inspect research documents uploaded by all researchers across the institution.
            </p>
          </div>
          <Link to="/admin/papers" className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-start' }}>
            <span>View All {stats?.total_papers ?? 0} Papers</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div style={{ padding: 8, background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent)', borderRadius: '8px' }}>
                <History size={20} />
              </div>
              <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Analysis History</h3>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: 0 }}>
              Access full historical audit logs of analysis generations, document extractions, and user operations.
            </p>
          </div>
          <Link to="/history" className="btn btn-secondary btn-sm" style={{ alignSelf: 'flex-start' }}>
            <span>Inspect System History</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* 2-Column Section: Audit Stream & User Roster */}
      <div className="dashboard-grid-2" style={{ gap: '1.5rem' }}>
        {/* Recent Activity */}
        <div className="glass-panel" style={{ padding: '1.75rem' }}>
          <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ margin: 0 }}>Recent System Activity</h3>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <Activity size={14} />
              Live Audit Stream
            </span>
          </div>

          {!stats?.recent_activity || stats?.recent_activity?.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
              No system activity recorded yet.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {stats?.recent_activity?.map((act, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    borderRadius: '8px',
                    border: '1px solid var(--border-color)'
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-main)' }}>
                      {act.action}: <span style={{ color: 'var(--accent)' }}>{act.paper_title}</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                      Performed by <strong>{act.user_name}</strong>
                    </div>
                  </div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                    {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* User Roster */}
        <div className="glass-panel" style={{ padding: '1.75rem' }}>
          <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <h3 style={{ margin: 0 }}>Registered Accounts</h3>
            <Link to="/admin/users" style={{ fontSize: '0.85rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
              <span>View All</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {stats?.recent_users?.map((u) => (
              <div
                key={u.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-color)'
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{u.name}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.email}</div>
                </div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                  <span className={u.role === 'ADMIN' ? 'badge badge-admin' : 'badge badge-user'} style={{ fontSize: '0.7rem' }}>
                    {u.role}
                  </span>
                  <span className="badge badge-analyzed" style={{ fontSize: '0.7rem' }}>
                    {u.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
