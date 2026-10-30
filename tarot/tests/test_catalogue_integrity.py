"""Whole-catalogue integrity checks for the tarot content set.

These tests are the single place that proves the invariants the harvest relies on:
every mentor row is complete in both locales with a real local portrait, exactly the
launch three are active, every spread has ordered unique roles, and every content
module only references things that exist.
"""

import json
import re
from pathlib import Path

import pytest

from mentors.models import Mentor
from tarot.enums import ReadingTypeEnum
from tarot.intents import InvalidIntentOptions, ThemeOptions, ToneOptions, ValidIntentOptions
from tarot.models import Reading
from tarot.spread_matrix import DEFAULT_SPREADS, TAROT_SPREADS
from tarot.spread_purpose import SPREAD_PURPOSE
from tarot.spreads import SPREADS
from tarot.tones import TONE_MODIFIERS, TONE_PROMPTS, ToneModifier

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "mentors" / "fixtures" / "mentor_data.json"
STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"

LAUNCH_MENTOR_SLUGS = {"neutral-reader", "milo-starwhisk", "lolly-kiddie"}
EXPECTED_MENTOR_COUNT = 7
EXPECTED_ACTIVE_MENTOR_COUNT = 3
EXPECTED_SPREAD_COUNT = 10
EXPECTED_ACTIVE_SPREAD_COUNT = 5
EXPECTED_TONE_MODIFIER_COUNT = 20
MIN_TONE_PROMPT_LENGTH = 40
EXPECTED_VALID_INTENT_COUNT = 4
EXPECTED_INVALID_INTENT_COUNT = 3
EXPECTED_THEME_COUNT = 14
EXPECTED_TONE_COUNT = 5

REQUIRED_MENTOR_TEXT_FIELDS = (
    "biography_en",
    "biography_uk",
    "display_name_uk",
    "style_instruction",
    "managed_image_path",
    "content_source",
)

# Reflective-guidance gate for persona copy. Deliberately NOT safety.DEFINITIVE_PATTERNS:
# that set targets high-stakes *responses* ("you must buy", "the diagnosis is") and would
# pass the certainty/occult framing this gate exists to reject.
BIOGRAPHY_BANNED_PATTERNS = (
    r"\bguarantee",
    r"\bwill definitely\b",
    r"\bprophec",
    r"\bforesee",
    r"\bfortune[- ]tell",
    r"\bpredicts?\b",
    r"\buncanny truths?\b",
    r"\bapocalyptic\b",
    r"\bchannels? (the )?(dead|spirits)\b",
    r"\bspeaks? (to|with) the dead\b",
    r"\bdestiny is\b",
    r"гарант",
    r"апокаліп",
    r"передбач",
    r"точно станеться",
    r"доля (є|буде)",
)


def _fixture_rows() -> list[dict]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fixture_rows() -> list[dict]:
    return _fixture_rows()


def test_fixture_has_expected_mentor_count(fixture_rows):
    assert len(fixture_rows) == EXPECTED_MENTOR_COUNT


def test_fixture_primary_keys_are_stable_and_unique(fixture_rows):
    pks = [row["pk"] for row in fixture_rows]
    assert pks == sorted(pks)
    assert len(pks) == len(set(pks))


def test_fixture_slugs_are_unique_and_non_empty(fixture_rows):
    slugs = [row["fields"]["slug"] for row in fixture_rows]
    assert all(slugs)
    assert len(slugs) == len(set(slugs))


def test_exactly_the_launch_mentors_are_active_in_the_fixture(fixture_rows):
    active = {row["fields"]["slug"] for row in fixture_rows if row["fields"]["is_active"]}
    assert active == LAUNCH_MENTOR_SLUGS
    assert len(active) == EXPECTED_ACTIVE_MENTOR_COUNT


@pytest.mark.parametrize("field", REQUIRED_MENTOR_TEXT_FIELDS)
def test_every_fixture_row_has_required_text(fixture_rows, field):
    for row in fixture_rows:
        value = row["fields"].get(field)
        assert isinstance(value, str), f"{row['fields']['slug']}.{field} is not a string"
        assert value.strip(), f"{row['fields']['slug']} is missing {field}"


