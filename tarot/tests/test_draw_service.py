import pytest
from asgiref.sync import async_to_sync

from mentors.models import Mentor
from tarot.enums import ReadingTypeEnum
from tarot.models import Card, Reading, Suit
from tarot.services.draw_service import persist_draw


@pytest.fixture
def card_catalogue(db):
    suit = Suit.objects.create(name="Major Arcana", arcana="major")
    return [
        Card.objects.create(
            name=f"Card {index}",
            description="Description",
            number=index,
            upright_meaning="Upright",
            reversed_meaning="Reversed",
            keywords="reflection",
            suit=suit,
        )
        for index in range(12)
    ]


@pytest.mark.django_db
def test_persist_draw_saves_distinct_cards_and_ordered_roles(card_catalogue):
    expected_card_count = 3
    mentor = Mentor.objects.create(name="Guide", mystical_level=5)
    reading = Reading.objects.create(
        mentor=mentor,
        question="What should I reflect on?",
        reading_type=ReadingTypeEnum.THREE_CARD_SPREAD,
    )

    async_to_sync(persist_draw)(reading)
    saved_reading = Reading.objects.get(id=reading.id)
    cards = list(saved_reading.cards.order_by("position"))

    assert saved_reading.draw_seed
    assert [card.role for card in cards] == ["Past", "Present", "Future"]
    assert len({card.card_id for card in cards}) == expected_card_count
    assert {card.orientation for card in cards} <= {"upright", "reversed"}


@pytest.mark.django_db
def test_persist_draw_is_idempotent(card_catalogue):
    mentor = Mentor.objects.create(name="Guide", mystical_level=5)
    reading = Reading.objects.create(
        mentor=mentor,
        question="What should I reflect on?",
        reading_type=ReadingTypeEnum.THREE_CARD_SPREAD,
    )

    async_to_sync(persist_draw)(reading)
    first_draw = list(
        Reading.objects.get(id=reading.id)
        .cards.order_by("position")
        .values_list("card_id", "orientation", "role")
    )
    async_to_sync(persist_draw)(reading)
    second_draw = list(
        Reading.objects.get(id=reading.id)
        .cards.order_by("position")
        .values_list("card_id", "orientation", "role")
    )

    assert second_draw == first_draw
