"""
Tests for the Ticket model.
"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from tickets.models import Ticket


class TicketModelTest(TestCase):
    """Test the Ticket model and its constraints."""

    def test_create_ticket_with_defaults(self):
        """A ticket with only required fields should get sensible defaults."""
        ticket = Ticket.objects.create(
            title='Test ticket',
            description='This is a test description for the ticket.',
        )
        self.assertEqual(ticket.category, 'general')
        self.assertEqual(ticket.priority, 'medium')
        self.assertEqual(ticket.status, 'open')
        self.assertIsNotNone(ticket.created_at)

    def test_create_ticket_with_all_fields(self):
        """A ticket with all fields explicitly set should persist correctly."""
        ticket = Ticket.objects.create(
            title='Billing issue',
            description='I was double-charged for my subscription.',
            category='billing',
            priority='high',
            status='open',
        )
        self.assertEqual(ticket.title, 'Billing issue')
        self.assertEqual(ticket.category, 'billing')
        self.assertEqual(ticket.priority, 'high')

    def test_ticket_ordering(self):
        """Tickets should be ordered by created_at descending (newest first)."""
        t1 = Ticket.objects.create(title='First', description='Desc 1')
        t2 = Ticket.objects.create(title='Second', description='Desc 2')
        tickets = list(Ticket.objects.all())
        self.assertEqual(tickets[0].id, t2.id)
        self.assertEqual(tickets[1].id, t1.id)

    def test_ticket_str_representation(self):
        """__str__ should return '[Priority] Title'."""
        ticket = Ticket.objects.create(
            title='Login broken',
            description='Cannot log in.',
            priority='critical',
        )
        self.assertEqual(str(ticket), '[Critical] Login broken')

    def test_title_max_length(self):
        """Title exceeding 200 chars should fail validation."""
        ticket = Ticket(
            title='A' * 201,
            description='Valid description.',
        )
        with self.assertRaises(ValidationError):
            ticket.full_clean()
