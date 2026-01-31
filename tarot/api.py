import logging

from django.contrib.auth.models import User
from django.shortcuts import aget_object_or_404
from ninja import Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.permissions import AllowAny, IsAuthenticated
from ninja_extra.throttling import throttle
from ninja_jwt.authentication import AsyncJWTAuth

from .enums import ReadingTypeEnum
from .filters import CardFilterSchema, ReadingFilterSchema
from .schemas import (
    CardSchema,
    CardSchemaShort,
    ReadingSchema,
    ReadingSchemaShort,
)
from .services.card_service import get_card, list_cards
from .services.reading_service import create_reading, generate_insight, get_reading, list_readings
from .throttling import UserReadingThrottle

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
    @throttle(UserReadingThrottle)
    async def create_tarot_reading(
        self, request, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None
    ):
        return await create_reading(request.user, question, mentor_id, reading_type)

    @http_get("/readings/my", response=list[ReadingSchemaShort])
    async def list_tarot_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        return await list_readings(request.user, filters)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    async def get_tarot_reading(self, request, reading_id: int):
        return await get_reading(request.user, reading_id)

    @http_post("/readings/{reading_id}/insight", response=ReadingSchema | str)
    @throttle(UserReadingThrottle)
    async def generate_tarot_insight(self, request, reading_id: int):
        return await generate_insight(request.user, reading_id)


@api_controller("/tg/tarot", tags=["Telegram Tarot"], auth=AsyncJWTAuth(), permissions=[IsAuthenticated])
class AsyncTarotTGController:
    """Handles Tarot-related actions for authenticated Telegram users."""

    # TAROT CARDS (Public Access)
    @http_get("/cards", response=list[CardSchemaShort], permissions=[AllowAny])
    async def list_tarot_cards(self, filters: CardFilterSchema = Query(...)):
        """Retrieve the list of tarot cards (public access)."""
        return await list_cards(filters)

    @http_get("/cards/{card_slug}", response=CardSchema, permissions=[AllowAny])
    async def get_tarot_card(self, card_slug: str):
        """Retrieve a single tarot card by slug (public access)."""
        return await get_card(card_slug)

    # TAROT READINGS (Authenticated)
    @http_post("/readings", response=ReadingSchema | str)
    @throttle(UserReadingThrottle)
    async def create_tarot_reading(
        self, request, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None
    ):
        """Create a tarot reading for an authenticated user."""
        user = await aget_object_or_404(User, username=request.user.username)
        return await create_reading(user, question, mentor_id, reading_type)

    @http_get("/readings/my", response=list[ReadingSchemaShort])
    async def list_tarot_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        """Retrieve the user's tarot reading history."""
        user = await aget_object_or_404(User, username=request.user.username)
        return await list_readings(user, filters)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    async def get_tarot_reading(self, request, reading_id: int):
        """Retrieve a specific tarot reading for the authenticated user."""
        user = await aget_object_or_404(User, username=request.user.username)
        return await get_reading(user, reading_id)

    @http_post("/readings/{reading_id}/insight", response=ReadingSchema | str)
    @throttle(UserReadingThrottle)
    async def generate_tarot_insight(self, request, reading_id: int):
        """Generate celestial insight for a specific tarot reading."""
        user = await aget_object_or_404(User, username=request.user.username)
        return await generate_insight(user, reading_id)
