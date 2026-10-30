import dataclasses

import pytest

import tarot.forms as forms_module
import tarot.spreads as spreads_module
from tarot.enums import ReadingTypeEnum
from tarot.spreads import SPREADS, get_active_spread, get_spread

EXPECTED_SPREAD_COUNT = 10
EXPECTED_ACTIVE_SPREAD_COUNT = 5
READING_TYPE_FIELD_MAX_LENGTH = 32


@pytest.fixture
def inactive_single_card(monkeypatch):
    patched = dict(spreads_module.SPREADS)
    patched[ReadingTypeEnum.SINGLE_CARD] = dataclasses.replace(
        patched[ReadingTypeEnum.SINGLE_CARD], is_active=False
    )
    monkeypatch.setattr(spreads_module, "SPREADS", patched)
    monkeypatch.setattr(forms_module, "SPREADS", patched)
    return patched


@pytest.mark.parametrize(
    ("reading_type", "position_count"),
    [
        (ReadingTypeEnum.SINGLE_CARD, 1),
        (ReadingTypeEnum.THREE_CARD_SPREAD, 3),
        (ReadingTypeEnum.CELTIC_CROSS_SPREAD, 10),
        (ReadingTypeEnum.CAREER_PATH_SPREAD, 5),
        (ReadingTypeEnum.LOVE_SPREAD, 5),
    ],
)
def test_launch_spreads_have_expected_position_count(reading_type, position_count):
    spread = get_spread(reading_type)

    assert len(spread.positions) == position_count
    assert all(position.role and position.description for position in spread.positions)


def test_launch_spreads_have_unique_roles():
    for spread in SPREADS.values():
        roles = [position.role for position in spread.positions]
        assert len(roles) == len(set(roles))


def test_unsupported_spread_is_rejected():
    with pytest.raises(ValueError, match="Unsupported spread"):
        get_spread(ReadingTypeEnum.HORSESHOE_SPREAD)


def test_get_spread_returns_inactive_definition(inactive_single_card):
    spread = get_spread(ReadingTypeEnum.SINGLE_CARD)

    assert spread.is_active is False

    with pytest.raises(ValueError, match="Inactive spread"):
        get_active_spread(ReadingTypeEnum.SINGLE_CARD)


def test_form_excludes_inactive_spreads(inactive_single_card):
    form = forms_module.ReadingJourneyForm()

    assert "single_card" not in dict(form.fields["reading_type"].choices)


def test_catalogue_has_ten_spreads_with_five_active():
    assert len(SPREADS) == EXPECTED_SPREAD_COUNT
    assert sum(1 for spread in SPREADS.values() if spread.is_active) == EXPECTED_ACTIVE_SPREAD_COUNT


def test_every_reading_type_key_fits_reading_type_field():
    for member in ReadingTypeEnum:
        if member in SPREADS:
            assert len(member.value) <= READING_TYPE_FIELD_MAX_LENGTH


def test_every_spread_has_unique_nonempty_roles():
    for spread in SPREADS.values():
        roles = [position.role for position in spread.positions]
        assert len(roles) == len(set(roles))
        assert all(position.role and position.description for position in spread.positions)
