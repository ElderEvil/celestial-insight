from ninja import Schema


class UserProfileSchema(Schema):
    available_tokens: int
    preferences: dict


class UserSchema(Schema):
    username: str
    is_authenticated: bool
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile: UserProfileSchema
