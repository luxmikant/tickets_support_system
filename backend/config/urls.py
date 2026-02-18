"""
URL configuration for the Support Ticket System.

Routes:
    /admin/          — Django admin
    /api/tickets/    — Ticket CRUD, stats, and classification
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/tickets/', include('tickets.urls')),
]
