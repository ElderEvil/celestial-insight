#!/usr/bin/env python
"""
Standalone Telegram bot script for Celestial Insight.

This script runs the Telegram bot as an independent service, communicating
with the Django application via HTTP API calls.

Usage:
    python bot.py

Commands supported:
    /start - Register user and show help
    /help - Show available commands
    /mentors - List available mentors
    /me - Show user profile and token balance
    /cards - Browse tarot cards by suit
    /reading - Create a tarot reading
    /history - Show reading history

Environment variables:
    TELEGRAM_BOT_SECRET - Telegram bot token (required)
    API_URL - Django API URL (default: http://localhost:8000)
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)

HTTP_OK = 200
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


class BotHandlers:
    """Handler mixin for Telegram bot commands."""

    def __init__(self, api_url: str):
        self.api_url = api_url

    async def fetch_data(self, endpoint: str) -> dict[str, Any] | None:
        """Fetch data from Django-Ninja API with error handling and retries."""
        import httpx

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.api_url}{endpoint}")
                    if response.status_code == HTTP_OK:
                        return response.json()
                    elif response.status_code == 401:
                        logger.warning("Unauthorized access to %s", endpoint)
                        return None
                    elif response.status_code == 404:
                        logger.warning("Endpoint not found: %s", endpoint)
                        return None
                    elif response.status_code == 422:
                        logger.error("Validation error for %s: %s", endpoint, response.text)
                        return None
                    elif response.status_code >= 500:
                        logger.error("Server error %s for %s", response.status_code, endpoint)
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                            continue
                        return None
                    else:
                        logger.error("API error %s for %s", response.status_code, endpoint)
                        return None
            except httpx.TimeoutException:
                logger.error("Timeout fetching %s (attempt %d/%d)", endpoint, attempt + 1, MAX_RETRIES)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return None
            except httpx.ConnectError as e:
                logger.error("Connection error fetching %s (attempt %d/%d): %s", endpoint, attempt + 1, MAX_RETRIES, e)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error("Unexpected error fetching %s: %s", endpoint, e)
                return None
        return None

    async def post_request(self, endpoint: str, data: dict) -> dict[str, Any] | None:
        """Send POST request to API with error handling and retries."""
        import httpx

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(f"{self.api_url}{endpoint}", json=data)
                    if response.status_code == HTTP_OK:
                        return response.json()
                    elif response.status_code == 401:
                        logger.warning("Unauthorized POST to %s", endpoint)
                        return None
                    elif response.status_code == 404:
                        logger.warning("Endpoint not found: %s", endpoint)
                        return None
                    elif response.status_code == 422:
                        logger.error("Validation error for %s: %s", endpoint, response.text)
                        return None
                    elif response.status_code >= 500:
                        logger.error("Server error %s for %s", response.status_code, endpoint)
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                            continue
                        return None
                    else:
                        logger.error("API error %s for %s", response.status_code, endpoint)
                        return None
            except httpx.TimeoutException:
                logger.error("Timeout posting to %s (attempt %d/%d)", endpoint, attempt + 1, MAX_RETRIES)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return None
            except httpx.ConnectError as e:
                logger.error(
                    "Connection error posting to %s (attempt %d/%d): %s", endpoint, attempt + 1, MAX_RETRIES, e
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error("Unexpected error posting to %s: %s", endpoint, e)
                return None
        return None

    async def send_menu(self, update, keyboard=None):
        """Send main menu with buttons."""
        if keyboard is None:
            keyboard = ReplyKeyboardMarkup(
                [
                    [KeyboardButton("/mentors"), KeyboardButton("/me")],
                    [KeyboardButton("/cards"), KeyboardButton("/start")],
                    [KeyboardButton("/reading"), KeyboardButton("/history")],
                ],
                resize_keyboard=True,
            )
        await update.message.reply_text("📜 Choose an option:", reply_markup=keyboard)

    async def start(self, update, context):
        """Handles /start command."""
        user = update.message.from_user
        username = user.username or f"user_{user.id}"

        # Attempt login first
        user_data = await self.post_request("/api/tg/users/auth", {"telegram_id": user.id, "username": username})

        if user_data and user_data.get("access"):
            await update.message.reply_text(f"🔑 Welcome back, {username}!")
        else:
            await update.message.reply_text(f"👋 Welcome, {username}! Use /help to see commands.")

        await self.send_menu(update)

    async def show_help(self, update, context):
        """Show help message."""
        text = """
📜 <b>Available Commands</b>

