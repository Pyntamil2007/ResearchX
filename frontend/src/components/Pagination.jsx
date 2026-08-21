import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export const Pagination = ({
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  totalItems = 0,
  limit = 10,
  onLimitChange
}) => {
  if (totalItems === 0) return null;

  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        pages.push(currentPage - 1);
        pages.push(currentPage);
        pages.push(currentPage + 1);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  const startItem = totalItems > 0 ? (currentPage - 1) * limit + 1 : 0;
  const endItem = Math.min(currentPage * limit, totalItems);

  return (
    <div className="pagination-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginTop: '1.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
      {/* Showing item counts */}
      <div className="pagination-info" style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
        Showing <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{startItem}-{endItem}</span> of <span style={{ color: 'var(--text-main)', fontWeight: 600 }}>{totalItems}</span> records
      </div>

      {/* Controls & Per Page Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        {onLimitChange && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
            <span>Per page:</span>
            <select
              className="form-select"
              value={limit}
              onChange={(e) => onLimitChange(Number(e.target.value))}
              style={{ padding: '4px 8px', fontSize: '0.82rem', width: 'auto' }}
              id="pagination-limit-select"
            >
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        )}

        {totalPages > 1 && (
          <div className="pagination-controls" style={{ display: 'flex', gap: '4px' }}>
            <button
              className="pagination-btn"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
              aria-label="Previous Page"
              id="pagination-prev"
            >
              <ChevronLeft size={16} />
              <span style={{ marginLeft: 2 }}>Prev</span>
            </button>

            {getPageNumbers().map((page, idx) => (
              typeof page === 'number' ? (
                <button
                  key={idx}
                  className={`pagination-btn ${page === currentPage ? 'active' : ''}`}
                  onClick={() => onPageChange(page)}
                >
                  {page}
                </button>
              ) : (
                <span key={idx} style={{ padding: '0 6px', color: 'var(--text-dim)', alignSelf: 'center' }}>...</span>
              )
            ))}

            <button
              className="pagination-btn"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              aria-label="Next Page"
              id="pagination-next"
            >
              <span style={{ marginRight: 2 }}>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
