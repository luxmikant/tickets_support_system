"""
URL routing for the tickets app.

Uses DRF's DefaultRouter for the TicketViewSet, with manual
registration for stats and classify endpoints (placed before
the router catch-all to avoid route conflicts).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'', views.TicketViewSet, basename='tickets')

# Stats and classify must be registered BEFORE the router
# so they don't get caught by the <id>/ pattern
urlpatterns = [
    path('stats/', views.StatsView.as_view(), name='ticket-stats'),
    path('classify/', views.ClassifyView.as_view(), name='ticket-classify'),
    path('', include(router.urls)),
]
