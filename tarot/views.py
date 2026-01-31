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
from tarot.services.reading_service import MIN_TOKEN_COST, create_reading
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
async def create_reading(request):
    """Display create reading form with mentor selection."""
    from asgiref.sync import sync_to_async
    from mentors.models import Mentor

    if request.method == "POST":
        # Use sync_to_async for the sync ORM call
        return await sync_to_async(_handle_create_reading, thread_sensitive=True)(request)

    # GET request - show form (sync, wrapped for async context)
    mentors = await sync_to_async(list, thread_sensitive=True)(Mentor.objects.all())
    context = {
        "mentors": mentors,
        "min_reading_cost": MIN_TOKEN_COST,
    }

    return render(request, "create_reading.html", context)


async def _handle_create_reading(request):
    """Handle POST request for creating a reading."""
    from mentors.models import Mentor

    mentor_id = request.POST.get("mentor_id")
    question = request.POST.get("question")

    # Validate mentor selection
    if not mentor_id:
        return HttpResponse(
            b'<article class="pico-background-red-100"><p>Please select a mentor.</p></article>',
            status=400,
            content_type="text/html",
        )

    # Validate question
    if not question or len(question.strip()) < 5:
        return HttpResponse(
            b'<article class="pico-background-red-100"><p>Question must be at least 5 characters.</p></article>',
            status=400,
            content_type="text/html",
        )

    # Create reading using service layer
    result = await create_reading(request.user, question.strip(), int(mentor_id))

    if isinstance(result, str):
        # Error occurred
        error_html = f'<article class="pico-background-red-100"><p>{result}</p></article>'
        return HttpResponse(
            error_html.encode(),
            status=400,
            content_type="text/html",
        )

    # Success - return partial with reading result
    return render(request, "reading_result.html", {"reading": result})
