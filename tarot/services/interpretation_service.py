from asgiref.sync import sync_to_async
from django.db import transaction

from tarot.agents.celestial_agent import CelestialInsightResponse, celestial_agent
from tarot.agents.common import ReadingDependencies
from tarot.models import Reading, ReadingCard
from tarot.safety import safety_prompt_context, validate_reflective_response


def build_interpretation_prompt(reading: Reading, cards: list[ReadingCard]) -> str:
    mentor_style = (
        reading.mentor.style_instruction or reading.mentor.specialization
        if reading.mentor
        else "calm and thoughtful"
    )
    card_lines = [
        (
            f"reading_card_id={item.id}; position={item.position}; role={item.role}; "
            f"card={item.card.name}; orientation={item.orientation}"
        )
        for item in cards
    ]
    return "\n".join(
        [
            f"Question: {reading.question}",
            f"Locale: {reading.locale}",
            f"Mentor style: {mentor_style}",
            f"Safety: {safety_prompt_context(reading.question)}",
            "Use reflective, non-deterministic language. The saved draw is authoritative:",
            *card_lines,
        ]
    )


def validate_interpretation(response: CelestialInsightResponse, cards: list[ReadingCard]) -> None:
    expected = {(item.id, item.position) for item in cards}
    received = {(item.reading_card_id, item.position) for item in response.positions}
    if received != expected or len(response.positions) != len(cards):
        message = "Interpretation must contain every persisted reading-card ID and position exactly once."
        raise ValueError(message)


def _load_for_interpretation(reading_id: int) -> tuple[Reading, list[ReadingCard]]:
    reading = Reading.objects.select_related("mentor").get(id=reading_id)
    cards = list(reading.cards.select_related("card").order_by("position"))
    if not cards:
        message = "A persisted draw is required before interpretation."
        raise ValueError(message)

    reading.interpretation_status = Reading.InterpretationStatus.PENDING
    reading.interpretation_error = ""
    reading.save(update_fields=["interpretation_status", "interpretation_error"])
    return reading, cards


def _save_completed_interpretation(
    reading_id: int,
    response: CelestialInsightResponse,
) -> Reading:
    with transaction.atomic():
        reading = Reading.objects.select_for_update().get(id=reading_id)
        cards = list(reading.cards.order_by("position"))
        validate_interpretation(response, cards)
        response_by_id = {item.reading_card_id: item for item in response.positions}
        for card in cards:
            card.interpretation = response_by_id[card.id].interpretation
        ReadingCard.objects.bulk_update(cards, ["interpretation"])

        reading.celestial_insight = response.text
        reading.interpretation_status = Reading.InterpretationStatus.COMPLETED
        reading.interpretation_error = ""
        reading.save(update_fields=["celestial_insight", "interpretation_status", "interpretation_error"])
        return reading


def _save_failed_interpretation(reading_id: int, error: Exception) -> Reading:
    reading = Reading.objects.get(id=reading_id)
    reading.interpretation_status = Reading.InterpretationStatus.FAILED
    reading.interpretation_error = str(error)[:1000]
    reading.save(update_fields=["interpretation_status", "interpretation_error"])
    return reading


async def generate_interpretation(reading_id: int, interpreter=celestial_agent) -> Reading:
    reading, cards = await sync_to_async(_load_for_interpretation, thread_sensitive=True)(reading_id)
    prompt = build_interpretation_prompt(reading, cards)
    deps = ReadingDependencies(
        question=reading.question,
        locale=reading.locale,
        mentor_style=(reading.mentor.style_instruction or reading.mentor.specialization) if reading.mentor else "",
    )

    try:
        result = await interpreter.run(prompt, deps=deps)
        response = result.data
        validate_interpretation(response, cards)
        validate_reflective_response(reading.question, response)
    except Exception as error:  # Provider and schema failures share the persisted failed state.
        return await sync_to_async(_save_failed_interpretation, thread_sensitive=True)(reading_id, error)

    return await sync_to_async(_save_completed_interpretation, thread_sensitive=True)(reading_id, response)


async def retry_interpretation(reading_id: int, interpreter=celestial_agent) -> Reading:
    return await generate_interpretation(reading_id, interpreter=interpreter)
