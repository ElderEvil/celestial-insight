from http import HTTPStatus
from types import SimpleNamespace

import pytest
from model_bakery import baker

from tarot.enums import ReadingTypeEnum
from tarot.models import Reading, ReadingCard
from tarot.services import reading_service
from users.models import UserProfile


class _FakeUsage:
    total_tokens = 0


class _FakeValidationResult:
    def __init__(self, spread_type):
        self.data = SimpleNamespace(
            is_valid=True,
            reason=None,
            theme="guidance",
            spread_type=spread_type,
        )

    def usage(self):
        return _FakeUsage()


class _FakeSupportAgent:
    def __init__(self, spread_type):
        self.spread_type = spread_type

    async def run(self, question, deps=None):
        return _FakeValidationResult(self.spread_type)


def _login_with_profile(client, django_user_model, username="seeker"):
    user = django_user_model.objects.create_user(username=username)
    UserProfile.objects.create(user=user)
    client.force_login(user)
    return user


@pytest.mark.django_db
def test_reading_api_returns_persisted_card_ids_and_roles(client, django_user_model):
    user = django_user_model.objects.create_user(username="seeker")
    reading = baker.make("tarot.Reading", user=user)
    cards = baker.make("tarot.Card", _quantity=3)
    reading_cards = [
        baker.make(
            ReadingCard,
            reading=reading,
            card=card,
            position=position,
            role=role,
            orientation="upright",
        )
        for position, (card, role) in enumerate(zip(cards, ("Past", "Present", "Future"), strict=True), start=1)
    ]
    client.force_login(user)

    response = client.get(f"/api/tarot/readings/{reading.id}")

    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert [item["id"] for item in payload["cards"]] == [item.id for item in reading_cards]
    assert [item["card"]["id"] for item in payload["cards"]] == [item.card_id for item in reading_cards]
    assert [item["role"] for item in payload["cards"]] == ["Past", "Present", "Future"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "reading_type",
    ["horseshoe_spread", "relationship_spread", "secret_reveal"],
)
def test_readings_api_rejects_unsupported_or_inactive_spread(
    client, django_user_model, monkeypatch, reading_type
):
    client.raise_request_exception = False
    _login_with_profile(client, django_user_model)
    mentor = baker.make("mentors.Mentor")
    monkeypatch.setattr(
        reading_service,
        "tarot_support_agent",
        _FakeSupportAgent(ReadingTypeEnum.THREE_CARD_SPREAD),
    )

    response = client.post(
        f"/api/tarot/readings?question=x&mentor_id={mentor.id}&reading_type={reading_type}",
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert Reading.objects.count() == 0


@pytest.mark.django_db
def test_readings_api_accepts_active_spread(client, django_user_model, monkeypatch):
    _login_with_profile(client, django_user_model)
    mentor = baker.make("mentors.Mentor")
    baker.make("tarot.Card", _quantity=3)
    monkeypatch.setattr(
        reading_service,
        "tarot_support_agent",
        _FakeSupportAgent(ReadingTypeEnum.THREE_CARD_SPREAD),
    )

    response = client.post(
        f"/api/tarot/readings?question=x&mentor_id={mentor.id}&reading_type=three_card_spread",
    )

    assert HTTPStatus.OK <= response.status_code < HTTPStatus.MULTIPLE_CHOICES
    assert Reading.objects.count() == 1
    assert Reading.objects.get().reading_type == ReadingTypeEnum.THREE_CARD_SPREAD


@pytest.mark.django_db
def test_create_reading_rejects_inactive_mentor(client, django_user_model, monkeypatch):
    client.raise_request_exception = False
    _login_with_profile(client, django_user_model)
    mentor = baker.make("mentors.Mentor", name="Dormant Mentor", is_active=False)
    baker.make("tarot.Card")
    monkeypatch.setattr(
        reading_service,
        "tarot_support_agent",
        _FakeSupportAgent(ReadingTypeEnum.SINGLE_CARD),
    )

    response = client.post(
        f"/api/tarot/readings?question=x&mentor_id={mentor.id}&reading_type=single_card",
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Reading.objects.count() == 0


@pytest.mark.django_db
def test_pick_mentor_rejects_inactive_mentor(client, django_user_model):
    user = _login_with_profile(client, django_user_model)
    mentor = baker.make("mentors.Mentor", name="Dormant Mentor", is_active=False)
    profile = UserProfile.objects.get(user=user)

    response = client.post(f"/api/mentors/{mentor.slug}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    profile.refresh_from_db()
    assert profile.preferred_mentor is None



