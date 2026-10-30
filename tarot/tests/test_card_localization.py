from tarot.models import Card


def test_localized_helpers_select_the_stored_locale():
    card = Card(name="Ace of Wands", description="EN", description_uk="UK")
    card.upright_meaning = "up"
    card.upright_meaning_uk = "вгору"
    card.reversed_meaning = "down"
    card.reversed_meaning_uk = "вниз"
    card.keywords = "a, b"
    card.keywords_uk = "а, б"  # noqa: RUF001

    assert card.localized_meaning("upright", "uk") == "вгору"
    assert card.localized_meaning("reversed", "uk") == "вниз"
    assert card.localized_meaning("upright", "en") == "up"
    assert card.localized_keywords("uk") == "а, б"  # noqa: RUF001
    assert card.localized_description("en") == "EN"


def test_localized_helpers_fall_back_to_english():
    card = Card(name="Ace of Wands", description="EN", description_uk="")
    card.upright_meaning = "up"
    card.upright_meaning_uk = ""
    card.reversed_meaning = "down"
    card.reversed_meaning_uk = ""
    card.keywords = "a, b"
    card.keywords_uk = ""

    assert card.localized_meaning("upright", "uk") == "up"
    assert card.localized_keywords("uk") == "a, b"
    assert card.localized_description("uk") == "EN"
