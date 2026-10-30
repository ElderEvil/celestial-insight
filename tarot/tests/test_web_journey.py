from http import HTTPStatus

import pytest
from model_bakery import baker

from tarot.models import Reading
from tarot.views import ANONYMOUS_OWNER_SESSION_KEY


@pytest.fixture
def journey_catalogue(db):
    baker.make("tarot.Card", _quantity=12)
    return baker.make("mentors.Mentor", name="Aster", is_active=True)


def journey_payload(mentor, **overrides):
    payload = {
        "mentor": mentor.id,
        "question": "What should I notice this week?",
        "reading_type": "three_card_spread",
        "locale": "en",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_journey_loads_and_creates_reading_without_javascript(client, journey_catalogue):
    expected_card_count = 3
    page = client.get("/")
    response = client.post("/", journey_payload(journey_catalogue))
    reading = Reading.objects.get()

    assert page.status_code == HTTPStatus.OK
    assert b"<form" in page.content
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f"/readings/{reading.id}/"
    assert reading.anonymous_owner_key == client.session[ANONYMOUS_OWNER_SESSION_KEY]
    assert reading.cards.count() == expected_card_count


@pytest.mark.django_db
def test_invalid_submission_preserves_values_and_creates_no_reading(client, journey_catalogue):
    response = client.post("/", journey_payload(journey_catalogue, question=""))

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert b"three_card_spread" in response.content
    assert Reading.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invalid_values",
    [
        {"reading_type": "horseshoe_spread"},
        {"reading_type": "unknown-spread"},
    ],
)
def test_unsupported_spread_is_rejected_by_journey_form(client, journey_catalogue, invalid_values):
    response = client.post("/", journey_payload(journey_catalogue, **invalid_values))

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert Reading.objects.count() == 0


@pytest.mark.django_db
def test_inactive_mentor_is_rejected_by_journey_form(client, journey_catalogue):
    inactive_mentor = baker.make("mentors.Mentor", is_active=False)

    response = client.post("/", journey_payload(inactive_mentor))

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert Reading.objects.count() == 0


@pytest.mark.django_db
def test_reading_is_private_to_owning_session(client, journey_catalogue, django_user_model):
    client.post("/", journey_payload(journey_catalogue))
    reading = Reading.objects.get()
    other_client = client.__class__()

    assert client.get(f"/readings/{reading.id}/").status_code == HTTPStatus.OK
    assert other_client.get(f"/readings/{reading.id}/").status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_htmx_creation_returns_only_journey_region(client, journey_catalogue):
    response = client.post("/", journey_payload(journey_catalogue), headers={"HX-Request": "true"})

    assert response.status_code == HTTPStatus.CREATED
    assert b'id="journey-region"' in response.content
    assert b"<html" not in response.content
    assert b"Interpretation is pending" in response.content
    assert b'hx-trigger="load"' in response.content


@pytest.mark.django_db
def test_ukrainian_saved_reading_uses_localized_reflection_notice(client, journey_catalogue):
    response = client.post("/", journey_payload(journey_catalogue, locale="uk"))

    detail = client.get(response.url)

    assert detail.status_code == HTTPStatus.OK
    assert "Ваше читання" in detail.content.decode()
    assert "простір для роздумів" in detail.content.decode()


@pytest.mark.django_db
def test_saved_reading_renders_in_stored_locale_regardless_of_accept_language(
    client, journey_catalogue
):
    client.post("/", journey_payload(journey_catalogue, locale="uk"))
    reading = Reading.objects.get()

    detail = client.get(f"/readings/{reading.id}/", HTTP_ACCEPT_LANGUAGE="en")

    content = detail.content.decode()
    assert detail.status_code == HTTPStatus.OK
    assert "Ваше читання" in content
    assert "простір для роздумів" in content
    assert "Tarot offers space for reflection" not in content


@pytest.mark.django_db
def test_ukrainian_journey_uses_localized_mentor_content(client, journey_catalogue):
    journey_catalogue.display_name_uk = "Астер"
    journey_catalogue.biography_en = "English biography"
    journey_catalogue.biography_uk = "Українська біографія"
    journey_catalogue.save()

    response = client.get("/?locale=uk")

    content = response.content.decode()
    assert "Почніть рефлексивне читання таро" in content
    assert "Begin a reflective tarot reading" not in content
    assert "Астер" in content
    assert "Українська біографія" in content
    assert "English biography" not in content


@pytest.mark.django_db
def test_pending_reading_auto_requests_interpretation_over_htmx(client, journey_catalogue, monkeypatch):
    client.post("/", journey_payload(journey_catalogue))
    reading = Reading.objects.get()

    async def fake_generate_interpretation(reading_id):
        saved_reading = await Reading.objects.aget(id=reading_id)
        saved_reading.celestial_insight = "Notice what is present."
        saved_reading.interpretation_status = Reading.InterpretationStatus.COMPLETED
        await saved_reading.asave(update_fields=["celestial_insight", "interpretation_status"])
        return saved_reading

    monkeypatch.setattr("tarot.views.generate_interpretation", fake_generate_interpretation)
    response = client.post(
        f"/readings/{reading.id}/interpret/",
        headers={"HX-Request": "true"},
    )

    reading.refresh_from_db()
    assert response.status_code == HTTPStatus.OK
    assert reading.interpretation_status == Reading.InterpretationStatus.COMPLETED
    assert b"Notice what is present." in response.content


@pytest.mark.django_db
def test_anonymous_reading_can_be_claimed_after_authentication(client, journey_catalogue, django_user_model):
    client.post("/", journey_payload(journey_catalogue))
    reading = Reading.objects.get()
    user = django_user_model.objects.create_user(username="seeker")
    client.force_login(user)

    response = client.post("/readings/claim/")
    reading.refresh_from_db()

    assert response.status_code == HTTPStatus.FOUND
    assert reading.user == user
    assert reading.anonymous_owner_key == ""


@pytest.mark.django_db
def test_journey_uses_product_managed_mentor_image(client):
    mentor = baker.make(
        "mentors.Mentor",
        is_active=True,
        managed_image_path="mentors/neutral.jpg",
        avatar_url="https://example.invalid/hotlinked.jpg",
    )

    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert b"/static/mentors/neutral.jpg" in response.content
    assert mentor.avatar_url.encode() not in response.content
