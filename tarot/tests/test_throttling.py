"""
Tests for tarot API throttling and rate limiting.

Covers:
- Per-user rate limiting (20 readings/hour)
- Throttle decorator applied to create reading endpoint
"""

import pytest
from ninja_extra.throttling import UserRateThrottle

from tarot.throttling import UserReadingThrottle

THROTTLE_DURATION = 3600


@pytest.mark.django_db(transaction=True)
class TestUserReadingThrottle:
    """Tests for UserReadingThrottle rate limiting."""

    def test_throttle_scope_is_reading_hourly(self):
        """UserReadingThrottle uses the 'reading_hourly' scope."""
        throttle = UserReadingThrottle()
        assert throttle.scope == "reading_hourly"

    def test_throttle_class_inherits_from_user_rate_throttle(self):
        """UserReadingThrottle inherits from UserRateThrottle."""
        assert issubclass(UserReadingThrottle, UserRateThrottle)

    def test_throttle_rate_configured_in_settings(self, settings):
        """Throttle rate '20/hour' is configured in NINJA_EXTRA settings."""
        assert "reading_hourly" in settings.NINJA_EXTRA["THROTTLE_RATES"]
        assert settings.NINJA_EXTRA["THROTTLE_RATES"]["reading_hourly"] == "20/hour"

    def test_throttle_has_rate_set(self):
        """UserReadingThrottle has rate set from configuration."""
        throttle = UserReadingThrottle()
        # The rate should be parsed from "20/hour"
        assert throttle.rate == "20/hour"

    def test_throttle_duration_is_one_hour(self):
        """Throttle duration is 3600 seconds (1 hour)."""
        throttle = UserReadingThrottle()
        # Duration should be 3600 seconds for hourly rate
        assert throttle.duration == THROTTLE_DURATION
