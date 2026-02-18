import React from 'react';
import { CATEGORIES, PRIORITIES, STATUSES } from '../utils/constants';

/**
 * Filter bar for the ticket list.
 *
 * Provides dropdowns for category, priority, status and a search input.
 * All filters are applied simultaneously (AND logic).
 */
export default function FilterBar({ filters, onFilterChange }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({ ...filters, [name]: value, page: 1 });
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    // Debounce is handled in the parent — just update immediately
    onFilterChange({ ...filters, search: value, page: 1 });
  };

  const clearFilters = () => {
    onFilterChange({ category: '', priority: '', status: '', search: '', page: 1 });
  };

  const hasActiveFilters =
    filters.category || filters.priority || filters.status || filters.search;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
      <div className="flex flex-wrap gap-3 items-end">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-gray-500 mb-1">Search</label>
          <input
            type="text"
            name="search"
            value={filters.search || ''}
            onChange={handleSearchChange}
            placeholder="Search title & description..."
            className="w-full px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Category filter */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
          <select
            name="category"
            value={filters.category || ''}
            onChange={handleChange}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
        </div>

        {/* Priority filter */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Priority</label>
          <select
            name="priority"
            value={filters.priority || ''}
            onChange={handleChange}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All</option>
            {PRIORITIES.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>

        {/* Status filter */}
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Status</label>
          <select
            name="status"
            value={filters.status || ''}
            onChange={handleChange}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All</option>
            {STATUSES.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>

        {/* Clear filters */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-blue-600 hover:text-blue-800 underline pb-0.5"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
