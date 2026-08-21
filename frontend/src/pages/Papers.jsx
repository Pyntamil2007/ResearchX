import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { paperService } from '../services/paperService';
import { analysisService } from '../services/analysisService';
import { useToast } from '../context/ToastContext';
import { PaperCard } from '../components/PaperCard';
import { SearchBar } from '../components/SearchBar';
import { Pagination } from '../components/Pagination';
import { Modal } from '../components/Modal';
import {
  FileText,
  UploadCloud,
  LayoutGrid,
  List,
  Sparkles,
  Trash2,
  Download,
  AlertTriangle,
  BookOpen
} from 'lucide-react';

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

export const Papers = () => {
  const [papers, setPapers] = useState([]);
  const [meta, setMeta] = useState({ page: 1, limit: 10, total: 0, total_pages: 1 });
  const [search, setSearch] = useState('');
  const [domain, setDomain] = useState('all');
  const [documentType, setDocumentType] = useState('all');
  const [status, setStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [limit, setLimit] = useState(10);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [loading, setLoading] = useState(true);
  const [analyzingId, setAnalyzingId] = useState(null);

  // Delete modal state
  const [paperToDelete, setPaperToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  const fetchPapers = async (pageNumber = 1, currentLimit = limit) => {
    try {
      setLoading(true);
      const res = await paperService.getPapers({
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
      toast.error('Failed to load research papers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPapers(1, limit);
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
    fetchPapers(1, newLimit);
  };

  const handleAnalyze = async (paperId) => {
    try {
      setAnalyzingId(paperId);
      toast.info('Starting AI / NLP analysis...');
      const res = await analysisService.analyzePaper(paperId);
      if (res.success && res.data) {
        toast.success('Paper analyzed successfully!');
        navigate(`/analysis/${res.data.analysis_id}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed.');
    } finally {
      setAnalyzingId(null);
      fetchPapers(meta.page, limit);
    }
  };

  const confirmDelete = async () => {
    if (!paperToDelete) return;
    setDeleting(true);
    try {
      await paperService.deletePaper(paperToDelete.id);
      toast.success(`'${paperToDelete.title}' deleted successfully.`);
      setPaperToDelete(null);
      fetchPapers(meta.page, limit);
    } catch (err) {
      toast.error('Failed to delete paper.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>Research Papers Explorer</h1>
          <p>Browse, inspect, filter, sort, and analyze research papers and documents in your workspace.</p>
        </div>
        <div className="dashboard-actions">
          <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', padding: 3, gap: 3 }}>
            <button
              className={`btn btn-sm ${viewMode === 'grid' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('grid')}
              style={{ padding: '6px 10px' }}
              title="Grid View"
            >
              <LayoutGrid size={16} />
            </button>
            <button
              className={`btn btn-sm ${viewMode === 'table' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('table')}
              style={{ padding: '6px 10px' }}
              title="Table View"
            >
              <List size={16} />
            </button>
          </div>

          <Link to="/upload" className="btn btn-primary" id="papers-new-upload-btn">
            <UploadCloud size={16} />
            <span>Upload Document</span>
          </Link>
        </div>
      </div>

      {/* Universal Search + Filter + Sort Bar */}
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
        placeholder="Search by title, author, keyword, or filename..."
      />

      {/* Papers Content */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
          <p>Loading research papers and documents...</p>
        </div>
      ) : papers.length === 0 ? (
        <div className="glass-panel empty-state">
          <div className="empty-state-icon">
            <FileText size={32} />
          </div>
          <h4>No research documents found</h4>
          <p>Try clearing your search filters or upload a new research document to begin analyzing.</p>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
            <button className="btn btn-secondary btn-sm" onClick={handleResetFilters}>
              Reset Filters
            </button>
            <Link to="/upload" className="btn btn-primary btn-sm">
              <UploadCloud size={16} />
              <span>Upload Document</span>
            </Link>
          </div>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="papers-grid">
          {papers.map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              onAnalyze={handleAnalyze}
              onDelete={(p) => setPaperToDelete(p)}
              isAnalyzing={analyzingId === paper.id}
            />
          ))}
        </div>
      ) : (
        /* Table View */
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document Title</th>
                <th>Domain</th>
                <th>Type</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {papers.map((paper) => (
                <tr key={paper.id}>
                  <td>
                    <Link
                      to={`/papers/${paper.id}`}
                      style={{ fontWeight: 600, color: 'var(--text-main)', display: 'block', marginBottom: 2 }}
                    >
                      {paper.title}
                    </Link>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {paper.authors}
                    </span>
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
                    <span className={`badge badge-${paper.status.toLowerCase()}`}>
                      {paper.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
                    {new Date(paper.uploaded_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: 6 }}>
                      {paper.status === 'Analyzed' && paper.latest_analysis_id ? (
                        <Link to={`/analysis/${paper.latest_analysis_id}`} className="btn btn-accent btn-sm">
                          <Sparkles size={14} />
                          <span>View Report</span>
                        </Link>
                      ) : (
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleAnalyze(paper.id)}
                          disabled={analyzingId === paper.id}
                        >
                          <Sparkles size={14} />
                          <span>{analyzingId === paper.id ? 'Analyzing...' : 'Analyze'}</span>
                        </button>
                      )}
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => setPaperToDelete(paper)}
                        title="Delete paper"
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
        onPageChange={(p) => fetchPapers(p, limit)}
        onLimitChange={handleLimitChange}
      />

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!paperToDelete}
        onClose={() => setPaperToDelete(null)}
        title="Confirm Document Deletion"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setPaperToDelete(null)} disabled={deleting}>
              Cancel
            </button>
            <button className="btn btn-danger" onClick={confirmDelete} disabled={deleting} id="confirm-delete-btn">
              {deleting ? 'Deleting...' : 'Delete Document'}
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
              Are you sure you want to delete '{paperToDelete?.title}'?
            </p>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              This will permanently remove the uploaded document file, raw extracted text, and all associated interactive analysis reports and extracted metrics.
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
};
