"""
Tests for the Ticket API views.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from tickets.models import Ticket


class TicketAPITest(TestCase):
    """Test the ticket CRUD API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.ticket_data = {
            'title': 'Test ticket',
            'description': 'A detailed description of the test issue.',
            'category': 'technical',
            'priority': 'high',
        }

    def test_create_ticket_returns_201(self):
        """POST /api/tickets/ should return 201 on success."""
        response = self.client.post('/api/tickets/', self.ticket_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'Test ticket')
        self.assertEqual(response.data['status'], 'open')

    def test_create_ticket_missing_title_returns_400(self):
        """POST /api/tickets/ without title should return 400."""
        data = {**self.ticket_data}
        del data['title']
        response = self.client.post('/api/tickets/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_tickets_newest_first(self):
        """GET /api/tickets/ should return tickets newest first."""
        Ticket.objects.create(title='First', description='Desc 1')
        Ticket.objects.create(title='Second', description='Desc 2')
        response = self.client.get('/api/tickets/')
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(results[0]['title'], 'Second')

    def test_filter_by_category(self):
        """GET /api/tickets/?category=billing should filter correctly."""
        Ticket.objects.create(title='T1', description='D1', category='billing')
        Ticket.objects.create(title='T2', description='D2', category='technical')
        response = self.client.get('/api/tickets/?category=billing')
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category'], 'billing')

    def test_search_by_title(self):
        """GET /api/tickets/?search=login should search title."""
        Ticket.objects.create(title='Login issue', description='Cannot log in')
        Ticket.objects.create(title='Billing problem', description='Overcharged')
        response = self.client.get('/api/tickets/?search=login')
        results = response.data['results']
        self.assertEqual(len(results), 1)

    def test_patch_ticket_status(self):
        """PATCH /api/tickets/<id>/ should update status."""
        ticket = Ticket.objects.create(title='T1', description='D1')
        response = self.client.patch(
            f'/api/tickets/{ticket.id}/',
            {'status': 'in_progress'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'in_progress')

    def test_combined_filters(self):
        """Multiple filters should be combined with AND logic."""
        Ticket.objects.create(title='T1', description='D1', category='billing', priority='high')
        Ticket.objects.create(title='T2', description='D2', category='billing', priority='low')
        Ticket.objects.create(title='T3', description='D3', category='technical', priority='high')
        response = self.client.get('/api/tickets/?category=billing&priority=high')
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'T1')


class StatsAPITest(TestCase):
    """Test the stats aggregation endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_stats_empty_database(self):
        """Stats should return zeros when no tickets exist."""
        response = self.client.get('/api/tickets/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_tickets'], 0)
        self.assertEqual(response.data['open_tickets'], 0)

    def test_stats_with_tickets(self):
        """Stats should aggregate correctly."""
        Ticket.objects.create(title='T1', description='D1', category='billing', priority='high')
        Ticket.objects.create(title='T2', description='D2', category='billing', priority='low')
        Ticket.objects.create(title='T3', description='D3', category='technical', priority='high', status='resolved')

        response = self.client.get('/api/tickets/stats/')
        data = response.data
        self.assertEqual(data['total_tickets'], 3)
        self.assertEqual(data['open_tickets'], 2)
        self.assertEqual(data['priority_breakdown']['high'], 2)
        self.assertEqual(data['category_breakdown']['billing'], 2)
        self.assertEqual(data['category_breakdown']['technical'], 1)
