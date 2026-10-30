"""Guard tests for the catalogue loader's fixture filtering behaviour."""

import json
from pathlib import Path

import pytest
from django.core.management import call_command

from tarot.models import Card, Reading, ReadingCard, Suit

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "tarot_data.json"
EXPECTED_SUIT_COUNT = 5
EXPECTED_CARD_COUNT = 78


def _fixture_model_counts() -> dict[str, int]:
    entries = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["model"]] = counts.get(entry["model"], 0) + 1
    return counts


@pytest.mark.django_db
def test_load_catalog_imports_only_suits_and_cards():
    call_command("load_catalog", verbosity=0)

    assert Suit.objects.count() == EXPECTED_SUIT_COUNT
    assert Card.objects.count() == EXPECTED_CARD_COUNT


@pytest.mark.django_db
def test_load_catalog_skips_historical_readings_present_in_fixture():
    fixture_counts = _fixture_model_counts()
    assert fixture_counts["tarot.reading"] > 0
    assert fixture_counts["tarot.readingcard"] > 0

    call_command("load_catalog", verbosity=0)

    assert Reading.objects.count() == 0
    assert ReadingCard.objects.count() == 0


@pytest.mark.django_db
def test_load_catalog_is_idempotent():
    call_command("load_catalog", verbosity=0)
    call_command("load_catalog", verbosity=0)

    assert Suit.objects.count() == EXPECTED_SUIT_COUNT
    assert Card.objects.count() == EXPECTED_CARD_COUNT
    assert Suit.objects.values("name").distinct().count() == EXPECTED_SUIT_COUNT
    assert Card.objects.values("name").distinct().count() == EXPECTED_CARD_COUNT


@pytest.mark.django_db
def test_load_catalog_does_not_import_legacy_copy():
    call_command("load_catalog", verbosity=0)

    assert not Card.objects.exclude(description="").exists()
    assert not Card.objects.exclude(upright_meaning="").exists()
    assert not Card.objects.exclude(reversed_meaning="").exists()
    assert not Card.objects.exclude(keywords="").exists()


@pytest.mark.django_db
def test_load_catalog_never_overwrites_existing_rows():
    call_command("load_catalog", verbosity=0)
    card = Card.objects.get(slug="the-fool")
    card.description = "Hand-edited description"
    card.upright_meaning = "Hand-edited meaning"
    card.save(update_fields=["description", "upright_meaning"])

    call_command("load_catalog", verbosity=0)

    card.refresh_from_db()
    assert card.description == "Hand-edited description"
    assert card.upright_meaning == "Hand-edited meaning"
