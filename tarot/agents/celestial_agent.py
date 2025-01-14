from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from .common import ReadingDependencies

Orientation = Literal["upright", "reversed"]


class CardResponse(BaseModel):
    name: str = Field(description="The name of the card (e.g., The Fool, The Magician).")
    orientation: Orientation = Field(description="The orientation of the card (upright or reversed).")
    interpretation: str = Field(description="The interpretation of the card in the given context.")


# Full response structure for celestial insights
class CelestialInsightResponse(BaseModel):
    text: str = Field(description="The mystical guidance text.")
    cards: list[CardResponse] = Field(description="List of cards with names, orientations, and interpretations.")


celestial_agent = Agent(
    "openai:gpt-4o",
    deps_type=ReadingDependencies,
    result_type=CelestialInsightResponse,
    system_prompt=(
        "You are a wise and mystical guide providing spiritual insights. "
        "For the given question and spread type, provide mystical guidance that is both profound and practical. "
        "Generate a textual insight and a list of cards (with their orientation and interpretation) "
        "that align with the spread type and the question's theme. "
        "Ensure the response is meaningful and resonates deeply with the seeker's intent."
    ),
)
