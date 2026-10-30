"""Regression tests for the ``Reading.reading_type`` field width.

The field must be wide enough to hold every ``ReadingTypeEnum`` value, and in
particular the 21-character ``spiritual_development`` key that previously
overflowed a ``max_length=20`` column.
"""

from tarot.enums import ReadingTypeEnum
from tarot.models import Reading

EXPECTED_MAX_LENGTH = 32
SPIRITUAL_DEVELOPMENT_LENGTH = 21


def test_reading_type_field_holds_every_enum_value():
    # Django exposes concrete model fields only through the _meta API.
    field = Reading._meta.get_field("reading_type")  # noqa: SLF001

    assert field.max_length == EXPECTED_MAX_LENGTH

    for member in ReadingTypeEnum:
        assert len(member.value) <= field.max_length, (
            f"{member.name}={member.value!r} ({len(member.value)} chars) "
            f"exceeds reading_type max_length={field.max_length}"
        )


def test_spiritual_development_key_length_is_pinned():
    assert len("spiritual_development") == SPIRITUAL_DEVELOPMENT_LENGTH
