from http import HTTPStatus

import pytest
from model_bakery import baker

from tarot.models import ReadingCard


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
