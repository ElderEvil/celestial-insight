from ninja_extra import NinjaExtraAPI

from mentors.api import AsyncMentorController
from tarot.api import AsyncTarotController, AsyncTarotTGController
from users.api import UsersController, UsersTGController

api = NinjaExtraAPI(urls_namespace="main_api")

api.register_controllers(
    UsersController, UsersTGController, AsyncTarotController, AsyncTarotTGController, AsyncMentorController
)
