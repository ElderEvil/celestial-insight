"""Seed the local public catalogue and mentor roster."""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from mentors.models import Mentor

LAUNCH_MENTOR_SLUGS = ("neutral-reader", "milo-starwhisk", "lolly-kiddie")


class Command(BaseCommand):
    help = "Load the tarot catalogue and bundled mentor roster for local development."

    def handle(self, *args, **options):
        call_command("load_catalog")
        Mentor.objects.exclude(slug__in=LAUNCH_MENTOR_SLUGS).update(is_active=False)
        call_command("loaddata", "mentors/fixtures/mentor_data.json")
        self.stdout.write(self.style.SUCCESS("Loaded local demo data."))
