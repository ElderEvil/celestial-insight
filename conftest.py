"""
Pytest configuration and fixtures for celestial-insight project.

Provides fixtures for:
- Django database access
- User and UserProfile creation
- Mentor creation
- Tarot cards and suits
- Mock PydanticAI agents
"""

import os
from unittest.mock import MagicMock

# Set dummy API key for tests - agents are mocked, never called
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")

import django
import pytest

# Configure Django settings before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celestial_insight.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from mentors.models import Mentor  # noqa: E402
from tarot.agents.celestial_agent import CardResponse, CelestialInsightResponse  # noqa: E402
from tarot.agents.tarot_support_agent import QuestionValidationResult  # noqa: E402
from tarot.enums import ReadingTypeEnum  # noqa: E402
from tarot.models import Card, Suit  # noqa: E402
from users.models import UserProfile  # noqa: E402


@pytest.fixture
def user(db) -> User:
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def user_profile(user) -> UserProfile:
    """Create a user profile with default tokens (handles signal-created profiles)."""
    profile, created = UserProfile.objects.get_or_create(user=user, defaults={"available_tokens": 1000})
    if not created:
        profile.available_tokens = 1000
        profile.save()
    return profile


@pytest.fixture
def user_with_low_tokens(db) -> tuple[User, UserProfile]:
    """Create a user with insufficient tokens for readings (handles signal-created profiles)."""
    user = User.objects.create_user(
        username="pooruser",
        email="poor@example.com",
        password="testpass123",
    )
    profile, created = UserProfile.objects.get_or_create(user=user, defaults={"available_tokens": 100})
    if not created:
        profile.available_tokens = 100
        profile.save()
    return user, profile


@pytest.fixture
def mentor(db) -> Mentor:
    """Create a test mentor."""
    return Mentor.objects.create(
        name="Test Mystic",
        mystical_level=5,
        specialization="Love & Relationships",
        is_active=True,
    )


@pytest.fixture
def suit(db) -> Suit:
    """Create a Major Arcana suit."""
    return Suit.objects.create(
        name="Major Arcana",
        description="The Major Arcana represents life's major themes and archetypes.",
        arcana="major",
    )


@pytest.fixture
def tarot_card(suit) -> Card:
    """Create a single tarot card (The Fool)."""
    return Card.objects.create(
        name="The Fool",
        description="The Fool represents new beginnings and unlimited potential.",
        number=0,
        upright_meaning="New beginnings, innocence, spontaneity",
        reversed_meaning="Recklessness, risk-taking, foolishness",
        keywords="beginnings,innocence,spontaneity",
        suit=suit,
    )


@pytest.fixture
def tarot_cards(suit) -> list[Card]:
    """Create multiple tarot cards for spread testing."""
    cards = [
        Card(
            name="The Fool",
            description="New beginnings and unlimited potential.",
            number=0,
            upright_meaning="New beginnings, innocence",
            reversed_meaning="Recklessness, foolishness",
            keywords="beginnings,innocence",
            suit=suit,
        ),
        Card(
            name="The Magician",
            description="Manifestation and resourcefulness.",
            number=1,
            upright_meaning="Manifestation, power, action",
            reversed_meaning="Manipulation, untapped talents",
            keywords="manifestation,power",
            suit=suit,
        ),
        Card(
            name="The High Priestess",
            description="Intuition and inner knowledge.",
            number=2,
            upright_meaning="Intuition, mystery, inner knowledge",
            reversed_meaning="Secrets, disconnected from intuition",
            keywords="intuition,mystery",
            suit=suit,
        ),
    ]
    return Card.objects.bulk_create(cards)


@pytest.fixture
def mock_validation_result():
    """Factory for creating mock validation results from tarot_support_agent."""

    def _create_result(
        *,
        is_valid: bool = True,
        reason: str | None = None,
        theme: str = "love",
        spread_type: ReadingTypeEnum = ReadingTypeEnum.SINGLE_CARD,
        total_tokens: int = 100,
    ):
        mock_result = MagicMock()
        mock_result.data = QuestionValidationResult(
            is_valid=is_valid,
            reason=reason,
            theme=theme,
            spread_type=spread_type,
        )
        mock_result.usage.return_value = MagicMock(total_tokens=total_tokens)
        return mock_result

    return _create_result


@pytest.fixture
def mock_celestial_result(tarot_cards):
    """Factory for creating mock celestial insight results."""

    def _create_result(
        text: str = "The cards reveal a path of transformation ahead.",
        card_names: list[str] | None = None,
        total_tokens: int = 200,
    ):
        if card_names is None:
            card_names = ["The Fool"]

        cards = [
            CardResponse(
                name=name,
                orientation="upright",
                role="Significator",
                interpretation=f"The {name} brings wisdom to your question.",
            )
            for name in card_names
        ]

        mock_result = MagicMock()
        mock_result.data = CelestialInsightResponse(text=text, cards=cards)
        mock_result.usage.return_value = MagicMock(total_tokens=total_tokens)
        return mock_result

    return _create_result
