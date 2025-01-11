import random

from django.db.models.query_utils import logger
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle
from pydantic_ai import RunContext

from celestial_insight.agents import ReadingDependencies, mystical_agent

from .filters import CardFilterSchema, ReadingFilterSchema
from .models import Card, Reading, ReadingCard
from .schemas import CardSchema, CelestialInsightResponseSchema, ReadingCardSchema, ReadingSchema
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
    # CARDS
    @http_get("/cards", response=list[CardSchema])
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
    def create_reading(
        self,
        request,
        question: str | None = None,
        reading_type: str | None = None,
    ):
        """Create a new reading for the authenticated user."""
        return Reading.objects.create(
            user=request.user,
            question=question,
            notes="Some notes",
            reading_type=reading_type or "single_card",
        )

    @http_get("/readings", response=list[ReadingSchema])
    def list_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        """List all readings for the authenticated user."""
        readings = Reading.objects.filter(user=request.user)
        return filters.filter(readings)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    def get_reading(self, request, reading_id: int):
        """Get details of a specific reading."""
        return get_object_or_404(
            Reading.objects.prefetch_related("cards__card"),
            id=reading_id,
            user=request.user,
        )

    @http_post("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def add_cards_to_reading(
        self,
        request,
        reading_id: int,
    ):
        """
        Add random cards to a specific reading based on the reading type.
        """
        # Define expected card counts for each reading type
        expected_card_counts = {
            "single_card": 1,
            "three_card_spread": 3,
            "celtic_cross_spread": 10,
            "love_spread": 5,
            "career_path_spread": 5,
            "relationship_spread": 7,
            "horseshoe_spread": 7,
        }

        # Fetch the reading and validate the reading type
        reading = get_object_or_404(Reading, id=reading_id, user=request.user)
        reading_type = reading.reading_type
        if reading_type not in expected_card_counts:
            msg = f"Unknown reading type: {reading_type}"
            raise ValueError(msg)

        # Determine the number of cards to add
        cards_number = expected_card_counts[reading_type]

        # Get all cards that are not already in the reading
        existing_card_ids = reading.cards.values_list("card_id", flat=True)
        available_cards = Card.objects.exclude(id__in=existing_card_ids)

        # Ensure there are enough cards to draw from
        if available_cards.count() < cards_number:
            msg = "Not enough cards available to add to the reading."
            raise ValueError(msg)

        # Randomly select the required number of cards
        random_cards = random.sample(list(available_cards), cards_number)

        # Add the selected cards to the reading
        reading_cards = []
        for index, card in enumerate(random_cards, start=len(existing_card_ids) + 1):
            reading_card = ReadingCard.objects.create(
                reading=reading,
                card=card,
                position=index,
                orientation=random.choice(["upright", "reversed"]),  # noqa: S311
                interpretation="",  # Optional: Generate an AI-based interpretation here
            )
            reading_cards.append(reading_card)

        return reading_cards

    @http_get("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def list_cards_in_reading(self, request, reading_id: int):
        """List all cards in a specific reading."""
        reading = get_object_or_404(
            Reading.objects.prefetch_related("cards__card"),
            id=reading_id,
            user=request.user,
        )
        return reading.cards.all()

    # CELESTIAL (aka AI)
    @http_get(
        "/readings/{reading_id}/celestial",
        response=CelestialInsightResponseSchema,
    )
    def get_celestial_reading(self, request, reading_id: int):
        """
        Generate a celestial insight for a specific reading using AI.
        """
        reading = get_object_or_404(
            Reading.objects.prefetch_related("cards__card"),
            id=reading_id,
            user=request.user,
        )

        insight_stub = "Unable to generate celestial insight at this time."
        if reading.celestial_insight and reading.celestial_insight != insight_stub:
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
                question=reading.question or "No specific question",
                validator=QuestionValidator(),
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
            result = mystical_agent.run_sync(
                "Provide guidance for: " + question,
                deps=deps,
            )

        except ValueError as e:
            logger.error(msg=f"Error: {e}")
            return str(e)

        else:
            return result.data.mystical_response
