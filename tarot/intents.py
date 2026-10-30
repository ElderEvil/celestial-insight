"""Tarot intent, theme, and tone option enums.

These mirror the archived prototype's ``celestial-neutral/src/data/enums.py``
definitions, but use lowercase snake_case values instead of display strings.
They are inert content only: nothing here is wired into a prompt, view, form,
or agent yet.
"""

from enum import StrEnum


class ValidIntentOptions(StrEnum):
    PREDICTION = "prediction"
    SELF_REFLECTION = "self_reflection"
    GUIDANCE = "guidance"
    WARNING = "warning"


class InvalidIntentOptions(StrEnum):
    HELP_REQUEST = "help_request"
    REACTION_CHECK = "reaction_check"
    AMBIGUITY = "ambiguity"


class ThemeOptions(StrEnum):
    LOVE = "love"
    CAREER = "career"
    FINANCE = "finance"
    HEALTH = "health"
    SPIRITUALITY = "spirituality"
    SELF_GROWTH = "self_growth"
    GENERAL_GUIDANCE = "general_guidance"
    DECISION_MAKING = "decision_making"
    PAST_LIFE = "past_life"
    ESOTERIC = "esoteric"
    DREAMS = "dreams"
    WARNING = "warning"
    COMMUNICATION = "communication"
    HIDDEN_TRUTHS = "hidden_truths"


class ToneOptions(StrEnum):
    CASUAL = "casual"
    SERIOUS = "serious"
    PLAYFUL = "playful"
    ANXIOUS = "anxious"
    SARCASTIC = "sarcastic"
