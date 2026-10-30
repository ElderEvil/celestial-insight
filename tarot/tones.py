"""Tone modifier content ported from the archived ``celestial-neutral`` prototype.

This module was harvested from ``celestial-neutral/src/data/enums.py``
(``ToneModifier`` / ``TONE_PROMPTS``) and
``celestial-neutral/src/data/tone_modifiers.py`` (``TONE_MODIFIERS``), but the
member values were converted to lowercase snake_case so they match the
``ValidIntentOptions`` / ``ToneOptions`` values in :mod:`tarot.intents`.

This is inert content only: nothing here is wired into an agent, prompt, view,
form, or service yet.
"""

from enum import StrEnum

from tarot.intents import ToneOptions, ValidIntentOptions


class ToneModifier(StrEnum):
    CASUAL_PREDICTION = "casual_prediction"
    CASUAL_SELF_REFLECTION = "casual_self_reflection"
    CASUAL_GUIDANCE = "casual_guidance"
    CASUAL_WARNING = "casual_warning"

    SERIOUS_PREDICTION = "serious_prediction"
    SERIOUS_SELF_REFLECTION = "serious_self_reflection"
    SERIOUS_GUIDANCE = "serious_guidance"
    SERIOUS_WARNING = "serious_warning"

    PLAYFUL_PREDICTION = "playful_prediction"
    PLAYFUL_SELF_REFLECTION = "playful_self_reflection"
    PLAYFUL_GUIDANCE = "playful_guidance"
    PLAYFUL_WARNING = "playful_warning"

    ANXIOUS_PREDICTION = "anxious_prediction"
    ANXIOUS_SELF_REFLECTION = "anxious_self_reflection"
    ANXIOUS_GUIDANCE = "anxious_guidance"
    ANXIOUS_WARNING = "anxious_warning"

    SARCASTIC_PREDICTION = "sarcastic_prediction"
    SARCASTIC_SELF_REFLECTION = "sarcastic_self_reflection"
    SARCASTIC_GUIDANCE = "sarcastic_guidance"
    SARCASTIC_WARNING = "sarcastic_warning"


TONE_PROMPTS: dict[ToneModifier, str] = {
    ToneModifier.CASUAL_PREDICTION: (
        "Respond in a friendly and light style. Make a prediction without excessive "
        "formality, as if you were talking to a friend."
    ),
    ToneModifier.CASUAL_SELF_REFLECTION: (
        "Help look inward and think, but present it as a conversation with a good friend."
    ),
    ToneModifier.CASUAL_GUIDANCE: ("Give advice in an informal and positive manner. Be simple and caring in tone."),
    ToneModifier.CASUAL_WARNING: (
        "Warn the person gently without creating tension, be like a good friend who suggests being more careful."
    ),
    ToneModifier.SERIOUS_PREDICTION: (
        "Make a prediction strictly and professionally, without jokes or unnecessary emotions."
    ),
    ToneModifier.SERIOUS_SELF_REFLECTION: ("Help reflect on important aspects, using a businesslike and serious tone."),
    ToneModifier.SERIOUS_GUIDANCE: "Give clear and serious advice, like a consultant or mentor.",
    ToneModifier.SERIOUS_WARNING: "Warn strictly and directly, don't soften your wording.",
    ToneModifier.PLAYFUL_PREDICTION: (
        "Predict with a sense of humor and lightness, add playfulness to your intonation."
    ),
    ToneModifier.PLAYFUL_SELF_REFLECTION: ("Help reflect on yourself easily and naturally, as if it were a game."),
    ToneModifier.PLAYFUL_GUIDANCE: ("Give advice cheerfully, with jokes and optimism, but without mockery."),
    ToneModifier.PLAYFUL_WARNING: ("Warn with humor, without being dramatic, but hint at the need for caution."),
    ToneModifier.ANXIOUS_PREDICTION: ("Respond with slight anxiety, as if you were a bit worried about the person."),
    ToneModifier.ANXIOUS_SELF_REFLECTION: (
        "Suggest reflection while expressing concern about the person's inner state."
    ),
    ToneModifier.ANXIOUS_GUIDANCE: (
        "Give advice with sympathy and concern, like a caring companion worried about the situation."
    ),
    ToneModifier.ANXIOUS_WARNING: "Warn cautiously and with care, expressing sympathy and concern.",
    ToneModifier.SARCASTIC_PREDICTION: ("Give a prediction with irony or sarcasm, but without direct offense."),
    ToneModifier.SARCASTIC_SELF_REFLECTION: ("Help reflect on yourself with a degree of irony and self-irony."),
    ToneModifier.SARCASTIC_GUIDANCE: ("Give advice with light sarcasm, as if gently poking fun at the situation."),
    ToneModifier.SARCASTIC_WARNING: ("Warn with sarcasm, as if hinting at the absurdity of possible consequences."),
}


