import re
from dataclasses import dataclass

from django.db.models.query_utils import logger
from django.shortcuts import get_object_or_404
from ninja_extra import NinjaExtraAPI, api_controller, http_get, http_post, permissions
from ninja_extra.throttling import DynamicRateThrottle
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from .models import Suit, Card, Reading, ReadingCard
from .schemas import SuitSchema, CardSchema, ReadingSchema, ReadingCardSchema

api = NinjaExtraAPI()




class QuestionValidator:
    """Validates if questions are appropriate for mystical readings"""

    @classmethod
    async def validate_question(cls, *, question: str) -> bool:
        personal_patterns = r"should i|will i|am i|my future|my path|my destiny|my life"
        return bool(re.search(personal_patterns, question.lower()))

    @classmethod
    async def get_question_theme(cls, *, question: str) -> str:
        themes = {
            r"love|relationship|partner": "love and relationships",
            r"job|career|work|business": "career and life purpose",
            r"health|wellness|energy": "health and wellness",
            r"money|finance|wealth": "abundance and prosperity"
        }

        for pattern, theme in themes.items():
            if re.search(pattern, question.lower()):
                return theme
        return "personal guidance"


@dataclass
class ReadingDependencies:
    question: str
    validator: QuestionValidator


class ReadingResult(BaseModel):
    mystical_response: str = Field(description='The mystical guidance for the seeker')
    theme: str = Field(description='The theme of the question')
    intensity: int = Field(description='The intensity/importance of the question', ge=1, le=10)

mystical_agent = Agent(
    'openai:gpt-4',
    deps_type=ReadingDependencies,
    result_type=ReadingResult,
    system_prompt=(
        'You are a wise and mystical guide providing spiritual insights. '
        'Offer guidance that is both profound and practical. '
    ),
)

@mystical_agent.system_prompt
async def add_question_theme(ctx: RunContext[ReadingDependencies]) -> str:
    theme = await ctx.deps.validator.get_question_theme(question=ctx.deps.question)
    return f"The seeker asks about {theme}."

@mystical_agent.tool
async def validate_question(ctx: RunContext[ReadingDependencies]) -> str:
    """Validates if the question is appropriate for mystical guidance."""
    is_valid = await ctx.deps.validator.validate_question(question=ctx.deps.question)
    if not is_valid:
        raise ValueError("Please ask a personal question about your path or future")
    return "Question is valid for mystical guidance."

@api_controller(
    "/tarot",
    tags=["Tarot"],
    permissions=[permissions.IsAuthenticatedOrReadOnly],
    throttle=DynamicRateThrottle(scope='burst')
)
class TarotController:
    @http_get("/suits", response=list[SuitSchema])
    def list_suits(self):
        suits = Suit.objects.all()
        return suits

    @http_get("/cards", response=list[CardSchema])
    def list_cards(self):
        cards = Card.objects.select_related('suit').all()
        return cards

    @http_get("/cards/{card_id}", response=CardSchema)
    def get_card(self, card_id: int):
        card = get_object_or_404(Card, id=card_id)
        return card

    @http_post("/readings", response=ReadingSchema)
    def create_reading(self, request, question: str | None = None, notes: str | None = None):
        reading = Reading.objects.create(
            user=request.user,
            question=question,
            notes=notes
        )
        return reading

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

    @http_post("/celestial", response=str)
    def celestial(self, question: str) -> str:
        """
        Provide an AI-generated answer to a user question.
        """
        try:
            deps = ReadingDependencies(
                question=question,
                validator=QuestionValidator()
            )

            result = mystical_agent.run_sync("Provide guidance for: " + question, deps=deps)
            return result.data.mystical_response

        except ValueError as e:
            logger.error(msg=f'Error: {e}')
            return str(e)