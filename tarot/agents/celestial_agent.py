from pydantic import BaseModel, Field
from pydantic.functional_validators import model_validator
from pydantic_ai import Agent

from .common import ReadingDependencies


class PositionInterpretation(BaseModel):
    reading_card_id: int = Field(description="The database ID supplied for this persisted reading card.")
    position: int = Field(ge=1, description="The persisted numeric position supplied in the request.")
    interpretation: str = Field(description="The interpretation of the card in the given context.")


# Full response structure for celestial insights
class CelestialInsightResponse(BaseModel):
    text: str = Field(description="A concise overall reflection about the persisted draw.")
    positions: list[PositionInterpretation] = Field(description="One interpretation for each supplied position.")
    follow_up_prompt: str | None = Field(default=None, description="An optional question for further reflection.")

    @model_validator(mode="after")
    def positions_must_be_unique(self):
        position_numbers = [item.position for item in self.positions]
        reading_card_ids = [item.reading_card_id for item in self.positions]
        if len(position_numbers) != len(set(position_numbers)) or len(reading_card_ids) != len(set(reading_card_ids)):
            message = "Interpretation positions and reading-card IDs must be unique."
            raise ValueError(message)
        return self


celestial_agent = Agent(
    "openai:gpt-4o",
    deps_type=ReadingDependencies,
    result_type=CelestialInsightResponse,
    system_prompt=(
        "You provide concise tarot reflections for a draw already selected by the application. "
        "Return exactly one interpretation for every supplied reading-card ID and position. "
        "Never add, remove, rename, reorder, or replace a card, role, orientation, ID, or position. "
        "Frame all output as reflective guidance and never claim certainty about future events, health, legal matters, "
        "financial outcomes, or another person's hidden thoughts or intentions."
    ),
)
