/**
 * Shared constants for the Support Ticket System frontend.
 * Must stay in sync with the Django model choices.
 */

export const CATEGORIES = [
  { value: 'billing', label: 'Billing', color: 'bg-green-100 text-green-800' },
  { value: 'technical', label: 'Technical', color: 'bg-blue-100 text-blue-800' },
  { value: 'account', label: 'Account', color: 'bg-purple-100 text-purple-800' },
  { value: 'general', label: 'General', color: 'bg-gray-100 text-gray-800' },
];

export const PRIORITIES = [
  { value: 'low', label: 'Low', color: 'bg-slate-100 text-slate-700' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' },
];

export const STATUSES = [
  { value: 'open', label: 'Open', color: 'bg-blue-100 text-blue-800' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'resolved', label: 'Resolved', color: 'bg-green-100 text-green-800' },
  { value: 'closed', label: 'Closed', color: 'bg-gray-100 text-gray-600' },
];

/**
 * Get display properties for a value from a constants array.
 */
export const getDisplayProps = (list, value) => {
  return list.find((item) => item.value === value) || { label: value, color: 'bg-gray-100 text-gray-600' };
};
