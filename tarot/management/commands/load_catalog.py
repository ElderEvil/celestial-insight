"""Load the public tarot catalogue without importing historical user readings."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.serializers import deserialize

from tarot.models import Card, Suit

TAROT_APP_DIR = Path(__file__).resolve().parents[2]

# The fixture is a structural catalogue (names, slugs, suits, numbers, images).
# Its copy fields are empty or scraped stubs, so they are never imported: the
# authored catalogue in tarot/content/cards.json is the only editorial source.
LEGACY_COPY_FIELDS = (
    "description",
    "description_uk",
    "upright_meaning",
    "upright_meaning_uk",
    "reversed_meaning",
    "reversed_meaning_uk",
    "keywords",
    "keywords_uk",
)


class Command(BaseCommand):
    help = "Load suits and cards from the bundled fixture."

    def handle(self, *args, **options):
        fixture_path = TAROT_APP_DIR / "fixtures" / "tarot_data.json"
        fixture_data = json.loads(fixture_path.read_text(encoding="utf-8"))
        catalogue_data = [entry for entry in fixture_data if entry["model"] in {"tarot.suit", "tarot.card"}]

        created = 0
        skipped = 0
        for deserialized_object in deserialize("json", json.dumps(catalogue_data)):
            model = type(deserialized_object.object)
            if model.objects.filter(pk=deserialized_object.object.pk).exists():
                skipped += 1
                continue
            if model is Card:
                for field in LEGACY_COPY_FIELDS:
                    setattr(deserialized_object.object, field, "")
            deserialized_object.save()
            created += 1

        message = (
            f"Loaded {Suit.objects.count()} suits and {Card.objects.count()} cards "
            f"({created} created, {skipped} already present)."
        )
        self.stdout.write(self.style.SUCCESS(message))
