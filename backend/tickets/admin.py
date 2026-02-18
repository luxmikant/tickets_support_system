from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin configuration for the Ticket model."""

    list_display = ('title', 'category', 'priority', 'status', 'created_at')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
