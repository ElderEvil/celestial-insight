from django.conf import settings
from django.db import models
from django.utils.html import format_html
from pydantic import ValidationError

ARCANA_CHOICES = [
    ("major", "Major"),
    ("minor", "Minor"),
]


class Suit(models.Model):
    name = models.CharField(max_length=50)
    arcana = models.CharField(max_length=10, choices=ARCANA_CHOICES, default="minor")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#000000", help_text="Color code (e.g. #FF0000)")

    def __str__(self):
        return self.name

    def colored_name(self):
        return format_html('<span style="color: {};">{}</span>', self.color, self.name)

    def clean(self):
        if self.arcana == "major" and Suit.objects.filter(arcana="major").exclude(id=self.id).exists():
            msg = "There can only be one Major Arcana suit."
            raise ValidationError(msg)

    colored_name.short_description = "Suit Name"


class Card(models.Model):
    ORIENTATION_CHOICES = [
        ("upright", "Upright"),
        ("reversed", "Reversed"),
    ]

    name = models.CharField(max_length=100)
    suit = models.ForeignKey(Suit, on_delete=models.CASCADE, related_name="cards")
    number = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="tarot_cards/", blank=True)

    upright_meaning = models.TextField()
    reversed_meaning = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords")
    description = models.TextField()

    class Meta:
        ordering = ["suit", "number"]

    def __str__(self):
        return f"{self.name} ({self.suit.name})"

    def preview_image(self):
        if self.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', self.image.url)
        return "No image"

    preview_image.short_description = "Card Image"


class Reading(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    question = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="readings",
        default=None,
        null=True,
    )

    celestial_insight = models.TextField(blank=True)

    def __str__(self):
        return f"Reading for {self.user} on {self.date}"


class ReadingCard(models.Model):
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name="cards")
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField()
    orientation = models.CharField(max_length=10, choices=Card.ORIENTATION_CHOICES)
    interpretation = models.TextField(blank=True)

    class Meta:
        ordering = ["position"]
        unique_together = ("reading", "position")

    def __str__(self):
        return f"{self.card.name} ({self.orientation}) in position {self.position}"
