from secrets import token_urlsafe

from asgiref.sync import async_to_sync
from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.utils import translation
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from tarot.forms import ReadingJourneyForm
from tarot.models import Reading
from tarot.services.draw_service import persist_draw
from tarot.services.interpretation_service import generate_interpretation, retry_interpretation

ANONYMOUS_OWNER_SESSION_KEY = "tarot_anonymous_owner_key"


def get_anonymous_owner_key(request) -> str:
    owner_key = request.session.get(ANONYMOUS_OWNER_SESSION_KEY)
    if not owner_key:
        owner_key = token_urlsafe(32)
        request.session[ANONYMOUS_OWNER_SESSION_KEY] = owner_key
    return owner_key


def is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


def get_journey_locale(value: str | None) -> str:
    return value if value in {"en", "uk"} else "en"


def journey_context(form: ReadingJourneyForm, locale: str) -> dict:
    return {"form": form, "locale": locale, "mentors": form.fields["mentor"].queryset}


def get_owned_reading(request, reading_id: int) -> Reading:
    owner_key = request.session.get(ANONYMOUS_OWNER_SESSION_KEY, "")
    ownership = (
        Q(user=request.user)
        if request.user.is_authenticated
        else Q(anonymous_owner_key=owner_key) & ~Q(anonymous_owner_key="")
    )
    try:
        return Reading.objects.prefetch_related("cards__card").get(ownership, id=reading_id)
    except Reading.DoesNotExist as error:
        raise Http404 from error


@require_http_methods(["GET", "POST"])
def reading_journey(request):
    if not settings.TAROT_JOURNEY_ENABLED:
        raise Http404

    if request.method == "GET":
        get_anonymous_owner_key(request)
        locale = get_journey_locale(request.GET.get("locale"))
        translation.activate(locale)
        form = ReadingJourneyForm(initial={"locale": locale})
        return render(request, "tarot/journey.html", journey_context(form, locale))

    form = ReadingJourneyForm(request.POST)
    if not form.is_valid():
        locale = get_journey_locale(request.POST.get("locale"))
        translation.activate(locale)
        template = "tarot/partials/journey_form.html" if is_htmx(request) else "tarot/journey.html"
        return render(request, template, journey_context(form, locale), status=422)

    owner_key = get_anonymous_owner_key(request)
    reading = Reading.objects.create(
        user=request.user if request.user.is_authenticated else None,
        anonymous_owner_key="" if request.user.is_authenticated else owner_key,
        mentor=form.cleaned_data["mentor"],
        question=form.cleaned_data["question"],
        reading_type=form.cleaned_data["reading_type"],
        locale=form.cleaned_data["locale"],
    )
    async_to_sync(persist_draw)(reading)
    translation.activate(reading.locale)

    if is_htmx(request):
        reading = Reading.objects.prefetch_related("cards__card").get(id=reading.id)
        return render(request, "tarot/partials/reading.html", {"reading": reading}, status=201)
    return redirect("tarot:reading-detail", reading_id=reading.id)


@require_GET
def reading_detail(request, reading_id: int):
    reading = get_owned_reading(request, reading_id)
    with translation.override(reading.locale):
        return render(request, "tarot/reading_detail.html", {"reading": reading})


@require_POST
def reading_retry(request, reading_id: int):
    reading = get_owned_reading(request, reading_id)
    reading = async_to_sync(retry_interpretation)(reading.id)
    reading = Reading.objects.prefetch_related("cards__card").get(id=reading.id)
    if is_htmx(request):
        with translation.override(reading.locale):
            return render(request, "tarot/partials/reading.html", {"reading": reading})
    return redirect("tarot:reading-detail", reading_id=reading.id)


@require_POST
def reading_interpret(request, reading_id: int):
    reading = get_owned_reading(request, reading_id)
    if reading.interpretation_status != Reading.InterpretationStatus.COMPLETED:
        reading = async_to_sync(generate_interpretation)(reading.id)
    reading = Reading.objects.prefetch_related("cards__card").get(id=reading.id)
    if is_htmx(request):
        with translation.override(reading.locale):
            return render(request, "tarot/partials/reading.html", {"reading": reading})
    return redirect("tarot:reading-detail", reading_id=reading.id)


@require_POST
def claim_readings(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    owner_key = request.session.get(ANONYMOUS_OWNER_SESSION_KEY, "")
    if owner_key:
        Reading.objects.filter(anonymous_owner_key=owner_key, user__isnull=True).update(
            user=request.user,
            anonymous_owner_key="",
        )
    return redirect("tarot:journey")
