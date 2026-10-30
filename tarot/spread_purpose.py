"""Reflective purpose statements for each tarot spread.

Ported from the archived prototype's ``spread_purpose.py`` and mapped onto the
target :class:`ReadingTypeEnum` keys. Outcome-asserting wording has been
rewritten as reflective language. This module is inert content: nothing here is
wired into a prompt, view, form, or agent yet.
"""

from .enums import ReadingTypeEnum

SPREAD_PURPOSE: dict[ReadingTypeEnum, str] = {
    ReadingTypeEnum.SINGLE_CARD: "A quick focal point for reflecting on a specific question.",
    ReadingTypeEnum.THREE_CARD_SPREAD: "A past, present, and future perspective to reflect on a situation.",
    ReadingTypeEnum.CELTIC_CROSS_SPREAD: "An in-depth structure for reflecting on a complex situation or life path.",
    ReadingTypeEnum.CAREER_PATH_SPREAD: "A framework for reflecting on professional development and opportunities.",
    ReadingTypeEnum.LOVE_SPREAD: "A structure for reflecting on romantic relationships and choices.",
    ReadingTypeEnum.ORACLE_OF_DESTINY: "A framework for reflecting on the forces that may shape your path.",
    ReadingTypeEnum.PATH_CROSS: "A way to explore crossroads and reflect on important life decisions.",
    ReadingTypeEnum.SPIRITUAL_DEVELOPMENT: "A structure for reflecting on your spiritual journey and inner growth.",
    ReadingTypeEnum.DREAM_CARDS: "A structure for reflecting on symbols and messages from your dreams.",
    ReadingTypeEnum.SECRET_REVEAL: "A framework for reflecting on hidden influences in your life.",
}
