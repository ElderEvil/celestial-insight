import random
import re

from .enums import ReadingTypeEnum


class QuestionValidator:
    """Validates if questions are appropriate for mystical readings"""

    @classmethod
    def validate_question(cls, *, question: str) -> bool:
        """
        Validates the question based on multiple patterns to determine if it's
        suitable for a tarot reading.
        """
        question = question.lower()

        # Check for personal patterns
        personal_patterns = r"should i|will i|am i|my future|my path|my destiny|my life"
        if re.search(personal_patterns, question):
            return True

        # Check for decision-making intent
        decision_patterns = r"should i do|what choice|which path|which option|what should i decide"
        if re.search(decision_patterns, question):
            return True

        # Check for seeking guidance
        guidance_patterns = r"what does|how can|what can|why is|what is my purpose|how to"
        if re.search(guidance_patterns, question):
            return True

        # Check for emotional or existential questions
        emotional_patterns = r"why do i feel|why am i|why can't i|why does this keep happening"
        if re.search(emotional_patterns, question):
            return True

        # Check for open-ended spiritual inquiries
        spiritual_patterns = r"what does the universe|what do the cards|what is the energy|what is happening"
        return bool(re.search(spiritual_patterns, question))


def determine_spread_type(question: str) -> str:
    """
    Determines or randomizes the spread type based on the content of the question.
    """
    question_lower = question.lower()

    match question_lower:
        case q if "love" in q or "relationship" in q:
            return ReadingTypeEnum.LOVE_SPREAD.value
        case q if "career" in q or "job" in q:
            return ReadingTypeEnum.CAREER_PATH_SPREAD.value
        case q if "future" in q or "guidance" in q:
            return random.choice(  # noqa: S311 (use of random for non-secure purpose)
                [
                    ReadingTypeEnum.THREE_CARD_SPREAD.value,
                    ReadingTypeEnum.HORSESHOE_SPREAD.value,
                ]
            )
        case q if "money" in q or "finance" in q:
            return ReadingTypeEnum.CAREER_PATH_SPREAD.value
        case _:
            return ReadingTypeEnum.SINGLE_CARD.value
