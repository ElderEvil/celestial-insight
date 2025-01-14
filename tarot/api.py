import logging

from ninja import Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions

from .enums import ReadingTypeEnum
from .filters import CardFilterSchema, ReadingFilterSchema
from .schemas import (
    CardSchema,
    CardSchemaShort,
    CelestialInsightResponseSchema,
    ReadingCardSchema,
    ReadingSchema,
    ReadingSchemaShort,
)
from .services.card_service import get_card, list_cards, list_cards_in_reading
from .services.reading_service import create_reading, generate_insight, get_reading, list_readings

api = NinjaExtraAPI()

logger = logging.getLogger(__name__)


@api_controller("/tarot", tags=["Tarot"], permissions=[permissions.IsAuthenticatedOrReadOnly])
class TarotController:
    # CARDS
    @http_get("/cards", response=list[CardSchemaShort])
    def list_tarot_cards(self, filters: CardFilterSchema = Query(...)):
        return list_cards(filters)

    @http_get("/cards/{card_id}", response=CardSchema)
    def get_tarot_card(self, card_id: int):
        return get_card(card_id)

    # READINGS
    @http_post("/readings", response=ReadingSchema | str)
    def create_tarot_reading(self, request, question: str, reading_type: ReadingTypeEnum | None = None):
        return create_reading(request, question, reading_type)

    @http_get("/readings/my", response=list[ReadingSchemaShort])
    def list_tarot_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        return list_readings(request, filters)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    def get_tarot_reading(self, request, reading_id: int):
        return get_reading(request, reading_id)

    @http_get("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def list_tarot_cards_in_reading(self, request, reading_id: int):
        return list_cards_in_reading(reading_id)

    @http_post("/readings/{reading_id}/insight", response=CelestialInsightResponseSchema | str)
    def generate_tarot_insight(self, request, reading_id: int):
        return generate_insight(request, reading_id)
