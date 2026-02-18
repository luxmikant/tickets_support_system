"""
Ticket model — core data entity for the support ticket system.

All field constraints (choices, NOT NULL) are enforced at the database level
via Django's CheckConstraint and field options.
"""

from django.db import models


class Ticket(models.Model):
    """
    Represents a customer support ticket.

    Fields:
        title: Short summary of the issue (max 200 chars)
        description: Full problem description
        category: Auto-suggested by LLM, user can override
        priority: Auto-suggested by LLM, user can override
        status: Workflow state, defaults to 'open'
        created_at: Timestamp, auto-set on creation
    """

    # --- Choice definitions ---
    class Category(models.TextChoices):
        BILLING = 'billing', 'Billing'
        TECHNICAL = 'technical', 'Technical'
        ACCOUNT = 'account', 'Account'
        GENERAL = 'general', 'General'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    # --- Fields ---
    title = models.CharField(
        max_length=200,
        blank=False,
        help_text='Short summary of the support issue',
    )
    description = models.TextField(
        blank=False,
        help_text='Full description of the problem',
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        help_text='Ticket category — auto-suggested by LLM, user can override',
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text='Ticket priority — auto-suggested by LLM, user can override',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        help_text='Current workflow status',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the ticket was created',
    )

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'

        # Database-level constraints — enforces valid choices even if
        # data is inserted outside Django (e.g., raw SQL, migrations)
        constraints = [
            models.CheckConstraint(
                condition=models.Q(category__in=['billing', 'technical', 'account', 'general']),
                name='valid_category',
            ),
            models.CheckConstraint(
                condition=models.Q(priority__in=['low', 'medium', 'high', 'critical']),
                name='valid_priority',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['open', 'in_progress', 'resolved', 'closed']),
                name='valid_status',
            ),
        ]

        indexes = [
            models.Index(fields=['category'], name='idx_ticket_category'),
            models.Index(fields=['priority'], name='idx_ticket_priority'),
            models.Index(fields=['status'], name='idx_ticket_status'),
        ]

    def __str__(self):
        return f'[{self.get_priority_display()}] {self.title}'
