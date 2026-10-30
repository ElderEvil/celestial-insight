from pathlib import Path

from celestial_insight.configuration import ProductionConfiguration, production_configuration_errors


def valid_configuration(**overrides):
    values = {
        "secret_key": "stable-production-secret",
        "allowed_hosts": ["tarot.example.com"],
        "trusted_origins": ["https://tarot.example.com"],
        "media_root": Path("/srv/celestial/media"),
        "media_url": "/media/",
        "journey_enabled": True,
        "openai_api_key": "configured",
        "telegram_enabled": True,
        "telegram_bot_token": "configured",
    }
    values.update(overrides)
    return ProductionConfiguration(**values)


def test_safe_production_configuration_has_no_errors():
    assert production_configuration_errors(valid_configuration()) == []


def test_unsafe_production_configuration_reports_every_missing_boundary():
    expected_error_count = 6
    errors = production_configuration_errors(
        valid_configuration(
            secret_key="",
            allowed_hosts=["*"],
            trusted_origins=["http://tarot.example.com"],
            media_root=Path("relative/media"),
            media_url="media",
            openai_api_key="",
            telegram_bot_token="",
        )
    )

    assert len(errors) == expected_error_count
