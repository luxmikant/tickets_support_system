"""
Custom filter for the Ticket model.

Supports filtering by:
    - category (exact match)
    - priority (exact match)
    - status (exact match)
    - search (case-insensitive search in title + description)
"""

import django_filters
from django.db.models import Q

from .models import Ticket


class TicketFilter(django_filters.FilterSet):
    """
    FilterSet for the Ticket model with combined search support.

    Usage:
        GET /api/tickets/?category=billing
        GET /api/tickets/?priority=high&status=open
        GET /api/tickets/?search=login+problem
        GET /api/tickets/?category=technical&search=error
    """

    category = django_filters.ChoiceFilter(choices=Ticket.Category.choices)
    priority = django_filters.ChoiceFilter(choices=Ticket.Priority.choices)
    status = django_filters.ChoiceFilter(choices=Ticket.Status.choices)
    search = django_filters.CharFilter(method='filter_search', label='Search')

    class Meta:
        model = Ticket
        fields = ['category', 'priority', 'status']

    def filter_search(self, queryset, name, value):
        """
        Search across title and description using case-insensitive contains.
        This uses database-level ILIKE (PostgreSQL) for performance.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(title__icontains=value) | Q(description__icontains=value)
        )
