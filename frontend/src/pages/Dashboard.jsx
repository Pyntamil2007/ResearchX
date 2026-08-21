import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { analysisService } from '../services/analysisService';
import { PaperCard } from '../components/PaperCard';
import {
  FileText,
  Sparkles,
  CheckCircle2,
  Clock,
  UploadCloud,
  History,
  TrendingUp,
  ArrowRight,
  PieChart as PieChartIcon
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const DOMAIN_COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export const Dashboard = () => {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzingId, setAnalyzingId] = useState(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const res = await analysisService.getUserDashboard();
      if (res.success) {
        setStats(res.data);
      }
    } catch (err) {
      toast.error('Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleAnalyze = async (paperId) => {
    try {
      setAnalyzingId(paperId);
      toast.info('Starting AI / NLP paper analysis...');
      const res = await analysisService.analyzePaper(paperId);
      if (res.success && res.data) {
        toast.success('Paper analyzed successfully!');
        navigate(`/analysis/${res.data.analysis_id}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Analysis failed.');
    } finally {
      setAnalyzingId(null);
      fetchDashboardData();
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '5rem 0', color: 'var(--text-muted)' }}>
        <p>Loading your research dashboard...</p>
      </div>
    );
  }

  const domainChartData = stats?.domain_distribution?.map((d) => ({
    name: d.domain,
    value: d.count
  })) || [];

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title-area">
          <h1>Welcome back, {user?.name}</h1>
          <p>Here is your research analysis workspace summary and recent insights.</p>
        </div>
        <div className="dashboard-actions">
          <Link to="/upload" className="btn btn-primary" id="dash-upload-btn">
            <UploadCloud size={18} />
            <span>Upload Paper</span>
          </Link>
          <Link to="/papers" className="btn btn-secondary" id="dash-view-papers-btn">
            <FileText size={18} />
            <span>View Papers</span>
          </Link>
          <Link to="/history" className="btn btn-secondary" id="dash-history-btn">
            <History size={18} />
            <span>Analysis History</span>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="glass-panel stat-card" style={{ '--stat-color': 'var(--primary)', '--stat-glow': 'rgba(99, 102, 241, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <FileText size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Uploaded</span>
            <span className="stat-value">{stats?.total_papers || 0}</span>
            <span className="stat-subtext">Research documents</span>
          </div>
        </div>

        <div className="glass-panel stat-card" style={{ '--stat-color': 'var(--accent)', '--stat-glow': 'rgba(6, 182, 212, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <Sparkles size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Analyzed Papers</span>
            <span className="stat-value">{stats?.total_analyzed || 0}</span>
            <span className="stat-subtext">Full NLP reports generated</span>
          </div>
        </div>

        <div className="glass-panel stat-card" style={{ '--stat-color': '#10b981', '--stat-glow': 'rgba(16, 185, 129, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <CheckCircle2 size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Analysis Completion Rate</span>
            <span className="stat-value">{stats?.metrics_summary?.analysis_rate_pct || 0}%</span>
            <span className="stat-subtext">Ready for reading</span>
          </div>
        </div>

        <div className="glass-panel stat-card" style={{ '--stat-color': '#f59e0b', '--stat-glow': 'rgba(245, 158, 11, 0.2)' }}>
          <div className="stat-icon-wrapper">
            <Clock size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Recent Analyses</span>
            <span className="stat-value">{stats?.recent_analyses?.length || 0}</span>
            <span className="stat-subtext">Saved in history</span>
          </div>
        </div>
      </div>

      {/* 2-Column Section: Recent Papers + Domain Distribution */}
      <div className="dashboard-grid-2">
        {/* Recent Papers */}
        <div>
          <div className="section-header">
            <h3>Recent Research Papers</h3>
            <Link to="/papers" style={{ fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600 }}>
              <span>View All</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {stats?.recent_papers?.length === 0 ? (
            <div className="glass-panel empty-state">
              <div className="empty-state-icon">
                <FileText size={32} />
              </div>
              <h4>No research papers uploaded yet</h4>
              <p>Upload your first PDF paper to extract key insights and easy summaries.</p>
              <Link to="/upload" className="btn btn-primary btn-sm">
                <UploadCloud size={16} />
                <span>Upload Paper Now</span>
              </Link>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {stats?.recent_papers?.map((paper) => (
                <PaperCard
                  key={paper.id}
                  paper={paper}
                  onAnalyze={handleAnalyze}
                  isAnalyzing={analyzingId === paper.id}
                />
              ))}
            </div>
          )}
        </div>

        {/* Domain Distribution & Quick Actions */}
        <div>
          <div className="section-header">
            <h3>Research Domains</h3>
          </div>

          <div className="glass-panel domain-chart-card">
            {domainChartData.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 0' }}>
                No domain data available yet.
              </p>
            ) : (
              <>
                <div className="domain-chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={domainChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {domainChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={DOMAIN_COLORS[index % DOMAIN_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: '#0f172a',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          borderRadius: '8px',
                          color: '#ffffff'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '1rem' }}>
                  {stats?.domain_distribution?.map((d, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          background: DOMAIN_COLORS[idx % DOMAIN_COLORS.length]
                        }} />
                        <span style={{ color: 'var(--text-main)' }}>{d.domain}</span>
                      </div>
                      <span style={{ fontWeight: 700, color: 'var(--accent)' }}>{d.count} papers</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Quick Upload Action */}
          <div style={{ marginTop: '1.5rem' }}>
            <Link to="/upload" style={{ textDecoration: 'none' }}>
              <div className="upload-hero-card">
                <div className="upload-icon-circle">
                  <UploadCloud size={32} />
                </div>
                <h4 style={{ fontSize: '1.1rem', color: '#ffffff', marginBottom: '4px' }}>
                  Upload New Paper
                </h4>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Drag and drop PDF or choose from demo samples
                </p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
