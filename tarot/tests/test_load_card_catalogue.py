import io
import json

import pytest
from django.core.management import CommandError, call_command
from model_bakery import baker

from tarot.catalogue_content import CatalogueContentError, load_catalogue

SLUG = "ace-of-wands"


def entry(**overrides):
    content = {
        "description": {
            "en": "A hand offers a budding wand above a bright landscape.",
            "uk": "Рука простягає паросток жезла над яскравим краєвидом.",
        },
        "upright_meaning": {
            "en": "This card invites you to notice a spark of energy that is ready to be tended.",
            "uk": "Ця карта запрошує помітити іскру енергії, яку вже час плекати.",
        },
        "reversed_meaning": {
            "en": "This card invites you to notice where momentum has stalled and what is holding it.",
            "uk": "Ця карта запрошує помітити, де рух завмер і що його стримує.",  # noqa: RUF001
        },
        "keywords": {
            "en": ["spark", "initiative", "potential", "beginning"],
            "uk": ["іскра", "ініціатива", "потенціал", "початок"],
        },
    }
    content.update(overrides)
    return content


def write_content(tmp_path, cards):
    path = tmp_path / "cards.json"
    payload = {
        "_meta": {
            "version": 1,
            "voice": "Reflective voice.",
            "provenance": "Authored for tests.",
        },
        "cards": cards,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def make_card(**overrides):
    values = {
        "name": "Ace of Wands",
        "slug": SLUG,
        "number": 1,
        "description": "",
        "upright_meaning": "",
        "reversed_meaning": "",
        "keywords": "",
    }
    values.update(overrides)
    return baker.make("tarot.Card", **values)


@pytest.mark.django_db
def test_loader_fills_blank_fields_without_touching_identity(tmp_path):
    card = make_card()
    original_identity = (card.name, card.slug, card.suit_id, card.number)
    path = write_content(tmp_path, {SLUG: entry()})

    call_command("load_card_catalogue", path=str(path), stdout=io.StringIO())

    card.refresh_from_db()
    assert card.description == entry()["description"]["en"]
    assert card.description_uk == entry()["description"]["uk"]
    assert card.upright_meaning == entry()["upright_meaning"]["en"]
    assert card.upright_meaning_uk == entry()["upright_meaning"]["uk"]
    assert card.reversed_meaning == entry()["reversed_meaning"]["en"]
    assert card.reversed_meaning_uk == entry()["reversed_meaning"]["uk"]
    assert card.keywords == "spark, initiative, potential, beginning"
    assert card.keywords_uk == "іскра, ініціатива, потенціал, початок"
    assert (card.name, card.slug, card.suit_id, card.number) == original_identity


@pytest.mark.django_db
def test_repeated_run_is_idempotent(tmp_path):
    make_card()
    path = write_content(tmp_path, {SLUG: entry()})
    call_command("load_card_catalogue", path=str(path), stdout=io.StringIO())

    output = io.StringIO()
    call_command("load_card_catalogue", path=str(path), stdout=output)

    assert "0 filled" in output.getvalue()
    assert "0 overwritten" in output.getvalue()


@pytest.mark.django_db
def test_local_edits_survive_without_overwrite_and_yield_to_it(tmp_path):
    card = make_card(description="Hand-edited description")
    path = write_content(tmp_path, {SLUG: entry()})

    call_command("load_card_catalogue", path=str(path), stdout=io.StringIO())
    card.refresh_from_db()
    assert card.description == "Hand-edited description"
    assert card.description_uk == entry()["description"]["uk"]

    call_command("load_card_catalogue", path=str(path), overwrite=True, stdout=io.StringIO())
    card.refresh_from_db()
    assert card.description == entry()["description"]["en"]


@pytest.mark.django_db
def test_unknown_slug_fails_loudly(tmp_path):
    make_card()
    path = write_content(tmp_path, {"not-a-real-card": entry()})

    with pytest.raises(CommandError, match="Unknown card slugs"):
        call_command("load_card_catalogue", path=str(path), stdout=io.StringIO())


@pytest.mark.django_db
def test_missing_entries_are_reported_without_failing(tmp_path):
    make_card()
    baker.make("tarot.Card", name="Two of Wands", slug="two-of-wands")
    path = write_content(tmp_path, {SLUG: entry()})

    output = io.StringIO()
    call_command("load_card_catalogue", path=str(path), stdout=output)

    assert "1 cards still have no authored entry" in output.getvalue()
    assert "two-of-wands" in output.getvalue()


def test_catalogue_file_loads_and_is_structurally_valid():
    content = load_catalogue()

    assert isinstance(content, dict)
    for slug, card_content in content.items():
        assert slug == card_content.slug
        assert set(card_content.english) == set(card_content.ukrainian)


def test_missing_ukrainian_copy_is_rejected(tmp_path):
    broken = entry()
    broken["upright_meaning"]["uk"] = ""
    path = write_content(tmp_path, {SLUG: broken})

    with pytest.raises(CatalogueContentError, match="non-empty"):
        load_catalogue(path)


def test_identical_translation_is_rejected(tmp_path):
    broken = entry()
    broken["description"]["uk"] = broken["description"]["en"]
    path = write_content(tmp_path, {SLUG: broken})

    with pytest.raises(CatalogueContentError, match="must differ"):
        load_catalogue(path)


def test_unknown_field_is_rejected(tmp_path):
    broken = entry()
    broken["lucky_number"] = {"en": "7", "uk": "7"}
    path = write_content(tmp_path, {SLUG: broken})

    with pytest.raises(CatalogueContentError, match="must define exactly"):
        load_catalogue(path)


def test_multiline_and_html_copy_is_rejected(tmp_path):
    multiline = entry()
    multiline["description"]["en"] = "Line one\nLine two"
    with pytest.raises(CatalogueContentError, match="one line"):
        load_catalogue(write_content(tmp_path, {SLUG: multiline}))


def test_keyword_bounds_are_enforced(tmp_path):
    short = entry()
    short["keywords"]["en"] = ["only-one"]
    with pytest.raises(CatalogueContentError, match="list of"):
        load_catalogue(write_content(tmp_path, {SLUG: short}))
