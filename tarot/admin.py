import csv

from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Card, Reading, ReadingCard

MAX_QUESTION_LENGTH = 25


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("name", "suit", "number", "keyword_links")
    search_fields = ("name", "keywords", "description")
    list_filter = ("suit",)
    ordering = ("suit", "number")
    readonly_fields = ("preview_image",)
    fieldsets = (
        ("Basic Information", {"fields": ("name", "suit", "number")}),
        ("Details", {"fields": ("keywords", "description")}),
        ("Image", {"fields": ("preview_image", "image")}),
    )

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
    list_display = ("id", "date", "question_summary", "theme_in_notes", "reading_type", "progress_status")
    search_fields = ("question", "notes", "reading_type")
    list_filter = ("date", "reading_type")
    ordering = ("-date",)
    actions = [export_readings_to_csv]
    inlines = [ReadingCardInline]
    readonly_fields = ("date", "theme_in_notes")
    fieldsets = (
        ("Basic Information", {"fields": ("date", "reading_type")}),
        (
            "Reading Details",
            {
                "fields": ("question", "notes", "theme_in_notes"),
            },
        ),
    )

    @admin.display(description="Question Summary")
    def question_summary(self, obj):
        return f"{obj.question[:MAX_QUESTION_LENGTH]}..." if len(obj.question) > MAX_QUESTION_LENGTH else obj.question

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
