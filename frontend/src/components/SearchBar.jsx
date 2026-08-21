import React from 'react';
import { Search, Filter, ArrowUpDown, RotateCcw } from 'lucide-react';

export const SearchBar = ({
  search = '',
  onSearchChange,
  domain,
  onDomainChange,
  domainsList = [],
  documentType,
  onDocumentTypeChange,
  documentTypesList = [],
  role,
  onRoleChange,
  status,
  onStatusChange,
  statusesList = [],
  sortBy,
  onSortByChange,
  sortOptions = [],
  onReset,
  placeholder = "Search by title, author, keyword..."
}) => {
  const hasActiveFilters = Boolean(
    search ||
    (domain && domain !== 'all') ||
    (documentType && documentType !== 'all') ||
    (role && role !== 'all') ||
    (status && status !== 'all') ||
    (sortBy && sortBy !== 'newest')
  );

  return (
    <div className="search-filter-bar" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center', marginBottom: '1.5rem' }}>
      {/* Search Input */}
      <div className="search-input-wrapper" style={{ flex: '1 1 260px', minWidth: '220px' }}>
        <Search size={18} />
        <input
          type="text"
          className="form-input"
          placeholder={placeholder}
          value={search}
          onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
          id="search-input"
        />
      </div>

      {/* Domain Filter */}
      {onDomainChange && (
        <div style={{ flex: '0 1 180px', minWidth: '150px' }}>
          <select
            className="form-select"
            value={domain || 'all'}
            onChange={(e) => onDomainChange(e.target.value)}
            id="filter-domain-select"
          >
            <option value="all">All Domains</option>
            {domainsList.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
      )}

      {/* Document Type Filter */}
      {onDocumentTypeChange && (
        <div style={{ flex: '0 1 180px', minWidth: '150px' }}>
          <select
            className="form-select"
            value={documentType || 'all'}
            onChange={(e) => onDocumentTypeChange(e.target.value)}
            id="filter-doctype-select"
          >
            <option value="all">All Document Types</option>
            {(documentTypesList.length > 0 ? documentTypesList : [
              'Research Paper',
              'Review Paper',
              'Conference Paper',
              'Journal Paper',
              'Academic Book',
              'Book Chapter',
              'Technical Report',
              'Academic Document'
            ]).map((dt) => (
              <option key={dt} value={dt}>{dt}</option>
            ))}
          </select>
        </div>
      )}

      {/* Role Filter */}
      {onRoleChange && (
        <div style={{ flex: '0 1 140px', minWidth: '120px' }}>
          <select
            className="form-select"
            value={role || 'all'}
            onChange={(e) => onRoleChange(e.target.value)}
            id="filter-role-select"
          >
            <option value="all">All Roles</option>
            <option value="ADMIN">Admin</option>
            <option value="USER">Researcher</option>
          </select>
        </div>
      )}

      {/* Status Filter */}
      {onStatusChange && (
        <div style={{ flex: '0 1 140px', minWidth: '120px' }}>
          <select
            className="form-select"
            value={status || 'all'}
            onChange={(e) => onStatusChange(e.target.value)}
            id="filter-status-select"
          >
            <option value="all">All Statuses</option>
            {statusesList.length > 0 ? (
              statusesList.map((st) => (
                <option key={st.value || st} value={st.value || st}>{st.label || st}</option>
              ))
            ) : (
              <>
                <option value="Uploaded">Uploaded</option>
                <option value="Processing">Processing</option>
                <option value="Analyzed">Analyzed</option>
                <option value="Failed">Failed</option>
              </>
            )}
          </select>
        </div>
      )}

      {/* Sort By Dropdown */}
      {onSortByChange && (
        <div style={{ flex: '0 1 170px', minWidth: '140px' }}>
          <select
            className="form-select"
            value={sortBy || 'newest'}
            onChange={(e) => onSortByChange(e.target.value)}
            id="sort-by-select"
          >
            {sortOptions.length > 0 ? (
              sortOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))
            ) : (
              <>
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="alphabetical">Title (A-Z)</option>
                <option value="domain">Domain (A-Z)</option>
                <option value="author">Author (A-Z)</option>
              </>
            )}
          </select>
        </div>
      )}

      {/* Reset Filters Button */}
      {onReset && (
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={onReset}
          disabled={!hasActiveFilters}
          title="Reset all filters and sorting to default"
          style={{
            opacity: hasActiveFilters ? 1 : 0.5,
            cursor: hasActiveFilters ? 'pointer' : 'default',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 12px'
          }}
          id="reset-filters-btn"
        >
          <RotateCcw size={14} />
          <span>Reset</span>
        </button>
      )}
    </div>
  );
};
