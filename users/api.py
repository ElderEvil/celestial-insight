from allauth.socialaccount.models import SocialAccount
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from ninja.errors import HttpError
from ninja_extra import api_controller, http_get, http_post
from ninja_jwt.authentication import AsyncJWTAuth
from ninja_jwt.tokens import RefreshToken

from .schemas import TelegramAuthSchema, TokenResponseSchema, UserSchema
from .services.telegram_auth import TelegramAuthenticationError, verify_telegram_init_data


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
    """Authenticates verified Telegram Web App identities."""

    @http_post("/auth", response=TokenResponseSchema)
    async def telegram_auth(self, data: TelegramAuthSchema):
        """Verify signed init data and issue a scoped backend JWT."""

        try:
            telegram_user = verify_telegram_init_data(
                data.init_data,
                settings.TELEGRAM_BOT_TOKEN,
                settings.TELEGRAM_INIT_DATA_MAX_AGE_SECONDS,
            )
        except TelegramAuthenticationError as error:
            raise HttpError(401, str(error)) from error

        telegram_id = str(telegram_user["id"])

        # Check if user already exists in SocialAccount
        social_account = await sync_to_async(
            lambda: SocialAccount.objects.filter(provider="telegram", uid=telegram_id).first()
        )()
        if social_account:
            user = await sync_to_async(lambda: social_account.user)()
        else:
            user, created = await sync_to_async(
                lambda: User.objects.get_or_create(
                    username=f"telegram_{telegram_id}",
                    defaults={
                        "first_name": str(telegram_user.get("first_name", ""))[:150],
                        "last_name": str(telegram_user.get("last_name", ""))[:150],
                    },
                )
            )()

            if created:
                user.set_unusable_password()
                await sync_to_async(user.save)()

            await sync_to_async(
                lambda: SocialAccount.objects.create(
                    provider="telegram",
                    uid=telegram_id,
                    user=user,
                    extra_data=telegram_user,
                )
            )()

        # Generate JWT Token
        token = RefreshToken.for_user(user)

        return {
            "access": str(token.access_token),
            "refresh": str(token),
            "username": user.username,
            "email": user.email,
        }

    @http_get("/me", response=UserSchema, auth=AsyncJWTAuth())
    async def me(self, request):
        """Retrieve authenticated user's info including profile data."""
        user = request.user

        if not user.is_authenticated:
            return HttpResponse("Unauthorized", status=401)

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
