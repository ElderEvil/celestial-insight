from datetime import datetime

from ninja import Schema


class SuitSchema(Schema):
    id: int
    name: str
    description: str | None = None
    color: str


class CardSchema(Schema):
    id: int
    name: str
    suit: SuitSchema
    number: int | None
    image: str | None
    upright_meaning: str
    reversed_meaning: str
    keywords: str
    description: str


class ReadingCardSchema(Schema):
    id: int
    card: CardSchema
    position: int
    orientation: str
    interpretation: str | None = None


class ReadingSchema(Schema):
    id: int
    date: datetime
    question: str | None = None
    notes: str | None = None
    cards: list[ReadingCardSchema] = []


class CelestialInsightResponseSchema(ReadingSchema):
    celestial_insight: str