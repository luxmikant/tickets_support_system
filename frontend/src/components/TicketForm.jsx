import React, { useState, useCallback, useRef } from 'react';
import { createTicket, classifyTicket } from '../api/ticketApi';
import { CATEGORIES, PRIORITIES } from '../utils/constants';
import LoadingSpinner from './LoadingSpinner';

/**
 * Ticket submission form with LLM-powered auto-classification.
 *
 * When the user types a description and blurs the field (or waits 1.5s),
 * the system calls the /classify/ endpoint to pre-fill category and priority.
 * The user can accept or override the suggestions before submitting.
 */
export default function TicketForm({ onTicketCreated }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'general',
    priority: 'medium',
  });
  const [isClassifying, setIsClassifying] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [llmSuggested, setLlmSuggested] = useState(false);

  const classifyTimeoutRef = useRef(null);

  // Debounced LLM classification — triggers 1.5s after user stops typing.
  // Note: deps array is empty intentionally — we only want to set up this
  // effect once during component mount. The closure captures the state updates.
  const handleDescriptionChange = useCallback(
    (e) => {
      const value = e.target.value;
      setFormData((prev) => ({ ...prev, description: value }));

      // Clear any pending classification
      if (classifyTimeoutRef.current) {
        clearTimeout(classifyTimeoutRef.current);
      }

      // Schedule classification after 1.5s of no typing
      if (value.trim().length >= 20) {
        classifyTimeoutRef.current = setTimeout(() => {
          handleClassify(value);
        }, 1500);
      }
    },
    []
  );

  // Call LLM classify endpoint
  const handleClassify = async (description) => {
    if (!description || description.trim().length < 10) return;

    setIsClassifying(true);
    try {
      const result = await classifyTicket(description);
      setFormData((prev) => ({
        ...prev,
        category: result.suggested_category || prev.category,
        priority: result.suggested_priority || prev.priority,
      }));
      setLlmSuggested(true);
    } catch (err) {
      console.warn('LLM classification failed — using defaults', err);
      // Don't show error to user — classification failure is non-blocking
    } finally {
      setIsClassifying(false);
    }
  };

  // Also classify on description blur (if not already classified)
  const handleDescriptionBlur = () => {
    if (
      formData.description.trim().length >= 20 &&
      !isClassifying &&
      !llmSuggested
    ) {
      handleClassify(formData.description);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.title.trim()) {
      setError('Title is required.');
      return;
    }
    if (!formData.description.trim()) {
      setError('Description is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      await createTicket(formData);
      setSuccess('Ticket created successfully!');
      setFormData({
        title: '',
        description: '',
        category: 'general',
        priority: 'medium',
      });
      setLlmSuggested(false);
      if (onTicketCreated) onTicketCreated();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const details = err.response?.data?.details;
      if (details && typeof details === 'object') {
        const messages = Object.values(details).flat().join(', ');
        setError(messages);
      } else {
        setError('Failed to create ticket. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Submit a Ticket</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-green-700 text-sm">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            name="title"
            type="text"
            maxLength={200}
            value={formData.title}
            onChange={handleChange}
            placeholder="Brief summary of your issue"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
          <p className="text-xs text-gray-400 mt-1">{formData.title.length}/200</p>
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="description"
            name="description"
            rows={4}
            value={formData.description}
            onChange={handleDescriptionChange}
            onBlur={handleDescriptionBlur}
            placeholder="Describe your problem in detail..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
          {isClassifying && (
            <div className="mt-1">
              <LoadingSpinner size="sm" text="AI is analyzing your description..." />
            </div>
          )}
          {llmSuggested && !isClassifying && (
            <p className="text-xs text-green-600 mt-1">
              ✓ AI suggested category and priority — you can override below
            </p>
          )}
        </div>

        {/* Category & Priority (side by side) */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {PRIORITIES.map((pri) => (
                <option key={pri.value} value={pri.value}>
                  {pri.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={isSubmitting || isClassifying}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed font-medium"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <LoadingSpinner size="sm" /> Submitting...
            </span>
          ) : (
            'Submit Ticket'
          )}
        </button>
      </form>
    </div>
  );
}
