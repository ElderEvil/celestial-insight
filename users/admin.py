from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "available_tokens")  # Fields to display in list view
    search_fields = ("user__username", "user__email")  # Enable search by username and email

    actions = ["reset_tokens"]

    @admin.action(description="Reset tokens to default")
    def reset_tokens(self, request, queryset):
        queryset.update(available_tokens=1_000)
