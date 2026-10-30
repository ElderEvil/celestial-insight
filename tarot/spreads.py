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
    is_active: bool = True


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
    ReadingTypeEnum.ORACLE_OF_DESTINY: SpreadDefinition(
        key=ReadingTypeEnum.ORACLE_OF_DESTINY,
        name="Oracle of Destiny",
        positions=(
            SpreadPosition("Overall Theme", "The primary focus of the reading."),
            SpreadPosition("Challenges", "Obstacles to reflect on."),
            SpreadPosition("Strengths", "Inner resources and talents."),
            SpreadPosition("Relationships", "The influence of others."),
            SpreadPosition("Finances & Career", "Material aspects to consider."),
            SpreadPosition("Health", "Well-being and vitality."),
            SpreadPosition("Emotions", "Inner feelings and intuition."),
            SpreadPosition("Guidance", "A perspective for the path ahead."),
            SpreadPosition("Hidden Factors", "Unseen influences to notice."),
            SpreadPosition("Potential Outcome", "A direction to reflect on, not a fixed prediction."),
        ),
        is_active=False,
    ),
    ReadingTypeEnum.PATH_CROSS: SpreadDefinition(
        key=ReadingTypeEnum.PATH_CROSS,
        name="Path Cross",
        positions=(
            SpreadPosition("The Self", "Core identity and nature."),
            SpreadPosition("The Path", "Current life direction."),
            SpreadPosition("The Crossing", "Challenges to reflect on."),
            SpreadPosition("The Wisdom", "Lessons to be learned."),
            SpreadPosition("The Integration", "A direction to reflect on as the journey unfolds."),
        ),
        is_active=False,
    ),
    ReadingTypeEnum.SPIRITUAL_DEVELOPMENT: SpreadDefinition(
        key=ReadingTypeEnum.SPIRITUAL_DEVELOPMENT,
        name="Spiritual Development",
        positions=(
            SpreadPosition("The Seeker", "Current spiritual state."),
            SpreadPosition("The Path", "Spiritual journey and growth."),
            SpreadPosition("The Challenge", "Obstacles in development."),
            SpreadPosition("The Resources", "Inner strengths."),
            SpreadPosition("The Guidance", "A perspective for progress."),
        ),
        is_active=False,
    ),
    ReadingTypeEnum.DREAM_CARDS: SpreadDefinition(
        key=ReadingTypeEnum.DREAM_CARDS,
        name="Dream Cards",
        positions=(
            SpreadPosition("The Dream", "The overall theme of the dream."),
            SpreadPosition("The Symbol", "A key image in the dream."),
            SpreadPosition("The Emotion", "Dominant feeling in the dream."),
            SpreadPosition("The Interpretation", "A possible meaning of the dream."),
            SpreadPosition("The Action", "What to consider doing with the dream's message."),
        ),
        is_active=False,
    ),
    ReadingTypeEnum.SECRET_REVEAL: SpreadDefinition(
        key=ReadingTypeEnum.SECRET_REVEAL,
        name="Secret Reveal",
        positions=(
            SpreadPosition(
                "The Obvious",
                "What is visible on the surface, what is already known or apparent in the situation.",
            ),
            SpreadPosition(
                "The Hidden",
                "What is concealed or unnoticed, unknown influences affecting the situation.",
            ),
            SpreadPosition("The True Motive", "Hidden intentions or desires of people involved."),
            SpreadPosition(
                "External Influence",
                "Outside factors or people influencing the situation from the sidelines.",
            ),
            SpreadPosition("The Danger", "A risk or tension worth examining in the situation."),
            SpreadPosition("Tarot's Advice", "A perspective on how to reveal or handle the hidden aspects safely."),
            SpreadPosition("The Outcome", "A direction to reflect on once the hidden truth comes to light."),
        ),
        is_active=False,
    ),
}


def get_spread(reading_type: ReadingTypeEnum | str) -> SpreadDefinition:
    try:
        spread_key = ReadingTypeEnum(reading_type)
        return SPREADS[spread_key]
    except (KeyError, ValueError) as error:
        message = f"Unsupported spread: {reading_type}"
        raise ValueError(message) from error


def get_active_spread(reading_type: ReadingTypeEnum | str) -> SpreadDefinition:
    spread = get_spread(reading_type)
    if not spread.is_active:
        message = f"Inactive spread: {reading_type}"
        raise ValueError(message)
    return spread
