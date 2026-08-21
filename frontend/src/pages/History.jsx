import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisService } from '../services/analysisService';
import { useToast } from '../context/ToastContext';
import { SearchBar } from '../components/SearchBar';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';
import { History as HistoryIcon, Sparkles, Trash2, Calendar, FileText, Search, AlertTriangle, ArrowRight } from 'lucide-react';

const ALL_DOMAINS = [
  'Artificial Intelligence',
  'Machine Learning',
  'Deep Learning',
  'Computer Vision',
  'Natural Language Processing',
  'Cybersecurity',
  'Data Science',
  'Software Engineering',
  'Cloud Computing',
  'Internet of Things',
  'Blockchain',
  'Robotics',
  'Healthcare',
  'Agriculture',
  'Education',
  'Finance',
  'Computer Networks',
  'Information Technology',
  'Database Systems',
  'Human-Computer Interaction',
  'Renewable Energy',
  'Environmental Science',
  'Biotechnology',
  'Physics',
  'Mathematics',
  'Business & Management',
  'Social Science',
  'Other'
];

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'title', label: 'Title (A-Z)' },
  { value: 'domain', label: 'Domain (A-Z)' }
];

export const History = () => {
  const [historyItems, setHistoryItems] = useState([]);
  const [meta, setMeta] = useState({ page: 1, limit: 10, total: 0, total_pages: 1 });
  const [search, setSearch] = useState('');
  const [domain, setDomain] = useState('all');
  const [status, setStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [itemToDelete, setItemToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const toast = useToast();

  const fetchHistory = async (pageNumber = 1, currentLimit = limit) => {
    try {
      setLoading(true);
      const res = await analysisService.getHistory({
        search: search.trim() || undefined,
        domain: domain !== 'all' ? domain : undefined,
        status: status !== 'all' ? status : undefined,
        sort_by: sortBy,
        page: pageNumber,
        limit: currentLimit
      });
      if (res.success && res.data) {
        setHistoryItems(res.data.items);
        setMeta(res.data.meta);
      }
    } catch (err) {
      toast.error('Failed to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchHistory(1, limit);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, domain, status, sortBy, limit]);

  const handleResetFilters = () => {
    setSearch('');
    setDomain('all');
    setStatus('all');
    setSortBy('newest');
    setLimit(10);
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    fetchHistory(1, newLimit);
  };

  const confirmDelete = async () => {
    if (!itemToDelete) return;
    setDeleting(true);
    try {
      await analysisService.deleteHistoryItem(itemToDelete.id);
      toast.success('History log removed.');
      setItemToDelete(null);
      fetchHistory(meta.page, limit);
    } catch (err) {
      toast.error('Failed to delete history record.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>Analysis History</h1>
          <p>Chronological log of all research documents analyzed in your workspace.</p>
        </div>
      </div>

      {/* Universal Search + Filter + Sort Bar */}
      <SearchBar
        search={search}
        onSearchChange={setSearch}
        domain={domain}
        onDomainChange={setDomain}
        domainsList={ALL_DOMAINS}
        status={status}
        onStatusChange={setStatus}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOptions={SORT_OPTIONS}
        onReset={handleResetFilters}
        placeholder="Search history by title, domain, author..."
      />

      {loading ? (
        <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
          <p>Loading analysis history records...</p>
        </div>
      ) : historyItems.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <HistoryIcon size={32} />
          </div>
          <h4>No analysis history found</h4>
          <p>Analyze your first research document to start keeping an interactive history log.</p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            <button className="btn btn-secondary btn-sm" onClick={handleResetFilters}>
              Reset Filters
            </button>
            <Link to="/upload" className="btn btn-primary btn-sm">
              <Sparkles size={16} />
              <span>Upload & Analyze Document</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document Title</th>
                <th>Domain</th>
                <th>Analysis Date</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {historyItems.map((item) => (
                <tr key={item.id}>
                  <td>
                    <Link
                      to={`/analysis/${item.analysis_id}`}
                      style={{ fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 2 }}
                    >
                      {item.paper_title}
                    </Link>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {item.authors}
                    </span>
                  </td>
                  <td>
                    <span className="domain-chip" style={{ fontSize: '0.74rem' }}>{item.domain}</span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <Calendar size={13} />
                      {new Date(item.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      <Link to={`/analysis/${item.analysis_id}`} className="btn btn-accent btn-sm" id={`open-report-${item.id}`}>
                        <Sparkles size={14} />
                        <span>Open Report</span>
                      </Link>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => setItemToDelete(item)}
                        title="Delete entry from history"
                        id={`delete-history-${item.id}`}
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
        onPageChange={(p) => fetchHistory(p, limit)}
        onLimitChange={handleLimitChange}
      />

      {/* Delete Modal */}
      <Modal
        isOpen={!!itemToDelete}
        onClose={() => setItemToDelete(null)}
        title="Delete Analysis History Record"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setItemToDelete(null)} disabled={deleting}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={confirmDelete} disabled={deleting} id="confirm-delete-history-btn">
              {deleting ? 'Deleting...' : 'Delete Record'}
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
              Remove this entry from your analysis history?
            </p>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              <strong>{itemToDelete?.paper_title}</strong>
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};
