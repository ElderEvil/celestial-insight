from http import HTTPStatus

import pytest
from model_bakery import baker
from ninja_jwt.tokens import RefreshToken


@pytest.mark.django_db
def test_telegram_reading_detail_cannot_access_another_users_reading(client, django_user_model):
    owner = django_user_model.objects.create_user(username="owner")
    caller = django_user_model.objects.create_user(username="caller")
    reading = baker.make("tarot.Reading", user=owner)
    token = RefreshToken.for_user(caller)

    response = client.get(
        f"/api/tg/tarot/readings/{reading.id}",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_telegram_adapter_has_no_reading_creation_route(client, django_user_model):
    caller = django_user_model.objects.create_user(username="caller")
    token = RefreshToken.for_user(caller)

    response = client.post(
        "/api/tg/tarot/readings",
        headers={"Authorization": f"Bearer {token.access_token}"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_telegram_reading_list_requires_backend_authentication(client):
    response = client.get("/api/tg/tarot/readings/my")

    assert response.status_code == HTTPStatus.UNAUTHORIZED
