# Tarot Journey Release Checklist

Last verified: 2026-09-15

## Clean environment

- [x] Apply every Django migration to a new SQLite database.
- [x] Run `uv run python manage.py seed_demo` twice.
- [x] Confirm both runs leave 5 suits, 78 cards, and 3 active curated mentors.

## Browser journey

- [x] Open `/` over HTTP with a new cookie session and confirm the reading form renders.
- [x] Submit an English three-card reading through the normal form POST.
- [x] Follow the redirect to the persisted reading and confirm the saved cards and reflective-guidance notice render.
- [x] Repeat with a separate session and Ukrainian locale.
- [x] Confirm the Ukrainian saved-reading heading and reflective-guidance notice render.

## Automated release gates

- [x] `uv run ruff check .`
- [x] `uv run pytest`
- [x] `openspec validate htmx-tarot-vertical-slice --strict`
- [x] Django configuration check with production-style environment values.

The Telegram client update remains outside this repository's current OpenSpec edit scope. Credential rotation must be
performed in BotFather before enabling `TELEGRAM_CHANNEL_ENABLED` in production.
