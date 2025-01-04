from django.utils.translation import gettext_lazy as _

ARCANA_CHOICES = [
    ("major", _("Major")),
    ("minor", _("Minor")),
]

ORIENTATION_CHOICES = [
    ("upright", _("Upright")),
    ("reversed", _("Reversed")),
]

READING_TYPE_CHOICES = [
    ("single_card", _("Single Card")),
    ("three_card_spread", _("Three-Card Spread")),
    ("celtic_cross_spread", _("Celtic Cross Spread")),
    ("love_spread", _("Love Spread")),
    ("career_path_spread", _("Career Path Spread")),
    ("relationship_spread", _("Relationship Spread")),
    ("horseshoe_spread", _("Horseshoe Spread")),
]
