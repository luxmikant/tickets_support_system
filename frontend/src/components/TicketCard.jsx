import React from 'react';
import { CATEGORIES, PRIORITIES, STATUSES, getDisplayProps } from '../utils/constants';

/**
 * Individual ticket card with status change capability.
 *
 * Displays: title, truncated description, category badge, priority badge,
 * status dropdown, and relative timestamp.
 */
export default function TicketCard({ ticket, onStatusChange }) {
  const categoryProps = getDisplayProps(CATEGORIES, ticket.category);
  const priorityProps = getDisplayProps(PRIORITIES, ticket.priority);

  // Truncate description to 120 chars
  const truncatedDesc =
    ticket.description.length > 120
      ? ticket.description.substring(0, 120) + '...'
      : ticket.description;

  // Format timestamp as relative time
  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const handleStatusChange = (e) => {
    const newStatus = e.target.value;
    if (newStatus !== ticket.status) {
      onStatusChange(ticket.id, { status: newStatus });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      {/* Header row: title + timestamp */}
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-800 text-sm leading-tight flex-1 mr-2">
          {ticket.title}
        </h3>
        <span className="text-xs text-gray-400 whitespace-nowrap">
          {formatTime(ticket.created_at)}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-3">{truncatedDesc}</p>

      {/* Badges row */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryProps.color}`}>
          {categoryProps.label}
        </span>
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityProps.color}`}>
          {priorityProps.label}
        </span>
      </div>

      {/* Status dropdown */}
      <div className="flex items-center gap-2">
        <label className="text-xs text-gray-500">Status:</label>
        <select
          value={ticket.status}
          onChange={handleStatusChange}
          className="text-xs px-2 py-1 border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
        >
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
