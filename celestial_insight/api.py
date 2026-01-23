from ninja_extra import NinjaExtraAPI

from mentors.api import AsyncMentorController
from tarot.api import AsyncTarotController
from users.api import UsersController

api = NinjaExtraAPI(urls_namespace="main_api")

api.register_controllers(UsersController, AsyncTarotController, AsyncMentorController)
