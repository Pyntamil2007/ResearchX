import React, { useState, useEffect, useRef } from 'react';
import { notificationService } from '../services/notificationService';
import {
  Bell,
  Check,
  CheckCheck,
  Trash2,
  X,
  FileText,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Key,
  BarChart3,
  UserCheck,
  UserX,
  Clock,
  BellOff,
  Cpu
} from 'lucide-react';

export const NotificationBell = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // 'all' or 'unread'
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  const fetchNotifications = async () => {
    try {
      const res = await notificationService.getNotifications(false, 50);
      if (res.success && res.data) {
        setNotifications(res.data.items || []);
        setUnreadCount(res.data.unread_count || 0);
        setTotalCount(res.data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    }
  };

  useEffect(() => {
    fetchNotifications();

    // Poll for new notifications every 15 seconds
    const interval = setInterval(fetchNotifications, 15000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on click outside or escape key
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleMarkAsRead = async (id, e) => {
    e.stopPropagation();
    try {
      await notificationService.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err);
    }
  };

  const handleDeleteNotification = async (id, e) => {
    e.stopPropagation();
    try {
      await notificationService.deleteNotification(id);
      const target = notifications.find((n) => n.id === id);
      if (target && !target.is_read) {
        setUnreadCount((prev) => Math.max(0, prev - 1));
      }
      setNotifications((prev) => prev.filter((n) => n.id !== id));
      setTotalCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to delete notification:', err);
    }
  };

  const handleClearAll = async () => {
    try {
      await notificationService.clearAll();
      setNotifications([]);
      setUnreadCount(0);
      setTotalCount(0);
    } catch (err) {
      console.error('Failed to clear notifications:', err);
    }
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString.endsWith('Z') ? dateString : `${dateString}Z`);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 30) return 'Just now';
    if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;

    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getNotificationVisuals = (type) => {
    switch (type) {
      case 'paper_uploaded':
      case 'admin_paper_uploaded':
        return {
          icon: <FileText size={16} />,
          color: '#6366f1',
          bg: 'rgba(99, 102, 241, 0.15)',
          badge: 'Paper'
        };
      case 'analysis_started':
        return {
          icon: <Cpu size={16} />,
          color: '#06b6d4',
          bg: 'rgba(6, 182, 212, 0.15)',
          badge: 'Processing'
        };
      case 'analysis_completed':
      case 'admin_analysis_completed':
        return {
          icon: <CheckCircle2 size={16} />,
          color: '#10b981',
          bg: 'rgba(16, 185, 129, 0.15)',
          badge: 'Completed'
        };
      case 'report_generated':
        return {
          icon: <BarChart3 size={16} />,
          color: '#8b5cf6',
          bg: 'rgba(139, 92, 246, 0.15)',
          badge: 'Report'
        };
      case 'analysis_failed':
      case 'admin_analysis_failed':
        return {
          icon: <AlertTriangle size={16} />,
          color: '#ef4444',
          bg: 'rgba(239, 68, 68, 0.15)',
          badge: 'Failed'
        };
      case 'account_created':
      case 'admin_new_user':
        return {
          icon: <UserCheck size={16} />,
          color: '#3b82f6',
          bg: 'rgba(59, 130, 246, 0.15)',
          badge: 'Account'
        };
      case 'password_changed':
        return {
          icon: <Key size={16} />,
          color: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.15)',
          badge: 'Security'
        };
      case 'admin_user_deleted':
        return {
          icon: <UserX size={16} />,
          color: '#f43f5e',
          bg: 'rgba(244, 63, 94, 0.15)',
          badge: 'Deleted'
        };
      default:
        return {
          icon: <Sparkles size={16} />,
          color: 'var(--primary)',
          bg: 'rgba(99, 102, 241, 0.15)',
          badge: 'Notice'
        };
    }
  };

  const displayedNotifications =
    activeTab === 'unread'
      ? notifications.filter((n) => !n.is_read)
      : notifications;

  return (
    <div className="notification-bell-wrapper" ref={dropdownRef} style={{ position: 'relative' }}>
      {/* 🔔 Notification Bell Button */}
      <button
        type="button"
        className={`notification-bell-btn ${unreadCount > 0 ? 'has-unread' : ''}`}
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) fetchNotifications();
        }}
        aria-label="View notifications"
        id="notification-bell-btn"
        title={unreadCount > 0 ? `${unreadCount} unread notification(s)` : 'Notifications'}
      >
        <Bell size={20} className={unreadCount > 0 ? 'bell-icon-pulse' : ''} />
        {unreadCount > 0 && (
          <span className="notification-badge" id="notification-unread-badge">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Interactive Notification Panel Dropdown */}
      {isOpen && (
        <div className="notification-panel animate-fade-in" id="notification-dropdown-panel">
          {/* Header */}
          <div className="notification-panel-header">
            <div className="notification-panel-title">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1rem', fontWeight: 700 }}>Notifications</span>
                {unreadCount > 0 && (
                  <span className="badge badge-primary" style={{ fontSize: '0.72rem', padding: '2px 8px' }}>
                    {unreadCount} new
                  </span>
                )}
              </div>
              <button
                type="button"
                className="btn-icon btn-sm"
                onClick={() => setIsOpen(false)}
                title="Close panel"
                style={{ color: 'var(--text-muted)' }}
              >
                <X size={16} />
              </button>
            </div>

            {/* Quick Actions & Tabs */}
            <div className="notification-tabs-actions">
              <div className="notification-tabs">
                <button
                  type="button"
                  className={`notification-tab-btn ${activeTab === 'all' ? 'active' : ''}`}
                  onClick={() => setActiveTab('all')}
                  id="tab-all-notifications"
                >
                  All ({totalCount})
                </button>
                <button
                  type="button"
                  className={`notification-tab-btn ${activeTab === 'unread' ? 'active' : ''}`}
                  onClick={() => setActiveTab('unread')}
                  id="tab-unread-notifications"
                >
                  Unread ({unreadCount})
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {unreadCount > 0 && (
                  <button
                    type="button"
                    className="notification-action-btn"
                    onClick={handleMarkAllAsRead}
                    title="Mark all as read"
                    id="mark-all-read-btn"
                  >
                    <CheckCheck size={14} />
                    <span>Mark all read</span>
                  </button>
                )}
                {totalCount > 0 && (
                  <button
                    type="button"
                    className="notification-action-btn notification-action-clear"
                    onClick={handleClearAll}
                    title="Clear all notifications"
                    id="clear-all-notifications-btn"
                  >
                    <Trash2 size={14} />
                    <span>Clear</span>
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* List Content */}
          <div className="notification-list-scroll custom-scrollbar">
            {displayedNotifications.length === 0 ? (
              <div className="notification-empty-state">
                <div className="notification-empty-icon">
                  <BellOff size={28} />
                </div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                  {activeTab === 'unread' ? 'No unread notifications' : 'No notifications yet'}
                </h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {activeTab === 'unread'
                    ? "You're all caught up! Great work."
                    : 'System alerts and paper analysis updates will appear here.'}
                </p>
              </div>
            ) : (
              displayedNotifications.map((notif) => {
                const visual = getNotificationVisuals(notif.notification_type);
                return (
                  <div
                    key={notif.id}
                    className={`notification-item ${!notif.is_read ? 'unread' : 'read'}`}
                    id={`notification-item-${notif.id}`}
                  >
                    <div
                      className="notification-icon-wrapper"
                      style={{
                        color: visual.color,
                        background: visual.bg
                      }}
                    >
                      {visual.icon}
                    </div>

                    <div className="notification-content">
                      <div className="notification-item-header">
                        <span className="notification-title">{notif.title}</span>
                        {!notif.is_read && <span className="notification-unread-dot" title="Unread notification" />}
                      </div>
                      <p className="notification-message">{notif.message}</p>
                      <div className="notification-footer">
                        <span className="notification-time">
                          <Clock size={11} style={{ display: 'inline', marginRight: '3px' }} />
                          {formatTimeAgo(notif.created_at)}
                        </span>
                        <span
                          className="notification-type-pill"
                          style={{
                            color: visual.color,
                            borderColor: visual.color + '40'
                          }}
                        >
                          {visual.badge}
                        </span>
                      </div>
                    </div>

                    {/* Per-item controls */}
                    <div className="notification-item-actions">
                      {!notif.is_read && (
                        <button
                          type="button"
                          className="notification-item-btn"
                          onClick={(e) => handleMarkAsRead(notif.id, e)}
                          title="Mark as read"
                          id={`mark-read-btn-${notif.id}`}
                        >
                          <Check size={14} />
                        </button>
                      )}
                      <button
                        type="button"
                        className="notification-item-btn notification-item-delete"
                        onClick={(e) => handleDeleteNotification(notif.id, e)}
                        title="Delete notification"
                        id={`delete-notif-btn-${notif.id}`}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};
