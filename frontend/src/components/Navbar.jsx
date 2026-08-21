import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { NotificationBell } from './NotificationBell';
import { Menu, LogOut, User as UserIcon, Shield, Sparkles } from 'lucide-react';

export const Navbar = ({ onToggleSidebar }) => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogoutClick = () => {
    logout();
    navigate('/login');
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : name[0].toUpperCase();
  };

  return (
    <header className="navbar">
      <div className="navbar-left">
        <button
          className="mobile-menu-toggle"
          onClick={onToggleSidebar}
          aria-label="Open Navigation Sidebar"
        >
          <Menu size={22} />
        </button>
        <span className="navbar-brand-mobile">ResearchX</span>
      </div>

      <div className="navbar-right">
        {user && (
          <>
            {isAdmin && (
              <Link
                to="/admin/dashboard"
                className="btn btn-primary btn-sm"
                id="navbar-admin-panel-btn"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}
              >
                <Shield size={15} />
                <span>Admin Dashboard</span>
              </Link>
            )}

            {/* In-App Notification Bell Component */}
            <NotificationBell />

            <Link to="/profile" className="user-profile-pill">
              <div className="user-avatar">{getInitials(user.name)}</div>
              <div className="user-info-text">
                <span className="user-name">{user.name}</span>
                <span className="user-role-tag">
                  {isAdmin ? '🛡️ Administrator' : '🎓 Researcher'}
                </span>
              </div>
            </Link>

            <button
              className="btn btn-secondary btn-sm"
              onClick={handleLogoutClick}
              title="Logout from session"
              id="navbar-logout-btn"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          </>
        )}
      </div>
    </header>
  );
};
