import random
from secrets import token_hex

from asgiref.sync import sync_to_async
from django.db import transaction

from tarot.models import Card, Reading, ReadingCard
from tarot.spreads import get_spread

ORIENTATIONS = ("upright", "reversed")


def _persist_draw(reading_id: int) -> Reading:
    with transaction.atomic():
        reading = Reading.objects.select_for_update().get(id=reading_id)
        existing_cards = reading.cards.order_by("position")
        if existing_cards.exists():
            return reading

        spread = get_spread(reading.reading_type)
        card_ids = list(Card.objects.values_list("id", flat=True))
        if len(card_ids) < len(spread.positions):
            message = f"The catalogue needs at least {len(spread.positions)} cards for this spread."
            raise ValueError(message)

        seed = reading.draw_seed or token_hex(32)
        generator = random.Random(seed)  # noqa: S311 - replayable selection is required for draw auditing.
        generator.shuffle(card_ids)
        selected_ids = card_ids[: len(spread.positions)]

        reading.draw_seed = seed
        reading.spread_version = spread.version
        reading.interpretation_status = Reading.InterpretationStatus.PENDING
        reading.interpretation_error = ""
        reading.save(
            update_fields=["draw_seed", "spread_version", "interpretation_status", "interpretation_error"]
        )

        ReadingCard.objects.bulk_create(
            [
                ReadingCard(
                    reading=reading,
                    card_id=card_id,
                    position=position,
                    orientation=generator.choice(ORIENTATIONS),
                    role=spread_position.role,
                )
                for position, (card_id, spread_position) in enumerate(
                    zip(selected_ids, spread.positions, strict=True),
                    start=1,
                )
            ]
        )
        return reading


async def persist_draw(reading: Reading) -> Reading:
    return await sync_to_async(_persist_draw, thread_sensitive=True)(reading.id)
