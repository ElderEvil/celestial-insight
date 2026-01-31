from ninja import Schema


class TelegramAuthSchema(Schema):
    telegram_id: int
    username: str


class UserProfileSchema(Schema):
    available_tokens: int
    preferences: dict


class UserSchema(Schema):
    username: str
    is_authenticated: bool
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile: UserProfileSchema | None = None


class TokenResponseSchema(Schema):
    access: str
    refresh: str
    username: str
    email: str | None = None


class EmailUpdateSchema(Schema):
    email: str
