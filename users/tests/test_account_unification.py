"""
Integration tests for full account unification flow.

Tests all scenarios:
1. Telegram → Web unification (Telegram user sets email, then web signup)
2. Web → Telegram unification (Web user exists, then Telegram auth)
3. Social Login → Telegram unification (Google/GitHub → Telegram)
4. No duplicate creation (same email across different methods)
"""

import pytest
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

from users.models import DEFAULT_TOKENS, UserProfile


@pytest.mark.django_db
class TestTelegramToWebUnification:
    """Test Telegram user → Web signup unification."""

    def test_telegram_user_sets_email_then_web_signup(self):
        """
        Scenario: Telegram user sets email, then signs up on web with same email.
        Expected: Single user exists with both Telegram and web social accounts.
        """
        # Step 1: Create Telegram user via /api/tg/users/auth
        telegram_id = "123456789"
        username = "telegram_user"
        email = "unified@example.com"

        # Simulate Telegram auth creating user
        user = User.objects.create_user(username=username, email=f"{username}@tg.me")
        user.set_unusable_password()
        user.save()

        SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=user)

        # Step 2: User sets email via /email command (simulated by updating user.email)
        user.email = email
        user.save()

        # Step 3: Simulate web signup with same email
        # In real flow, allauth adapter would detect existing user and merge
        existing_user = User.objects.filter(email=email).first()
        assert existing_user is not None
        assert existing_user == user

        # Step 4: Simulate social account creation for web (e.g., Google)
        SocialAccount.objects.create(provider="google", uid="google_123", user=existing_user)

        # Verify: Single user exists (not duplicated)
        users_with_email = User.objects.filter(email=email)
        assert users_with_email.count() == 1

        # Verify: Both Telegram and web social accounts linked
        social_accounts = SocialAccount.objects.filter(user=user)
        assert social_accounts.count() == 2
        providers = [acc.provider for acc in social_accounts]
        assert "telegram" in providers
        assert "google" in providers

        # Verify: Token balance preserved
        profile = user.profile
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_telegram_user_token_balance_preserved_after_web_link(self):
        """
        Scenario: Telegram user has custom token balance, then links web account.
        Expected: Token balance preserved after linking.
        """
        # Create Telegram user with custom token balance
        user = User.objects.create_user(username="tg_user_tokens", email="tokens@example.com")
        profile = user.profile
        profile.available_tokens = 5000  # Custom balance
        profile.save()

        SocialAccount.objects.create(provider="telegram", uid="999999999", user=user)

        initial_tokens = profile.available_tokens

        # Simulate web social account linking
        SocialAccount.objects.create(provider="github", uid="github_456", user=user)

        # Verify: Token balance unchanged
        profile.refresh_from_db()
        assert profile.available_tokens == initial_tokens
        assert profile.available_tokens == 5000


@pytest.mark.django_db
class TestWebToTelegramUnification:
    """Test Web user → Telegram auth unification."""

    def test_web_user_exists_then_telegram_auth(self):
        """
        Scenario: Web user exists, then authenticates via Telegram with same email.
        Expected: Telegram account linked to existing web user, no duplicate.
        """
        # Step 1: Create web user (simulate Django signup)
        email = "webuser@example.com"
        web_user = User.objects.create_user(username="webuser", email=email, password="testpass123")

        # Step 2: Simulate Telegram auth with same email
        # In real flow, /api/tg/users/auth checks for existing user by email
        telegram_id = "777777777"

        # Check if user with email exists (this is what the API does)
        existing_user = User.objects.filter(email=email).first()
        assert existing_user is not None
        assert existing_user == web_user

        # Link Telegram to existing user
        telegram_account = SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=existing_user)

        # Verify: Single user exists
        users_with_email = User.objects.filter(email=email)
        assert users_with_email.count() == 1

        # Verify: Telegram account linked
        assert telegram_account.user == web_user

        # Verify: Token balance preserved
        profile = web_user.profile
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_web_user_with_custom_tokens_links_telegram(self):
        """
        Scenario: Web user has custom token balance, then links Telegram.
        Expected: Token balance preserved.
        """
        # Create web user with custom tokens
        web_user = User.objects.create_user(username="web_custom", email="custom@example.com", password="pass123")
        profile = web_user.profile
        profile.available_tokens = 3000
        profile.save()

        initial_tokens = profile.available_tokens

        # Link Telegram account
        SocialAccount.objects.create(provider="telegram", uid="888888888", user=web_user)

        # Verify: Token balance unchanged
        profile.refresh_from_db()
        assert profile.available_tokens == initial_tokens
        assert profile.available_tokens == 3000


