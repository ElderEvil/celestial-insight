from ninja_extra import NinjaExtraAPI

from tarot.api import TarotController
from users.api import UsersController

api = NinjaExtraAPI(urls_namespace="main_api")

api.register_controllers(UsersController, TarotController)
