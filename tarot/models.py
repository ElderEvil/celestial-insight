from django.db import models
from django.utils.html import format_html
from django.conf import settings


class Suit(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#000000", help_text="Color code (e.g. #FF0000)")

    def colored_name(self):
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color,
            self.name
        )

    colored_name.short_description = 'Suit Name'

    def __str__(self):
        return self.name


class Card(models.Model):
    ORIENTATION_CHOICES = [
        ('upright', 'Upright'),
        ('reversed', 'Reversed'),
    ]

    name = models.CharField(max_length=100)
    suit = models.ForeignKey(Suit, on_delete=models.CASCADE, related_name='cards')
    number = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='tarot_cards/', blank=True)

    upright_meaning = models.TextField()
    reversed_meaning = models.TextField()
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords")
    description = models.TextField()

    class Meta:
        ordering = ['suit', 'number']

    def __str__(self):
        return f"{self.name} ({self.suit.name})"

    def preview_image(self):
        if self.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', self.image.url)
        return "No image"

    preview_image.short_description = 'Card Image'


class Reading(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    question = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Reading on {self.date}"


class ReadingCard(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Refers to the User model
        on_delete=models.CASCADE,  # Delete readings if the user is deleted
        related_name="readings",    # Allows reverse lookups: user.readings.all()
        default=None,
        null=True,
    )
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name='cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    position = models.IntegerField()
    orientation = models.CharField(max_length=10, choices=Card.ORIENTATION_CHOICES)
    interpretation = models.TextField(blank=True)

    class Meta:
        ordering = ['position']
        unique_together = ('reading', 'position')

    def __str__(self):
        return f"{self.card.name} ({self.orientation}) in position {self.position}"