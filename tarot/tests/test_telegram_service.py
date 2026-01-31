"""
Tests for Telegram Bot service wrapper.

Covers:
- TelegramBotClient initialization
- API request handling with mocked httpx
- send_reading_to_telegram helper function
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tarot.services.telegram_service import TelegramBotClient, send_reading_to_telegram


@pytest.mark.asyncio
async def test_telegram_bot_client_init():
    """Test TelegramBotClient initialization with token."""
    client = TelegramBotClient(bot_token="test-token-123")
    assert client.bot_token == "test-token-123"
    assert client.base_url == "https://api.telegram.org/bottest-token-123"


@pytest.mark.asyncio
async def test_telegram_bot_client_init_missing_token():
    """Test TelegramBotClient raises error when token is missing."""
    with pytest.raises(ValueError, match="TELEGRAM_BOT_SECRET environment variable is required"):
        with patch.dict("os.environ", {}, clear=True):
            TelegramBotClient(bot_token=None)


@pytest.mark.asyncio
async def test_get_me():
    """Test getMe API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "id": 123456789,
            "is_bot": True,
            "first_name": "test_bot",
            "username": "testbot",
        },
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    async with TelegramBotClient(bot_token="test-token-123") as client:
        client._client = mock_client
        result = await client.get_me()

    mock_client.post.assert_called_once_with(
        "https://api.telegram.org/bottest-token-123/getMe",
        json=None,
    )
    assert result["ok"] is True
    assert result["result"]["username"] == "testbot"


@pytest.mark.asyncio
async def test_send_message():
    """Test sendMessage API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 123,
            "chat": {"id": 123456789, "type": "private"},
            "text": "Hello!",
        },
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    async with TelegramBotClient(bot_token="test-token-123") as client:
        client._client = mock_client
        result = await client.send_message(chat_id=123456789, text="Hello!")

    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert "sendMessage" in call_args[0][0]
    assert call_args[1]["json"]["chat_id"] == 123456789
    assert call_args[1]["json"]["text"] == "Hello!"
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_message_with_keyboard():
    """Test sendMessage with inline keyboard."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": {"message_id": 123, "chat": {"id": 123456789}},
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    keyboard = {"inline_keyboard": [[{"text": "Start", "callback_data": "/start"}]]}
    async with TelegramBotClient(bot_token="test-token-123") as client:
        client._client = mock_client
        result = await client.send_message(chat_id=123456789, text="Choose:", reply_markup=keyboard)

    call_args = mock_client.post.call_args
    assert call_args[1]["json"]["reply_markup"] == keyboard
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_get_updates():
    """Test getUpdates API call."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 123456789,
                "message": {
                    "message_id": 123,
                    "chat": {"id": 123456789, "type": "private"},
                    "text": "/start",
                },
            },
        ],
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.aclose = AsyncMock()

    async with TelegramBotClient(bot_token="test-token-123") as client:
        client._client = mock_client
        result = await client.get_updates(offset=0, timeout=10)

    call_args = mock_client.post.call_args
    assert call_args[1]["json"]["offset"] == 0
    assert call_args[1]["json"]["timeout"] == 10
    assert len(result["result"]) == 1
    assert result["result"][0]["message"]["text"] == "/start"


@pytest.mark.asyncio
async def test_send_reading_to_telegram():
    """Test send_reading_to_telegram helper function."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 456}}

    mock_client = AsyncMock()
    mock_client.send_message = AsyncMock(return_value=mock_response.json.return_value)

    with patch("tarot.services.telegram_service.TelegramBotClient") as MockClient:
        mock_instance = MagicMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_client)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        MockClient.return_value = mock_instance

        result = await send_reading_to_telegram(
            chat_id=123456789,
            reading_text="The stars align in your favor.",
            question="Should I pursue this opportunity?",
            mentor_name="Celestial Guide",
        )

        mock_client.send_message.assert_called_once()
        call_args = mock_client.send_message.call_args
        assert call_args[1]["chat_id"] == 123456789
        assert "Celestial Guide" in call_args[1]["text"]
        assert "opportunity" in call_args[1]["text"]
        assert result["ok"] is True


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test TelegramBotClient can be used as async context manager."""
    # This test verifies the context manager is properly set up
    # The actual httpx.AsyncClient is mocked in other tests
    with patch("tarot.services.telegram_service.httpx.AsyncClient") as MockClient:
        mock_instance = AsyncMock()
        mock_client = AsyncMock()
        mock_instance.__aenter__.return_value = mock_client
        mock_instance.__aexit__.return_value = None
        MockClient.return_value = mock_instance

        # Verify context manager initializes properly
        async with TelegramBotClient(bot_token="test-token-123") as client:
            # Client should be properly initialized
            assert client.bot_token == "test-token-123"
            assert "telegram.org" in client.base_url

        # Verify httpx.AsyncClient was called with correct timeout
        MockClient.assert_called_once_with(timeout=30.0)