/start - Register and get started
/help - Show this help message
/mentors - List all available mentors
/me - Show your profile and token balance
/cards - Browse tarot cards by suit
/reading - Create a tarot reading
/history - View your reading history
        """
        await update.message.reply_text(text, parse_mode="HTML")

    async def list_mentors(self, update, context):
        """Fetch and display mentors."""
        mentors = await self.fetch_data("/api/mentors/")

        if not mentors:
            await update.message.reply_text("⚠️ No mentors found.")
            return

        # API returns list directly, not dict with "results"
        mentor_list: list[dict[str, Any]] = mentors if isinstance(mentors, list) else []
        if not mentor_list:
            await update.message.reply_text("⚠️ No mentors found.")
            return

        for mentor in mentor_list:
            level = mentor.get("mystical_level", 1)
            spec = mentor.get("specialization", "General")
            text = f"*{mentor['name']}*\n🔢 Level: {level}\n🎭 Specialization: {spec}"
            await update.message.reply_text(text, parse_mode="Markdown")

    async def get_user_info(self, update, context):
        """Fetch and display user details."""
        user = update.message.from_user

        user_data = await self.fetch_data(f"/api/tg/users/me?telegram_id={user.id}")

        # API returns flat JSON directly, not wrapped in {"ok": true, "result": {...}}
        if user_data and user_data.get("is_authenticated"):
            profile = user_data.get("profile", {})
            username = user.username or user_data.get("username", "N/A")
            tokens = profile.get("available_tokens", 0)
            text = f"👤 *Your Profile*\n🔹 Username: {username}\n🔢 Tokens: {tokens}"
            await update.message.reply_text(text, parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ No user found. Try /start.")

    def group_cards_by_suit(self, cards, suits=None):
        """Group tarot cards by suit."""
        if suits is None:
            suits = ["Wands", "Cups", "Swords", "Pentacles", "Major Arcana"]
        grouped = {suit: [] for suit in suits}

        for card in cards:
            found_suit = next((suit for suit in suits if suit in card.get("name", "")), "Major Arcana")
            grouped[found_suit].append({"name": card.get("name"), "slug": card.get("slug")})

        return grouped

    async def list_tarot_suits(self, update, context):
        """Display tarot suits as inline buttons."""
        cards = await self.fetch_data("/api/tarot/cards")

        if not cards:
            await update.message.reply_text("⚠️ No tarot cards found.")
            return

        # API returns list directly, not dict with "results"
        card_list = cards if isinstance(cards, list) else cards.get("results", [])
        grouped_cards = self.group_cards_by_suit(card_list)
        buttons = [
            [InlineKeyboardButton(f"📜 {suit}", callback_data=f"suit_{suit.replace(' ', '_')}")]
            for suit in grouped_cards
        ]
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("🔮 *Choose a Tarot Suit:*", reply_markup=markup, parse_mode="Markdown")

    async def list_suit_cards(self, update, context):
        """Display all tarot cards for the selected suit."""
        query = update.callback_query
        suit_name = query.data.replace("suit_", "").replace("_", " ")

        cards = await self.fetch_data("/api/tarot/cards")
        # API returns list directly, not dict with "results"
        card_list = cards if isinstance(cards, list) else cards.get("results", [])
        grouped_cards = self.group_cards_by_suit(card_list)

        if suit_name not in grouped_cards:
            await query.answer("Suit not found!", show_alert=True)
            return

        buttons = [
            [InlineKeyboardButton(f"🃏 {card['name']}", callback_data=f"card_{card['slug']}")]
            for card in grouped_cards[suit_name]
        ]
        buttons.append([InlineKeyboardButton("⬅ Back to Suits", callback_data="back_to_suits")])
        markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(f"📜 *{suit_name} Cards:*", reply_markup=markup, parse_mode="Markdown")

    async def show_card_details(self, update, context):
        """Display detailed tarot card information."""
        query = update.callback_query
        slug = query.data.replace("card_", "")

        card = await self.fetch_data(f"/api/tarot/cards/{slug}")

        if not card:
            await query.answer("Card not found!", show_alert=True)
            return

        text = (
            f"🃏 *{card.get('name')}*\n"
            f"📜 *Suit:* {card.get('suit', {}).get('name', 'Unknown')}\n"
            f"🔢 *Number:* {card.get('number', 'N/A')}\n"
            f"🔮 *Keywords:* {card.get('keywords', 'N/A')}\n"
            f"📝 *Description:* {card.get('description', 'N/A')}"
        )
        buttons = [
            [
                InlineKeyboardButton(
                    "⬅ Back to Suit",
                    callback_data=f"suit_{card.get('suit', {}).get('name', 'Major_Arcana').replace(' ', '_')}",
                )
            ]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")

    async def back_to_suits(self, update, context):
        """Return to tarot suits selection."""
        await self.list_tarot_suits(update, context)

    async def create_reading(self, update, context):
        """Create a tarot reading for the user."""
        import httpx

        user = update.message.from_user

        auth = await self.post_request(
            "/api/tg/users/auth", {"telegram_id": user.id, "username": user.username or f"user_{user.id}"}
        )

        if not auth or not auth.get("ok"):
            await update.message.reply_text("⚠️ Authentication failed. Try /start first.")
            return

        access_token = auth.get("access")

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    headers = {"Authorization": f"Bearer {access_token}"}
                    response = await client.post(
                        f"{self.api_url}/api/tg/tarot/readings",
                        data={"question": "What guidance do you have for me?", "mentor_id": 1},
                        headers=headers,
                    )

                if response.status_code == HTTP_OK:
                    result = response.json()
                    # API returns flat JSON: ReadingSchema or error string
                    if isinstance(result, dict):
                        insight = result.get("celestial_insight", "The cards have spoken.")
                        text = f"🔮 *Your Reading*\n\n{insight}"
                        await update.message.reply_text(text, parse_mode="Markdown")
                    else:
                        await update.message.reply_text(f"⚠️ {result}")
                elif response.status_code == 401:
                    logger.warning("Unauthorized reading creation for user %s", user.id)
                    await update.message.reply_text("⚠️ Authentication failed. Try /start first.")
                elif response.status_code == 422:
                    logger.error("Validation error creating reading: %s", response.text)
                    await update.message.reply_text("⚠️ Invalid request. Please try again.")
                elif response.status_code >= 500:
                    logger.error("Server error %s creating reading", response.status_code)
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    await update.message.reply_text("⚠️ Server error. Please try again later.")
                else:
                    logger.error("API error %s creating reading", response.status_code)
                    await update.message.reply_text("⚠️ Error creating tarot reading.")
                return
            except httpx.TimeoutException:
                logger.error("Timeout creating reading (attempt %d/%d)", attempt + 1, MAX_RETRIES)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                await update.message.reply_text("⚠️ Unable to connect to server. Please try again.")
                return
            except httpx.ConnectError as e:
                logger.error("Connection error creating reading (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, e)
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                await update.message.reply_text("⚠️ Unable to connect to server. Please try again.")
                return
            except Exception as e:
                logger.error("Unexpected error creating reading: %s", e)
                await update.message.reply_text("⚠️ An unexpected error occurred. Please try again.")
                return

    async def list_reading_history(self, update, context):
        """Fetch and display the user's tarot reading history."""
        user = update.message.from_user

        readings = await self.fetch_data(f"/api/tg/tarot/readings/my?telegram_id={user.id}")

        if not readings or not readings.get("results"):
            await update.message.reply_text("⚠️ No past readings found.")
            return

        text = "📜 *Your Tarot Readings:*\n\n"
        for reading in readings.get("results", [])[:5]:  # Limit to 5 recent
            text += (
                f"🔮 *Type:* {reading.get('reading_type', 'Unknown').replace('_', ' ').title()}\n"
                f"📅 *Date:* {reading.get('date', 'N/A')[:10]}\n"
                f"❓ *Question:* {reading.get('question', 'N/A')}\n"
                f"-------\n"
            )

        await update.message.reply_text(text, parse_mode="Markdown")

    async def error_handler(self, update, context):
        """Handle errors globally."""
        logger.error("Exception while handling update %s: %s", update, context.error)


