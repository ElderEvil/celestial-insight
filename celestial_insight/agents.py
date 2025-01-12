from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from tarot.enums import ReadingTypeEnum

# Define card orientation as a Literal type
Orientation = Literal["upright", "reversed"]


@dataclass
class ReadingDependencies:
    question: str


# Result for validating questions and determining spread type
class QuestionValidationResult(BaseModel):
    is_valid: bool = Field(description="Indicates whether the question is valid for a tarot reading.")
    reason: str | None = Field(description="The reason for the negative validation result.")
    theme: str = Field(description="The theme of the question (e.g., love, career).")
    spread_type: ReadingTypeEnum | None = Field(description="The determined or suggested spread type for the reading.")


# Card details in the celestial insight response
class CardResponse(BaseModel):
    name: str = Field(description="The name of the card (e.g., The Fool, The Magician).")
    orientation: Orientation = Field(description="The orientation of the card (upright or reversed).")
    interpretation: str = Field(description="The interpretation of the card in the given context.")


# Full response structure for celestial insights
class CelestialInsightResponse(BaseModel):
    text: str = Field(description="The mystical guidance text.")
    cards: list[CardResponse] = Field(description="List of cards with names, orientations, and interpretations.")


# Agent for validating questions and determining spread type
tarot_support_agent = Agent(
    "openai:gpt-3.5-turbo",
    deps_type=ReadingDependencies,
    result_type=QuestionValidationResult,
    system_prompt=(
        "You are a wise and mystical guide providing spiritual insights. "
        "Your role is to validate questions for tarot readings and determine "
        "the appropriate spread type based on the question's theme. "
        "Select spreads from the provided list: single_card, three_card_spread, celtic_cross_spread, "
        "love_spread, career_path_spread, relationship_spread, horseshoe_spread. "
        "Ensure your theme and spread suggestions align with the question and are appropriate for the seeker. "
        "Additionally, return a boolean field 'is_valid' to indicate if the question is appropriate for a tarot reading."  # noqa: E501
        "If the question is not valid, return a reason for the negative validation result."
    ),
)


# Agent for providing mystical responses
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
