from django.contrib.auth import get_user_model
from django.db import models

user = get_user_model()

DEFAULT_TOKENS = 1_000


class UserProfile(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name="profile")
    available_tokens = models.PositiveIntegerField(default=DEFAULT_TOKENS)
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
