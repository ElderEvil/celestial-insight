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
    build_interpretation_prompt,
    generate_interpretation,
    retry_interpretation,
    validate_interpretation,
)

CELTIC_CROSS_CARD_COUNT = 10
PROMPT_SIZE_LIMIT = 12_000


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


def reading_card_for(reading, *, orientation, name="The Sun", position=1, **card_fields):
    defaults = {
        "upright_meaning": "UP",
        "reversed_meaning": "DOWN",
        "upright_meaning_uk": "ВГОРУ",
        "reversed_meaning_uk": "ВНИЗ",
        "keywords": "joy, hope",
        "keywords_uk": "радість, надія",
    }
    defaults.update(card_fields)
    card = baker.make("tarot.Card", name=name, **defaults)
    return baker.make(
        ReadingCard,
        reading=reading,
        card=card,
        position=position,
        orientation=orientation,
        role="Focus",
    )


@pytest.mark.django_db
def test_prompt_uses_the_meaning_matching_the_persisted_orientation():
    reading = baker.make("tarot.Reading", locale="en", mentor=None, question="What now?")
    upright = reading_card_for(reading, orientation="upright", position=1)
    reversed_card = reading_card_for(reading, orientation="reversed", name="The Moon", position=2)

    prompt = build_interpretation_prompt(reading, [upright, reversed_card])

    assert "card=The Sun; orientation=upright; keywords=joy, hope; meaning=UP" in prompt
    assert "card=The Moon; orientation=reversed; keywords=joy, hope; meaning=DOWN" in prompt


@pytest.mark.django_db
def test_prompt_uses_the_stored_locale_with_english_fallback():
    ukrainian = baker.make("tarot.Reading", locale="uk", mentor=None, question="Що далі?")
    uk_card = reading_card_for(ukrainian, orientation="upright")

    uk_prompt = build_interpretation_prompt(ukrainian, [uk_card])
    assert "keywords=радість, надія; meaning=ВГОРУ" in uk_prompt

    english = baker.make("tarot.Reading", locale="en", mentor=None, question="What now?")
    fallback_card = reading_card_for(english, orientation="reversed", upright_meaning_uk="", reversed_meaning_uk="")
    fallback_prompt = build_interpretation_prompt(english, [fallback_card])
    assert "meaning=DOWN" in fallback_prompt


@pytest.mark.django_db
def test_prompt_stays_bounded_for_a_full_celtic_cross():
    reading = baker.make("tarot.Reading", locale="en", mentor=None, reading_type=ReadingTypeEnum.CELTIC_CROSS_SPREAD)
    long_meaning = " ".join(["reflection"] * 55)
    cards = [
        baker.make(
            ReadingCard,
            reading=reading,
            card=baker.make(
                "tarot.Card",
                name=f"Card {position}",
                upright_meaning=long_meaning,
                reversed_meaning=long_meaning,
            ),
            position=position,
            orientation="upright",
            role=f"Role {position}",
        )
        for position in range(1, 11)
    ]

    prompt = build_interpretation_prompt(reading, cards)

    assert len(prompt) < PROMPT_SIZE_LIMIT
    assert prompt.count("reading_card_id=") == CELTIC_CROSS_CARD_COUNT
