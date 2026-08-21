import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Sparkles, Trash2, Download, Calendar, User as UserIcon, ArrowRight } from 'lucide-react';
import { paperService } from '../services/paperService';

export const PaperCard = ({ paper, onAnalyze, onDelete, isAnalyzing = false }) => {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'Analyzed':
        return <span className="badge badge-analyzed">Analyzed</span>;
      case 'Processing':
        return <span className="badge badge-processing">Processing</span>;
      case 'Failed':
        return <span className="badge badge-failed">Failed</span>;
      default:
        return <span className="badge badge-uploaded">Uploaded</span>;
    }
  };

  const formattedDate = new Date(paper.uploaded_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  return (
    <div className="glass-panel paper-card">
      <div>
        <div className="paper-card-header">
          <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
            {getStatusBadge(paper.status)}
            <span className="badge badge-user" style={{ fontSize: '0.7rem' }}>
              {paper.document_type || 'Research Paper'}
            </span>
          </div>
          <span className="domain-chip" style={{ fontSize: '0.74rem' }}>{paper.domain}</span>
        </div>

        <h3 className="paper-card-title" title={paper.title}>
          <Link to={`/papers/${paper.id}`} style={{ color: 'inherit' }}>
            {paper.title}
          </Link>
        </h3>

        <p className="paper-card-authors" title={paper.authors}>
          {paper.authors || 'Information not available in the paper.'}
        </p>
      </div>

      <div>
        <div className="paper-card-meta">
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
            <Calendar size={13} />
            {formattedDate}
          </span>
          {paper.user_name && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
              <UserIcon size={13} />
              {paper.user_name}
            </span>
          )}
        </div>

        <div className="paper-card-actions">
          {paper.status === 'Analyzed' && paper.latest_analysis_id ? (
            <Link
              to={`/analysis/${paper.latest_analysis_id}`}
              className="btn btn-accent btn-sm"
              style={{ flex: 1 }}
              id={`view-report-btn-${paper.id}`}
            >
              <Sparkles size={14} />
              <span>View Report</span>
            </Link>
          ) : (
            <button
              className="btn btn-primary btn-sm"
              style={{ flex: 1 }}
              onClick={() => onAnalyze(paper.id)}
              disabled={isAnalyzing || paper.status === 'Processing'}
              id={`analyze-btn-${paper.id}`}
            >
              <Sparkles size={14} />
              <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Paper'}</span>
            </button>
          )}

          <Link
            to={`/papers/${paper.id}`}
            className="btn btn-secondary btn-sm"
            title="Inspect paper text"
            id={`inspect-paper-btn-${paper.id}`}
          >
            <FileText size={14} />
          </Link>

          {onDelete && (
            <button
              className="btn btn-danger btn-sm"
              onClick={() => onDelete(paper)}
              title="Delete paper"
              id={`delete-paper-btn-${paper.id}`}
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
