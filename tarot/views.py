"""
HTMX views for tarot UI - Dashboard and reading flows.

Provides session-authenticated pages for:
- Dashboard with token balance and recent readings
- Create reading form with mentor selection
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from tarot.models import Reading
from tarot.services.reading_service import MIN_TOKEN_COST
from users.models import UserProfile


@login_required
def dashboard(request):
    """Display user dashboard with token balance and recent readings."""
    try:
        profile = request.user.profile
        token_balance = profile.available_tokens
    except UserProfile.DoesNotExist:
        token_balance = 0

    # Get recent readings (last 10)
    readings = Reading.objects.filter(user=request.user).order_by("-date")[:10]

    context = {
        "token_balance": token_balance,
        "min_reading_cost": MIN_TOKEN_COST,
        "readings": readings,
    }

    return render(request, "dashboard.html", context)


@login_required
def create_reading(request):
    """Display create reading form with mentor selection."""
    from mentors.models import Mentor

    mentors = Mentor.objects.all()
    context = {
        "mentors": mentors,
        "min_reading_cost": MIN_TOKEN_COST,
    }

    return render(request, "create_reading.html", context)
