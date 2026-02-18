import React, { useState, useEffect, useCallback } from 'react';
import { getStats } from '../api/ticketApi';
import LoadingSpinner from './LoadingSpinner';

/**
 * Stats dashboard showing aggregated ticket metrics.
 *
 * Displays: total tickets, open count, avg per day,
 * priority breakdown, and category breakdown.
 * Auto-refreshes when refreshKey changes (new ticket created).
 */
export default function StatsDashboard({ refreshKey }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    try {
      const data = await getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats, refreshKey]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Dashboard</h2>
        <div className="flex justify-center py-8">
          <LoadingSpinner text="Loading stats..." />
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Dashboard</h2>
        <p className="text-gray-400 text-center py-4">Unable to load statistics.</p>
      </div>
    );
  }

  const priorityColors = {
    low: 'bg-slate-200',
    medium: 'bg-yellow-300',
    high: 'bg-orange-400',
    critical: 'bg-red-500',
  };

  const categoryColors = {
    billing: 'bg-green-400',
    technical: 'bg-blue-400',
    account: 'bg-purple-400',
    general: 'bg-gray-400',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Dashboard</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-blue-700">{stats.total_tickets}</p>
          <p className="text-xs text-blue-500 mt-1">Total Tickets</p>
        </div>
        <div className="bg-amber-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-amber-700">{stats.open_tickets}</p>
          <p className="text-xs text-amber-500 mt-1">Open</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-green-700">{stats.avg_tickets_per_day}</p>
          <p className="text-xs text-green-500 mt-1">Avg / Day</p>
        </div>
      </div>

      {/* Priority breakdown */}
      <div className="mb-5">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Priority Breakdown</h3>
        <div className="space-y-2">
          {Object.entries(stats.priority_breakdown).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-14 capitalize">{key}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                <div
                  className={`h-full rounded-full ${priorityColors[key]} transition-all`}
                  style={{
                    width: stats.total_tickets > 0
                      ? `${(value / stats.total_tickets) * 100}%`
                      : '0%',
                  }}
                />
              </div>
              <span className="text-xs font-medium text-gray-600 w-8 text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Category breakdown */}
      <div>
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Category Breakdown</h3>
        <div className="space-y-2">
          {Object.entries(stats.category_breakdown).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2">
              <span className="text-xs text-gray-500 w-14 capitalize">{key}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                <div
                  className={`h-full rounded-full ${categoryColors[key]} transition-all`}
                  style={{
                    width: stats.total_tickets > 0
                      ? `${(value / stats.total_tickets) * 100}%`
                      : '0%',
                  }}
                />
              </div>
              <span className="text-xs font-medium text-gray-600 w-8 text-right">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
