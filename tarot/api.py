import logging

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle

from celestial_insight.agents import CardResponse, ReadingDependencies, celestial_agent, tarot_support_agent

from .enums import ReadingTypeEnum
from .filters import CardFilterSchema, ReadingFilterSchema
from .models import Card, Reading, ReadingCard
from .schemas import CardSchema, CelestialInsightResponseSchema, ReadingCardSchema, ReadingSchema, ReadingSchemaShort

api = NinjaExtraAPI()

logger = logging.getLogger(__name__)


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
    def create_reading(self, request, question: str):
        """
        Create a reading by analyzing the user's question.
        - Validate the question using `tarot_support_agent`.
        - Match the question to a spread type.
        - Save the reading to the database.
        """
        # Step 1: Validate question and determine spread
        try:
            deps = ReadingDependencies(question=question)
            validation_result = tarot_support_agent.run_sync(
                "Validate the question and determine the spread type.", deps=deps
            )
            print(f"Validation result: {validation_result.data}")  # noqa: T201

            if not validation_result:
                raise ValueError("Failed to validate question or determine spread type.")  # noqa: EM101, TRY003, TRY301

            # Extract results
            theme = validation_result.data.theme
            spread_type = validation_result.data.spread_type or ReadingTypeEnum.SINGLE_CARD.value

        except Exception as e:
            err_msg = f"Error validating question: {e}"
            logger.exception(err_msg)
            return err_msg

        # Step 2: Create and save reading

        return Reading.objects.create(
            user=request.user,
            question=question,
            notes=f"Theme: {theme}",
            reading_type=spread_type,
        )

    @http_get("/readings/my", response=list[ReadingSchemaShort])
    def list_readings(self, request, filters: ReadingFilterSchema = Query(...)):
        """List all readings for the authenticated user."""
        readings = Reading.objects.filter(user=request.user).order_by("-date")
        return filters.filter(readings)

    @http_get("/readings/{reading_id}", response=ReadingSchema)
    def get_reading(self, request, reading_id: int):
        """Get details of a specific reading."""
        return get_object_or_404(
            Reading.objects.prefetch_related("cards__card"),
            id=reading_id,
            user=request.user,
        )

    @http_get("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def list_cards_in_reading(self, request, reading_id: int):
        """List all cards in a specific reading."""
        reading = get_object_or_404(
            Reading.objects.prefetch_related("cards__card"),
            id=reading_id,
            user=request.user,
        )
        return reading.cards.all()

    @http_post("/readings/{reading_id}/insight", response=CelestialInsightResponseSchema | str)
    def generate_insight(self, request, reading_id: int):
        """
        Generate celestial insight based on a created reading.
        - Use `celestial_agent` to generate the insight text and cards.
        - Validate and map cards to database entries.
        - Update the reading with insight text and associated cards.
        """
        # Step 1: Fetch the reading
        reading = get_object_or_404(Reading, id=reading_id, user=request.user)

        # Step 2: Generate insight
        try:
            prompt = (
                f"Provide mystical guidance for the question: '{reading.question}' "
                f"and create a card spread of type '{reading.reading_type}'."
            )
            deps = ReadingDependencies(question=reading.question)
            insight_result = celestial_agent.run_sync(prompt, deps=deps)

            if not insight_result:
                err_msg = f"Failed to generate celestial insight: {insight_result.error}"
                print(err_msg)  # noqa: T201
                raise ValueError(err_msg)  # noqa: TRY301

            # Validate the response structure
            celestial_response = insight_result.data  # Pydantic model validation
            cards_data = celestial_response.cards  # List of card names
            print(f"Card names: {cards_data}")  # noqa: T201
            insight_text = celestial_response.text
            print(f"Insight text: {insight_text}")  # noqa: T201

        except Exception as e:
            err_msg = f"Error generating celestial insight: {e}"
            logger.exception(err_msg)
            return err_msg

        # Step 3: Map cards to database
        try:
            card_objects: list[tuple[Card, CardResponse]] = []
            for card_data in cards_data:
                card_name = card_data.name

                # Normalize card names to handle "The " prefix
                normalized_card_name = card_name.lower().removeprefix("the ").strip()

                # Use Q object to find the card by exact match or ignoring "The "
                card = Card.objects.filter(Q(name__iexact=card_name) | Q(name__iexact=normalized_card_name)).first()

                if not card:
                    err_msg = f"Card '{card_name}' not found in the database."
                    print(err_msg)  # noqa: T201
                    return err_msg
                card_objects.append((card, card_data))

        except Exception as e:
            err_msg = f"Error mapping cards to database: {e}"
            logger.exception(err_msg)
            return err_msg

        # Step 4: Update reading with insight
        print(f"Insight: {insight_text}")  # noqa: T201
        reading.celestial_insight = insight_text
        reading.save()

        # Step 5: Save associated cards
        ReadingCard.objects.filter(reading=reading).delete()  # Clear existing cards
        for position, (card, card_data) in enumerate(card_objects, start=1):
            ReadingCard.objects.create(
                reading=reading,
                card=card,
                position=position,
                orientation=card_data.orientation,
                interpretation=card_data.interpretation,
            )

        return reading
