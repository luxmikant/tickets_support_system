"""
Tests for the LLM service.

Covers:
  - Prompt-based classification (mocked Gemini API)
  - Response parsing (valid JSON, markdown, reasoning + JSON, invalid)
  - Keyword fallback (no API key, API failure)
  - Signal extraction
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from tickets.services.llm_service import LLMService, _extract_signals


class LLMServiceParseTest(TestCase):
    """Test response parsing and validation."""

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

    def test_parse_json_embedded_in_reasoning(self):
        """Should extract JSON from chain-of-thought reasoning text."""
        response_text = (
            'Analysis: The user mentions "crash" which is technical. '
            'They say "urgent" so priority is critical.\n'
            'Output: {"suggested_category": "technical", "suggested_priority": "critical"}'
        )
        result = LLMService._parse_response(response_text)
        self.assertEqual(result['suggested_category'], 'technical')
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


class LLMServiceKeywordFallbackTest(TestCase):
    """Test keyword-based heuristic classification (fallback)."""

    def test_fallback_detects_billing(self):
        """Should classify payment-related text as billing."""
        result = LLMService._keyword_fallback('I was charged twice for my subscription')
        self.assertEqual(result['suggested_category'], 'billing')

    def test_fallback_detects_technical(self):
        """Should classify bug/error text as technical."""
        result = LLMService._keyword_fallback('The application crashes on startup')
        self.assertEqual(result['suggested_category'], 'technical')

    def test_fallback_detects_account(self):
        """Should classify login/password text as account."""
        result = LLMService._keyword_fallback('I forgot my password and cannot log in')
        self.assertEqual(result['suggested_category'], 'account')

    def test_fallback_detects_urgency_critical(self):
        """Should set critical priority for extreme urgency words."""
        result = LLMService._keyword_fallback(
            'Production is down! This is an emergency, someone can die'
        )
        self.assertEqual(result['suggested_priority'], 'critical')

    def test_fallback_detects_urgency_high(self):
        """Should set high priority for moderate urgency words."""
        result = LLMService._keyword_fallback('This is urgent, please fix ASAP')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_fallback_broken_means_high(self):
        """Should set high priority when something is broken/not working."""
        result = LLMService._keyword_fallback('The search feature is broken')
        self.assertEqual(result['suggested_priority'], 'high')

    def test_fallback_feature_request_low(self):
        """General topics with no urgency should get low priority."""
        result = LLMService._keyword_fallback(
            'It would be nice to have a dark mode option in settings'
        )
        self.assertEqual(result['suggested_priority'], 'low')

    def test_fallback_default_general_medium(self):
        """Ambiguous text with no signals should get general/medium."""
        result = LLMService._keyword_fallback(
            'I have a question about the product roadmap'
        )
        self.assertEqual(result['suggested_category'], 'general')
        self.assertEqual(result['suggested_priority'], 'medium')


class LLMServiceSignalExtractionTest(TestCase):
    """Test keyword signal pre-extraction."""

    def test_extracts_urgency_signals(self):
        """Should detect urgency keywords in description."""
        signals = _extract_signals('This is urgent and needs immediate help ASAP')
        self.assertIn('URGENCY SIGNALS DETECTED', signals)
        self.assertIn('urgent', signals)

    def test_extracts_category_signals(self):
        """Should detect category keywords."""
        signals = _extract_signals('I was charged twice for an invoice payment')
        self.assertIn('BILLING', signals)

    def test_no_signals_returns_empty(self):
        """Should return empty string when no keywords match."""
        signals = _extract_signals('Hello there, I have a question')
        self.assertEqual(signals, '')


class LLMServiceClassifyTest(TestCase):
    """Test the classify() orchestrator method."""

    def test_classify_without_api_key_uses_fallback(self):
        """Should use keyword fallback when API key is missing."""
        with patch.dict('os.environ', {'GEMINI_API_KEY': ''}):
            result = LLMService.classify('I cannot log in to my account')
        # Keyword fallback should detect "log in" + "account" → account category
        self.assertEqual(result['suggested_category'], 'account')
        self.assertIn(result['suggested_priority'], {'high', 'critical'})

    @patch('tickets.services.llm_service.LLMService._call_gemini')
    def test_classify_handles_api_exception_with_fallback(self, mock_call):
        """Should fall back to keyword analysis when Gemini API fails."""
        mock_call.side_effect = Exception('API connection timeout')
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            result = LLMService.classify('Server is down and nothing works')
        # Keyword fallback should detect "down" → technical, urgency → high/critical
        self.assertEqual(result['suggested_category'], 'technical')
        self.assertIn(result['suggested_priority'], {'high', 'critical'})
        self.assertIn('warning', result)

    @patch('tickets.services.llm_service.LLMService._call_gemini')
    def test_classify_returns_gemini_result_on_success(self, mock_call):
        """Should return Gemini's result when API call succeeds."""
        mock_call.return_value = {
            'suggested_category': 'billing',
            'suggested_priority': 'medium',
        }
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'}):
            result = LLMService.classify('Double charge on my credit card')
        self.assertEqual(result['suggested_category'], 'billing')
        self.assertEqual(result['suggested_priority'], 'medium')