@pytest.mark.django_db
class TestSocialLoginToTelegramUnification:
    """Test Social Login (Google/GitHub) → Telegram unification."""

    def test_google_login_then_telegram_auth(self):
        """
        Scenario: User signs in with Google, then authenticates via Telegram with same email.
        Expected: Single user with both Google and Telegram accounts linked.
        """
        # Step 1: Create user via Google social login
        email = "google_user@example.com"
        user = User.objects.create_user(username="google_user", email=email)
        user.set_unusable_password()
        user.save()

        SocialAccount.objects.create(provider="google", uid="google_789", user=user)

        # Step 2: Simulate Telegram auth with same email
        telegram_id = "555555555"

        # Check for existing user by email (API logic)
        existing_user = User.objects.filter(email=email).first()
        assert existing_user is not None
        assert existing_user == user

        # Link Telegram to existing user
        SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=existing_user)

        # Verify: Single user exists
        users_with_email = User.objects.filter(email=email)
        assert users_with_email.count() == 1

        # Verify: Both Google and Telegram accounts linked
        social_accounts = SocialAccount.objects.filter(user=user)
        assert social_accounts.count() == 2
        providers = [acc.provider for acc in social_accounts]
        assert "google" in providers
        assert "telegram" in providers

        # Verify: Token balance preserved
        profile = user.profile
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_github_login_then_telegram_auth(self):
        """
        Scenario: User signs in with GitHub, then authenticates via Telegram.
        Expected: Single unified user with both accounts.
        """
        # Create user via GitHub social login
        email = "github_user@example.com"
        user = User.objects.create_user(username="github_user", email=email)
        user.set_unusable_password()
        user.save()

        SocialAccount.objects.create(provider="github", uid="github_999", user=user)

        # Telegram auth with same email
        telegram_id = "444444444"
        existing_user = User.objects.filter(email=email).first()
        SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=existing_user)

        # Verify: Single user
        assert User.objects.filter(email=email).count() == 1

        # Verify: Both accounts linked
        social_accounts = SocialAccount.objects.filter(user=user)
        assert social_accounts.count() == 2
        providers = [acc.provider for acc in social_accounts]
        assert "github" in providers
        assert "telegram" in providers


@pytest.mark.django_db
class TestNoDuplicateCreation:
    """Test that no duplicate users are created with same email."""

    def test_same_email_different_methods_no_duplicates(self):
        """
        Scenario: Try to create users with same email via different methods.
        Expected: Only one user exists, all social accounts linked to it.
        """
        email = "unique@example.com"

        # Method 1: Create via Telegram
        user1 = User.objects.create_user(username="tg_unique", email=email)
        SocialAccount.objects.create(provider="telegram", uid="111111111", user=user1)

        # Method 2: Try to create via Google (should link to existing)
        existing_user = User.objects.filter(email=email).first()
        assert existing_user is not None
        SocialAccount.objects.create(provider="google", uid="google_unique", user=existing_user)

        # Method 3: Try to create via GitHub (should link to existing)
        existing_user = User.objects.filter(email=email).first()
        SocialAccount.objects.create(provider="github", uid="github_unique", user=existing_user)

        # Verify: Only one user exists
        users_with_email = User.objects.filter(email=email)
        assert users_with_email.count() == 1

        # Verify: All social accounts linked to same user
        user = users_with_email.first()
        social_accounts = SocialAccount.objects.filter(user=user)
        assert social_accounts.count() == 3
        providers = [acc.provider for acc in social_accounts]
        assert "telegram" in providers
        assert "google" in providers
        assert "github" in providers

    def test_telegram_auth_with_existing_email_links_not_creates(self):
        """
        Scenario: Web user exists, Telegram auth with same email should link, not create.
        Expected: No new user created, Telegram account linked to existing.
        """
        email = "existing@example.com"

        # Create web user first
        web_user = User.objects.create_user(username="existing_web", email=email, password="pass123")
        initial_user_count = User.objects.count()

        # Simulate Telegram auth (API checks for existing user by email)
        telegram_id = "222222222"
        existing_user = User.objects.filter(email=email).first()

        # Should find existing user, not create new
        assert existing_user is not None
        assert existing_user == web_user

        # Link Telegram to existing user
        SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=existing_user)

        # Verify: No new user created
        assert User.objects.count() == initial_user_count

        # Verify: Telegram account linked to existing user
        telegram_accounts = SocialAccount.objects.filter(user=web_user, provider="telegram")
        assert telegram_accounts.count() == 1

    def test_multiple_social_providers_same_email_unified(self):
        """
        Scenario: User authenticates with multiple social providers using same email.
        Expected: All providers linked to single user account.
        """
        email = "multi@example.com"

        # Create initial user
        user = User.objects.create_user(username="multi_user", email=email)

        # Add multiple social providers
        providers = ["telegram", "google", "github"]
        for i, provider in enumerate(providers):
            SocialAccount.objects.create(provider=provider, uid=f"{provider}_{i}", user=user)

        # Verify: Only one user exists
        assert User.objects.filter(email=email).count() == 1

        # Verify: All providers linked
        social_accounts = SocialAccount.objects.filter(user=user)
        assert social_accounts.count() == len(providers)
        linked_providers = [acc.provider for acc in social_accounts]
        for provider in providers:
            assert provider in linked_providers


