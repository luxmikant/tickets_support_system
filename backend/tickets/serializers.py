"""
DRF serializers for the Ticket model.

TicketSerializer — full CRUD serializer
TicketUpdateSerializer — restricted to status/category/priority (PATCH)
ClassifyRequestSerializer — input validation for the classify endpoint
"""

from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """
    Full serializer for creating and reading tickets.
    `created_at` is read-only (auto-set by the database).
    """

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description',
            'category', 'priority', 'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be blank.')
        return value.strip()

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Description cannot be blank.')
        return value.strip()


class TicketUpdateSerializer(serializers.ModelSerializer):
    """
    Restricted serializer for PATCH updates.
    Only allows changing status, category, and priority.
    Title and description are immutable after creation.
    """

    class Meta:
        model = Ticket
        fields = ['status', 'category', 'priority']


class ClassifyRequestSerializer(serializers.Serializer):
    """
    Input serializer for the /api/tickets/classify/ endpoint.
    Accepts a description string and validates it's not empty.
    """

    description = serializers.CharField(
        required=True,
        min_length=10,
        help_text='The ticket description to classify via LLM.',
    )

    def validate_description(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Description cannot be blank.')
        return value.strip()
