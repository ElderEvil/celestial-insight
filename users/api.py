from ninja_extra import api_controller, http_get
from .schemas import UserSchema

@api_controller("/users", tags=["Users"])
class UsersController:
    @http_get("/me", response=UserSchema)
    def me(self, request):
        return request.user

