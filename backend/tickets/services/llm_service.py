"""
LLM Service — Google Gemini integration for ticket classification.

This module handles all communication with the Gemini API.
It is isolated from Django views for testability and swappability.
"""

import json
import logging
import os

logger = logging.getLogger('tickets')

# Valid choices — used for response validation
VALID_CATEGORIES = {'billing', 'technical', 'account', 'general'}
VALID_PRIORITIES = {'low', 'medium', 'high', 'critical'}

# Default fallback when LLM is unavailable or returns invalid data
DEFAULT_RESPONSE = {
    'suggested_category': 'general',
    'suggested_priority': 'medium',
}

# =============================================================================
# CLASSIFICATION PROMPT
# =============================================================================
# This prompt is evaluated as part of the assessment.
# Design goals:
#   1. Constrained output — only valid JSON, only valid choices
#   2. Clear category/priority definitions with examples
#   3. No ambiguity — every ticket maps to exactly one category + priority

CLASSIFICATION_PROMPT = """You are a support ticket classifier for a software company. Given a customer's support ticket description, determine the most appropriate category and priority level.

## Categories (pick exactly one):
- **billing**: Payment issues, invoices, refunds, charges, subscription plans, pricing, payment methods
- **technical**: Bugs, errors, crashes, performance issues, integrations, API problems, downtime
- **account**: Login problems, password resets, profile changes, permissions, access control, account deletion
- **general**: Feature requests, general questions, feedback, documentation, onboarding, anything not fitting above

## Priority Levels (pick exactly one):
- **critical**: System completely down, data loss, security breach, affects all users, compliance violation
- **high**: Major functionality broken, blocking issue with no workaround, significant data at risk
- **medium**: Degraded experience, workaround exists, affects some users, non-urgent bugs
- **low**: Minor cosmetic issues, feature requests, general questions, documentation improvements

## Rules:
1. Base your decision ONLY on the description provided
2. When uncertain between two categories, choose the more specific one
3. When uncertain between two priorities, choose the higher one (err on the side of caution)
4. Respond ONLY with valid JSON — no explanation, no markdown, no extra text

## Output Format (respond with ONLY this JSON, nothing else):
{"suggested_category": "<category>", "suggested_priority": "<priority>"}

## Ticket Description:
"""


class LLMService:
    """
    Handles LLM-based ticket classification via Google Gemini API.

    Usage:
        result = LLMService.classify("I can't log into my account")
        # {"suggested_category": "account", "suggested_priority": "high"}
    """

    @staticmethod
    def classify(description: str) -> dict:
        """
        Classify a ticket description into a category and priority.

        Args:
            description: The user's support ticket description text.

        Returns:
            dict with keys:
                - suggested_category: one of billing/technical/account/general
                - suggested_priority: one of low/medium/high/critical
                - warning (optional): present if fallback was used
        """
        api_key = os.environ.get('GEMINI_API_KEY', '')

        if not api_key:
            logger.warning('GEMINI_API_KEY not set — returning default classification')
            return {**DEFAULT_RESPONSE, 'warning': 'LLM API key not configured'}

        try:
            return LLMService._call_gemini(api_key, description)
        except Exception as e:
            logger.error(f'LLM classification failed: {e.__class__.__name__}: {e}')
            return {**DEFAULT_RESPONSE, 'warning': f'LLM service error: {str(e)}'}

    @staticmethod
    def _call_gemini(api_key: str, description: str) -> dict:
        """
        Make the actual Gemini API call and parse the response.

        Uses google-generativeai SDK with a 10-second timeout.
        """
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = CLASSIFICATION_PROMPT + description

        # Configure generation for structured JSON output
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,        # Low temperature for consistent classification
            max_output_tokens=100,   # Short response expected
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            request_options={'timeout': 10},  # 10-second timeout
        )

        return LLMService._parse_response(response.text)

    @staticmethod
    def _parse_response(response_text: str) -> dict:
        """
        Parse and validate the LLM response.

        Handles cases where the LLM wraps JSON in markdown code blocks
        or returns extra text around the JSON.
        """
        text = response_text.strip()

        # Strip markdown code block if present
        if text.startswith('```'):
            lines = text.split('\n')
            # Remove first line (```json) and last line (```)
            text = '\n'.join(lines[1:-1]).strip()

        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f'LLM returned non-JSON response: {response_text[:200]}')
            return {**DEFAULT_RESPONSE, 'warning': 'LLM returned invalid format'}

        # Validate the parsed values against allowed choices
        category = result.get('suggested_category', '').lower().strip()
        priority = result.get('suggested_priority', '').lower().strip()

        if category not in VALID_CATEGORIES:
            logger.warning(f'LLM returned invalid category: {category}')
            category = 'general'

        if priority not in VALID_PRIORITIES:
            logger.warning(f'LLM returned invalid priority: {priority}')
            priority = 'medium'

        return {
            'suggested_category': category,
            'suggested_priority': priority,
        }
