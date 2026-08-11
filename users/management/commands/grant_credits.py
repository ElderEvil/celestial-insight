"""
Django management command to grant credits to a user.

Usage:
    python manage.py grant_credits --telegram_id 382660930 --amount 10000
"""

from allauth.socialaccount.models import SocialAccount
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Management command to grant credits to a user by telegram_id."""

    help = "Grant credits to a user by their Telegram ID"

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            "--telegram_id",
            type=int,
            required=True,
            help="Telegram user ID",
        )
        parser.add_argument(
            "--amount",
            type=int,
            required=True,
            help="Amount of credits to grant",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        telegram_id = options["telegram_id"]
        amount = options["amount"]

        # Find user by telegram_id via SocialAccount
        try:
            social_account = SocialAccount.objects.get(provider="telegram", uid=str(telegram_id))
        except SocialAccount.DoesNotExist as e:
            error_msg = f"User with Telegram ID {telegram_id} not found"
            raise CommandError(error_msg) from e

        user = social_account.user

        # Get or create user profile
        profile = user.profile

        # Store previous balance
        previous_balance = profile.available_tokens

        # Add credits
        profile.available_tokens += amount
        profile.save()

        # Display success message
        self.stdout.write(self.style.SUCCESS(f"✓ User found: {user.username}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Credits added: {amount}"))
        self.stdout.write(self.style.SUCCESS(f"✓ Previous balance: {previous_balance}"))
        self.stdout.write(self.style.SUCCESS(f"✓ New balance: {profile.available_tokens}"))
