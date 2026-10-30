import pytest

from tarot.intents import ThemeOptions, ValidIntentOptions
from tarot.spread_matrix import DEFAULT_SPREADS, TAROT_SPREADS, suggest_spreads
from tarot.spread_purpose import SPREAD_PURPOSE
from tarot.spreads import SPREADS


def test_spread_purpose_covers_every_spread():
    assert set(SPREAD_PURPOSE) == set(SPREADS)


def test_spread_purpose_values_are_non_empty_strings():
    for reading_type, purpose in SPREAD_PURPOSE.items():
        assert isinstance(purpose, str), reading_type
        assert purpose.strip(), reading_type


@pytest.mark.parametrize(("intent", "theme"), TAROT_SPREADS)
def test_matrix_keys_use_real_enum_members(intent, theme):
    assert isinstance(intent, ValidIntentOptions)
    assert isinstance(theme, ThemeOptions)


@pytest.mark.parametrize(("key", "reading_types"), TAROT_SPREADS.items())
def test_matrix_spreads_exist_and_are_active(key, reading_types):
    for reading_type in reading_types:
        assert reading_type in SPREADS, (key, reading_type)
        spread = SPREADS[reading_type]
        assert spread.is_active is True, (key, reading_type)


@pytest.mark.parametrize(("key", "reading_types"), TAROT_SPREADS.items())
def test_matrix_tuples_have_no_duplicates(key, reading_types):
    assert len(reading_types) == len(set(reading_types)), key


def test_suggest_spreads_returns_non_empty_for_prediction_love():
    spreads = suggest_spreads(ValidIntentOptions.PREDICTION, ThemeOptions.LOVE)

    assert isinstance(spreads, tuple)
    assert spreads


def test_suggest_spreads_falls_back_to_default_for_unlisted_pair():
    unlisted_pair = (ValidIntentOptions.PREDICTION, ThemeOptions.PAST_LIFE)

    assert unlisted_pair not in TAROT_SPREADS
    assert suggest_spreads(*unlisted_pair) == DEFAULT_SPREADS
