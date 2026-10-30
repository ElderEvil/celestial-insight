import re

import pytest

from tarot.intents import ToneOptions, ValidIntentOptions
from tarot.tones import TONE_MODIFIERS, TONE_PROMPTS, ToneModifier

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")
EXPECTED_PAIR_COUNT = len(ValidIntentOptions) * len(ToneOptions)
EXPECTED_TONE_COUNT = 20
MIN_PROMPT_LENGTH = 40


def test_tone_modifier_member_count():
    assert len(ToneModifier) == EXPECTED_TONE_COUNT


def test_tone_modifier_values_are_lowercase_snake_case():
    for member in ToneModifier:
        assert SNAKE_CASE.fullmatch(member.value), f"{member.name} has invalid value {member.value!r}"


def test_tone_modifier_values_are_unique():
    values = [member.value for member in ToneModifier]
    assert len(values) == len(set(values))


def test_tone_modifiers_cover_every_intent_tone_pair():
    expected = {(intent, tone) for intent in ValidIntentOptions for tone in ToneOptions}
    assert set(TONE_MODIFIERS) == expected
    assert len(TONE_MODIFIERS) == EXPECTED_PAIR_COUNT == EXPECTED_TONE_COUNT


def test_tone_modifiers_values_are_all_tone_modifiers():
    assert set(TONE_MODIFIERS.values()) == set(ToneModifier)


def test_tone_prompts_cover_every_tone_modifier():
    assert set(TONE_PROMPTS) == set(ToneModifier)
    assert len(TONE_PROMPTS) == EXPECTED_TONE_COUNT


@pytest.mark.parametrize("modifier", list(ToneModifier), ids=[m.name for m in ToneModifier])
def test_tone_prompt_is_a_substantive_string(modifier):
    prompt = TONE_PROMPTS[modifier]
    assert isinstance(prompt, str)
    assert prompt
    assert len(prompt) >= MIN_PROMPT_LENGTH, f"{modifier.name} prompt is too short: {prompt!r}"


@pytest.mark.parametrize(
    ("intent", "tone"),
    sorted(TONE_MODIFIERS),
    ids=[f"{intent.value}_{tone.value}" for intent, tone in sorted(TONE_MODIFIERS)],
)
def test_tone_modifier_value_starts_with_tone(intent, tone):
    modifier = TONE_MODIFIERS[(intent, tone)]
    assert modifier.value.startswith(f"{tone.value}_"), f"{intent.value}/{tone.value} mapped to {modifier.value!r}"


@pytest.mark.parametrize(
    ("intent", "tone"),
    sorted(TONE_MODIFIERS),
    ids=[f"{intent.value}_{tone.value}" for intent, tone in sorted(TONE_MODIFIERS)],
)
def test_tone_modifier_value_ends_with_intent(intent, tone):
    modifier = TONE_MODIFIERS[(intent, tone)]
    assert modifier.value.endswith(f"_{intent.value}"), f"{intent.value}/{tone.value} mapped to {modifier.value!r}"
