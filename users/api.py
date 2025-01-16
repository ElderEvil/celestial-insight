from ninja_extra import api_controller, http_get

from .schemas import UserSchema


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
