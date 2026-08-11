"""
Custom throttling classes for tarot API rate limiting.

Provides per-user throttling for reading endpoints to prevent abuse.
"""

from ninja_extra.throttling import UserRateThrottle


class UserReadingThrottle(UserRateThrottle):
    """
    Throttle reading creation to 20 requests per hour per authenticated user.

    Uses the 'reading_hourly' scope defined in NINJA_EXTRA["THROTTLE_RATES"].
    Returns HTTP 429 with Retry-After header when limit exceeded.
    """

    scope = "reading_hourly"
