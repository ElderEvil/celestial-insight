from dataclasses import dataclass

from .enums import ReadingTypeEnum

SPREAD_CONTENT_VERSION = 1


@dataclass(frozen=True)
class SpreadPosition:
    role: str
    description: str


@dataclass(frozen=True)
class SpreadDefinition:
    key: ReadingTypeEnum
    name: str
    positions: tuple[SpreadPosition, ...]
    version: int = SPREAD_CONTENT_VERSION


SPREADS = {
    ReadingTypeEnum.SINGLE_CARD: SpreadDefinition(
        key=ReadingTypeEnum.SINGLE_CARD,
        name="Single Card",
        positions=(SpreadPosition("Focus", "The central theme to reflect on now."),),
    ),
    ReadingTypeEnum.THREE_CARD_SPREAD: SpreadDefinition(
        key=ReadingTypeEnum.THREE_CARD_SPREAD,
        name="Past, Present, and Future",
        positions=(
            SpreadPosition("Past", "An influence or pattern carried from the past."),
            SpreadPosition("Present", "The energy or choice active in the present."),
            SpreadPosition("Future", "A possible direction to reflect on."),
        ),
    ),
    ReadingTypeEnum.CELTIC_CROSS_SPREAD: SpreadDefinition(
        key=ReadingTypeEnum.CELTIC_CROSS_SPREAD,
        name="Celtic Cross",
        positions=(
            SpreadPosition("Present", "The heart of the situation."),
            SpreadPosition("Challenge", "The immediate tension or obstacle."),
            SpreadPosition("Foundation", "The deeper basis of the situation."),
            SpreadPosition("Past", "A receding influence."),
            SpreadPosition("Possibility", "A consciously held possibility or aim."),
            SpreadPosition("Near Future", "The next influence likely to emerge."),
            SpreadPosition("Self", "The seeker's stance or inner resources."),
            SpreadPosition("Environment", "External influences and relationships."),
            SpreadPosition("Hopes and Fears", "Expectations that shape perception."),
            SpreadPosition("Outcome", "A direction to consider, not a fixed prediction."),
        ),
    ),
    ReadingTypeEnum.CAREER_PATH_SPREAD: SpreadDefinition(
        key=ReadingTypeEnum.CAREER_PATH_SPREAD,
        name="Career Growth",
        positions=(
            SpreadPosition("Current Path", "The present career landscape."),
            SpreadPosition("Strength", "A quality or resource to draw upon."),
            SpreadPosition("Challenge", "A constraint or lesson to examine."),
            SpreadPosition("Next Step", "A practical direction for reflection."),
            SpreadPosition("Growth", "A possible area of longer-term development."),
        ),
    ),
    ReadingTypeEnum.LOVE_SPREAD: SpreadDefinition(
        key=ReadingTypeEnum.LOVE_SPREAD,
        name="Love Choice",
        positions=(
            SpreadPosition("You", "Your needs and perspective."),
            SpreadPosition("Connection", "The current relational dynamic."),
            SpreadPosition("Path One", "What one choice invites you to consider."),
            SpreadPosition("Path Two", "What the other choice invites you to consider."),
            SpreadPosition("Guidance", "A value or boundary to carry forward."),
        ),
    ),
}


def get_spread(reading_type: ReadingTypeEnum | str) -> SpreadDefinition:
    try:
        spread_key = ReadingTypeEnum(reading_type)
        return SPREADS[spread_key]
    except (KeyError, ValueError) as error:
        message = f"Unsupported spread: {reading_type}"
        raise ValueError(message) from error
