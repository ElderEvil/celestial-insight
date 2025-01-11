import random
from logging import getLogger

from django.db.models.query_utils import logger
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle

from celestial_insight.agents import CardResponse, ReadingDependencies, celestial_agent, tarot_support_agent

from .enums import ReadingTypeEnum
from .filters import CardFilterSchema, ReadingFilterSchema
from .models import Card, Reading, ReadingCard
from .schemas import CardSchema, CelestialInsightResponseSchema, ReadingCardSchema, ReadingSchema

api = NinjaExtraAPI()

logger = getLogger(__name__)  # noqa: F811


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
        Phase 1: Create a reading by analyzing the user's question.
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
            logger.info(f"Validation result: {validation_result.data}")  # noqa: G004

            if not validation_result:
                raise ValueError("Failed to validate question or determine spread type.")  # noqa: EM101, TRY003, TRY301

            if not validation_result.data.is_valid:
                return "Invalid question. Please refine your input."

            # Extract results
            theme = validation_result.data.theme
            spread_type = validation_result.data.spread_type or ReadingTypeEnum.SINGLE_CARD.value

        except Exception as e:
            logger.error(f"Error validating question: {e}")  # noqa: G004, TRY400
            raise ValueError("Invalid question. Please refine your input.")  # noqa: B904, EM101, TRY003

        # Step 2: Create and save reading
        reading = Reading.objects.create(
            user=request.user,
            question=question,
            notes=f"Theme: {theme}",
            reading_type=spread_type,
        )

        return reading  # noqa: RET504

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

    @http_post("/readings/{reading_id}/insight", response=CelestialInsightResponseSchema)
    def generate_insight(self, request, reading_id: int):
        """
        Phase 2: Generate celestial insight based on a created reading.
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
                logger.info(f"Failed to generate celestial insight: {insight_result.error}")  # noqa: G004
                raise ValueError("Failed to generate celestial insight.")  # noqa: EM101, TRY003, TRY301

            # Validate the response structure
            celestial_response = insight_result.data  # Pydantic model validation
            cards_data = celestial_response.cards  # List of card names
            logger.info(f"Card names: {cards_data}")  # noqa: G004
            insight_text = celestial_response.text
            logger.info(f"Insight text: {insight_text}")  # noqa: G004

        except Exception as e:
            logger.error(f"Error generating celestial insight: {e}")  # noqa: G004, TRY400
            raise ValueError("Failed to generate celestial insight.")  # noqa: B904, EM101, TRY003

        # Step 3: Map cards to database
        try:
            card_objects: list[tuple[Card, CardResponse]] = []
            for card_data in cards_data:
                card_name = card_data.name.removeprefix("The ")
                card = Card.objects.filter(name__iexact=card_name).first()
                if not card:
                    logger.info(f"Card '{card_name}' not found in the database.")  # noqa: G004
                    # raise ValueError(f"Card '{card_name}' not found in the database.")  # noqa: ERA001
                card_objects.append((card, card_data))

            # Check if the card count matches the spread type
            expected_card_count = {  # noqa: F841
                ReadingTypeEnum.SINGLE_CARD.value: 1,
                ReadingTypeEnum.THREE_CARD_SPREAD.value: 3,
                ReadingTypeEnum.CELTIC_CROSS_SPREAD.value: 10,
                ReadingTypeEnum.LOVE_SPREAD.value: 5,
                ReadingTypeEnum.CAREER_PATH_SPREAD.value: 5,
                ReadingTypeEnum.RELATIONSHIP_SPREAD.value: 7,
                ReadingTypeEnum.HORSESHOE_SPREAD.value: 7,
            }.get(reading.reading_type, 1)

            # if len(card_objects) != expected_card_count:
            #     raise ValueError("Mismatch between card count and spread type.")  # noqa: ERA001

        except Exception as e:
            logger.error(f"Error mapping cards to database: {e}")  # noqa: G004, TRY400
            raise ValueError("Failed to map cards to the database.")  # noqa: B904, EM101, TRY003

        # Step 4: Update reading with insight
        reading.celestial_insight = insight_text
        reading.save()

        # Step 5: Save associated cards
        ReadingCard.objects.filter(reading=reading).delete()  # Clear existing cards
        for position, (card, card_data) in enumerate(card_objects, start=1):
            ReadingCard.objects.create(
                reading=reading,
                card=card,
                position=position,
                orientation=card_data.orientation,  # This can be included in the agent's response
                interpretation=card_data.interpretation,  # Optionally generate interpretations
            )

        return reading
