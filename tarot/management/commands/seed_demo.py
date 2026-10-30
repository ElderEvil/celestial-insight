"""Seed the local public catalogue and mentor roster."""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load the tarot catalogue, authored card copy, and bundled mentor roster for local development."

    def handle(self, *args, **options):
        call_command("load_catalog")
        call_command("load_card_catalogue")
        call_command("loaddata", "mentors/fixtures/mentor_data.json")
        self.stdout.write(self.style.SUCCESS("Loaded local demo data."))
