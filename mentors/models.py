from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Mentor(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    mystical_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_("Mystical Level"),
        help_text=_("Select a mystical level from 0 (Skeptical) to 10 (Fortune Teller)."),
    )
    avatar_url = models.URLField(max_length=500, blank=True, verbose_name=_("Avatar URL"))
    specialization = models.CharField(max_length=255, blank=True, verbose_name=_("Specialization"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Mentor")
        verbose_name_plural = _("Mentors")

    def __str__(self):
        return f"{self.name} (Mystical Level: {self.mystical_level})"
