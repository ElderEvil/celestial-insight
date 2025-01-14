from pydantic import BaseModel, Field
from pydantic_ai import Agent

from tarot.enums import ReadingTypeEnum

from .common import ReadingDependencies


class QuestionValidationResult(BaseModel):
    is_valid: bool = Field(description="Indicates whether the question is valid for a tarot reading.")
    reason: str | None = Field(description="The reason for the negative validation result.")
    theme: str = Field(description="The theme of the question (e.g., love, career).")
    spread_type: ReadingTypeEnum | None = Field(description="The determined or suggested spread type for the reading.")


tarot_support_agent = Agent(
    "openai:gpt-4-turbo",
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
