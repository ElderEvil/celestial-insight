from django.shortcuts import get_object_or_404

from tarot.filters import CardFilterSchema
from tarot.models import Card, Reading


def list_cards(filters: CardFilterSchema):
    cards = Card.objects.select_related("suit").all()
    return filters.filter(cards)


def get_card(card_id: int):
    return get_object_or_404(Card, id=card_id)


def list_cards_in_reading(reading_id: int):
    reading = get_object_or_404(Reading, id=reading_id)
    return reading.cards.all()
