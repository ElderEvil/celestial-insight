from django.shortcuts import get_object_or_404

from tarot.agents.celestial_agent import celestial_agent
from tarot.agents.common import ReadingDependencies
from tarot.agents.tarot_support_agent import tarot_support_agent
from tarot.enums import ReadingTypeEnum
from tarot.models import Card, Reading, ReadingCard


def create_reading(request, question: str, reading_type: ReadingTypeEnum | None = None):
    try:
        deps = ReadingDependencies(question=question)
        validation_result = tarot_support_agent.run_sync("Validate the question", deps=deps)

        if not validation_result or not validation_result.data.is_valid:
            return f"Invalid question: {validation_result.data.reason}"

        theme = validation_result.data.theme
        spread_type = reading_type or validation_result.data.spread_type

    except Exception as e:
        return f"Error validating question: {e}"

    return Reading.objects.create(
        user=request.user,
        question=question,
        notes=f"Theme: {theme}",
        reading_type=spread_type,
    )


def list_readings(request, filters):
    readings = Reading.objects.filter(user=request.user).order_by("-date")
    return filters.filter(readings)


def get_reading(request, reading_id: int):
    return get_object_or_404(Reading, id=reading_id, user=request.user)


def generate_insight(request, reading_id: int):
    reading = get_object_or_404(Reading, id=reading_id, user=request.user)

    try:
        prompt = (
            f"Provide mystical guidance for the question: '{reading.question}' "
            f"and create a card spread of type '{reading.reading_type}'."
        )
        insight_result = celestial_agent.run_sync(prompt, deps=ReadingDependencies(question=reading.question))

        if not insight_result:
            return f"Failed to generate celestial insight: {insight_result.error}"

        celestial_response = insight_result.data
        cards_data = celestial_response.cards

    except Exception as e:
        return f"Error generating celestial insight: {e}"

    try:
        card_objects = []
        for card_data in cards_data:
            card_name = card_data.name.lower().removeprefix("the ").strip()
            card = Card.objects.filter(name__iexact=card_name).first()
            if not card:
                return f"Card '{card_name}' not found in the database."
            card_objects.append((card, card_data))

    except Exception as e:
        return f"Error mapping cards to database: {e}"

    reading.celestial_insight = celestial_response.text
    reading.save()

    ReadingCard.objects.filter(reading=reading).delete()  # Clear existing cards
    for position, (card, card_data) in enumerate(card_objects, start=1):
        ReadingCard.obj1ects.create(
            reading=reading,
            card=card,
            position=position,
            orientation=card_data.orientation,
            interpretation=card_data.interpretation,
        )

    return reading