def test_every_fixture_row_has_no_remote_avatar(fixture_rows):
    for row in fixture_rows:
        assert row["fields"]["avatar_url"] == "", row["fields"]["slug"]


def test_every_managed_image_resolves_to_a_local_file(fixture_rows):
    for row in fixture_rows:
        image_path = row["fields"]["managed_image_path"]
        assert image_path.startswith("mentors/"), row["fields"]["slug"]
        assert (STATIC_ROOT / image_path).is_file(), f"missing image for {row['fields']['slug']}: {image_path}"


def test_every_biography_stays_reflective(fixture_rows):
    for row in fixture_rows:
        slug = row["fields"]["slug"]
        for field in ("biography_en", "biography_uk"):
            text = row["fields"][field].casefold()
            for pattern in BIOGRAPHY_BANNED_PATTERNS:
                assert not re.search(pattern, text), f"{slug}.{field} matches banned pattern {pattern!r}"


def test_every_fixture_row_records_provenance(fixture_rows):
    for row in fixture_rows:
        assert row["fields"]["content_source"].startswith("celestial-neutral/"), row["fields"]["slug"]


@pytest.mark.django_db
def test_seed_demo_activates_only_the_launch_mentors():
    from django.core.management import call_command

    call_command("seed_demo", verbosity=0)

    assert Mentor.objects.count() == EXPECTED_MENTOR_COUNT
    assert set(Mentor.objects.filter(is_active=True).values_list("slug", flat=True)) == LAUNCH_MENTOR_SLUGS


def test_spread_catalogue_size_and_activation():
    assert len(SPREADS) == EXPECTED_SPREAD_COUNT
    assert sum(1 for spread in SPREADS.values() if spread.is_active) == EXPECTED_ACTIVE_SPREAD_COUNT


def test_every_spread_has_unique_non_empty_roles():
    for key, spread in SPREADS.items():
        roles = [position.role for position in spread.positions]
        assert roles, key
        assert len(roles) == len(set(roles)), key
        assert all(position.role.strip() and position.description.strip() for position in spread.positions), key


def test_every_reading_type_value_fits_the_database_field():
    max_length = Reading._meta.get_field("reading_type").max_length  # noqa: SLF001 - Django exposes fields via _meta
    for member in ReadingTypeEnum:
        assert len(member.value) <= max_length, member.value


def test_spread_purpose_covers_every_defined_spread():
    assert set(SPREAD_PURPOSE) == set(SPREADS)
    assert all(purpose.strip() for purpose in SPREAD_PURPOSE.values())


def test_spread_matrix_references_only_defined_active_spreads():
    assert set(DEFAULT_SPREADS) <= set(SPREADS)
    for key, spreads in TAROT_SPREADS.items():
        intent, theme = key
        assert isinstance(intent, ValidIntentOptions)
        assert isinstance(theme, ThemeOptions)
        assert spreads, key
        assert len(spreads) == len(set(spreads)), key
        for reading_type in spreads:
            assert reading_type in SPREADS, (key, reading_type)
            assert SPREADS[reading_type].is_active, (key, reading_type)


def test_tone_catalogue_is_complete_and_consistent():
    assert len(ToneModifier) == EXPECTED_TONE_MODIFIER_COUNT
    assert set(TONE_PROMPTS) == set(ToneModifier)
    assert all(len(prompt) >= MIN_TONE_PROMPT_LENGTH for prompt in TONE_PROMPTS.values())
    assert set(TONE_MODIFIERS) == {(intent, tone) for intent in ValidIntentOptions for tone in ToneOptions}
    assert set(TONE_MODIFIERS.values()) == set(ToneModifier)


def test_intent_enums_have_expected_sizes():
    assert len(ValidIntentOptions) == EXPECTED_VALID_INTENT_COUNT
    assert len(InvalidIntentOptions) == EXPECTED_INVALID_INTENT_COUNT
    assert len(ThemeOptions) == EXPECTED_THEME_COUNT
    assert len(ToneOptions) == EXPECTED_TONE_COUNT
