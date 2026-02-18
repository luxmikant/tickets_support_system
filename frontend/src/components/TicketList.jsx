import React, { useState, useEffect, useCallback, useRef } from 'react';
import { getTickets, updateTicket } from '../api/ticketApi';
import TicketCard from './TicketCard';
import FilterBar from './FilterBar';
import LoadingSpinner from './LoadingSpinner';

/**
 * Ticket list with filtering, searching, and pagination.
 *
 * Displays all tickets newest first. Filters by category, priority,
 * status, and search (title + description). Supports status changes
 * on individual tickets via the TicketCard component.
 */
export default function TicketList({ refreshKey }) {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    priority: '',
    status: '',
    search: '',
    page: 1,
  });
  const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });

  const searchTimeoutRef = useRef(null);
  const prevSearchRef = useRef('');

  // Fetch tickets whenever filters or refreshKey change
  // Note: deps array is correctly minimal — we reuse the same fetchTickets
  // function instance across renders for efficiency
  const fetchTickets = useCallback(async (currentFilters) => {
    setLoading(true);
    setError('');
    try {
      const data = await getTickets(currentFilters);
      setTickets(data.results || []);
      setPagination({
        count: data.count || 0,
        next: data.next,
        previous: data.previous,
      });
    } catch (err) {
      setError('Failed to load tickets.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounce search input — wait 300ms after user stops typing
  const handleFilterChange = useCallback(
    (newFilters) => {
      const searchChanged = newFilters.search !== prevSearchRef.current;
      prevSearchRef.current = newFilters.search;

      if (searchChanged) {
        setFilters(newFilters);
        if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
        searchTimeoutRef.current = setTimeout(() => {
          fetchTickets(newFilters);
        }, 300);
      } else {
        setFilters(newFilters);
        fetchTickets(newFilters);
      }
    },
    [fetchTickets]
  );

  // Re-fetch when refreshKey changes (new ticket created)
  useEffect(() => {
    fetchTickets(filters);
  }, [refreshKey]);

  // Initial load
  useEffect(() => {
    fetchTickets(filters);
  }, []);

  // Handle status change on a ticket
  const handleStatusChange = async (ticketId, data) => {
    try {
      const updated = await updateTicket(ticketId, data);
      setTickets((prev) =>
        prev.map((t) => (t.id === ticketId ? updated : t))
      );
    } catch (err) {
      console.error('Failed to update ticket:', err);
    }
  };

  // Pagination handlers
  const handleNextPage = () => {
    if (pagination.next) {
      const newFilters = { ...filters, page: filters.page + 1 };
      setFilters(newFilters);
      fetchTickets(newFilters);
    }
  };

  const handlePrevPage = () => {
    if (pagination.previous && filters.page > 1) {
      const newFilters = { ...filters, page: filters.page - 1 };
      setFilters(newFilters);
      fetchTickets(newFilters);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Tickets</h2>
        <span className="text-sm text-gray-500">{pagination.count} total</span>
      </div>

      <FilterBar filters={filters} onFilterChange={handleFilterChange} />

      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="lg" text="Loading tickets..." />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-red-500">{error}</div>
      ) : tickets.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p className="text-lg">No tickets found</p>
          <p className="text-sm mt-1">Try adjusting your filters or create a new ticket.</p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {tickets.map((ticket) => (
              <TicketCard
                key={ticket.id}
                ticket={ticket}
                onStatusChange={handleStatusChange}
              />
            ))}
          </div>

          {/* Pagination */}
          {(pagination.next || pagination.previous) && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t">
              <button
                onClick={handlePrevPage}
                disabled={!pagination.previous}
                className="px-3 py-1.5 text-sm border rounded-md disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                ← Previous
              </button>
              <span className="text-sm text-gray-500">Page {filters.page}</span>
              <button
                onClick={handleNextPage}
                disabled={!pagination.next}
                className="px-3 py-1.5 text-sm border rounded-md disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
