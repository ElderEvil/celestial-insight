"""Whole-catalogue gates for the authored card copy.

These tests are the definition of done for ``tarot/content/cards.json``: every one
of the 78 catalogue cards must carry non-empty English and Ukrainian copy, within
the published length contract, with no certainty language and no leftover scrape
markers.
"""

import json
import re
from pathlib import Path

import pytest
from asgiref.sync import async_to_sync
from django.core.management import call_command

from tarot.catalogue_content import CONTENT_FIELDS, KEYWORDS_FIELD, load_catalogue
from tarot.enums import ReadingTypeEnum
from tarot.models import Card, Reading
from tarot.services.draw_service import persist_draw
from tarot.services.interpretation_service import build_interpretation_prompt

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "tarot_data.json"
PROSE_FIELDS = tuple(field for field in CONTENT_FIELDS if field != KEYWORDS_FIELD)

EXPECTED_CARD_COUNT = 78
DESCRIPTION_WORD_RANGE = {"en": (18, 55), "uk": (15, 45)}
MEANING_WORD_RANGE = {"en": (28, 60), "uk": (20, 55)}
KEYWORD_COUNT_RANGE = (4, 6)
KEYWORDS_MAX_LENGTH = 255

# Certainty and outcome language, in both locales. The interpretation contract
# forbids it in responses; the card copy that feeds the prompt must not model it.
BANNED_PATTERNS = (
    r"\bguarantee",
    r"\bwill definitely\b",
    r"\bcertainly will\b",
    r"\bpredict",
    r"\bprophec",
    r"\bforesee",
    r"\bdiagnosis is\b",
    r"\byou must (buy|sell|sue)\b",
    r"гарант",
    r"передбач",
    r"пророк",
    r"віщу",
    r"точно станеться",
    r"діагноз",
    r"доля (є|буде)",
    r"ви повинні (купити|продати|подати до суду)",
)
STUB_MARKERS = ("...", "The The ", "represents...", "\r", "\n")


def fixture_card_slugs() -> set[str]:
    fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return {entry["fields"]["slug"] for entry in fixture_data if entry["model"] == "tarot.card"}


@pytest.fixture(scope="module")
def content():
    return load_catalogue()


def test_every_catalogue_card_has_a_complete_entry(content):
    assert len(content) == EXPECTED_CARD_COUNT
    assert set(content) == fixture_card_slugs()


@pytest.mark.parametrize("field", list(CONTENT_FIELDS))
@pytest.mark.parametrize("locale", ["en", "uk"])
def test_no_field_is_blank(content, field, locale):
    for slug, entry in content.items():
        values = entry.english if locale == "en" else entry.ukrainian
        assert values[field].strip(), f"{slug}.{field}.{locale} is blank"


def test_descriptions_stay_within_the_length_contract(content):
    for slug, entry in content.items():
        for locale in ("en", "uk"):
            words = (entry.english if locale == "en" else entry.ukrainian)["description"].split()
            low, high = DESCRIPTION_WORD_RANGE[locale]
            assert low <= len(words) <= high, f"{slug}.description.{locale} has {len(words)} words"


def test_meanings_stay_within_the_length_contract(content):
    for slug, entry in content.items():
        for locale in ("en", "uk"):
            values = entry.english if locale == "en" else entry.ukrainian
            low, high = MEANING_WORD_RANGE[locale]
            for field in ("upright_meaning", "reversed_meaning"):
                words = values[field].split()
                assert low <= len(words) <= high, f"{slug}.{field}.{locale} has {len(words)} words"


def test_keywords_stay_within_the_length_contract(content):
    for slug, entry in content.items():
        for locale in ("en", "uk"):
            keywords = (entry.english if locale == "en" else entry.ukrainian)[KEYWORDS_FIELD]
            assert KEYWORD_COUNT_RANGE[0] <= len(keywords.split(", ")) <= KEYWORD_COUNT_RANGE[1], slug
            assert len(keywords) <= KEYWORDS_MAX_LENGTH, slug


def test_ukrainian_copy_is_not_reused_english(content):
    for slug, entry in content.items():
        for field in CONTENT_FIELDS:
            assert entry.english[field].casefold() != entry.ukrainian[field].casefold(), f"{slug}.{field}"


def test_card_copy_avoids_certainty_language(content):
    for slug, entry in content.items():
        for locale, values in (("en", entry.english), ("uk", entry.ukrainian)):
            for field, value in values.items():
                for pattern in BANNED_PATTERNS:
                    assert not re.search(pattern, value, re.IGNORECASE), f"{slug}.{field}.{locale} matches {pattern!r}"


def test_card_copy_contains_no_scrape_or_stub_markers(content):
    for slug, entry in content.items():
        for locale, values in (("en", entry.english), ("uk", entry.ukrainian)):
            for field, value in values.items():
                for marker in STUB_MARKERS:
                    assert marker not in value, f"{slug}.{field}.{locale} contains {marker!r}"


def test_card_copy_contains_no_html(content):
    for slug, entry in content.items():
        for values in (entry.english, entry.ukrainian):
            for field, value in values.items():
                assert "<" not in value, f"{slug}.{field}"
                assert ">" not in value, f"{slug}.{field}"


@pytest.mark.django_db
def test_seed_demo_fills_every_card_and_preserves_local_edits():
    call_command("seed_demo", verbosity=0)

    assert Card.objects.count() == EXPECTED_CARD_COUNT
    for card in Card.objects.all():
        for field in ("description", "description_uk", "upright_meaning", "upright_meaning_uk"):
            assert getattr(card, field).strip(), f"{card.slug}.{field} is blank"
        for field in ("reversed_meaning", "reversed_meaning_uk", "keywords", "keywords_uk"):
            assert getattr(card, field).strip(), f"{card.slug}.{field} is blank"

    card = Card.objects.get(slug="the-fool")
    card.description = "Hand-edited description"
    card.save(update_fields=["description"])

    call_command("seed_demo", verbosity=0)

    card.refresh_from_db()
    assert card.description == "Hand-edited description"


@pytest.mark.django_db
def test_seeded_meaning_reaches_the_interpretation_prompt():
    call_command("seed_demo", verbosity=0)
    reading = Reading.objects.create(
        reading_type=ReadingTypeEnum.THREE_CARD_SPREAD,
        question="What can I learn from this change?",
        locale="en",
    )
    async_to_sync(persist_draw)(reading)
    reading = Reading.objects.get(id=reading.id)
    reading_cards = list(reading.cards.select_related("card").order_by("position"))

    prompt = build_interpretation_prompt(reading, reading_cards)

    for item in reading_cards:
        expected = item.card.localized_meaning(item.orientation, reading.locale)
        assert expected
        assert f"meaning={expected}" in prompt
