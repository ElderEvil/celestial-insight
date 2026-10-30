from types import SimpleNamespace

import pytest
from asgiref.sync import async_to_sync
from model_bakery import baker
from pydantic import ValidationError

from tarot.agents.celestial_agent import CelestialInsightResponse, PositionInterpretation
from tarot.enums import ReadingTypeEnum
from tarot.models import Reading, ReadingCard
from tarot.services.draw_service import persist_draw
from tarot.services.interpretation_service import (
    generate_interpretation,
    retry_interpretation,
    validate_interpretation,
)


class FakeInterpreter:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    async def run(self, prompt, deps):
        if self.error:
            raise self.error
        return SimpleNamespace(data=self.response)


@pytest.fixture
def reading_with_draw(db):
    baker.make("tarot.Card", _quantity=12)
    reading = baker.make(
        "tarot.Reading",
        reading_type=ReadingTypeEnum.THREE_CARD_SPREAD,
        question="What can I learn from this change?",
    )
    async_to_sync(persist_draw)(reading)
    return Reading.objects.get(id=reading.id)


def response_for(reading):
    return CelestialInsightResponse(
        text="Consider what these themes invite you to notice.",
        positions=[
            PositionInterpretation(
                reading_card_id=card.id,
                position=card.position,
                interpretation=f"Reflect on {card.role}.",
            )
            for card in reading.cards.order_by("position")
        ],
        follow_up_prompt="What feels most useful here?",
    )


def test_response_schema_rejects_duplicate_positions():
    with pytest.raises(ValidationError, match="must be unique"):
        CelestialInsightResponse(
            text="Reflection",
            positions=[
                PositionInterpretation(reading_card_id=1, position=1, interpretation="First"),
                PositionInterpretation(reading_card_id=2, position=1, interpretation="Duplicate"),
            ],
        )


@pytest.mark.django_db
def test_validation_rejects_missing_or_unknown_persisted_positions(reading_with_draw):
    response = response_for(reading_with_draw)
    response.positions.pop()
    response.positions[0].reading_card_id = 999999
    cards = list(reading_with_draw.cards.order_by("position"))

    with pytest.raises(ValueError, match="every persisted"):
        validate_interpretation(response, cards)


@pytest.mark.django_db
def test_provider_failure_preserves_draw_and_retry_updates_same_rows(reading_with_draw):
    initial_draw = list(
        reading_with_draw.cards.order_by("position").values_list("id", "card_id", "orientation", "role")
    )
    failed = async_to_sync(generate_interpretation)(
        reading_with_draw.id,
        interpreter=FakeInterpreter(error=RuntimeError("provider unavailable")),
    )

    assert failed.interpretation_status == Reading.InterpretationStatus.FAILED
    assert "provider unavailable" in failed.interpretation_error

    completed = async_to_sync(retry_interpretation)(
        reading_with_draw.id,
        interpreter=FakeInterpreter(response=response_for(reading_with_draw)),
    )
    final_draw = list(
        ReadingCard.objects.filter(reading=reading_with_draw)
        .order_by("position")
        .values_list("id", "card_id", "orientation", "role")
    )

    assert completed.interpretation_status == Reading.InterpretationStatus.COMPLETED
    assert completed.interpretation_error == ""
    assert final_draw == initial_draw
    assert all(card.interpretation for card in ReadingCard.objects.filter(reading=reading_with_draw))


@pytest.mark.django_db
def test_unknown_model_card_id_fails_without_remapping_draw(reading_with_draw):
    response = response_for(reading_with_draw)
    response.positions[0].reading_card_id = 999999
    initial_card_ids = list(reading_with_draw.cards.order_by("position").values_list("card_id", flat=True))

    result = async_to_sync(generate_interpretation)(
        reading_with_draw.id,
        interpreter=FakeInterpreter(response=response),
    )

    assert result.interpretation_status == Reading.InterpretationStatus.FAILED
    assert list(reading_with_draw.cards.order_by("position").values_list("card_id", flat=True)) == initial_card_ids
