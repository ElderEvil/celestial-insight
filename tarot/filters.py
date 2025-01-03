from datetime import datetime

from ninja import Field, FilterSchema


class CardFilterSchema(FilterSchema):
    suit: int | None = Field(None, description="Filter by suit ID")
    name: str | None = Field(None, q="name__icontains", description="Filter by card name (partial match)")
    keywords: str | None = Field(None, q="keywords__icontains", description="Filter by keywords (comma-separated)")


class ReadingFilterSchema(FilterSchema):
    question: str | None = Field(None, q="question__icontains", description="Filter by question")
    date: datetime | None = Field(None, q="date__gte", description="Filter by readings newer than this date")
