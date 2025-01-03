from datetime import datetime

from ninja import Schema


class SuitSchema(Schema):
    id: int
    name: str
    arcana: str
    description: str | None = None
    color: str


class CardSchemaShort(Schema):
    id: int
    name: str
    number: int | None
    image: str | None
    upright_meaning: str
    reversed_meaning: str
    keywords: str
    description: str


class CardSchema(CardSchemaShort):
    suit: SuitSchema


class ReadingCardSchema(Schema):
    id: int
    card: CardSchemaShort
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
