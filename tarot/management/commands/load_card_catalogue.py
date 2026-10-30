"""Apply authored English and Ukrainian copy to the tarot card catalogue."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tarot.catalogue_content import CONTENT_FIELDS, CatalogueContentError, load_catalogue
from tarot.models import Card


def _apply_entry(card: Card, entry, *, overwrite: bool, counts: dict[str, int]) -> list[str]:
    """Set the copy fields on one card and return the names that changed."""
    updates = {}
    for field, ukrainian_field in CONTENT_FIELDS.items():
        for target, value in ((field, entry.english[field]), (ukrainian_field, entry.ukrainian[field])):
            current = getattr(card, target)
            if current == value:
                counts["unchanged"] += 1
            elif not current:
                setattr(card, target, value)
                updates[target] = value
                counts["filled"] += 1
            elif overwrite:
                setattr(card, target, value)
                updates[target] = value
                counts["overwritten"] += 1
            else:
                counts["unchanged"] += 1
    return list(updates)


class Command(BaseCommand):
    help = "Apply authored English and Ukrainian copy to the tarot card catalogue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace non-empty fields instead of preserving local edits.",
        )
        parser.add_argument(
            "--path",
            default=None,
            help="Read content from this JSON file instead of the bundled catalogue.",
        )

    def handle(self, *args, **options):
        try:
            content = load_catalogue(options["path"])
        except CatalogueContentError as error:
            raise CommandError(str(error)) from error

        cards_by_slug = self._cards_by_slug()
        missing = self._unknown_and_missing(content, cards_by_slug)

        counts = {"filled": 0, "overwritten": 0, "unchanged": 0}
        with transaction.atomic():
            for slug, entry in content.items():
                card = cards_by_slug[slug]
                updates = _apply_entry(card, entry, overwrite=options["overwrite"], counts=counts)
                if updates:
                    card.save(update_fields=updates)

        message = (
            f"Card copy: {counts['filled']} filled, {counts['overwritten']} overwritten, "
            f"{counts['unchanged']} unchanged."
        )
        self.stdout.write(self.style.SUCCESS(message))
        if missing:
            warning = f"{len(missing)} cards still have no authored entry: {', '.join(missing)}"
            self.stdout.write(self.style.WARNING(warning))

    def _cards_by_slug(self) -> dict[str, Card]:
        cards = list(Card.objects.all())
        cards_by_slug = {card.slug: card for card in cards}
        if len(cards_by_slug) != len(cards):
            message = "The card catalogue contains duplicate slugs; resolve them before loading copy."
            raise CommandError(message)
        return cards_by_slug

    def _unknown_and_missing(self, content, cards_by_slug: dict[str, Card]) -> list[str]:
        unknown = sorted(set(content) - set(cards_by_slug))
        if unknown:
            message = f"Unknown card slugs: {', '.join(unknown)}"
            raise CommandError(message)
        return sorted(set(cards_by_slug) - set(content))
