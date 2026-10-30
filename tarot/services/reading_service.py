import logging

from django.contrib.auth.models import User
from django.shortcuts import aget_object_or_404
from ninja.errors import HttpError
from pydantic import ValidationError

from mentors.models import Mentor
from tarot.agents.common import ReadingDependencies
from tarot.agents.tarot_support_agent import tarot_support_agent
from tarot.enums import ReadingTypeEnum
from tarot.models import Reading
from tarot.services.draw_service import persist_draw
from tarot.services.interpretation_service import generate_interpretation
from tarot.spreads import get_active_spread
from tarot.utils import deduct_tokens

MIN_TOKEN_COST = 250  # Minimum upfront tokens required

logger = logging.getLogger(__name__)


async def create_reading(user, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None):
    if reading_type is not None:
        try:
            get_active_spread(reading_type)
        except ValueError as error:
            raise HttpError(422, str(error)) from error

    has_tokens = await deduct_tokens(user, MIN_TOKEN_COST)
    if not has_tokens:
        return "Insufficient tokens to create a reading."

    mentor = await aget_object_or_404(Mentor, id=mentor_id)

    try:
        deps = ReadingDependencies(question=question)
        validation_result = await tarot_support_agent.run(question, deps=deps)

        if not validation_result or not validation_result.data.is_valid:
            return f"Invalid question: {validation_result.data.reason}"

        actual_usage = validation_result.usage().total_tokens
        msg = f"Actual token usage: {actual_usage}"
        logger.info(msg)

        # Deduct the difference between actual usage and upfront tokens
        if actual_usage and actual_usage > MIN_TOKEN_COST:
            extra_cost = actual_usage - MIN_TOKEN_COST
            await deduct_tokens(user, extra_cost)

        theme = validation_result.data.theme
        spread_type = reading_type or validation_result.data.spread_type

    except AttributeError as e:
        return f"Data validation error: Missing attribute - {e}"
    except ValidationError as e:
        return f"Validation error: {e}"

    try:
        get_active_spread(spread_type)
    except ValueError:
        logger.info(
            "Support agent suggested unavailable spread %s; falling back to %s",
            spread_type,
            ReadingTypeEnum.SINGLE_CARD.value,
        )
        spread_type = ReadingTypeEnum.SINGLE_CARD

    reading = await Reading.objects.acreate(
        user=user,
        mentor=mentor,
        question=question,
        notes=f"Theme: {theme}, Tokens spent for validation: {validation_result.usage()}",
        reading_type=spread_type,
    )
    return await persist_draw(reading)


async def list_readings(user, filters):
    readings = Reading.objects.filter(user=user).order_by("-date")
    return filters.filter(readings)


async def get_reading(user, reading_id: int):
    return await aget_object_or_404(Reading, id=reading_id, user=user)


async def generate_insight(user: User, reading_id: int):
    has_tokens = await deduct_tokens(user, MIN_TOKEN_COST)
    if not has_tokens:
        return "Insufficient tokens to generate celestial insight."

    reading = await aget_object_or_404(Reading, id=reading_id, user=user)
    return await generate_interpretation(reading.id)
