import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { analysisService } from '../services/analysisService';
import { useToast } from '../context/ToastContext';
import { EasySummaryCard } from '../components/EasySummaryCard';
import { ChartComponent } from '../components/ChartComponent';
import { Modal } from '../components/Modal';
import {
  Sparkles,
  ArrowLeft,
  Calendar,
  Layers,
  Award,
  Target,
  Lightbulb,
  Cpu,
  Database,
  TrendingUp,
  AlertOctagon,
  Compass,
  Printer,
  FileCode,
  Tag,
  Search,
  BookOpen,
  User,
  Users,
  CheckCircle2,
  HelpCircle,
  BarChart2
} from 'lucide-react';

const ALL_DOMAINS_LIST = [
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

export const AnalysisReport = () => {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  // Domain search modal state
  const [isDomainSearchOpen, setIsDomainSearchOpen] = useState(false);
  const [domainSearchQuery, setDomainSearchQuery] = useState('');
  const [updatingDomain, setUpdatingDomain] = useState(false);

  const toast = useToast();
  const navigate = useNavigate();

  const fetchReport = async () => {
    try {
      setLoading(true);
      const res = await analysisService.getAnalysis(id);
      if (res.success && res.data) {
        setReport(res.data);
      }
    } catch (err) {
      toast.error('Failed to load analysis report.');
      navigate('/papers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  const handleExportJSON = () => {
    if (!report) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `ResearchX_Report_${report.id}_${(report.paper_title || 'report').slice(0, 25)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    toast.success('Analysis report exported as JSON.');
  };

  const handleSelectDomain = async (newDomain) => {
    if (!report || report.research_domain === newDomain) {
      setIsDomainSearchOpen(false);
      return;
    }
    setUpdatingDomain(true);
    try {
      const res = await analysisService.updateAnalysisDomain(report.id, newDomain);
      if (res.success && res.data) {
        setReport(prev => ({
          ...prev,
          research_domain: newDomain,
          domain_explanation: res.data.domain_explanation
        }));
        toast.success(`Research domain updated to '${newDomain}'.`);
        setIsDomainSearchOpen(false);
      }
    } catch (err) {
      toast.error('Failed to update research domain.');
    } finally {
      setUpdatingDomain(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <p>Loading interactive research analysis report...</p>
      </div>
    );
  }

  if (!report) return null;

  const filteredDomains = ALL_DOMAINS_LIST.filter(d =>
    d.toLowerCase().includes(domainSearchQuery.toLowerCase())
  );

  // Parse Authors
  const authorsRaw = report.authors || '';
  const isAuthorsUnavailable = !authorsRaw ||
    authorsRaw.toLowerCase().includes('information not available') ||
    authorsRaw.toLowerCase().includes('not available');

  const parsedAuthorsList = !isAuthorsUnavailable
    ? authorsRaw.split(/[,;\n]+/).map(a => a.trim()).filter(a => a.length > 1)
    : [];

  return (
    <div className="analysis-report-page">
      {/* Printable Header (Visible only in print) */}
      <div className="print-only-header">
        <div style={{ fontSize: '1.8rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#0f172a', marginBottom: '2px' }}>
          RESEARCHX
        </div>
        <div style={{ fontSize: '1rem', color: '#475569', fontWeight: 600, borderBottom: '2px solid #0f172a', paddingBottom: '8px' }}>
          Academic Research Analysis Report
        </div>
      </div>

      {/* Top Action Bar (Hidden in print) */}
      <div className="report-action-header-row no-print" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: 12 }}>
        <Link to="/papers" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontWeight: 600 }}>
          <ArrowLeft size={16} />
          <span>Back to Research Papers</span>
        </Link>

        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={handleExportJSON} title="Export raw analysis as JSON" id="export-json-btn">
            <FileCode size={14} />
            <span>Export JSON</span>
          </button>
          <button className="btn btn-primary btn-sm" onClick={handlePrint} title="Print structured academic report" id="print-report-btn">
            <Printer size={14} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 1. PAPER OVERVIEW                                                         */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section report-header" id="section-paper-overview">
        <div className="report-meta-top">
          <span className="badge badge-analyzed">
            <Sparkles size={12} />
            Academic Research Analysis
          </span>
          <span className="badge badge-admin" style={{ fontSize: '0.8rem', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <BookOpen size={13} />
            Document Type: {report.document_type || 'Research Paper'}
          </span>
          <span className="domain-chip" style={{ fontWeight: 600 }}>
            {report.research_domain}
          </span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
            Analyzed on {new Date(report.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </span>
        </div>

        <h1 className="report-title">{report.paper_title}</h1>

        {report.publication_info && !report.publication_info.toLowerCase().includes('not available') && (
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            <strong>Publication / Venue:</strong> {report.publication_info}
          </p>
        )}

        {/* Keywords */}
        <div className="report-actions-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <Tag size={13} />
              Keywords:
            </span>
            <div className="keywords-container">
              {report.keywords && report.keywords.length > 0 ? (
                report.keywords.map((kw, idx) => (
                  <span key={idx} className="keyword-chip">
                    #{kw}
                  </span>
                ))
              ) : (
                <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>Information not available</span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 2. AUTHORS                                                                */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-authors" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)' }}>
            <Users size={20} />
          </div>
          <div>
            <h2 className="section-heading">Authors</h2>
            <p className="section-subheading">Principal researchers and authors extracted from the document header.</p>
          </div>
        </div>

        <div className="section-content-block">
          {parsedAuthorsList.length > 0 ? (
            <div className="authors-academic-grid">
              {parsedAuthorsList.map((authorName, index) => (
                <div key={index} className="author-academic-card">
                  <div className="author-avatar-icon">
                    <User size={16} />
                  </div>
                  <div className="author-info">
                    <div className="author-name-text">{authorName}</div>
                    <div className="author-role-subtext">Author / Contributor</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="not-available-box">
              <p><strong>Authors:</strong> Information not available in the document.</p>
            </div>
          )}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. DOMAIN                                                                 */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section domain-intelligence-panel" id="section-domain" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <div className="section-header-block" style={{ marginBottom: 0 }}>
            <div className="section-icon-badge" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent)' }}>
              <Layers size={20} />
            </div>
            <div>
              <h2 className="section-heading">Research Domain</h2>
              <p className="section-subheading">Primary academic discipline and taxonomy classification.</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="domain-chip" style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
              {report.research_domain}
            </span>
            <button
              className="btn btn-secondary btn-sm no-print"
              onClick={() => setIsDomainSearchOpen(true)}
              id="open-domain-search-btn"
              title="Search and change research domain"
            >
              <Search size={14} />
              <span>Change Domain</span>
            </button>
          </div>
        </div>

        {/* Domain Rationale Explanation */}
        {report.domain_explanation && (
          <div className="domain-explanation-box" style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--accent)', marginBottom: 6 }}>
              Classification Rationale:
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>
              {report.domain_explanation.summary || report.domain_explanation.definition || 'Domain assigned based on contextual terminology and core algorithmic methodologies.'}
            </p>
          </div>
        )}

        {/* Recommended Domains */}
        {report.recommended_domains && report.recommended_domains.length > 0 && (
          <div className="no-print" style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-dim)' }}>
              Alternative Recommendations:
            </span>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {report.recommended_domains.map((rec, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="domain-recommendation-chip"
                  onClick={() => handleSelectDomain(rec.domain)}
                  disabled={updatingDomain}
                  title={`Switch to ${rec.domain} (${rec.match_percentage || 85}% match)`}
                >
                  <span>{rec.domain}</span>
                  <span style={{ opacity: 0.7, fontSize: '0.72rem' }}>({rec.match_percentage || 85}%)</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* ========================================================================= */}
      {/* 4. RESEARCH PROBLEM                                                       */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-research-problem" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
            <AlertOctagon size={20} />
          </div>
          <div>
            <h2 className="section-heading">Research Problem</h2>
            <p className="section-subheading">Core challenge, research bottleneck, or fundamental limitation investigated.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.research_problem || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 5. OBJECTIVE                                                              */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-objective" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <Target size={20} />
          </div>
          <div>
            <h2 className="section-heading">Objective</h2>
            <p className="section-subheading">Primary research goal, hypothesis, and intended scientific outcomes.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.objective || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 6. METHODOLOGY                                                            */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-methodology" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
            <Compass size={20} />
          </div>
          <div>
            <h2 className="section-heading">Methodology</h2>
            <p className="section-subheading">Architectural framework, experimental workflow, and theoretical procedures.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.methodology || 'Methodology could not be reliably identified.'}</p>
          {report.proposed_solution && report.proposed_solution !== report.methodology && (
            <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <h4 style={{ fontSize: '0.95rem', color: 'var(--accent)', marginBottom: 4 }}>Proposed Solution Mechanism:</h4>
              <p className="academic-paragraph">{report.proposed_solution}</p>
            </div>
          )}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 7. ALGORITHMS                                                             */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-algorithms" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#facc15' }}>
            <Cpu size={20} />
          </div>
          <div>
            <h2 className="section-heading">Algorithms & Models</h2>
            <p className="section-subheading">Computational algorithms, model architectures, and mathematical techniques.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.algorithms || 'Information not available in the document.'}</p>
          {report.technologies && !report.technologies.toLowerCase().includes('not available') && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              <strong>Software Frameworks & Infrastructure:</strong> {report.technologies}
            </div>
          )}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 8. DATASET                                                                */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-dataset" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <Database size={20} />
          </div>
          <div>
            <h2 className="section-heading">Dataset & Benchmarks</h2>
            <p className="section-subheading">Evaluation corpora, benchmark datasets, and data distributions analyzed.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.dataset || 'Information not available in the document.'}</p>
          {report.experimental_setup && !report.experimental_setup.toLowerCase().includes('not available') && (
            <div style={{ marginTop: '0.75rem', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              <strong>Experimental Configuration:</strong> {report.experimental_setup}
            </div>
          )}
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 9. RESULTS                                                                */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-results" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(14, 165, 233, 0.15)', color: '#38bdf8' }}>
            <TrendingUp size={20} />
          </div>
          <div>
            <h2 className="section-heading">Results & Experimental Evaluation</h2>
            <p className="section-subheading">Empirical validation, comparative benchmark performance, and statistical data.</p>
          </div>
        </div>

        <div className="section-content-block">
          <p className="academic-paragraph" style={{ marginBottom: '1.5rem' }}>
            {report.results || 'Information not available in the document.'}
          </p>

          {/* Visualizations (Interactive Charts & Benchmarks) */}
          <div className="report-chart-container" style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
            <ChartComponent visualizationData={report.visualization_data} />
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 10. KEY FINDINGS                                                          */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-key-findings" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <Lightbulb size={20} />
          </div>
          <div>
            <h2 className="section-heading">Key Findings</h2>
            <p className="section-subheading">Principal conclusions, insights, and observed phenomena.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.key_findings || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 11. LIMITATIONS                                                           */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-limitations" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
            <AlertOctagon size={20} />
          </div>
          <div>
            <h2 className="section-heading">Limitations</h2>
            <p className="section-subheading">Identified computational constraints, edge cases, and threats to validity.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.limitations || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 12. FUTURE WORK                                                           */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-future-work" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#a78bfa' }}>
            <Compass size={20} />
          </div>
          <div>
            <h2 className="section-heading">Future Work</h2>
            <p className="section-subheading">Recommended future research directions and system extensions.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.future_work || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 13. MAIN CONTRIBUTION                                                     */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-main-contribution" style={{ padding: '1.75rem', marginBottom: '1.75rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#f472b6' }}>
            <Award size={20} />
          </div>
          <div>
            <h2 className="section-heading">Main Contribution</h2>
            <p className="section-subheading">Primary novel scientific and technological contributions delivered to the field.</p>
          </div>
        </div>
        <div className="section-content-block">
          <p className="academic-paragraph">{report.contribution || 'Information not available in the document.'}</p>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 14. EASY SUMMARY (6 Questions)                                            */}
      {/* ========================================================================= */}
      <section className="glass-panel report-section" id="section-easy-summary" style={{ padding: '1.75rem', marginBottom: '2rem' }}>
        <div className="section-header-block">
          <div className="section-icon-badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)' }}>
            <HelpCircle size={20} />
          </div>
          <div>
            <h2 className="section-heading">Easy Summary</h2>
            <p className="section-subheading">Six foundational questions structured for rapid research comprehension.</p>
          </div>
        </div>

        <div className="easy-summary-grid" style={{ marginTop: '1.25rem' }}>
          <EasySummaryCard
            question="What is this paper about?"
            answer={report.easy_summary?.what_is_this_paper_about}
            iconName="book"
            color="#6366f1"
          />
          <EasySummaryCard
            question="What problem does it solve?"
            answer={report.easy_summary?.what_problem_does_it_solve}
            iconName="target"
            color="#ec4899"
          />
          <EasySummaryCard
            question="Why was the research conducted?"
            answer={report.easy_summary?.why_was_the_research_conducted}
            iconName="lightbulb"
            color="#f59e0b"
          />
          <EasySummaryCard
            question="How was it performed?"
            answer={report.easy_summary?.how_was_it_performed}
            iconName="cpu"
            color="#10b981"
          />
          <EasySummaryCard
            question="What was the result?"
            answer={report.easy_summary?.what_was_the_result}
            iconName="trending-up"
            color="#06b6d4"
          />
          <EasySummaryCard
            question="What is the main contribution?"
            answer={report.easy_summary?.what_is_the_main_contribution}
            iconName="check-circle"
            color="#8b5cf6"
          />
        </div>
      </section>

      {/* Domain Selection Modal */}
      <Modal
        isOpen={isDomainSearchOpen}
        onClose={() => setIsDomainSearchOpen(false)}
        title="Search & Select Research Domain"
        footer={
          <button className="btn btn-secondary" onClick={() => setIsDomainSearchOpen(false)}>
            Close
          </button>
        }
      >
        <div>
          <div className="search-input-wrapper" style={{ marginBottom: '1rem' }}>
            <Search size={18} />
            <input
              type="text"
              className="form-input"
              placeholder="Search through 28 canonical domains..."
              value={domainSearchQuery}
              onChange={(e) => setDomainSearchQuery(e.target.value)}
              autoFocus
            />
          </div>

          <div style={{ maxHeight: '320px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
            {filteredDomains.map((d) => {
              const isSelected = report.research_domain === d;
              return (
                <button
                  key={d}
                  type="button"
                  onClick={() => handleSelectDomain(d)}
                  disabled={updatingDomain}
                  style={{
                    padding: '10px 14px',
                    textAlign: 'left',
                    borderRadius: '8px',
                    background: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    border: isSelected ? '1px solid var(--primary)' : '1px solid transparent',
                    color: isSelected ? '#ffffff' : 'var(--text-main)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <span style={{ fontWeight: isSelected ? 600 : 400 }}>{d}</span>
                  {isSelected && <CheckCircle2 size={16} color="var(--accent)" />}
                </button>
              );
            })}
          </div>
        </div>
      </Modal>
    </div>
  );
};
