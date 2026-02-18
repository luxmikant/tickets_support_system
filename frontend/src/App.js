import React, { useState } from 'react';
import TicketForm from './components/TicketForm';
import TicketList from './components/TicketList';
import StatsDashboard from './components/StatsDashboard';

/**
 * Main application component.
 *
 * Layout: Two-column — left (form + ticket list), right (stats dashboard).
 * State: `refreshKey` counter lifts refresh coordination to this level.
 * When a ticket is created, both the list and dashboard re-fetch.
 */
function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTicketCreated = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            🎫 Support Ticket System
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Submit, track, and manage support tickets with AI-powered classification
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column: Form + List */}
          <div className="lg:col-span-2 space-y-6">
            <TicketForm onTicketCreated={handleTicketCreated} />
            <TicketList refreshKey={refreshKey} />
          </div>

          {/* Right column: Stats Dashboard */}
          <div className="lg:col-span-1">
            <div className="sticky top-6">
              <StatsDashboard refreshKey={refreshKey} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
