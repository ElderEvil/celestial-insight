# Learnings - dev-mvp-htmx-telegram

## Task 1: Settings/Env Configuration

### Pre-existing Issues Found
- `ninja_extra.decorators.throttle` import was broken - moved to `ninja_extra.throttling` in newer versions
- Fixed in tarot/api.py line 7

### Settings Configuration
- All sensitive settings already use `os.getenv()` with safe dev defaults:
  - `SECRET_KEY`: Has insecure dev default (flagged in comment)
  - `DEBUG`: Defaults to "True" for dev
  - `ALLOWED_HOSTS`: Defaults to "*" for dev
  - `HEADLESS_ONLY`: Defaults to "False" (enables session auth UI for HTMX)

### Social Auth
- GitHub, Google, Telegram credentials all read from env vars
- No hardcoded secrets in settings.py

### Database
- Uses SQLite by default (no env config needed for dev)
- Added DATABASE_URL placeholder in .env.example for PostgreSQL production use

### Verification
- `uv run python manage.py check` requires OPENAI_API_KEY set (PydanticAI agent initializes at import time)
- Create .env with at least `OPENAI_API_KEY=sk-xxx` to run manage.py commands
