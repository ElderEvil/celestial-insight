"""
HTMX views for tarot UI - Dashboard and reading flows.

Provides session-authenticated pages for:
- Dashboard with token balance and recent readings
- Create reading form with mentor selection
"""

from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from mentors.models import Mentor
from tarot.models import Reading
from tarot.services.reading_service import MIN_TOKEN_COST, create_reading
from users.models import UserProfile

MIN_QUESTION_LENGTH = 5


@login_required
def dashboard(request):
    """Display user dashboard with token balance and recent readings."""
    try:
        # Handle both AnonymousUser (no profile attribute) and authenticated users without profile
        if hasattr(request.user, "profile"):
            profile = request.user.profile
            token_balance = profile.available_tokens
        else:
            token_balance = 0
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


async def create_reading_view(request):
    """Display create reading form with mentor selection."""

    # Check authentication - wrap the entire sync operation
    @sync_to_async
    def require_auth(request):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login

            return redirect_to_login(request.get_full_path())
        return None

    auth_result = await require_auth(request)
    if auth_result:
        return auth_result

    if request.method == "POST":
        # _handle_create_reading is already async, call directly
        return await _handle_create_reading(request)

    # GET request - show form (sync, wrapped for async context)
    mentors = await sync_to_async(list, thread_sensitive=True)(Mentor.objects.all())
    context = {
        "mentors": mentors,
        "min_reading_cost": MIN_TOKEN_COST,
    }

    return render(request, "create_reading.html", context)


async def _handle_create_reading(request):
    """Handle POST request for creating a reading."""

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
    if not question or len(question.strip()) < MIN_QUESTION_LENGTH:
        return HttpResponse(
            b'<article class="pico-background-red-100"><p>Question must be at least 5 characters.</p></article>',
            status=400,
            content_type="text/html",
        )

    # Create reading using service layer
    result = await create_reading(request.user, question.strip(), int(mentor_id))

    if isinstance(result, str):
        # Error occurred - show user-friendly message
        error_html = f'<article class="pico-background-red-100"><p>{result}</p></article>'
        return HttpResponse(
            error_html.encode(),
            status=400,
            content_type="text/html",
        )

    # Success - return partial with reading result
    return render(request, "reading_result.html", {"reading": result})
