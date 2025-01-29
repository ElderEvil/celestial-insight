from django.shortcuts import aget_object_or_404

from tarot.filters import CardFilterSchema
from tarot.models import Card, Reading


async def list_cards(filters: CardFilterSchema):
    cards = Card.objects.all()
    return filters.filter(cards)


async def get_card(card_slug: str):
    return await aget_object_or_404(Card, slug=card_slug)


async def list_cards_in_reading(reading_id: int):
    reading = await aget_object_or_404(Reading, id=reading_id)
    return reading.cards.all()
