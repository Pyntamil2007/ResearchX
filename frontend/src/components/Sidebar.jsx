import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  History as HistoryIcon,
  UserCheck,
  Users,
  ShieldCheck,
  FileStack,
  Sparkles,
  X
} from 'lucide-react';

export const Sidebar = ({ isOpen, onClose }) => {
  const { isAdmin } = useAuth();

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'active' : ''}`} onClick={onClose} />
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <Link to={isAdmin ? "/admin/dashboard" : "/dashboard"} className="brand-logo" onClick={onClose}>
            <div className="brand-icon">
              <Sparkles size={20} />
            </div>
            <span>Research<span className="brand-accent">X</span></span>
          </Link>
          <button className="modal-close-btn mobile-menu-toggle" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {isAdmin ? (
            <>
              <span className="sidebar-section-title">Admin Management</span>
              
              <NavLink
                to="/admin/dashboard"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-admin-dashboard"
              >
                <ShieldCheck size={18} />
                <span>Administrator Dashboard</span>
              </NavLink>

              <NavLink
                to="/admin/users"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-admin-users"
              >
                <Users size={18} />
                <span>User Management</span>
              </NavLink>

              <NavLink
                to="/admin/papers"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-admin-papers"
              >
                <FileStack size={18} />
                <span>Paper Management</span>
              </NavLink>

              <span className="sidebar-section-title">Research Tools</span>

              <NavLink
                to="/upload"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-upload"
              >
                <UploadCloud size={18} />
                <span>Upload & Analyze</span>
              </NavLink>

              <NavLink
                to="/papers"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-papers"
              >
                <FileText size={18} />
                <span>All Research Papers</span>
              </NavLink>

              <NavLink
                to="/history"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-history"
              >
                <HistoryIcon size={18} />
                <span>Analysis History</span>
              </NavLink>

              <NavLink
                to="/profile"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-profile"
              >
                <UserCheck size={18} />
                <span>Profile & Account</span>
              </NavLink>
            </>
          ) : (
            <>
              <span className="sidebar-section-title">Researcher Workspace</span>
              
              <NavLink
                to="/dashboard"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-dashboard"
              >
                <LayoutDashboard size={18} />
                <span>User Dashboard</span>
              </NavLink>

              <NavLink
                to="/upload"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-upload"
              >
                <UploadCloud size={18} />
                <span>Upload Paper</span>
              </NavLink>

              <NavLink
                to="/papers"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-papers"
              >
                <FileText size={18} />
                <span>My Research Papers</span>
              </NavLink>

              <NavLink
                to="/history"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-history"
              >
                <HistoryIcon size={18} />
                <span>Analysis History</span>
              </NavLink>

              <NavLink
                to="/profile"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                onClick={onClose}
                id="nav-profile"
              >
                <UserCheck size={18} />
                <span>Profile & Account</span>
              </NavLink>
            </>
          )}
        </nav>
      </aside>
    </>
  );
};
