"""Load the public tarot catalogue without importing historical user readings."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.serializers import deserialize

from tarot.models import Card, Suit

TAROT_APP_DIR = Path(__file__).resolve().parents[2]


class Command(BaseCommand):
    help = "Load suits and cards from the bundled fixture."

    def handle(self, *args, **options):
        fixture_path = TAROT_APP_DIR / "fixtures" / "tarot_data.json"
        fixture_data = json.loads(fixture_path.read_text(encoding="utf-8"))
        catalogue_data = [entry for entry in fixture_data if entry["model"] in {"tarot.suit", "tarot.card"}]

        for deserialized_object in deserialize("json", json.dumps(catalogue_data)):
            deserialized_object.save()

        self.stdout.write(self.style.SUCCESS(f"Loaded {Suit.objects.count()} suits and {Card.objects.count()} cards."))
