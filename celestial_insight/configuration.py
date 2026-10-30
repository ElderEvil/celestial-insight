from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductionConfiguration:
    secret_key: str
    allowed_hosts: list[str]
    trusted_origins: list[str]
    media_root: Path
    media_url: str
    journey_enabled: bool
    openai_api_key: str
    telegram_enabled: bool
    telegram_bot_token: str


def production_configuration_errors(config: ProductionConfiguration) -> list[str]:
    errors = []
    if not config.secret_key:
        errors.append("DJANGO_SECRET_KEY must contain a stable production secret")
    if not config.allowed_hosts or "*" in config.allowed_hosts:
        errors.append("DJANGO_ALLOWED_HOSTS must list explicit production hosts")
    if not config.trusted_origins or any(not origin.startswith("https://") for origin in config.trusted_origins):
        errors.append("CSRF_TRUSTED_ORIGINS must contain only explicit HTTPS origins")
    if (
        not config.media_root.is_absolute()
        or not config.media_url.startswith("/")
        or not config.media_url.endswith("/")
    ):
        errors.append("MEDIA_ROOT and MEDIA_URL must identify local managed media")
    if config.journey_enabled and not config.openai_api_key:
        errors.append("OPENAI_API_KEY is required when TAROT_JOURNEY_ENABLED is true")
    if config.telegram_enabled and not config.telegram_bot_token:
        errors.append("TELEGRAM_BOT_TOKEN is required when TELEGRAM_CHANNEL_ENABLED is true")
    return errors
