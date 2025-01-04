from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError

ARCANA_CHOICES = [
    ("major", _("Major")),
    ("minor", _("Minor")),
]


class Suit(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    arcana = models.CharField(
        _("Arcana"),
        max_length=10,
        choices=ARCANA_CHOICES,
        default="minor",
    )
    description = models.TextField(_("Description"), blank=True)
    color = models.CharField(
        _("Color"),
        max_length=7,
        default="#000000",
        help_text=_("Color code (e.g. #FF0000)"),
    )

    def __str__(self):
        return self.name

    def colored_name(self):
        return format_html('<span style="color: {};">{}</span>', self.color, self.name)

    def clean(self):
        if self.arcana == "major" and Suit.objects.filter(arcana="major").exclude(id=self.id).exists():
            msg = _("There can only be one Major Arcana suit.")
            raise ValidationError(msg)

    colored_name.short_description = _("Suit Name")


class Card(models.Model):
    ORIENTATION_CHOICES = [
        ("upright", _("Upright")),
        ("reversed", _("Reversed")),
    ]

    name = models.CharField(_("Name"), max_length=100)
    suit = models.ForeignKey(
        Suit,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("Suit"),
    )
    number = models.IntegerField(_("Number"), null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="tarot_cards/", blank=True)

    upright_meaning = models.TextField(_("Upright Meaning"))
    reversed_meaning = models.TextField(_("Reversed Meaning"))
    keywords = models.CharField(
        _("Keywords"),
        max_length=255,
        help_text=_("Comma-separated keywords"),
    )
    description = models.TextField(_("Description"))

    class Meta:
        ordering = ["suit", "number"]
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self):
        return f"{self.name} ({self.suit.name})"

    def preview_image(self):
        if self.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;"/>',
                self.image.url,
            )
        return _("No image")

    preview_image.short_description = _("Card Image")


class Reading(models.Model):
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    question = models.TextField(_("Question"), blank=True)
    notes = models.TextField(_("Notes"), blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name=_("User"),
        default=None,
        null=True,
    )

    celestial_insight = models.TextField(_("Celestial Insight"), blank=True)

    def __str__(self):
        return _("Reading for {user} on {date}").format(user=self.user, date=self.date)


class ReadingCard(models.Model):
    reading = models.ForeignKey(
        Reading,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("Reading"),
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        verbose_name=_("Card"),
    )
    position = models.IntegerField(_("Position"))
    orientation = models.CharField(
        _("Orientation"),
        max_length=10,
        choices=Card.ORIENTATION_CHOICES,
    )
    interpretation = models.TextField(_("Interpretation"), blank=True)

    class Meta:
        ordering = ["position"]
        unique_together = ("reading", "position")
        verbose_name = _("Reading Card")
        verbose_name_plural = _("Reading Cards")

    def __str__(self):
        return _("{card_name} ({orientation}) in position {position}").format(
            card_name=self.card.name,
            orientation=self.orientation,
            position=self.position,
        )
