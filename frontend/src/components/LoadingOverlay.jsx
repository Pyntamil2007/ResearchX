import React from 'react';
import { Sparkles } from 'lucide-react';

export const LoadingOverlay = ({ message = "Processing your research paper...", subtext = "Extracting text, identifying sections, and analyzing findings..." }) => {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(10, 14, 23, 0.85)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      flexDirection: 'column',
      padding: '2rem',
      textAlign: 'center'
    }}>
      <div style={{ position: 'relative', marginBottom: '1.5rem' }}>
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          border: '3px solid rgba(99, 102, 241, 0.2)',
          borderTopColor: '#6366f1',
          borderRightColor: '#06b6d4',
          animation: 'spin 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite',
          margin: '0 auto'
        }} />
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#06b6d4'
        }}>
          <Sparkles size={24} />
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>

      <h3 style={{ fontSize: '1.35rem', color: '#ffffff', marginBottom: '0.5rem' }}>
        {message}
      </h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: '420px' }}>
        {subtext}
      </p>
    </div>
  );
};
