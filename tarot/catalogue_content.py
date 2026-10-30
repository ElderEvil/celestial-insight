"""Load and validate the authored English/Ukrainian card copy.

Content lives in ``tarot/content/cards.json`` and is applied to the database by
``load_card_catalogue``. It is deliberately not a Django fixture: deserializing a
partial ``tarot.card`` row calls ``save()`` with ``raw=True``, which writes every
field and would erase each card's name, slug, suit, number and image.
"""

import json
from dataclasses import dataclass
from pathlib import Path

CONTENT_PATH = Path(__file__).resolve().parent / "content" / "cards.json"

CONTENT_FIELDS = {
    "description": "description_uk",
    "upright_meaning": "upright_meaning_uk",
    "reversed_meaning": "reversed_meaning_uk",
    "keywords": "keywords_uk",
}
KEYWORDS_FIELD = "keywords"
LOCALES = ("en", "uk")

MIN_KEYWORDS = 3
MAX_KEYWORDS = 6
KEYWORDS_MAX_LENGTH = 255
MAX_PROSE_CHARACTERS = 900


class CatalogueContentError(ValueError):
    """Raised when the authored catalogue file is structurally invalid."""


@dataclass(frozen=True)
class CardContent:
    slug: str
    english: dict[str, str]
    ukrainian: dict[str, str]


def _require_text(slug: str, field: str, locale: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        message = f"{slug}.{field}.{locale} must be a non-empty string"
        raise CatalogueContentError(message)
    text = value.strip()
    if "\n" in text or "\r" in text:
        message = f"{slug}.{field}.{locale} must stay on one line"
        raise CatalogueContentError(message)
    if "<" in text or ">" in text:
        message = f"{slug}.{field}.{locale} must not contain HTML"
        raise CatalogueContentError(message)
    if len(text) > MAX_PROSE_CHARACTERS:
        message = f"{slug}.{field}.{locale} exceeds {MAX_PROSE_CHARACTERS} characters"
        raise CatalogueContentError(message)
    return text


def _require_keywords(slug: str, locale: str, value: object) -> str:
    if not isinstance(value, list) or not MIN_KEYWORDS <= len(value) <= MAX_KEYWORDS:
        message = f"{slug}.{KEYWORDS_FIELD}.{locale} must be a list of {MIN_KEYWORDS}-{MAX_KEYWORDS}"
        raise CatalogueContentError(message)
    words = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            message = f"{slug}.{KEYWORDS_FIELD}.{locale} contains a blank keyword"
            raise CatalogueContentError(message)
        word = item.strip().casefold()
        if "," in word:
            message = f"{slug}.{KEYWORDS_FIELD}.{locale} keyword must not contain a comma"
            raise CatalogueContentError(message)
        words.append(word)
    if len(set(words)) != len(words):
        message = f"{slug}.{KEYWORDS_FIELD}.{locale} contains duplicate keywords"
        raise CatalogueContentError(message)
    joined = ", ".join(words)
    if len(joined) > KEYWORDS_MAX_LENGTH:
        message = f"{slug}.{KEYWORDS_FIELD}.{locale} exceeds {KEYWORDS_MAX_LENGTH} characters"
        raise CatalogueContentError(message)
    return joined


def _validate_entry(slug: str, entry: object) -> CardContent:
    if not isinstance(entry, dict) or set(entry) != set(CONTENT_FIELDS):
        expected = ", ".join(sorted(CONTENT_FIELDS))
        message = f"{slug} must define exactly: {expected}"
        raise CatalogueContentError(message)

    english: dict[str, str] = {}
    ukrainian: dict[str, str] = {}
    for field in CONTENT_FIELDS:
        locales = entry[field]
        if not isinstance(locales, dict) or set(locales) != set(LOCALES):
            expected_locales = ", ".join(LOCALES)
            message = f"{slug}.{field} must define exactly: {expected_locales}"
            raise CatalogueContentError(message)
        if field == KEYWORDS_FIELD:
            english[field] = _require_keywords(slug, "en", locales["en"])
            ukrainian[field] = _require_keywords(slug, "uk", locales["uk"])
        else:
            english[field] = _require_text(slug, field, "en", locales["en"])
            ukrainian[field] = _require_text(slug, field, "uk", locales["uk"])
        if english[field].casefold() == ukrainian[field].casefold():
            message = f"{slug}.{field} Ukrainian copy must differ from English"
            raise CatalogueContentError(message)

    return CardContent(slug=slug, english=english, ukrainian=ukrainian)


def _load_payload(content_path: Path) -> dict:
    try:
        payload = json.loads(content_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        message = f"Card content file not found: {content_path}"
        raise CatalogueContentError(message) from error
    except json.JSONDecodeError as error:
        message = f"Card content file is not valid JSON: {error}"
        raise CatalogueContentError(message) from error
    if not isinstance(payload, dict) or set(payload) != {"_meta", "cards"}:
        message = 'Card content must contain exactly "_meta" and "cards"'
        raise CatalogueContentError(message)
    return payload


def _validate_meta(meta: object) -> None:
    if not isinstance(meta, dict):
        message = "_meta must be an object"
        raise CatalogueContentError(message)
    if not isinstance(meta.get("version"), int) or meta["version"] < 1:
        message = "_meta.version must be a positive integer"
        raise CatalogueContentError(message)
    for key in ("voice", "provenance"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            message = f"_meta.{key} must be a non-empty string"
            raise CatalogueContentError(message)


def load_catalogue(path: Path | str | None = None) -> dict[str, CardContent]:
    """Read the content file and return validated entries keyed by card slug."""
    content_path = CONTENT_PATH if path is None else Path(path)
    payload = _load_payload(content_path)
    _validate_meta(payload["_meta"])

    cards = payload["cards"]
    if not isinstance(cards, dict):
        message = "cards must be an object keyed by card slug"
        raise CatalogueContentError(message)

    return {slug: _validate_entry(slug, entry) for slug, entry in cards.items()}