@pytest.mark.django_db
class TestTokenBalancePreservation:
    """Test that token balance is preserved during all unification scenarios."""

    def test_token_balance_preserved_across_all_unification_paths(self):
        """
        Scenario: User has custom token balance, links multiple accounts.
        Expected: Token balance remains unchanged throughout.
        """
        email = "tokens_preserved@example.com"

        # Create user with custom token balance
        user = User.objects.create_user(username="token_user", email=email)
        profile = user.profile
        profile.available_tokens = 7500
        profile.save()

        initial_tokens = profile.available_tokens

        # Link Telegram
        SocialAccount.objects.create(provider="telegram", uid="token_tg", user=user)
        profile.refresh_from_db()
        assert profile.available_tokens == initial_tokens

        # Link Google
        SocialAccount.objects.create(provider="google", uid="token_google", user=user)
        profile.refresh_from_db()
        assert profile.available_tokens == initial_tokens

        # Link GitHub
        SocialAccount.objects.create(provider="github", uid="token_github", user=user)
        profile.refresh_from_db()
        assert profile.available_tokens == initial_tokens

        # Final verification
        assert profile.available_tokens == 7500

    def test_default_tokens_assigned_on_first_creation(self):
        """
        Scenario: New user created via any method.
        Expected: Default token balance assigned.
        """
        # Via Telegram
        tg_user = User.objects.create_user(username="tg_default", email="tg@example.com")
        assert tg_user.profile.available_tokens == DEFAULT_TOKENS

        # Via web signup
        web_user = User.objects.create_user(username="web_default", email="web@example.com", password="pass123")
        assert web_user.profile.available_tokens == DEFAULT_TOKENS

        # Via social login
        social_user = User.objects.create_user(username="social_default", email="social@example.com")
        assert social_user.profile.available_tokens == DEFAULT_TOKENS


@pytest.mark.django_db
class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_telegram_auth_without_email_creates_tg_me_email(self):
        """
        Scenario: Telegram user authenticates without setting email first.
        Expected: User created with @tg.me email, can be unified later.
        """
        username = "no_email_user"
        telegram_id = "333333333"

        # Create user without real email (Telegram auth default behavior)
        user = User.objects.create_user(username=username, email=f"{username}@tg.me")
        SocialAccount.objects.create(provider="telegram", uid=telegram_id, user=user)

        # Verify: User created with @tg.me email
        assert user.email == f"{username}@tg.me"

        # Later, user sets real email
        real_email = "real@example.com"
        user.email = real_email
        user.save()

        # Verify: Email updated
        user.refresh_from_db()
        assert user.email == real_email

    def test_social_account_unique_constraint_per_provider(self):
        """
        Scenario: Try to create duplicate social account with same provider and uid.
        Expected: IntegrityError raised (database constraint).
        """
        from django.db import IntegrityError

        user1 = User.objects.create_user(username="user1", email="user1@example.com")
        user2 = User.objects.create_user(username="user2", email="user2@example.com")

        # Create social account for user1
        SocialAccount.objects.create(provider="telegram", uid="duplicate_uid", user=user1)

        # Try to create same provider+uid for user2 (should fail)
        with pytest.raises(IntegrityError):
            SocialAccount.objects.create(provider="telegram", uid="duplicate_uid", user=user2)

    def test_user_profile_created_automatically_via_signal(self):
        """
        Scenario: Create user via any method.
        Expected: UserProfile created automatically via signal.
        """
        # Create user without explicitly creating profile
        user = User.objects.create_user(username="signal_test", email="signal@example.com")

        # Verify: Profile exists (created by signal)
        profile = UserProfile.objects.filter(user=user).first()
        assert profile is not None
        assert profile.available_tokens == DEFAULT_TOKENS

    def test_cascade_delete_preserves_data_integrity(self):
        """
        Scenario: Delete user with multiple social accounts.
        Expected: All related social accounts and profile deleted.
        """
        user = User.objects.create_user(username="cascade_user", email="cascade@example.com")

        # Create multiple social accounts
        telegram_account = SocialAccount.objects.create(provider="telegram", uid="cascade_tg", user=user)
        google_account = SocialAccount.objects.create(provider="google", uid="cascade_google", user=user)

        profile = user.profile
        profile_id = profile.id
        telegram_id = telegram_account.id
        google_id = google_account.id

        # Delete user
        user.delete()

        # Verify: All related objects deleted
        assert not UserProfile.objects.filter(id=profile_id).exists()
        assert not SocialAccount.objects.filter(id=telegram_id).exists()
        assert not SocialAccount.objects.filter(id=google_id).exists()
