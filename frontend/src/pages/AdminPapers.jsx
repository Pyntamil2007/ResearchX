import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminService } from '../services/adminService';
import { useToast } from '../context/ToastContext';
import { SearchBar } from '../components/SearchBar';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';
import { FileStack, Trash2, Sparkles, FileText, Download, AlertTriangle, User } from 'lucide-react';

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

const DOCUMENT_TYPES = [
  'Research Paper',
  'Review Paper',
  'Conference Paper',
  'Journal Paper',
  'Academic Book',
  'Book Chapter',
  'Technical Report',
  'Academic Document'
];

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'alphabetical', label: 'Title (A-Z)' },
  { value: 'domain', label: 'Domain (A-Z)' },
  { value: 'author', label: 'Author (A-Z)' }
];

export const AdminPapers = () => {
  const [papers, setPapers] = useState([]);
  const [meta, setMeta] = useState({ page: 1, limit: 10, total: 0, total_pages: 1 });
  const [search, setSearch] = useState('');
  const [domain, setDomain] = useState('all');
  const [documentType, setDocumentType] = useState('all');
  const [status, setStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [paperToDelete, setPaperToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const toast = useToast();

  const fetchAllPapers = async (pageNumber = 1, currentLimit = limit) => {
    try {
      setLoading(true);
      const res = await adminService.getAllPapers({
        search: search.trim() || undefined,
        domain: domain !== 'all' ? domain : undefined,
        document_type: documentType !== 'all' ? documentType : undefined,
        status: status !== 'all' ? status : undefined,
        sort_by: sortBy,
        page: pageNumber,
        limit: currentLimit
      });
      if (res.success && res.data) {
        setPapers(res.data.items);
        setMeta(res.data.meta);
      }
    } catch (err) {
      toast.error('Failed to load system research papers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchAllPapers(1, limit);
    }, 250);
    return () => clearTimeout(timer);
  }, [search, domain, documentType, status, sortBy, limit]);

  const handleResetFilters = () => {
    setSearch('');
    setDomain('all');
    setDocumentType('all');
    setStatus('all');
    setSortBy('newest');
    setLimit(10);
  };

  const handleLimitChange = (newLimit) => {
    setLimit(newLimit);
    fetchAllPapers(1, newLimit);
  };

  const confirmDelete = async () => {
    if (!paperToDelete) return;
    setDeleting(true);
    try {
      await adminService.deletePaper(paperToDelete.id);
      toast.success(`'${paperToDelete.title}' removed by administrator.`);
      setPaperToDelete(null);
      fetchAllPapers(meta.page, limit);
    } catch (err) {
      toast.error('Failed to delete paper.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>All Research Papers (Admin)</h1>
          <p>Global oversight of all research papers uploaded by any user in the system.</p>
        </div>
      </div>

      <SearchBar
        search={search}
        onSearchChange={setSearch}
        domain={domain}
        onDomainChange={setDomain}
        domainsList={ALL_DOMAINS}
        documentType={documentType}
        onDocumentTypeChange={setDocumentType}
        documentTypesList={DOCUMENT_TYPES}
        status={status}
        onStatusChange={setStatus}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        sortOptions={SORT_OPTIONS}
        onReset={handleResetFilters}
        placeholder="Search by title, author, user name or email..."
      />

      {loading ? (
        <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
          <p>Loading all research papers...</p>
        </div>
      ) : papers.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <FileStack size={32} />
          </div>
          <h4>No research papers found</h4>
          <p>Try adjusting your search criteria or domain filters.</p>
          <button className="btn btn-secondary btn-sm" onClick={handleResetFilters}>
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Paper Title</th>
                <th>Owner / Researcher</th>
                <th>Domain</th>
                <th>Type</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th style={{ textAlign: 'right' }}>Admin Actions</th>
              </tr>
            </thead>
            <tbody>
              {papers.map((paper) => (
                <tr key={paper.id}>
                  <td>
                    <Link to={`/papers/${paper.id}`} style={{ fontWeight: 600, color: 'var(--text-main)', display: 'block' }}>
                      {paper.title}
                    </Link>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {paper.authors}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <User size={13} color="var(--text-dim)" />
                      <span style={{ fontWeight: 500 }}>{paper.user_name || 'User #' + paper.user_id}</span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{paper.user_email}</div>
                  </td>
                  <td>
                    <span className="domain-chip" style={{ fontSize: '0.74rem' }}>{paper.domain}</span>
                  </td>
                  <td>
                    <span className="badge badge-admin" style={{ fontSize: '0.7rem' }}>
                      {paper.document_type || 'Research Paper'}
                    </span>
                  </td>
                  <td>
                    {paper.status === 'Analyzed' && <span className="badge badge-analyzed">Analyzed</span>}
                    {paper.status === 'Processing' && <span className="badge badge-processing">Processing</span>}
                    {paper.status === 'Uploaded' && <span className="badge badge-uploaded">Uploaded</span>}
                    {paper.status === 'Failed' && <span className="badge badge-failed">Failed</span>}
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                    {new Date(paper.uploaded_at).toLocaleDateString()}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      {paper.status === 'Analyzed' && paper.latest_analysis_id && (
                        <Link to={`/analysis/${paper.latest_analysis_id}`} className="btn btn-accent btn-sm">
                          <Sparkles size={14} />
                          <span>Report</span>
                        </Link>
                      )}
                      <Link to={`/papers/${paper.id}`} className="btn btn-secondary btn-sm" title="Inspect">
                        <FileText size={14} />
                      </Link>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => setPaperToDelete(paper)}
                        title="Delete paper (Admin)"
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

      <Pagination
        currentPage={meta.page}
        totalPages={meta.total_pages}
        totalItems={meta.total}
        limit={meta.limit}
        onPageChange={(p) => fetchAllPapers(p, limit)}
        onLimitChange={handleLimitChange}
      />

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!paperToDelete}
        onClose={() => setPaperToDelete(null)}
        title="Admin: Confirm Paper Deletion"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setPaperToDelete(null)} disabled={deleting}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={confirmDelete} disabled={deleting} id="admin-confirm-delete-btn">
              {deleting ? 'Deleting...' : 'Permanently Delete Paper'}
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
              Delete paper '{paperToDelete?.title}' uploaded by {paperToDelete?.user_name}?
            </p>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
              This will remove the file from storage and remove all associated analyses.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};
