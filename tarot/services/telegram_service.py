"""
Telegram Bot API client wrapper for long-polling bot operations.

Provides async HTTP client for Telegram Bot API calls:
- send_message: Send text messages to chat
- get_me: Get bot info
- get_updates: Long polling for updates
"""

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class TelegramBotConfig:
    """Configuration for Telegram Bot."""

    bot_token: str
    api_url: str = "https://api.telegram.org/bot"


class TelegramBotClient:
    """Async client for Telegram Bot API."""

    def __init__(self, bot_token: str | None = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_SECRET")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_SECRET environment variable is required")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "TelegramBotClient":
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()

    async def _request(self, method: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a request to the Telegram Bot API."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        url = f"{self.base_url}/{method}"
        response = await self._client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    async def get_me(self) -> dict[str, Any]:
        """Get information about the bot."""
        return await self._request("getMe")

    async def send_message(
        self, chat_id: int, text: str, parse_mode: str = "HTML", reply_markup: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a text message to a chat."""
        data: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        return await self._request("sendMessage", data)

    async def get_updates(self, offset: int = 0, limit: int = 100, timeout: int = 0) -> dict[str, Any]:
        """Get updates using long polling."""
        data: dict[str, Any] = {
            "offset": offset,
            "limit": limit,
            "timeout": timeout,
        }
        return await self._request("getUpdates", data)


async def send_reading_to_telegram(chat_id: int, reading_text: str, question: str, mentor_name: str) -> dict[str, Any]:
    """
    Send a tarot reading result to a Telegram user.

    Args:
        chat_id: The Telegram chat ID to send to
        reading_text: The AI-generated reading text
        question: The user's question
        mentor_name: The name of the mentor who gave the reading

    Returns:
        The API response from Telegram
    """
    async with TelegramBotClient() as client:
        message = f"🔮 <b>{mentor_name}'s Insight</b>\n\n"
        message += f"<i>Question: {question}</i>\n\n"
        message += f"{reading_text}"

        return await client.send_message(chat_id=chat_id, text=message)
