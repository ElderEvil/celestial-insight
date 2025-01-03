from django.db.models.query_utils import logger
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.pagination import paginate
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle
from pydantic_ai import RunContext

from celestial_insight.agents import ReadingDependencies, mystical_agent

from .filters import CardFilterSchema, ReadingFilterSchema
from .models import Card, Reading, ReadingCard, Suit
from .schemas import CardSchema, CelestialInsightResponseSchema, ReadingCardSchema, ReadingSchema, SuitSchema
from .validators import QuestionValidator

api = NinjaExtraAPI()


@mystical_agent.system_prompt
async def add_question_theme(ctx: RunContext[ReadingDependencies]) -> str:
    theme = await ctx.deps.validator.get_question_theme(question=ctx.deps.question)
    return f"The seeker asks about {theme}."


@mystical_agent.tool
async def validate_question(ctx: RunContext[ReadingDependencies]) -> str:
    """Validates if the question is appropriate for mystical guidance."""
    is_valid = await ctx.deps.validator.validate_question(question=ctx.deps.question)
    if not is_valid:
        msg = "Please ask a personal question about your path or future"
        raise ValueError(msg)
    return "Question is valid for mystical guidance."


@api_controller(
    "/tarot",
    tags=["Tarot"],
    permissions=[permissions.IsAuthenticatedOrReadOnly],
    throttle=DynamicRateThrottle(scope="burst"),
)
class TarotController:
    # SUITS
    @http_get("/suits", response=list[SuitSchema])
    def list_suits(self):
        """List all suits."""
        return Suit.objects.all()

    # CARDS
    @http_get("/cards", response=list[CardSchema])
    @paginate()
    def list_cards(self, filters: CardFilterSchema = Query(...)):
        """List all cards."""
        cards = Card.objects.select_related("suit").all()
        return filters.filter(cards)

    @http_get("/cards/{card_id}", response=CardSchema)
    def get_card(self, card_id: int):
        """Get details of a specific card."""
        return get_object_or_404(Card, id=card_id)

    # READINGS
    @http_post("/readings", response=ReadingSchema)
    def create_reading(self, request, question: str | None = None, notes: str | None = None):
        """Create a new reading for the authenticated user."""
        return Reading.objects.create(
            user=request.user,
            question=question,
            notes=notes,
        )

    @http_get("/readings", response=list[ReadingSchema])
    def list_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        """List all readings for the authenticated user."""
        readings = Reading.objects.filter(user=request.user)
        return filters.filter(readings)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    def get_reading(self, request, reading_id: int):
        """Get details of a specific reading."""
        return get_object_or_404(Reading.objects.prefetch_related("cards__card"), id=reading_id, user=request.user)

    @http_post("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def add_cards_to_reading(self, request, reading_id: int, cards: list[ReadingCardSchema]):
        """
        Add cards to a specific reading.
        - `cards` is a list of card details with position, orientation, and interpretation.
        """
        reading = get_object_or_404(Reading, id=reading_id, user=request.user)
        reading_cards = []
        for card_data in cards:
            card = get_object_or_404(Card, id=card_data.card.id)
            reading_card = ReadingCard.objects.create(
                reading=reading,
                card=card,
                position=card_data.position,
                orientation=card_data.orientation,
                interpretation=card_data.interpretation or "",
            )
            reading_cards.append(reading_card)
        return reading_cards

    @http_get("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def list_cards_in_reading(self, request, reading_id: int):
        """List all cards in a specific reading."""
        reading = get_object_or_404(Reading.objects.prefetch_related("cards__card"), id=reading_id, user=request.user)
        return reading.cards.all()

    # CELESTIAL (aka AI)
    @http_get("/readings/{reading_id}/celestial", response=CelestialInsightResponseSchema)
    def get_celestial_reading(self, request, reading_id: int):
        """
        Generate a celestial insight for a specific reading using AI.
        """
        reading = get_object_or_404(Reading.objects.prefetch_related("cards__card"), id=reading_id, user=request.user)

        insight_stub = "Unable to generate celestial insight at this time."
        if reading.celestial_insight and reading.celestial_insight == insight_stub:
            return reading

        # Prepare cards data for the AI
        cards_data = [
            (
                f"Card: {card.card.name}, "
                f"Position: {card.position}, "
                f"Orientation: {card.orientation}, "
                f"Interpretation: {card.interpretation or 'None'}"
            )
            for card in reading.cards.all()
        ]
        cards_summary = "; ".join(cards_data)
        prompt = f"Summarize and provide mystical guidance for this tarot reading: {cards_summary}"

        # Generate celestial insight using the mystical agent
        try:
            deps = ReadingDependencies(
                question=reading.question or "No specific question", validator=QuestionValidator()
            )
            result = mystical_agent.run_sync(prompt, deps=deps)
            celestial_insight = result.data.mystical_response
        except Exception as e:
            logger.error(f"Error generating celestial insight: {e}")
            celestial_insight = insight_stub

        reading.celestial_insight = celestial_insight
        reading.save()
        # Return the celestial insight with reading details
        return reading

    @http_post("/celestial", response=str)
    def celestial(self, question: str) -> str:
        """
        Provide an AI-generated answer to a user question.
        """
        try:
            deps = ReadingDependencies(question=question, validator=QuestionValidator())
            result = mystical_agent.run_sync("Provide guidance for: " + question, deps=deps)
            return result.data.mystical_response

        except ValueError as e:
            logger.error(msg=f"Error: {e}")
            return str(e)
