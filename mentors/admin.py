from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import mark_safe
from django.utils.text import slugify

from .models import Mentor


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "mystical_level",
        "specialization",
        "is_active",
        "preferred_by_count",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "specialization")
    ordering = ("name",)
    list_per_page = 25
    readonly_fields = ("slug", "avatar_preview", "preferred_by_count", "created_at", "updated_at")

    actions = ["populate_empty_slugs"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "mystical_level",
                    "specialization",
                    "avatar_url",
                    "avatar_preview",
                    "is_active",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.action(description="Populate empty slugs for selected mentors")
    def populate_empty_slugs(self, request, queryset):
        # Filter only mentors with empty slug
        mentors_to_update = queryset.filter(Q(slug__isnull=False) | Q(slug__exact=""))
        updated_count = 0
        for mentor in mentors_to_update:
            mentor.slug = slugify(mentor.name)
            mentor.save()
            updated_count += 1
        self.message_user(
            request, f"Successfully populated {updated_count} slugs)", level="success" if updated_count else "warning"
        )

    def get_queryset(self, request):
        """Annotate the queryset with the count of preferred users."""
        queryset = super().get_queryset(request)
        return queryset.annotate(preferred_by_count=Count("preferred_by_profiles"))

    @admin.display(description="Avatar Preview")
    def avatar_preview(self, obj):
        """Render the avatar image in the admin edit page."""
        if obj.avatar_url:
            return mark_safe(f'<img src="{obj.avatar_url}" style="width: 150px; height: auto; border-radius: 5px;" />')  # noqa: S308
        return "No Image"

    @admin.display(
        description="Preferred By (Users)",
        ordering="preferred_by_count",
    )
    def preferred_by_count(self, obj):
        """Count profiles that prefer this mentor."""
        return obj.preferred_by_profiles.count()
