from datetime import datetime

from ninja import Schema
from pydantic.networks import HttpUrl


class MentorSchema(Schema):
    id: int
    name: str
    slug: str
    mystical_level: int
    specialization: str | None
    avatar_url: HttpUrl | None
    is_active: bool


class MentorDetailSchema(MentorSchema):
    created_at: datetime
    updated_at: datetime
