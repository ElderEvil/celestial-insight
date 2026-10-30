# Tarot Journey Release Checklist

Last verified: 2026-10-30

## Clean environment

- [x] Apply every Django migration to a new SQLite database.
- [x] Run `uv run python manage.py seed_demo` twice.
- [x] Confirm both runs leave 5 suits, 78 cards, 7 mentor rows, and 3 active curated mentors.
- [x] Confirm both runs leave all 78 cards with non-empty English and Ukrainian description, upright meaning,
      reversed meaning and keywords, and that the second run reports `0 filled`.
- [x] Confirm the spread catalogue defines 10 spreads and exactly 5 are active.
- [x] Run `uv run python manage.py compilemessages` and confirm `locale/uk/LC_MESSAGES/django.mo` is current.

## Browser journey

- [x] Open `/` over HTTP with a new cookie session and confirm the reading form renders.
- [x] Submit an English three-card reading through the normal form POST.
- [x] Follow the redirect to the persisted reading and confirm the saved cards and reflective-guidance notice render.
- [x] Repeat with a separate session and Ukrainian locale.
- [x] Confirm the Ukrainian saved-reading heading and reflective-guidance notice render.
- [x] Reopen the Ukrainian reading with an English `Accept-Language` header and confirm it still renders in Ukrainian.
- [x] Confirm an inactive mentor is absent from the journey, the mentor API, and `create_reading`.

## Automated release gates

- [x] `uv run ruff check .`
- [x] `uv run pytest`
- [x] `uv run python manage.py makemigrations --check --dry-run`
- [x] `uv run python manage.py check`
- [x] `openspec validate htmx-tarot-vertical-slice --strict`
- [x] Django configuration check with production-style environment values.
- [x] Confirm `manage.py check` and `makemigrations --check` run with a non-empty `OPENAI_API_KEY`
      (the URLconf builds the AI clients at import). The pytest suite sets its own placeholder and
      never calls the provider.

## Known deferred work

- Per-reading mentor-copy snapshotting is **not** implemented. `Reading.spread_version` and each mentor's
  `content_source` are recorded, but the interpretation prompt still reads `mentor.style_instruction` live, so
  editing a biography changes how past readings present. Snapshotting was deliberately dropped rather than shipped
  as a write-only field.
- Localized card copy is not exposed through the public card API. `CardSchemaShort` still returns the English
  `description`, `upright_meaning`, `reversed_meaning` and `keywords`; the `_uk` columns are admin- and
  prompt-only until a channel needs them.
- `tarot/filters.py` still filters cards by the English `keywords__icontains`; Ukrainian keyword filtering is a
  follow-up.
- The intent×theme→spread matrix and the 20 tone prompts are stored and tested as inert content; they are not yet
  wired into the interpretation prompt.
- `celestial-neutral` has not been archived yet; the port must land and be verified first.

The Telegram client update remains outside this repository's current OpenSpec edit scope. Credential rotation must be
performed in BotFather before enabling `TELEGRAM_CHANNEL_ENABLED` in production.
