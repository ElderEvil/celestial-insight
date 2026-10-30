import hashlib
import hmac
import json
import time
from http import HTTPStatus
from urllib.parse import urlencode

import pytest
from django.test import override_settings

from users.services.telegram_auth import TelegramAuthenticationError, verify_telegram_init_data

BOT_TOKEN = "123456:test-token"  # noqa: S105
AUTH_DATE = 1_700_000_000
TELEGRAM_USER_ID = 42


def signed_init_data(*, auth_date=AUTH_DATE, user=None):
    values = {
        "auth_date": str(auth_date),
        "query_id": "AAExample",
        "user": json.dumps(
            user or {"id": TELEGRAM_USER_ID, "first_name": "Ada", "username": "ada"},
            separators=(",", ":"),
        ),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_telegram_init_data_returns_verified_identity():
    result = verify_telegram_init_data(signed_init_data(), BOT_TOKEN, 300, now=AUTH_DATE + 10)

    assert result["id"] == TELEGRAM_USER_ID
    assert result["username"] == "ada"


def test_invalid_hash_is_rejected():
    with pytest.raises(TelegramAuthenticationError, match="signature"):
        verify_telegram_init_data(f"{signed_init_data()}tampered", BOT_TOKEN, 300, now=AUTH_DATE + 10)


def test_expired_init_data_is_rejected():
    with pytest.raises(TelegramAuthenticationError, match="expired"):
        verify_telegram_init_data(signed_init_data(), BOT_TOKEN, 300, now=AUTH_DATE + 301)


@pytest.mark.django_db
@override_settings(TELEGRAM_BOT_TOKEN=BOT_TOKEN, TELEGRAM_INIT_DATA_MAX_AGE_SECONDS=300)
def test_username_only_auth_request_is_rejected(client):
    response = client.post(
        "/api/tg/users/auth",
        data={"telegram_id": 42, "username": "ada"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
@override_settings(TELEGRAM_BOT_TOKEN=BOT_TOKEN, TELEGRAM_INIT_DATA_MAX_AGE_SECONDS=300)
def test_verified_init_data_issues_backend_tokens(client):
    response = client.post(
        "/api/tg/users/auth",
        data={"init_data": signed_init_data(auth_date=int(time.time()))},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["access"]
    assert response.json()["refresh"]
    assert response.json()["username"] == f"telegram_{TELEGRAM_USER_ID}"


@pytest.mark.django_db
@override_settings(TELEGRAM_BOT_TOKEN=BOT_TOKEN, TELEGRAM_INIT_DATA_MAX_AGE_SECONDS=300)
def test_invalid_init_data_endpoint_is_unauthorized(client):
    response = client.post(
        "/api/tg/users/auth",
        data={"init_data": f"{signed_init_data(auth_date=int(time.time()))}tampered"},
        content_type="application/json",
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
