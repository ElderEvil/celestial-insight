import pytest

from tarot.enums import ReadingTypeEnum
from tarot.spreads import SPREADS, get_spread


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
