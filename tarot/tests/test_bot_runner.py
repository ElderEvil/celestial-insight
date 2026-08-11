"""
Tests for Telegram bot runner management command.

Covers:
- Command initialization and arguments
- Update handling for different commands
- API call mocking
- Error handling
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tarot.management.commands.run_bot import Command


@pytest.fixture
def mock_context():
    """Create a mock context with bot_data."""
    context = MagicMock()
    context.bot_data = {"api_url": "http://localhost:8000"}
    return context


@pytest.fixture
def mock_update():
    """Create a mock update object."""
    update = MagicMock()
    message = MagicMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.reply_text = AsyncMock()
    message.reply_photo = AsyncMock()
    update.message = message
    update.callback_query = None
    return update


@pytest.fixture
def mock_callback_query():
    """Create a mock callback query."""
    query = MagicMock()
    query.data = "test_data"
    query.message = MagicMock()
    query.message.edit_text = AsyncMock()
    query.message.edit_caption = AsyncMock()
    query.answer = AsyncMock()
    return query


class TestCommandInitialization:
    """Tests for command initialization."""

    def test_command_initialization(self):
        """Test Command can be instantiated."""
        cmd = Command()
        # Verify it's a Django management command
        assert hasattr(cmd, "handle")
        assert hasattr(cmd, "add_arguments")

    def test_command_arguments(self):
        """Test Command accepts expected arguments."""
        cmd = Command()
        parser = MagicMock()
        cmd.add_arguments(parser)
        parser.add_argument.assert_called()


class TestHelpCommand:
    """Tests for /help command."""

    @pytest.mark.asyncio
    async def test_help_shows_commands(self, mock_update, mock_context):
        """Test /help command shows help text."""
        cmd = Command()
        await cmd.show_help(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        text = call_args[0][0]
        assert "/start" in text
        assert "/help" in text
        assert "/mentors" in text
        assert "/reading" in text


class TestStartCommand:
    """Tests for /start command."""

    @pytest.mark.asyncio
    async def test_start_welcomes_user(self, mock_update, mock_context):
        """Test /start command welcomes user."""
        cmd = Command()

        with patch.object(cmd, "post_request", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = {"ok": True, "result": {"id": 1}}

            await cmd.start(mock_update, mock_context)

            mock_update.message.reply_text.assert_called()
            # Should call send_menu which calls reply_text
            assert mock_update.message.reply_text.call_count >= 1


class TestMentorsCommand:
    """Tests for /mentors command."""

    @pytest.mark.asyncio
    async def test_mentors_lists_available(self, mock_update, mock_context):
        """Test /mentors shows available mentors."""
        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "results": [{"name": "Test Mentor", "mystical_level": 1, "specialization": "General"}]
            }

            await cmd.list_mentors(mock_update, mock_context)

            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args
            assert "Test Mentor" in call_args[0][0]


class TestUserInfoCommand:
    """Tests for /me command."""

    @pytest.mark.asyncio
    async def test_me_shows_profile(self, mock_update, mock_context):
        """Test /me shows user profile."""
        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"ok": True, "result": {"available_tokens": 100}}

            await cmd.get_user_info(mock_update, mock_context)

            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "100" in call_args[0][0]


class TestCardGrouping:
    """Tests for card grouping utility."""

    def test_group_cards_by_suit(self):
        """Test grouping cards by suit."""
        cmd = Command()
        cards = [
            {"name": "Ace of Wands", "slug": "ace-wands"},
            {"name": "Ace of Cups", "slug": "ace-cups"},
            {"name": "The Fool", "slug": "the-fool"},
        ]

        grouped = cmd.group_cards_by_suit(cards)

        assert "Wands" in grouped
        assert "Cups" in grouped
        assert "Major Arcana" in grouped
        assert len(grouped["Wands"]) == 1
        assert len(grouped["Cups"]) == 1
        assert len(grouped["Major Arcana"]) == 1


class TestCardSuitsCommand:
    """Tests for /cards command."""

    @pytest.mark.asyncio
    async def test_cards_shows_suits(self, mock_update, mock_context):
        """Test /cards shows suits as inline buttons."""
        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "results": [
                    {"name": "Ace of Wands", "slug": "ace-wands"},
                    {"name": "Ace of Cups", "slug": "ace-cups"},
                ]
            }

            await cmd.list_tarot_suits(mock_update, mock_context)

            mock_update.message.reply_text.assert_called_once()


class TestCallbackHandlers:
    """Tests for callback query handlers."""

    @pytest.mark.asyncio
    async def test_list_suit_cards(self, mock_callback_query, mock_context):
        """Test list_suit_cards handles callback."""
        update = MagicMock()
        update.callback_query = mock_callback_query
        mock_callback_query.data = "suit_Wands"

        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "results": [
                    {"name": "Ace of Wands", "slug": "ace-wands"},
                ]
            }

            await cmd.list_suit_cards(update, mock_context)

            # Verify the message was edited (main assertion)
            mock_callback_query.message.edit_text.assert_called()

    @pytest.mark.asyncio
    async def test_show_card_details(self, mock_callback_query, mock_context):
        """Test show_card_details handles callback."""
        update = MagicMock()
        update.callback_query = mock_callback_query
        mock_callback_query.data = "card_the-fool"

        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "name": "The Fool",
                "suit": {"name": "Major Arcana"},
                "number": 0,
                "keywords": "New beginnings, innocence",
                "description": "The Fool represents new beginnings.",
            }

            await cmd.show_card_details(update, mock_context)

            mock_callback_query.message.edit_text.assert_called_once()


class TestReadingCommand:
    """Tests for /reading command."""

    @pytest.mark.asyncio
    async def test_reading_requires_auth(self, mock_update, mock_context):
        """Test /reading requires authentication."""
        cmd = Command()

        with patch.object(cmd, "post_request", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = None  # Auth failed

            await cmd.create_reading(mock_update, mock_context)

            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args
            assert "Authentication" in call_args[0][0] or "failed" in call_args[0][0].lower()


class TestHistoryCommand:
    """Tests for /history command."""

    @pytest.mark.asyncio
    async def test_history_shows_readings(self, mock_update, mock_context):
        """Test /history shows reading history."""
        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "results": [
                    {"reading_type": "single_card", "date": "2024-01-01T12:00:00Z", "question": "Test?"},
                ]
            }

            await cmd.list_reading_history(mock_update, mock_context)

            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "Tarot Readings" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_history_empty_state(self, mock_update, mock_context):
        """Test /history shows message when no readings."""
        cmd = Command()

        with patch.object(cmd, "fetch_data", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {"results": []}

            await cmd.list_reading_history(mock_update, mock_context)

            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "No past readings" in call_args[0][0]


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_error_handler_logs(self, mock_update):
        """Test error handler logs errors."""
        cmd = Command()
        context = MagicMock()
        context.error = Exception("Test error")

        # Should not raise
        await cmd.error_handler(mock_update, context)


class TestAPIHelpers:
    """Tests for API helper methods."""

    @pytest.mark.asyncio
    async def test_fetch_data_failure(self):
        """Test fetch_data returns None on failure."""
        cmd = Command()

        with patch("tarot.management.commands.run_bot.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Server error"}

            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await cmd.fetch_data("http://localhost:8000", "/api/test")

            assert result is None

    @pytest.mark.asyncio
    async def test_post_request_success(self):
        """Test post_request returns data on success."""
        cmd = Command()

        with patch("tarot.management.commands.run_bot.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}

            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            result = await cmd.post_request("http://localhost:8000", "/api/test", {"key": "value"})

            assert result == {"ok": True}
