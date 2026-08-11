from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self):
        # Import signals here to avoid AppRegistryNotReady error
        # Signals must be connected after Django apps are loaded
        from . import signals  # noqa: F401
