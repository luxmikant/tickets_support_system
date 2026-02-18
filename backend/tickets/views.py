"""
API views for the Support Ticket System.

TicketViewSet — CRUD operations for tickets (list, create, partial_update)
StatsView — aggregated ticket statistics (DB-level, no Python loops)
ClassifyView — LLM-based ticket classification
"""

import logging
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import TicketFilter
from .models import Ticket
from .serializers import (
    ClassifyRequestSerializer,
    TicketSerializer,
    TicketUpdateSerializer,
)
from .services.llm_service import LLMService

logger = logging.getLogger('tickets')


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for tickets — supports list, create, retrieve, and partial_update.
    PUT and DELETE are intentionally disabled (not in the spec).

    Endpoints:
        GET    /api/tickets/       — List all tickets (newest first, filtered)
        POST   /api/tickets/       — Create a new ticket (returns 201)
        GET    /api/tickets/<id>/  — Retrieve a single ticket
        PATCH  /api/tickets/<id>/  — Update status/category/priority
    """

    queryset = Ticket.objects.all()
    filterset_class = TicketFilter

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return TicketUpdateSerializer
        return TicketSerializer

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH requests — only status, category, priority are writable."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return full ticket data after update
        return Response(TicketSerializer(instance).data)

    def create(self, request, *args, **kwargs):
        """Create a new ticket — returns 201 on success."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StatsView(APIView):
    """
    GET /api/tickets/stats/

    Returns aggregated ticket statistics using database-level aggregation.
    All computation uses Django ORM aggregate/annotate — NO Python-level loops.

    Response format:
    {
        "total_tickets": 124,
        "open_tickets": 67,
        "avg_tickets_per_day": 8.3,
        "priority_breakdown": {"low": 30, "medium": 52, "high": 31, "critical": 11},
        "category_breakdown": {"billing": 28, "technical": 55, "account": 22, "general": 19}
    }
    """

    def get(self, request):
        # --- Aggregate counts ---
        counts = Ticket.objects.aggregate(
            total=Count('id'),
            open_count=Count('id', filter=Q(status='open')),
        )

        total_tickets = counts['total']
        open_tickets = counts['open_count']

        # --- Average tickets per day ---
        # Uses the date range from first ticket to now
        avg_per_day = 0.0
        if total_tickets > 0:
            first_ticket = Ticket.objects.earliest('created_at')
            days_elapsed = (timezone.now() - first_ticket.created_at).total_seconds() / 86400
            days_elapsed = max(days_elapsed, 1)  # Avoid division by zero
            avg_per_day = round(total_tickets / days_elapsed, 1)

        # --- Priority breakdown (DB-level grouping) ---
        priority_qs = (
            Ticket.objects
            .values('priority')
            .annotate(count=Count('id'))
            .order_by('priority')
        )
        # Initialize all priorities to 0, then fill from query
        priority_breakdown = {p.value: 0 for p in Ticket.Priority}
        for row in priority_qs:
            priority_breakdown[row['priority']] = row['count']

        # --- Category breakdown (DB-level grouping) ---
        category_qs = (
            Ticket.objects
            .values('category')
            .annotate(count=Count('id'))
            .order_by('category')
        )
        category_breakdown = {c.value: 0 for c in Ticket.Category}
        for row in category_qs:
            category_breakdown[row['category']] = row['count']

        return Response({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'avg_tickets_per_day': avg_per_day,
            'priority_breakdown': priority_breakdown,
            'category_breakdown': category_breakdown,
        })


class ClassifyView(APIView):
    """
    POST /api/tickets/classify/

    Accepts a JSON body with a `description` field and returns
    LLM-suggested category and priority.

    Request:  {"description": "I can't log into my account..."}
    Response: {"suggested_category": "account", "suggested_priority": "high"}

    On LLM failure, returns defaults with a warning field.
    """

    def post(self, request):
        serializer = ClassifyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        description = serializer.validated_data['description']

        logger.info(f'Classifying ticket description ({len(description)} chars)')
        result = LLMService.classify(description)

        return Response(result, status=status.HTTP_200_OK)
