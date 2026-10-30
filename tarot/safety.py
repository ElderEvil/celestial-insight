import re
from enum import StrEnum

from tarot.agents.celestial_agent import CelestialInsightResponse


class HighStakesCategory(StrEnum):
    HEALTH = "health"
    LEGAL = "legal"
    FINANCIAL = "financial"
    THIRD_PARTY_INTENT = "third_party_intent"


HIGH_STAKES_PATTERNS = {
    HighStakesCategory.HEALTH: (r"\b(health|diagnos|disease|pregnan|medication|лікуван|здоров|вагітн)\w*",),
    HighStakesCategory.LEGAL: (r"\b(legal|lawyer|court|sue|lawsuit|арешт|суд|юрист)\w*",),
    HighStakesCategory.FINANCIAL: (
        r"\b(invest|stock|crypto|loan|debt|financial|акці|крипт|інвест|борг)\w*",  # noqa: RUF001
    ),
    HighStakesCategory.THIRD_PARTY_INTENT: (
        r"\b(does|will|is|are) (he|she|they|my partner|my ex)\b.*\b(feel|think|want|cheat|return|leave)",
        r"\b(він|вона|вони)\b.*\b(дума|відчува|хоче|зрад|поверн|піде)",
    ),
}

DEFINITIVE_PATTERNS = (
    r"\b(will definitely|guaranteed|certainly will|you must (buy|sell|sue|stop taking)|the diagnosis is)\b",
    r"\b(точно станеться|гарантовано|ви повинні (купити|продати|подати до суду)|діагноз)\b",
)


def classify_high_stakes_question(question: str) -> set[HighStakesCategory]:
    normalized = question.casefold()
    return {
        category
        for category, patterns in HIGH_STAKES_PATTERNS.items()
        if any(re.search(pattern, normalized) for pattern in patterns)
    }


def safety_prompt_context(question: str) -> str:
    categories = classify_high_stakes_question(question)
    if not categories:
        return "Keep the reading reflective and avoid claims of certainty."

    category_names = ", ".join(sorted(category.value for category in categories))
    return (
        f"High-stakes context detected ({category_names}). Do not predict an outcome or infer hidden intent. "
        "Offer questions for reflection, acknowledge uncertainty, and direct the seeker to an appropriate qualified "
        "professional for decisions that require health, legal, or financial expertise."
    )


def validate_reflective_response(question: str, response: CelestialInsightResponse) -> None:
    if not classify_high_stakes_question(question):
        return

    response_text = " ".join(
        [response.text, *(position.interpretation for position in response.positions), response.follow_up_prompt or ""]
    ).casefold()
    if any(re.search(pattern, response_text) for pattern in DEFINITIVE_PATTERNS):
        message = "High-stakes interpretations must use calibrated, reflective language."
        raise ValueError(message)
