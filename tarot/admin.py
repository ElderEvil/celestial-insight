import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

from .models import Suit, Card, Reading, ReadingCard


class CardInline(admin.TabularInline):
    model = Card
    extra = 1


@admin.register(Suit)
class SuitAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'description')
    search_fields = ('name',)
    list_filter = ('arcana',)
    ordering = ('name',)

    inlines = [CardInline]

    def colored_name(self, obj):
        return format_html('<span style="color: {};">{}</span>', obj.color, obj.name)

    colored_name.short_description = 'Name (Colored)'


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'suit', 'number', 'keyword_links')
    search_fields = ('name', 'keywords', 'description')
    list_filter = ('suit',)
    ordering = ('suit', 'number')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px;"/>', obj.image.url)
        return "No image"

    preview_image.short_description = 'Image Preview'

    def keyword_links(self, obj):
        if obj.keywords:
            keywords = obj.keywords.split(',')  # Assuming keywords are comma-separated
            links = [
                format_html(
                    '<a href="{}" style="text-decoration: underline;">{}</a>',
                    reverse(
                        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_changelist') + f'?keywords__icontains={keyword.strip()}',
                    keyword.strip()
                )
                for keyword in keywords
            ]
            return format_html(', '.join(links))
        return "No keywords"


@admin.action(description='Export selected readings to CSV')
def export_readings_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="readings.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Question', 'Notes'])
    for reading in queryset:
        writer.writerow([reading.id, reading.date, reading.question, reading.notes])

    return response


class ReadingCardInline(admin.TabularInline):
    model = ReadingCard
    fields = ('card', 'position', 'orientation', 'interpretation')
    ordering = ['position']

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
    list_display = ('id', 'date', 'question', 'notes')
    search_fields = ('question', 'notes')
    list_filter = ('date',)
    ordering = ('-date',)
    actions = [export_readings_to_csv]
    inlines = [ReadingCardInline]
