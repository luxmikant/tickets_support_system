/**
 * Axios API client for the Support Ticket System.
 *
 * All API calls are centralized here for maintainability.
 * Base URL uses relative paths so Nginx proxy handles routing.
 */

import axios from 'axios';

const api = axios.create({
  baseURL: '/api/tickets',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30s — accounts for LLM classification time
});

// --- Response interceptor for consistent error handling ---
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.error ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

/**
 * Fetch paginated list of tickets with optional filters.
 * @param {Object} filters - { category, priority, status, search, page }
 */
export const getTickets = async (filters = {}) => {
  const params = {};
  if (filters.category) params.category = filters.category;
  if (filters.priority) params.priority = filters.priority;
  if (filters.status) params.status = filters.status;
  if (filters.search) params.search = filters.search;
  if (filters.page) params.page = filters.page;

  const response = await api.get('/', { params });
  return response.data;
};

/**
 * Create a new ticket.
 * @param {Object} data - { title, description, category, priority }
 */
export const createTicket = async (data) => {
  const response = await api.post('/', data);
  return response.data;
};

/**
 * Update a ticket (status, category, or priority).
 * @param {number} id - Ticket ID
 * @param {Object} data - Fields to update
 */
export const updateTicket = async (id, data) => {
  const response = await api.patch(`/${id}/`, data);
  return response.data;
};

/**
 * Fetch aggregated ticket statistics.
 */
export const getStats = async () => {
  const response = await api.get('/stats/');
  return response.data;
};

/**
 * Classify a description via the LLM endpoint.
 * @param {string} description - Ticket description text
 */
export const classifyTicket = async (description) => {
  const response = await api.post('/classify/', { description });
  return response.data;
};
