import random
import re
from dataclasses import dataclass

from .enums import ReadingTypeEnum

MIN_QUESTION_LENGTH = 5
MAX_QUESTION_LENGTH = 500

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous\s+)?instructions",
    r"ignore\s+above",
    r"disregard\s+(all\s+)?(previous\s+)?instructions",
    r"system\s*prompt",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+if\s+you\s+are",
    r"pretend\s+(you\s+are|to\s+be)",
    r"roleplay\s+as",
    r"jailbreak",
    r"dan\s+mode",
    r"developer\s+mode",
    r"bypass\s+(safety|filter|restriction)",
    r"override\s+(system|instruction|rule)",
    r"forget\s+(everything|your\s+instructions|what\s+i\s+said)",
    r"new\s+instructions?\s*:",
    r"from\s+now\s+on\s+you\s+(will|must|are)",
    r"\[system\]",
    r"\[admin\]",
    r"<\s*system\s*>",
    r"</?\s*instruction",
    r"reveal\s+(your\s+)?(system\s+)?prompt",
    r"what\s+(is|are)\s+your\s+instructions",
    r"show\s+(me\s+)?your\s+(system\s+)?prompt",
    r"print\s+(your\s+)?(system\s+)?prompt",
]


@dataclass
class ValidationResult:
    """Result of question validation."""

    is_valid: bool
    error_message: str | None = None


class QuestionValidator:
    """Validates if questions are appropriate for mystical readings."""

    _injection_regex: re.Pattern | None = None

    @classmethod
    def _get_injection_regex(cls) -> re.Pattern:
        if cls._injection_regex is None:
            combined_pattern = "|".join(f"({p})" for p in INJECTION_PATTERNS)
            cls._injection_regex = re.compile(combined_pattern, re.IGNORECASE)
        return cls._injection_regex

    @classmethod
    def validate_length(cls, question: str) -> ValidationResult:
        normalized = " ".join(question.split())

        if len(normalized) < MIN_QUESTION_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Question too short. Minimum {MIN_QUESTION_LENGTH} characters required.",
            )

        if len(normalized) > MAX_QUESTION_LENGTH:
            return ValidationResult(
                is_valid=False,
                error_message=f"Question too long. Maximum {MAX_QUESTION_LENGTH} characters allowed.",
            )

        return ValidationResult(is_valid=True)

    @classmethod
    def detect_injection(cls, question: str) -> ValidationResult:
        regex = cls._get_injection_regex()
        if regex.search(question):
            return ValidationResult(
                is_valid=False,
                error_message=(
                    "Your question contains patterns that cannot be processed. Please rephrase your question."
                ),
            )
        return ValidationResult(is_valid=True)

    @classmethod
    def validate_input(cls, question: str) -> ValidationResult:
        """Validates length constraints and detects injection patterns."""
        if not question or not question.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Question cannot be empty.",
            )

        length_result = cls.validate_length(question)
        if not length_result.is_valid:
            return length_result

        injection_result = cls.detect_injection(question)
        if not injection_result.is_valid:
            return injection_result

        return ValidationResult(is_valid=True)

    @classmethod
    def validate_question(cls, *, question: str) -> bool:
        """
        Validates the question based on multiple patterns to determine if it's
        suitable for a tarot reading.

        Note: This method checks thematic appropriateness, not security.
        Use validate_input() for security validation first.
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
