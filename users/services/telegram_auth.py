import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

NOT_CONFIGURED_MESSAGE = "Telegram authentication is not configured."
MISSING_HASH_MESSAGE = "Telegram init data has no hash."
INVALID_SIGNATURE_MESSAGE = "Telegram init data signature is invalid."
INCOMPLETE_DATA_MESSAGE = "Telegram init data is incomplete."
EXPIRED_DATA_MESSAGE = "Telegram init data has expired."


class TelegramAuthenticationError(ValueError):
    pass


def verify_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int,
    *,
    now: int | None = None,
) -> dict:
    if not bot_token:
        raise TelegramAuthenticationError(NOT_CONFIGURED_MESSAGE)

    values = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    supplied_hash = values.pop("hash", "")
    if not supplied_hash:
        raise TelegramAuthenticationError(MISSING_HASH_MESSAGE)

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, supplied_hash):
        raise TelegramAuthenticationError(INVALID_SIGNATURE_MESSAGE)

    try:
        auth_date = int(values["auth_date"])
        user_data = json.loads(values["user"])
        telegram_id = int(user_data["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise TelegramAuthenticationError(INCOMPLETE_DATA_MESSAGE) from error

    current_time = int(time.time()) if now is None else now
    if auth_date > current_time + 30 or current_time - auth_date > max_age_seconds:
        raise TelegramAuthenticationError(EXPIRED_DATA_MESSAGE)

    user_data["id"] = telegram_id
    return user_data
