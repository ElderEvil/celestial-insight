"""
Tests for tarot reading service - core flows and error cases.

Covers:
- Token deduction behavior
- create_reading with mocked AI validation
- generate_insight with mocked celestial agent
- Error handling for insufficient tokens
- Error handling for invalid questions
"""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic_ai.exceptions import AgentRunError

from tarot.enums import ReadingTypeEnum
from tarot.models import Reading
from tarot.services.reading_service import MAX_TOKENS_PER_READING, MIN_TOKEN_COST, create_reading, generate_insight
from tarot.utils import deduct_tokens


@pytest.mark.django_db(transaction=True)
class TestDeductTokens:
    """Tests for token deduction utility."""

    @pytest.mark.asyncio
    async def test_deduct_tokens_success(self, user, user_profile):
        """Token deduction succeeds when user has sufficient tokens."""
        initial_tokens = user_profile.available_tokens
        amount = 250

        result = await deduct_tokens(user, amount)

        assert result is True
        await user_profile.arefresh_from_db()
        assert user_profile.available_tokens == initial_tokens - amount

    @pytest.mark.asyncio
    async def test_deduct_tokens_insufficient(self, user_with_low_tokens):
        """Token deduction fails when user has insufficient tokens."""
        user, profile = user_with_low_tokens
        amount = MIN_TOKEN_COST  # 250 tokens required, user has 100

        result = await deduct_tokens(user, amount)

        low_token_amount = 100
        assert result is False
        await profile.arefresh_from_db()
        assert profile.available_tokens == low_token_amount  # Unchanged

    @pytest.mark.asyncio
    async def test_deduct_tokens_no_profile(self, db):
        """Token deduction fails gracefully when user has no profile."""
        from django.contrib.auth.models import User

        user = await User.objects.acreate(
            username="noprofile",
            email="noprofile@example.com",
        )

        result = await deduct_tokens(user, 100)

        assert result is False