TONE_MODIFIERS: dict[tuple[ValidIntentOptions, ToneOptions], ToneModifier] = {
    # PREDICTION
    (ValidIntentOptions.PREDICTION, ToneOptions.CASUAL): ToneModifier.CASUAL_PREDICTION,
    (ValidIntentOptions.PREDICTION, ToneOptions.SERIOUS): ToneModifier.SERIOUS_PREDICTION,
    (ValidIntentOptions.PREDICTION, ToneOptions.PLAYFUL): ToneModifier.PLAYFUL_PREDICTION,
    (ValidIntentOptions.PREDICTION, ToneOptions.ANXIOUS): ToneModifier.ANXIOUS_PREDICTION,
    (ValidIntentOptions.PREDICTION, ToneOptions.SARCASTIC): ToneModifier.SARCASTIC_PREDICTION,
    # SELF-REFLECTION
    (ValidIntentOptions.SELF_REFLECTION, ToneOptions.CASUAL): ToneModifier.CASUAL_SELF_REFLECTION,
    (ValidIntentOptions.SELF_REFLECTION, ToneOptions.SERIOUS): ToneModifier.SERIOUS_SELF_REFLECTION,
    (ValidIntentOptions.SELF_REFLECTION, ToneOptions.PLAYFUL): ToneModifier.PLAYFUL_SELF_REFLECTION,
    (ValidIntentOptions.SELF_REFLECTION, ToneOptions.ANXIOUS): ToneModifier.ANXIOUS_SELF_REFLECTION,
    (ValidIntentOptions.SELF_REFLECTION, ToneOptions.SARCASTIC): ToneModifier.SARCASTIC_SELF_REFLECTION,
    # GUIDANCE
    (ValidIntentOptions.GUIDANCE, ToneOptions.CASUAL): ToneModifier.CASUAL_GUIDANCE,
    (ValidIntentOptions.GUIDANCE, ToneOptions.SERIOUS): ToneModifier.SERIOUS_GUIDANCE,
    (ValidIntentOptions.GUIDANCE, ToneOptions.PLAYFUL): ToneModifier.PLAYFUL_GUIDANCE,
    (ValidIntentOptions.GUIDANCE, ToneOptions.ANXIOUS): ToneModifier.ANXIOUS_GUIDANCE,
    (ValidIntentOptions.GUIDANCE, ToneOptions.SARCASTIC): ToneModifier.SARCASTIC_GUIDANCE,
    # WARNING
    (ValidIntentOptions.WARNING, ToneOptions.CASUAL): ToneModifier.CASUAL_WARNING,
    (ValidIntentOptions.WARNING, ToneOptions.SERIOUS): ToneModifier.SERIOUS_WARNING,
    (ValidIntentOptions.WARNING, ToneOptions.PLAYFUL): ToneModifier.PLAYFUL_WARNING,
    (ValidIntentOptions.WARNING, ToneOptions.ANXIOUS): ToneModifier.ANXIOUS_WARNING,
    (ValidIntentOptions.WARNING, ToneOptions.SARCASTIC): ToneModifier.SARCASTIC_WARNING,
}
