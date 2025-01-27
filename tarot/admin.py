import csv
import random

from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.forms import Textarea, TextInput
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext as _

from mentors.models import Mentor

from .models import Card, Reading, ReadingCard

MAX_QUESTION_LENGTH = 25


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "suit", "number", "keyword_links")
    search_fields = ("name", "keywords", "description")
    list_filter = ("suit",)
    ordering = ("suit", "number")
    readonly_fields = (
        "slug",
        "preview_image",
    )
    fieldsets = (
        ("Basic Information", {"fields": ("name", "suit", "number")}),
        ("Details", {"fields": ("slug", "keywords", "description")}),
        ("Image", {"fields": ("preview_image", "image")}),
    )
    actions = ["populate_empty_slugs"]

    @admin.display(description="Image Preview")
    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 150px;"/>',
                obj.image.url,
            )
        return "No image"

    @admin.display(description="Keyword Links")
    def keyword_links(self, obj):
        if obj.keywords:
            keywords = obj.keywords.split(",")  # Assuming keywords are comma-separated
            links = [
                format_html(
                    '<a href="{}" style="text-decoration: underline;">{}</a>',
                    reverse(
                        f"admin:{obj._meta.app_label}_{obj._meta.model_name}_changelist",  # noqa: SLF001
                    )
                    + f"?keywords__icontains={keyword.strip()}",
                    keyword.strip(),
                )
                for keyword in keywords
            ]
            return format_html(", ".join(links))
        return "No keywords"

    @admin.action(description="Populate empty slugs for selected cards")
    def populate_empty_slugs(self, request, queryset):
        # Filter only cards with empty slug
        cards_to_update = queryset.filter(Q(slug__isnull=False) | Q(slug__exact=""))
        updated_count = 0

        for card in cards_to_update:
            card.slug = slugify(card.name)
            card.save()
            updated_count += 1

        self.message_user(
            request,
            _(f"Successfully updated slugs for {updated_count} cards."),  # noqa: INT001
            level="success" if updated_count else "warning",
        )


@admin.action(description="Export selected readings to CSV")
def export_readings_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="readings.csv"'

    writer = csv.writer(response)
    writer.writerow(["Date", "Question", "Notes", "Reading Type"])
    for reading in queryset:
        writer.writerow([reading.date, reading.question, reading.notes, reading.reading_type])

    return response


class ReadingCardInline(admin.TabularInline):
    model = ReadingCard
    fields = ("card", "position", "orientation", "role", "interpretation")
    ordering = ["position"]
    extra = 0
    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"style": "width: 90%;"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "style": "width: 95%;"})},
    }

    def get_extra(self, request, obj=None, **kwargs):
        """
        Dynamically calculate the number of empty rows to display.
        """
        if obj:
            existing_cards_count = obj.cards.count()
            return max(3 - existing_cards_count, 0)
        return 3


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "mentor", "theme_in_notes", "reading_type", "progress_status")
    search_fields = ("question", "notes", "reading_type")
    list_filter = ("date", "mentor", "reading_type")
    ordering = ("-date",)
    actions = ["assign_random_mentor", export_readings_to_csv]
    inlines = [ReadingCardInline]
    readonly_fields = ("date", "theme_in_notes")
    fieldsets = (
        ("Basic Information", {"fields": ("date", "mentor", "reading_type")}),
        (
            "Reading Details",
            {
                "fields": ("question", "notes", "theme_in_notes", "celestial_insight"),
            },
        ),
    )

    @admin.action(description=_("Assign random mentor to selected readings"))
    def assign_random_mentor(self, request, queryset):
        # Get all active mentors
        mentors = list(Mentor.objects.filter(active=True))
        if not mentors:
            self.message_user(request, _("No mentors available to assign."), level="error")
            return

        updated_count = 0
        for reading in queryset:
            if reading.mentor is None:  # Only assign if no mentor is set
                reading.mentor = random.choice(mentors)  # noqa: S311
                reading.save()
                updated_count += 1

        if updated_count:
            self.message_user(request, _(f"Random mentors assigned to {updated_count} readings."), level="success")  # noqa: INT001
        else:
            self.message_user(request, _("No readings needed a mentor."), level="info")

    @admin.display(description="Theme in Notes")
    def theme_in_notes(self, obj):
        if "Theme:" in obj.notes:
            return obj.notes.split("Theme:", 1)[1].strip().capitalize()
        return "No theme detected"

    @admin.display(description="Progress Status")
    def progress_status(self, obj):
        if obj.celestial_insight and obj.cards.exists():
            return format_html('<span style="color:green;">Completed</span>')
        if obj.notes and "Theme:" in obj.notes:
            return format_html('<span style="color:orange;">Validated</span>')
        return format_html('<span style="color:red;">Invalid</span>')
