import re

import pytest

from tarot.intents import InvalidIntentOptions, ThemeOptions, ToneOptions, ValidIntentOptions

EXPECTED_COUNTS = {
    ValidIntentOptions: 4,
    InvalidIntentOptions: 3,
    ThemeOptions: 14,
    ToneOptions: 5,
}

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


def test_member_counts():
    for enum_cls, expected_count in EXPECTED_COUNTS.items():
        assert len(enum_cls) == expected_count


@pytest.mark.parametrize("enum_cls", EXPECTED_COUNTS)
def test_values_are_lowercase_snake_case(enum_cls):
    for member in enum_cls:
        assert SNAKE_CASE.fullmatch(member.value), f"{member.name} has invalid value {member.value!r}"


@pytest.mark.parametrize("enum_cls", EXPECTED_COUNTS)
def test_values_are_unique(enum_cls):
    values = [member.value for member in enum_cls]
    assert len(values) == len(set(values))
