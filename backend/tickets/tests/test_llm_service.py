"""
Tests for the LLM service.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from tickets.services.llm_service import LLMService


class LLMServiceTest(TestCase):
    """Test LLM classification service with mocked API calls."""

    def test_classify_without_api_key(self):
        """Should return defaults with a warning when API key is missing."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': ''}):
            result = LLMService.classify('I cannot log in')
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'medium')
        self.assertIn('warning', result)

    def test_parse_valid_json_response(self):
        """Should correctly parse a valid JSON response from the LLM."""
        response_text = '{"suggested_category": "account", "suggested_priority": "high"}'
        result = LLMService._parse_response(response_text)
        self.assertEqual(result['suggested_category'], 'account')
        self.assertEqual(result['suggested_priority'], 'high')
        self.assertNotIn('warning', result)

    def test_parse_markdown_wrapped_json(self):
        """Should handle JSON wrapped in markdown code blocks."""
        response_text = '```json\n{"suggested_category": "billing", "suggested_priority": "critical"}\n```'
        result = LLMService._parse_response(response_text)
        self.assertEqual(result['suggested_category'], 'billing')
        self.assertEqual(result['suggested_priority'], 'critical')

    def test_parse_invalid_json_returns_defaults(self):
        """Should return defaults when LLM returns non-JSON."""
        result = LLMService._parse_response('This is not JSON at all.')
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'medium')
        self.assertIn('warning', result)

    def test_parse_invalid_category_falls_back(self):
        """Should fall back to 'general' for invalid category values."""
        response_text = '{"suggested_category": "invalid_cat", "suggested_priority": "high"}'
        result = LLMService._parse_response(response_text)
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_parse_invalid_priority_falls_back(self):
        """Should fall back to 'medium' for invalid priority values."""
        response_text = '{"suggested_category": "billing", "suggested_priority": "urgent"}'
        result = LLMService._parse_response(response_text)
        self.assertEqual(result['suggested_category'], 'billing')
        self.assertEqual(result['suggested_priority'], 'medium')

    @patch('tickets.services.llm_service.LLMService._call_gemini')
    def test_classify_handles_api_exception(self, mock_call):
        """Should return defaults when the Gemini API throws an exception."""
        mock_call.side_effect = Exception('API connection timeout')
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            result = LLMService.classify('Server is down and nothing works')
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'medium')
        self.assertIn('warning', result)
