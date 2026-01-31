"""
Tests for HTMX UI views - Dashboard and reading flows.

Covers:
- Dashboard authentication and content
- Create reading form rendering
- Session auth requirements
"""

from unittest.mock import AsyncMock, patch

import pytest

from tarot.models import Reading


@pytest.mark.django_db(transaction=True)
class TestDashboard:
    """Tests for dashboard view."""

    def test_dashboard_requires_authentication(self, client):
        """Anonymous user should be redirected to login."""
        response = client.get("/dashboard/")
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_dashboard_shows_token_balance(self, user, user_profile, client):
        """Authenticated user sees their token balance."""
        client.force_login(user)
        response = client.get("/dashboard/")
        assert response.status_code == 200
        assert str(user_profile.available_tokens) in response.content.decode()

    def test_dashboard_shows_reading_list(self, user, user_profile, mentor, client):
        """Dashboard shows user's recent readings."""
        client.force_login(user)

        # Create some readings
        Reading.objects.create(
            user=user,
            mentor=mentor,
            question="Test question 1",
            reading_type="single_card",
        )
        Reading.objects.create(
            user=user,
            mentor=mentor,
            question="Test question 2",
            reading_type="single_card",
        )

        response = client.get("/dashboard/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Test question 1" in content
        assert "Test question 2" in content

    def test_dashboard_shows_empty_state(self, user, user_profile, client):
        """Dashboard shows message when no readings exist."""
        client.force_login(user)
        response = client.get("/dashboard/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "No readings yet" in content

    def test_dashboard_has_create_reading_cta(self, user, user_profile, client):
        """Dashboard has a button to create new reading."""
        client.force_login(user)
        response = client.get("/dashboard/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Draw a Card" in content
        assert "/read/" in content


@pytest.mark.django_db(transaction=True)
class TestCreateReading:
    """Tests for create reading view."""

    def test_create_reading_requires_authentication(self, client):
        """Anonymous user should be redirected to login."""
        response = client.get("/read/")
        assert response.status_code == 302
        assert "/accounts/login" in response.url

    def test_create_reading_shows_mentors(self, user, user_profile, mentor, client):
        """Create reading page shows available mentors."""
        client.force_login(user)
        response = client.get("/read/")
        assert response.status_code == 200
        content = response.content.decode()
        assert mentor.name in content

    def test_create_reading_has_form(self, user, user_profile, client):
        """Create reading page has a form with required fields."""
        client.force_login(user)
        response = client.get("/read/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="mentor_id"' in content
        assert 'name="question"' in content
        assert "csrfmiddlewaretoken" in content

    def test_create_reading_has_htmx_attributes(self, user, user_profile, client):
        """Create reading form has HTMX attributes for dynamic updates."""
        client.force_login(user)
        response = client.get("/read/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'hx-post="/read/"' in content
        assert 'hx-target="#reading-result"' in content
        assert 'hx-swap="innerHTML"' in content

    @pytest.mark.asyncio
    @pytest.mark.django_db(transaction=True)
    async def test_create_reading_post_async_behavior(self, user, user_profile, mentor):
        """Regression test: POST /read/ works without sync_to_async misuse.

        Prevents bug where sync_to_async incorrectly wrapped an already-async
        function, causing RuntimeWarnings about coroutines.
        """
        from asgiref.sync import sync_to_async
        from django.test import AsyncClient

        client = AsyncClient()
        await sync_to_async(client.force_login)(user)

        with patch(
            "tarot.views.create_reading", new_callable=AsyncMock, return_value="Mocked error"
        ) as mock_create_reading:
            response = await client.post(
                "/read/",
                {
                    "mentor_id": mentor.id,
                    "question": "Test question for async behavior",
                },
            )

        assert response.status_code == 400
        assert "Mocked error" in response.content.decode()
        mock_create_reading.assert_called_once()
