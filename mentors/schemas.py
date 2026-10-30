from datetime import datetime

from ninja import Schema


class MentorSchema(Schema):
    id: int
    name: str
    slug: str
    mystical_level: int
    specialization: str | None
    avatar_url: str | None
    display_name_uk: str
    biography_en: str
    biography_uk: str
    style_instruction: str
    visual_description: str
    managed_image_path: str
    content_source: str
    is_active: bool


class MentorDetailSchema(MentorSchema):
    created_at: datetime
    updated_at: datetime
