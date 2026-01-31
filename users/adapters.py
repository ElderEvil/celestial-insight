"""
Custom allauth adapter for auto-merging Telegram and web accounts.

When a user signs up via Google/GitHub with an email that matches an existing
Telegram user, this adapter merges the accounts instead of creating a duplicate.
"""

import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


class AccountAdapter(DefaultAccountAdapter):
    """Custom adapter to merge Telegram and web social accounts."""

    def pre_social_login(self, request, sociallogin):
        """
        Merge accounts when social login email matches existing Telegram user.

        This method is called before a social login is processed. If the social
        login email matches an existing user with a Telegram account, we merge
        the accounts by linking the new social account to the existing user.

        Args:
            request: The HTTP request object
            sociallogin: The SocialLogin instance being processed
        """
        # Get email from social login
        email = sociallogin.account.extra_data.get("email")
        if not email:
            logger.debug("No email in social login data, skipping merge check")
            return

        # If user is already connected, skip merge logic
        if sociallogin.is_existing:
            logger.debug(f"Social login already connected for {email}")
            return

        # Check if user with this email already exists
        try:
            existing_user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.debug(f"No existing user found for email {email}")
            return
        except User.MultipleObjectsReturned:
            # If multiple users with same email, use the first one (shouldn't happen with proper constraints)
            existing_user = User.objects.filter(email=email).first()
            logger.warning(f"Multiple users found for email {email}, using first: {existing_user.id}")

        # Check if existing user has Telegram account
        telegram_accounts = SocialAccount.objects.filter(user=existing_user, provider="telegram")
        if not telegram_accounts.exists():
            logger.debug(f"Existing user {existing_user.username} has no Telegram account, skipping merge")
            return

        # Merge accounts: link social login to existing user
        logger.info(
            f"Merging {sociallogin.account.provider} account for {email} "
            f"with existing Telegram user {existing_user.username}"
        )

        # Connect the new social account to the existing user
        sociallogin.connect(request, existing_user)
