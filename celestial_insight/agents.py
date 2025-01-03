from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from tarot.validators import QuestionValidator


@dataclass
class ReadingDependencies:
    question: str
    validator: QuestionValidator


class ReadingResult(BaseModel):
    mystical_response: str = Field(description="The mystical guidance for the seeker")
    theme: str = Field(description="The theme of the question")
    intensity: int = Field(description="The intensity/importance of the question", ge=1, le=10)


mystical_agent = Agent(
    "openai:gpt-3.5-turbo",
    deps_type=ReadingDependencies,
    result_type=ReadingResult,
    system_prompt=(
        "You are a wise and mystical guide providing spiritual insights. "
        "Offer guidance that is both profound and practical. "
    ),
)
