import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { paperService } from '../services/paperService';
import { analysisService } from '../services/analysisService';
import { useToast } from '../context/ToastContext';
import {
  FileText,
  Sparkles,
  Download,
  Calendar,
  User as UserIcon,
  Layers,
  ArrowLeft,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export const PaperDetails = () => {
  const { id } = useParams();
  const [paper, setPaper] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('raw'); // 'raw', 'preview'

  const toast = useToast();
  const navigate = useNavigate();

  const fetchPaper = async () => {
    try {
      setLoading(true);
      const res = await paperService.getPaperById(id);
      if (res.success && res.data) {
        setPaper(res.data);
      }
    } catch (err) {
      toast.error('Failed to load paper details.');
      navigate('/papers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPaper();
  }, [id]);

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      toast.info('Starting AI/NLP analysis...');
      const res = await analysisService.analyzePaper(paper.id);
      if (res.success && res.data) {
        toast.success('Paper analyzed successfully!');
        navigate(`/analysis/${res.data.analysis_id}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDownload = () => {
    window.open(paperService.downloadPaperUrl(paper.id), '_blank');
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <p>Loading research paper details...</p>
      </div>
    );
  }

  if (!paper) return null;

  return (
    <div>
      {/* Back Link */}
      <Link to="/papers" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', marginBottom: '1.5rem', fontWeight: 600 }}>
        <ArrowLeft size={16} />
        <span>Back to Research Papers</span>
      </Link>

      {/* Header Panel */}
      <div className="glass-panel report-header" style={{ marginBottom: '1.5rem' }}>
        <div className="report-meta-top">
          {paper.status === 'Analyzed' && <span className="badge badge-analyzed">Analyzed</span>}
          {paper.status === 'Processing' && <span className="badge badge-processing">Processing</span>}
          {paper.status === 'Uploaded' && <span className="badge badge-uploaded">Uploaded</span>}
          {paper.status === 'Failed' && <span className="badge badge-failed">Failed</span>}
          <span className="badge badge-admin" style={{ fontSize: '0.8rem' }}>
            Document Type: {paper.document_type || 'Research Paper'}
          </span>
          <span className="domain-chip">{paper.domain}</span>
        </div>

        <h1 className="report-title">{paper.title}</h1>
        <p className="report-authors">
          <strong>Authors:</strong> {paper.authors || 'Information not available in the paper.'}
        </p>

        <div className="report-actions-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <Calendar size={14} />
              Uploaded on {new Date(paper.uploaded_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            </span>
            <span>File: {paper.file_name}</span>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-secondary" onClick={handleDownload} id="download-pdf-btn">
              <Download size={16} />
              <span>Download PDF</span>
            </button>

            {paper.status === 'Analyzed' && paper.latest_analysis_id ? (
              <Link to={`/analysis/${paper.latest_analysis_id}`} className="btn btn-accent" id="view-analysis-report-btn">
                <Sparkles size={16} />
                <span>View Analysis Report</span>
              </Link>
            ) : (
              <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing} id="trigger-analyze-btn">
                <Sparkles size={16} />
                <span>{analyzing ? 'Analyzing Paper...' : 'Run AI Analysis'}</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Raw Extracted Text Inspection */}
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
          <h3 style={{ fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileText size={18} color="var(--primary)" />
            Extracted Text Content
          </h3>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
            Parsed via PyPDF Text Extractor
          </span>
        </div>

        {paper.raw_text ? (
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-md)',
            padding: '1.5rem',
            maxHeight: '600px',
            overflowY: 'auto',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.85rem',
            lineHeight: 1.7,
            color: '#cbd5e1',
            whiteSpace: 'pre-wrap'
          }}>
            {paper.raw_text}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-muted)' }}>
            <p>No extracted text available for this paper yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};