def main():
    """Main entry point - synchronous for python-telegram-bot v21+."""
    token = os.getenv("TELEGRAM_BOT_SECRET")
    api_url = os.getenv("API_URL", "http://localhost:8000")

    if not token:
        print("ERROR: TELEGRAM_BOT_SECRET environment variable is not set")
        print("Please set it before running the bot:")
        print("  export TELEGRAM_BOT_SECRET='your_bot_token'")
        return 1

    print(f"Starting Telegram bot with API URL: {api_url}")

    # Create application
    app = Application.builder().token(token).build()

    # Create handlers instance for method access
    handlers = BotHandlers(api_url)

    # Register command handlers
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.show_help))
    app.add_handler(CommandHandler("mentors", handlers.list_mentors))
    app.add_handler(CommandHandler("me", handlers.get_user_info))
    app.add_handler(CommandHandler("cards", handlers.list_tarot_suits))
    app.add_handler(CommandHandler("reading", handlers.create_reading))
    app.add_handler(CommandHandler("history", handlers.list_reading_history))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(handlers.list_suit_cards, pattern=r"suit_.*"))
    app.add_handler(CallbackQueryHandler(handlers.show_card_details, pattern=r"card_.*"))
    app.add_handler(CallbackQueryHandler(handlers.back_to_suits, pattern="back_to_suits"))

    # Error handling
    app.add_error_handler(handlers.error_handler)

    print("Bot is running. Press Ctrl+C to stop.")

    # python-telegram-bot v21+ handles event loop internally
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        print(f"Error running bot: {e}")
