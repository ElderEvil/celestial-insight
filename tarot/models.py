from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from pydantic import ValidationError

from tarot.choices import ARCANA_CHOICES, ORIENTATION_CHOICES, READING_TYPE_CHOICES


class Suit(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    color = models.CharField(
        _("Color"),
        max_length=7,
        default="#000000",
        help_text=_("Color code (e.g. #FF0000)"),
    )

    arcana = models.CharField(
        _("Arcana"),
        max_length=10,
        choices=ARCANA_CHOICES,
        default="minor",
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.arcana == "major" and Suit.objects.filter(arcana="major").exclude(id=self.id).exists():
            msg = _("There can only be one Major Arcana suit.")
            raise ValidationError(msg)

    def colored_name(self):
        return format_html('<span style="color: {};">{}</span>', self.color, self.name)

    colored_name.short_description = _("Suit Name")


class Card(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"))
    number = models.PositiveSmallIntegerField(_("Number"), null=True, blank=True)
    image = models.ImageField(_("Image"), upload_to="tarot_cards/", blank=True)
    upright_meaning = models.TextField(_("Upright Meaning"))
    reversed_meaning = models.TextField(_("Reversed Meaning"))

    keywords = models.CharField(
        _("Keywords"),
        max_length=255,
        help_text=_("Comma-separated keywords"),
    )
    suit = models.ForeignKey(
        Suit,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("Suit"),
        db_index=True,
    )

    class Meta:
        ordering = ["suit", "number"]
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self):
        return f"{self.name} ({self.suit.name})"

    def clean(self):
        super().clean()
        if self.suit.arcana == "major" and self.number is not None:
            raise ValidationError(_("Major Arcana cards cannot have a number."))

    def preview_image(self):
        if self.image:
            return format_html(
                '<img src="{}" style="max-height: 100px;"/>',
                self.image.url,
            )
        return _("No image")

    preview_image.short_description = _("Card Image")


class Reading(models.Model):
    reading_type = models.CharField(
        _("Reading Type"), max_length=20, choices=READING_TYPE_CHOICES, default="single_card"
    )
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    question = models.TextField(_("Question"), blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    celestial_insight = models.TextField(_("Celestial Insight"), blank=True, default="")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="readings",
        verbose_name=_("User"),
        default=None,
        null=True,
    )

    def __str__(self):
        return _("Reading for {user} on {date}").format(user=self.user, date=self.date)


class ReadingCard(models.Model):
    position = models.IntegerField(_("Position"))
    orientation = models.CharField(
        _("Orientation"),
        max_length=10,
        choices=ORIENTATION_CHOICES,
    )
    interpretation = models.TextField(_("Interpretation"), blank=True)

    reading = models.ForeignKey(
        Reading,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("Reading"),
        db_index=True,
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        verbose_name=_("Card"),
    )

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
