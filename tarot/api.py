from django.shortcuts import get_object_or_404
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle

from .models import Suit, Card, Reading, ReadingCard
from .schemas import SuitSchema, CardSchema, ReadingSchema, ReadingCardSchema

api = NinjaExtraAPI()


@api_controller(
    "/tarot",
    tags=["Tarot"],
    permissions=[permissions.IsAuthenticatedOrReadOnly],
    throttle=DynamicRateThrottle(scope='burst')
)
class TarotController:
    # GET all suits
    @http_get("/suits", response=list[SuitSchema])
    def list_suits(self):
        suits = Suit.objects.all()
        return suits

    # GET all cards
    @http_get("/cards", response=list[CardSchema])
    def list_cards(self):
        cards = Card.objects.select_related('suit').all()
        return cards

    # GET a specific card by ID
    @http_get("/cards/{card_id}", response=CardSchema)
    def get_card(self, card_id: int):
        card = get_object_or_404(Card, id=card_id)
        return card

    # POST create a reading
    @http_post("/readings", response=ReadingSchema)
    def create_reading(self, request, question: str | None = None, notes: str | None = None):
        reading = Reading.objects.create(
            user=request.user,
            question=question,
            notes=notes
        )
        return reading

    # POST add cards to a reading
    @http_post("/readings/{reading_id}/cards", response=list[ReadingCardSchema])
    def add_cards_to_reading(self, reading_id: int, cards: list[ReadingCardSchema]):
        reading = get_object_or_404(Reading, id=reading_id)
        reading_cards = []
        for card_data in cards:
            card = get_object_or_404(Card, id=card_data.card.id)
            reading_card = ReadingCard.objects.create(
                reading=reading,
                card=card,
                position=card_data.position,
                orientation=card_data.orientation,
                interpretation=card_data.interpretation or ""
            )
            reading_cards.append(reading_card)
        return reading_cards

    # GET a specific reading with its cards
    @http_get("/readings/{reading_id}", response=ReadingSchema)
    def get_reading(self, reading_id: int):
        reading = get_object_or_404(Reading.objects.prefetch_related('cards__card'), id=reading_id)
        return reading

    @http_get("/readings/{reading_id}/celestial", response=ReadingSchema)
    def get_celestial_reading(self, reading_id: int):
        reading = get_object_or_404(Reading.objects.prefetch_related('cards__card'), id=reading_id)
        #
        # # Generate a full reading summary using OpenAI
        # cards_data = [
        #     f"Card: {card.card.name}, Position: {card.position}, Orientation: {card.orientation}, Interpretation: {card.interpretation}"
        #     for card in reading.cards.all()
        # ]
        # prompt = f"Summarize the following tarot reading: {'; '.join(cards_data)}"
        # response = openai.Completion.create(
        #     engine="text-davinci-003",
        #     prompt=prompt,
        #     max_tokens=200
        # )
        # ai_summary = response.choices[0].text.strip()
        #
        # # Return the reading with the summary
        # return {
        #     "id": reading.id,
        #     "date": reading.date,
        #     "question": reading.question,
        #     "notes": reading.notes,
        #     "ai_summary": ai_summary,
        #     "cards": reading.cards.all()
        # }

    @http_get("/celestial", response=str)
    def celestial(self, question: str):
        """
        Provide an AI-generated answer to a user question.
        """
        prompt = f"Provide a mystical and tarot-inspired response to the question: '{question}'."
        # response = openai.Completion.create(
        #     engine="text-davinci-003",
        #     prompt=prompt,
        #     max_tokens=150
        # )
        # return response.choices[0].text.strip()
