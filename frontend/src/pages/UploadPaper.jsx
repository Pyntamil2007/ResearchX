import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { paperService } from '../services/paperService';
import { analysisService } from '../services/analysisService';
import { useToast } from '../context/ToastContext';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Sparkles, ArrowRight, BookOpen, Image as ImageIcon } from 'lucide-react';

export const UploadPaper = () => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [domain, setDomain] = useState('Computer Vision & Deep Learning');
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const fileInputRef = useRef(null);

  const toast = useToast();
  const navigate = useNavigate();

  const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'];
  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB

  const DOMAINS = [
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

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (selectedFile) => {
    const fileName = selectedFile.name.toLowerCase();
    const isAllowed = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));
    
    if (!isAllowed) {
      toast.error('Unsupported file type. Please upload PDF, DOC, DOCX, JPG, JPEG, or PNG.');
      return;
    }
    if (selectedFile.size > MAX_FILE_SIZE) {
      toast.error('File size exceeds the 100 MB maximum limit.');
      return;
    }
    setFile(selectedFile);
    if (!title) {
      const cleanTitle = selectedFile.name.replace(/\.(pdf|docx?|jpg|jpeg|png)$/i, '').replace(/[-_]/g, ' ');
      setTitle(cleanTitle);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.warning('Please select a research paper or document image to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (title.trim()) formData.append('title', title.trim());
    if (domain) formData.append('domain', domain);

    setUploading(true);
    setUploadProgress(10);

    try {
      const uploadRes = await paperService.uploadPaper(formData, (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      if (uploadRes.success && uploadRes.data) {
        const paperId = uploadRes.data.id;
        toast.success(`'${uploadRes.data.title}' uploaded successfully!`);

        if (autoAnalyze) {
          toast.info('Initiating AI / NLP analysis...');
          const analyzeRes = await analysisService.analyzePaper(paperId);
          if (analyzeRes.success && analyzeRes.data) {
            toast.success('Paper analysis complete!');
            navigate(`/analysis/${analyzeRes.data.analysis_id}`);
            return;
          }
        }
        navigate(`/papers/${paperId}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Upload failed. Please check the file and try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleLoadDemo = async (demoFileName) => {
    setUploading(true);
    try {
      toast.info(`Loading sample paper: ${demoFileName}...`);
      const res = await paperService.loadDemoPaper(demoFileName);
      if (res.success && res.data) {
        toast.success('Sample paper loaded into your workspace!');
        if (autoAnalyze) {
          toast.info('Analyzing sample research paper...');
          const analyzeRes = await analysisService.analyzePaper(res.data.id);
          if (analyzeRes.success && analyzeRes.data) {
            navigate(`/analysis/${analyzeRes.data.analysis_id}`);
            return;
          }
        }
        navigate(`/papers/${res.data.id}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to load demo paper.');
    } finally {
      setUploading(false);
    }
  };

  const isImageFile = file && ['.jpg', '.jpeg', '.png', '.webp'].some(ext => file.name.toLowerCase().endsWith(ext));

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.85rem', marginBottom: '0.35rem' }}>Upload Research Document</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Upload an academic paper or document (PDF, DOC, DOCX, JPG, JPEG, PNG). ResearchX extracts text via intelligent parsing & OCR, performs NLP + LLM analysis, and builds an interactive report.
        </p>
      </div>

      {/* 1-Click Demo Sample Papers Box */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '2rem', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: '1rem' }}>
          <Sparkles size={18} color="var(--accent)" />
          <h3 style={{ fontSize: '1.05rem', margin: 0 }}>
            Don't have a document ready? Try our built-in sample research papers:
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '10px' }}>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => handleLoadDemo('ResNet_Deep_Residual_Learning.pdf')}
            disabled={uploading}
            style={{ justifyContent: 'flex-start', padding: '10px 14px' }}
            id="demo-resnet-btn"
          >
            <BookOpen size={16} color="var(--accent)" />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>ResNet (Deep Learning)</div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>Empirical vision benchmark</div>
            </div>
          </button>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => handleLoadDemo('Attention_Is_All_You_Need.pdf')}
            disabled={uploading}
            style={{ justifyContent: 'flex-start', padding: '10px 14px' }}
            id="demo-transformer-btn"
          >
            <BookOpen size={16} color="#10b981" />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Transformer Architecture</div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>NLP Attention benchmark</div>
            </div>
          </button>

          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => handleLoadDemo('Qualitative_AI_Ethics_Governance.pdf')}
            disabled={uploading}
            style={{ justifyContent: 'flex-start', padding: '10px 14px' }}
            id="demo-ethics-btn"
          >
            <BookOpen size={16} color="#f59e0b" />
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>AI Ethics & Governance</div>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)' }}>Qualitative survey study</div>
            </div>
          </button>
        </div>
      </div>

      {/* Upload Form */}
      <form onSubmit={handleUploadSubmit}>
        <div className="glass-panel" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
          {/* Dropzone */}
          <div
            className={`upload-hero-card ${isDragging ? 'dragover' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{ marginBottom: '1.5rem', cursor: 'pointer' }}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/jpeg,image/png"
              style={{ display: 'none' }}
              id="document-file-input"
            />

            <div className="upload-icon-circle">
              {file ? (isImageFile ? <ImageIcon size={34} color="var(--accent)" /> : <FileText size={34} color="var(--accent)" />) : <UploadCloud size={34} />}
            </div>

            {file ? (
              <div>
                <h4 style={{ fontSize: '1.15rem', color: 'var(--accent)', marginBottom: '4px' }}>
                  {file.name}
                </h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Click or drop another file to replace
                </p>
              </div>
            ) : (
              <div>
                <h4 style={{ fontSize: '1.2rem', color: '#ffffff', marginBottom: '6px' }}>
                  Choose a document file or drag & drop it here
                </h4>
                <p style={{ color: 'var(--text-dim)', fontSize: '0.88rem', fontWeight: 500 }}>
                  Supported formats: PDF, DOC, DOCX, JPG, JPEG, PNG | Maximum size: 100 MB
                </p>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {uploading && (
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Uploading & processing document...</span>
                <span style={{ color: 'var(--accent)', fontWeight: 700 }}>{uploadProgress}%</span>
              </div>
              <div style={{ height: '6px', background: 'var(--bg-input)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${uploadProgress}%`,
                  background: 'linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%)',
                  transition: 'width 0.2s ease'
                }} />
              </div>
            </div>
          )}

          {/* Metadata Inputs */}
          <div className="form-group">
            <label className="form-label" htmlFor="paper-title-input">Document Title (Optional override)</label>
            <input
              id="paper-title-input"
              type="text"
              className="form-input"
              placeholder="Leave empty to automatically extract title via NLP/OCR"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="paper-domain-select">Research Domain</label>
            <select
              id="paper-domain-select"
              className="form-select"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            >
              {DOMAINS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: '1rem' }}>
            <input
              type="checkbox"
              id="auto-analyze-checkbox"
              checked={autoAnalyze}
              onChange={(e) => setAutoAnalyze(e.target.checked)}
              style={{ width: '18px', height: '18px', accentColor: 'var(--primary)' }}
            />
            <label htmlFor="auto-analyze-checkbox" style={{ fontSize: '0.9rem', color: 'var(--text-main)', cursor: 'pointer' }}>
              Automatically run AI / NLP Analysis immediately after upload
            </label>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/papers')}
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn btn-primary btn-lg"
            disabled={!file || uploading}
            id="start-upload-btn"
          >
            {uploading ? (
              <span>Uploading & Processing...</span>
            ) : (
              <>
                <UploadCloud size={18} />
                <span>Upload & Start Analysis</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
