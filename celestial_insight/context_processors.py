"""Custom context processors for Celestial Insight."""

from django.conf import settings


def oauth_settings(request):
    """Add OAuth-related settings to template context."""
    return {
        "telegram_oauth_enabled": getattr(settings, "TELEGRAM_OAUTH_ENABLED", False),
    }
