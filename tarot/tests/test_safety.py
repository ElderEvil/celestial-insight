import pytest

from tarot.agents.celestial_agent import CelestialInsightResponse, PositionInterpretation
from tarot.safety import HighStakesCategory, classify_high_stakes_question, validate_reflective_response


@pytest.mark.parametrize(
    ("question", "category"),
    [
        ("Will this medication cure my health condition?", HighStakesCategory.HEALTH),
        ("Should I sue my landlord?", HighStakesCategory.LEGAL),
        ("Should I invest in this crypto token?", HighStakesCategory.FINANCIAL),
        ("Will my ex return because she still wants me?", HighStakesCategory.THIRD_PARTY_INTENT),
        ("Чи варто інвестувати в ці акції?", HighStakesCategory.FINANCIAL),
    ],
)
def test_high_stakes_question_classification(question, category):
    assert category in classify_high_stakes_question(question)


def make_response(text):
    return CelestialInsightResponse(
        text=text,
        positions=[PositionInterpretation(reading_card_id=1, position=1, interpretation="Consider your options.")],
    )


def test_calibrated_high_stakes_response_is_accepted():
    response = make_response(
        "The card may invite you to clarify your priorities and consult a qualified financial professional."
    )

    validate_reflective_response("Should I invest my savings?", response)


def test_definitive_high_stakes_response_is_rejected():
    response = make_response("You must buy this investment; it is guaranteed to rise.")

    with pytest.raises(ValueError, match="calibrated"):
        validate_reflective_response("Should I invest my savings?", response)
