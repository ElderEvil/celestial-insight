from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from ninja_extra import api_controller, http_get, http_post
from ninja_jwt.authentication import AsyncJWTAuth
from ninja_jwt.tokens import RefreshToken

from .schemas import TelegramAuthSchema, UserSchema


@api_controller("/users", tags=["Users"])
class UsersController:
    @http_get("/me", response=UserSchema)
    def me(self, request):
        user = request.user

        if not user.is_authenticated:
            return {"username": "", "is_authenticated": False}

        profile = user.profile

        return {
            "username": user.username,
            "is_authenticated": user.is_authenticated,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "available_tokens": profile.available_tokens,
                "preferences": profile.preferences,
            },
        }


@api_controller("/tg/users", tags=["Telegram Users"])
class UsersTGController:
    """Handles Telegram OAuth authentication and user creation."""

    @http_post("/auth", response=UserSchema)
    async def telegram_auth(self, data: TelegramAuthSchema):
        """
        Authenticate Telegram user via Django-Allauth.
        - Checks if the user exists in SocialAccount.
        - If not, registers the user via Telegram OAuth.
        - Issues a JWT token for future API requests.
        """

        # Check if user already exists in SocialAccount
        social_account = SocialAccount.objects.filter(provider="telegram", uid=str(data.telegram_id)).first()
        if social_account:
            user = social_account.user
        else:
            # Create user if not exists
            user, created = User.objects.get_or_create(
                username=data.username, defaults={"email": f"{data.username}@tg.me"}
            )

            if created:
                user.set_unusable_password()
                user.save()

            # Create a SocialAccount entry
            social_account = SocialAccount.objects.create(provider="telegram", uid=str(data.telegram_id), user=user)
            social_account.save()

        # Generate JWT Token
        token = RefreshToken.for_user(user.access_token)

        return {"token": token, "username": user.username, "email": user.email}

    @http_get("/me", response=UserSchema, auth=AsyncJWTAuth())
    async def me(self, request):
        """Retrieve authenticated user's info including profile data."""
        user = request.user

        if not user.is_authenticated:
            return {"error": "Unauthorized"}, 401

        profile = getattr(user, "profile", None)

        return {
            "username": user.username,
            "email": user.email,
            "is_authenticated": user.is_authenticated,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile": {
                "available_tokens": getattr(profile, "available_tokens", 0),
                "preferences": getattr(profile, "preferences", {}),
            },
        }