@pytest.mark.django_db(transaction=True)
class TestCreateReading:
    """Tests for create_reading service function."""

    @pytest.mark.asyncio
    async def test_create_reading_success(self, user, user_profile, mentor, mock_validation_result):
        """Successfully create a reading with valid question."""
        mock_result = mock_validation_result(
            is_valid=True,
            theme="love",
            spread_type=ReadingTypeEnum.THREE_CARD_SPREAD,
            total_tokens=150,
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="What does the future hold for my relationship?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, Reading)
        assert result.user == user
        assert result.mentor == mentor
        assert result.question == "What does the future hold for my relationship?"
        assert result.reading_type == ReadingTypeEnum.THREE_CARD_SPREAD
        assert "Theme: love" in result.notes

    @pytest.mark.asyncio
    async def test_create_reading_with_explicit_reading_type(self, user, user_profile, mentor, mock_validation_result):
        """Reading type can be explicitly specified, overriding AI suggestion."""
        mock_result = mock_validation_result(
            is_valid=True,
            theme="career",
            spread_type=ReadingTypeEnum.SINGLE_CARD,
            total_tokens=100,
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="Should I change careers?",
                mentor_id=mentor.id,
                reading_type=ReadingTypeEnum.CELTIC_CROSS_SPREAD,
            )

        assert isinstance(result, Reading)
        assert result.reading_type == ReadingTypeEnum.CELTIC_CROSS_SPREAD

    @pytest.mark.asyncio
    async def test_create_reading_insufficient_tokens(self, user_with_low_tokens, mentor):
        """Returns error message when user lacks tokens."""
        user, _profile = user_with_low_tokens

        result = await create_reading(
            user=user,
            question="What does my future hold?",
            mentor_id=mentor.id,
        )

        assert result == "Insufficient tokens to create a reading."

    @pytest.mark.asyncio
    async def test_create_reading_invalid_question(self, user, user_profile, mentor, mock_validation_result):
        """Returns error message when question is invalid."""
        mock_result = mock_validation_result(
            is_valid=False,
            reason="Question is too vague for meaningful guidance.",
            theme="",
            spread_type=None,
            total_tokens=50,
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="Tell me everything",
                mentor_id=mentor.id,
            )

        assert isinstance(result, str)
        assert "Invalid question" in result
        assert "too vague" in result

    @pytest.mark.asyncio
    async def test_create_reading_deducts_extra_tokens(self, user, user_profile, mentor, mock_validation_result):
        """Extra tokens are deducted when usage exceeds MIN_TOKEN_COST."""
        initial_tokens = user_profile.available_tokens
        mock_result = mock_validation_result(
            is_valid=True,
            theme="spirituality",
            spread_type=ReadingTypeEnum.SINGLE_CARD,
            total_tokens=400,  # Exceeds MIN_TOKEN_COST of 250
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="What spiritual lesson awaits me?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, Reading)
        await user_profile.arefresh_from_db()
        # Should deduct MIN_TOKEN_COST (250) + extra (400-250=150) = 400 total
        assert user_profile.available_tokens == initial_tokens - 400

    @pytest.mark.asyncio
    async def test_create_reading_agent_run_error(self, user, user_profile, mentor):
        """Returns error string when tarot_support_agent raises AgentRunError."""
        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            side_effect=AgentRunError("Agent service unavailable"),
        ):
            result = await create_reading(
                user=user,
                question="Will I find love this year?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, str)
        assert "reading service encountered an error" in result
        assert "Please try again" in result


@pytest.mark.django_db(transaction=True)
class TestGenerateInsight:
    """Tests for generate_insight service function."""

    @pytest.mark.asyncio
    async def test_generate_insight_success(self, user, user_profile, mentor, tarot_cards, mock_celestial_result):
        """Successfully generate celestial insight for a reading."""
        # First create a reading
        reading = await Reading.objects.acreate(
            user=user,
            mentor=mentor,
            question="What guidance do the stars offer?",
            reading_type=ReadingTypeEnum.SINGLE_CARD,
        )

        mock_result = mock_celestial_result(
            text="The Fool appears to guide you toward new beginnings.",
            card_names=["The Fool"],
            total_tokens=180,
        )

        with patch(
            "tarot.services.reading_service.celestial_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await generate_insight(user=user, reading_id=reading.id)

        assert isinstance(result, Reading)
        assert "new beginnings" in result.celestial_insight
        # Check that cards were associated
        reading_cards = await result.cards.acount()
        assert reading_cards == 1

    @pytest.mark.asyncio
    async def test_generate_insight_insufficient_tokens(self, user_with_low_tokens, mentor):
        """Returns error message when user lacks tokens for insight."""
        user, _profile = user_with_low_tokens

        # Create reading first (manually, to bypass token check in test)
        reading = await Reading.objects.acreate(
            user=user,
            mentor=mentor,
            question="A question",
            reading_type=ReadingTypeEnum.SINGLE_CARD,
        )

        result = await generate_insight(user=user, reading_id=reading.id)

        assert result == "Insufficient tokens to generate celestial insight."

    @pytest.mark.asyncio
    async def test_generate_insight_card_not_found(self, user, user_profile, mentor, mock_celestial_result):
        """Returns error when AI suggests a card not in database."""
        reading = await Reading.objects.acreate(
            user=user,
            mentor=mentor,
            question="What does destiny hold?",
            reading_type=ReadingTypeEnum.SINGLE_CARD,
        )

        # No cards in database, but AI returns a card name
        mock_result = mock_celestial_result(
            text="The mysterious Unknown Card appears.",
            card_names=["Unknown Mystery Card"],
            total_tokens=150,
        )

        with patch(
            "tarot.services.reading_service.celestial_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await generate_insight(user=user, reading_id=reading.id)

        assert isinstance(result, str)
        assert "not found in the database" in result

    @pytest.mark.asyncio
    async def test_generate_insight_agent_run_error(self, user, user_profile, mentor):
        """Returns error string when celestial_agent raises AgentRunError."""
        reading = await Reading.objects.acreate(
            user=user,
            mentor=mentor,
            question="Test question",
            reading_type=ReadingTypeEnum.SINGLE_CARD,
        )

        with patch(
            "tarot.services.reading_service.celestial_agent.run",
            new_callable=AsyncMock,
            side_effect=AgentRunError("Agent service unavailable"),
        ):
            result = await generate_insight(user=user, reading_id=reading.id)

        assert isinstance(result, str)
        assert "insight generation service encountered an error" in result
        assert "Please try again" in result


@pytest.mark.django_db(transaction=True)
class TestCostGuardrails:
    """Tests for token cost guardrails (per-reading cap + daily budget)."""

    @pytest.mark.asyncio
    async def test_create_reading_per_reading_cap_enforced(self, user, user_profile, mentor, mock_validation_result):
        """Reading exceeding 2500 tokens is rejected."""
        # Mock usage > 2500 tokens
        mock_result = mock_validation_result(
            is_valid=True,
            theme="career",
            spread_type=ReadingTypeEnum.SINGLE_CARD,
            total_tokens=3000,  # Exceeds MAX_TOKENS_PER_READING of 2500
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="What is my complete life story including past present and future for every aspect including career love health family finances spiritual growth and personal development?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, str)
        assert "exceeds maximum token limit" in result
        assert "2500" in result
        assert "3000" in result

    @pytest.mark.asyncio
    async def test_create_reading_at_max_cap_allowed(self, user, user_profile, mentor, mock_validation_result):
        """Reading at exactly 2500 tokens is allowed."""
        # Mock usage = 2500 tokens (at the limit)
        mock_result = mock_validation_result(
            is_valid=True,
            theme="career",
            spread_type=ReadingTypeEnum.SINGLE_CARD,
            total_tokens=2500,  # Exactly at MAX_TOKENS_PER_READING
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="What career guidance do the cards offer?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, Reading)
        assert result.reading_type == ReadingTypeEnum.SINGLE_CARD

    @pytest.mark.asyncio
    async def test_create_reading_below_cap_allowed(self, user, user_profile, mentor, mock_validation_result):
        """Reading below 2500 tokens is allowed."""
        mock_result = mock_validation_result(
            is_valid=True,
            theme="love",
            spread_type=ReadingTypeEnum.SINGLE_CARD,
            total_tokens=500,  # Well below limit
        )

        with patch(
            "tarot.services.reading_service.tarot_support_agent.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await create_reading(
                user=user,
                question="What does the future hold for my love life?",
                mentor_id=mentor.id,
            )

        assert isinstance(result, Reading)
        assert result.reading_type == ReadingTypeEnum.SINGLE_CARD
