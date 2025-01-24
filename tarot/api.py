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
class AsyncTarotController:
    # CARDS
    @http_get("/cards", response=list[CardSchemaShort])
    async def list_tarot_cards(self, filters: CardFilterSchema = Query(...)):
        return await list_cards(filters)

    @http_get("/cards/{card_slug}", response=CardSchema)
    async def get_tarot_card(self, card_slug: str):
        return await get_card(card_slug)

    # READINGS
    @http_post("/readings", response=ReadingSchema | str)
    async def create_tarot_reading(
        self, request, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None
    ):
        return await create_reading(request, question, mentor_id, reading_type)

    @http_get("/readings/my", response=list[ReadingSchemaShort])
    async def list_tarot_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        return await list_readings(request, filters)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    async def get_tarot_reading(self, request, reading_id: int):
        return await get_reading(request, reading_id)

    @http_get("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    async def list_tarot_cards_in_reading(self, request, reading_id: int):
        return await list_cards_in_reading(reading_id)

    @http_post("/readings/{reading_id}/insight", response=CelestialInsightResponseSchema | str)
    async def generate_tarot_insight(self, request, reading_id: int):
        return await generate_insight(request, reading_id)
