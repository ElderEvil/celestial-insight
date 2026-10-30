"""Intent x theme -> spread suggestions.

Ported from the archived prototype's ``tarot_spreads.py`` matrix. Prototype
``SpreadType`` members are mapped onto target :class:`ReadingTypeEnum` values.
Prototype ``ValidIntentOptions.REFLECTION`` maps onto the target
``ValidIntentOptions.SELF_REFLECTION``.

Only active (launch) spreads may appear in a suggested tuple: inactive spreads
are dropped rather than activated. A tuple that would become empty falls back to
:data:`DEFAULT_SPREADS`. This module is inert content: nothing here is wired
into a prompt, view, form, or agent yet.
"""

from .enums import ReadingTypeEnum
from .intents import ThemeOptions, ValidIntentOptions

DEFAULT_SPREADS: tuple[ReadingTypeEnum, ...] = (
    ReadingTypeEnum.SINGLE_CARD,
    ReadingTypeEnum.THREE_CARD_SPREAD,
    ReadingTypeEnum.CELTIC_CROSS_SPREAD,
)

TAROT_SPREADS: dict[tuple[ValidIntentOptions, ThemeOptions], tuple[ReadingTypeEnum, ...]] = {
    (ValidIntentOptions.PREDICTION, ThemeOptions.GENERAL_GUIDANCE): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.SELF_GROWTH): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.CAREER): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.FINANCE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.LOVE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.LOVE_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.HEALTH): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.SPIRITUALITY): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.DECISION_MAKING): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.LOVE_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.COMMUNICATION): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
        ReadingTypeEnum.SINGLE_CARD,
    ),
    (ValidIntentOptions.PREDICTION, ThemeOptions.HIDDEN_TRUTHS): (
        ReadingTypeEnum.LOVE_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.GENERAL_GUIDANCE): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.SELF_GROWTH): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.CAREER): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.FINANCE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.LOVE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.LOVE_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.HEALTH): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.SPIRITUALITY): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.DECISION_MAKING): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.COMMUNICATION): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.PAST_LIFE): DEFAULT_SPREADS,
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.ESOTERIC): DEFAULT_SPREADS,
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.DREAMS): DEFAULT_SPREADS,
    (ValidIntentOptions.SELF_REFLECTION, ThemeOptions.HIDDEN_TRUTHS): (
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.GENERAL_GUIDANCE): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.SELF_GROWTH): (
        ReadingTypeEnum.SINGLE_CARD,
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.CAREER): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.FINANCE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CAREER_PATH_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.LOVE): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.LOVE_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.HEALTH): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
        ReadingTypeEnum.SINGLE_CARD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.SPIRITUALITY): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.DECISION_MAKING): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.COMMUNICATION): (
        ReadingTypeEnum.THREE_CARD_SPREAD,
    ),
    (ValidIntentOptions.GUIDANCE, ThemeOptions.PAST_LIFE): DEFAULT_SPREADS,
    (ValidIntentOptions.GUIDANCE, ThemeOptions.ESOTERIC): DEFAULT_SPREADS,
    (ValidIntentOptions.GUIDANCE, ThemeOptions.DREAMS): DEFAULT_SPREADS,
    (ValidIntentOptions.GUIDANCE, ThemeOptions.HIDDEN_TRUTHS): (
        ReadingTypeEnum.LOVE_SPREAD,
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.WARNING, ThemeOptions.GENERAL_GUIDANCE): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.HIDDEN_TRUTHS): (
        ReadingTypeEnum.CELTIC_CROSS_SPREAD,
    ),
    (ValidIntentOptions.WARNING, ThemeOptions.ESOTERIC): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.WARNING): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.LOVE): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.CAREER): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.FINANCE): DEFAULT_SPREADS,
    (ValidIntentOptions.WARNING, ThemeOptions.SPIRITUALITY): DEFAULT_SPREADS,
}


def suggest_spreads(
    intent: ValidIntentOptions,
    theme: ThemeOptions,
) -> tuple[ReadingTypeEnum, ...]:
    """Return the suggested active spreads for an intent and theme pair."""
    return TAROT_SPREADS.get((intent, theme), DEFAULT_SPREADS)
