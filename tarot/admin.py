import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import Suit, Card, Reading, ReadingCard


class CardInline(admin.TabularInline):
    model = Card
    extra = 1


@admin.register(Suit)
class SuitAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'description')
    search_fields = ('name',)
    list_filter = ('color',)
    ordering = ('name',)

    inlines = [CardInline]

    def colored_name(self, obj):
        return format_html('<span style="color: {};">{}</span>', obj.color, obj.name)

    colored_name.short_description = 'Name (Colored)'


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'suit', 'number', 'preview_image', 'keywords')
    search_fields = ('name', 'keywords', 'description')
    list_filter = ('suit',)
    ordering = ('suit', 'number')
    readonly_fields = ('preview_image',)

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px;"/>', obj.image.url)
        return "No image"

    preview_image.short_description = 'Image Preview'


@admin.action(description='Export selected readings to CSV')
def export_readings_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="readings.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Question', 'Notes'])
    for reading in queryset:
        writer.writerow([reading.id, reading.date, reading.question, reading.notes])

    return response


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'question', 'notes')
    search_fields = ('question', 'notes')
    list_filter = ('date',)
    ordering = ('-date',)
    actions = [export_readings_to_csv]


@admin.register(ReadingCard)
class ReadingCardAdmin(admin.ModelAdmin):
    list_display = ('reading', 'card', 'position', 'orientation', 'interpretation')
    search_fields = ('interpretation',)
    list_filter = ('orientation', 'reading')
    ordering = ('reading', 'position')
