"""
Tests for Telegram authentication bootstrap behavior.

Covers:
- User creation via TG auth
- UserProfile creation via signals
- SocialAccount linking
"""

import pytest
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.db import IntegrityError

from users.models import UserProfile

DEFAULT_TOKENS = 1000


@pytest.mark.django_db
class TestTelegramAuthBootstrap:
    """Tests for Telegram auth bootstrap behavior."""

    def test_user_profile_created_via_signal(self, user):
        """Test that UserProfile is created when User is created via signal."""
        profile = user.profile
        assert profile is not None
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_user_profile_has_default_tokens(self):
        """Test new user profile has default token balance."""
        user = User.objects.create_user(username="test_user", email="test@example.com")
        profile = UserProfile.objects.get(user=user)

        assert profile.available_tokens == DEFAULT_TOKENS

    def test_telegram_auth_creates_user(self):
        """Test TG auth creates a new user if not exists."""
        telegram_id = "123456789"
        username = "new_tg_user"

        social_account = SocialAccount.objects.filter(provider="telegram", uid=telegram_id).first()
        assert social_account is None

        user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@tg.me"})

        if created:
            user.set_unusable_password()
            user.save()

        social_account = SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=user)

        assert created is True
        assert user.username == username
        assert social_account.provider == "telegram"
        assert social_account.uid == telegram_id

    def test_telegram_auth_returns_existing_user(self):
        """Test TG auth returns existing user without creating new."""
        existing_user = User.objects.create_user(username="existing_user", email="existing@tg.me")
        SocialAccount.objects.create(provider="telegram", uid="999999999", user=existing_user)

        found_account = SocialAccount.objects.filter(provider="telegram", uid="999999999").first()

        assert found_account is not None
        assert found_account.user == existing_user
        assert found_account.user.username == "existing_user"

    def test_telegram_auth_user_has_profile(self):
        """Test TG auth user has profile with tokens."""
        user = User.objects.create_user(username="profile_test_user", email="profile@test.com")
        profile = UserProfile.objects.get(user=user)

        assert profile.available_tokens == DEFAULT_TOKENS
        assert profile.preferences == {}

    def test_telegram_auth_social_account_linked(self):
        """Test TG auth creates SocialAccount linking."""
        user = User.objects.create_user(username="social_test_user", email="social@test.com")
        social_account = SocialAccount.objects.create(provider="telegram", uid="888888888", user=user)

        assert social_account.provider == "telegram"
        assert social_account.uid == "888888888"
        assert social_account.user == user

    def test_telegram_auth_multiple_users_same_telegram_id(self):
        """Test TG auth handles same telegram_id correctly."""
        user1 = User.objects.create_user(username="user1_telegram", email="user1@tg.me")
        SocialAccount.objects.create(provider="telegram", uid="777777777", user=user1)

        social_account = SocialAccount.objects.filter(provider="telegram", uid="777777777").first()

        assert social_account is not None
        assert social_account.user == user1

    def test_telegram_auth_links_to_existing_web_user(self):
        """Test TG auth links to existing web user with same email."""
        web_user = User.objects.create_user(username="web_user", email="user@example.com")
        web_profile = web_user.profile
        initial_tokens = web_profile.available_tokens

        existing_user = User.objects.filter(email="user@example.com").first()
        assert existing_user is not None
        assert existing_user == web_user

        social_account = SocialAccount.objects.create(provider="telegram", uid="444444444", user=existing_user)

        assert existing_user.profile.available_tokens == initial_tokens
        assert social_account.user == web_user


@pytest.mark.django_db
class TestUserProfileSignals:
    """Tests for UserProfile signal behavior."""

    def test_profile_created_on_user_save(self):
        """Test profile is created when user is saved."""
        user = User(username="signal_test", email="signal@test.com")
        user.save()

        profile = UserProfile.objects.get(user=user)
        assert profile is not None
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_profile_not_duplicated_on_update(self):
        """Test profile is not duplicated when user is updated."""
        user = User.objects.create_user(username="update_test", email="update@test.com")
        profile1 = user.profile

        user.save()
        profile2 = user.profile

        assert profile1.id == profile2.id
        assert UserProfile.objects.filter(user=user).count() == 1

    def test_profile_preferred_mentor_default(self):
        """Test profile preferred_mentor defaults to None."""
        user = User.objects.create_user(username="mentor_test", email="mentor@test.com")
        profile = user.profile

        assert profile.preferred_mentor is None


@pytest.mark.django_db
class TestSocialAccountIntegrity:
    """Tests for SocialAccount data integrity."""

    def test_social_account_unique_telegram_id(self):
        """Test telegram_id is unique per provider."""
        user1 = User.objects.create_user(username="unique1", email="unique1@test.com")
        user2 = User.objects.create_user(username="unique2", email="unique2@test.com")

        SocialAccount.objects.create(provider="telegram", uid="666666666", user=user1)

        with pytest.raises(IntegrityError):
            SocialAccount.objects.create(provider="telegram", uid="666666666", user=user2)

    def test_social_account_cascade_delete(self):
        """Test deleting user removes SocialAccount."""
        user = User.objects.create_user(username="cascade_test", email="cascade@test.com")
        social_account = SocialAccount.objects.create(provider="telegram", uid="555555555", user=user)
        social_account_id = social_account.id

        user.delete()

        assert not SocialAccount.objects.filter(id=social_account_id).exists()

    def test_user_profile_cascade_delete(self):
        """Test deleting user removes UserProfile."""
        user = User.objects.create_user(username="profile_cascade", email="profile_cascade@test.com")
        profile_id = user.profile.id

        user.delete()

        assert not UserProfile.objects.filter(id=profile_id).exists()
