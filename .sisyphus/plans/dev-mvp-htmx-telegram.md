# Dev-first MVP: HTMX UI + Telegram Bot + Guardrails (Celestial Insight)

## TL;DR

> **Quick Summary**: Make the project dev-ready with tests+CI, add safety guardrails around AI usage, then ship an MVP: session-auth HTMX dashboard + `/read`, and a long-polling Telegram bot that calls the existing `/api/tg/*` endpoints.
>
> **Deliverables**:
> - Dev setup: env + PostgreSQL docker-compose + prod-safe settings toggles
> - Guardrails: input validation, prompt-injection hardening, cost caps (per-reading + daily), rate limiting
> - MVP UI: HTMX dashboard + `/read` (session auth via allauth)
> - Telegram bot: management command (long polling) + uses `/api/tg/users/auth` and `/api/tg/tarot/*`
> - Quality: pytest TDD for core flows + CI runs tests
> - Updated `ROADMAP.md` with MVP checklist
>
> **Estimated Effort**: Medium (1–2 weeks)
> **Parallel Execution**: YES (3 waves)
> **Critical Path**: Dev config → Guardrails + tests → HTMX UI → Telegram bot → Roadmap polish

---

## Context

### Original Request
Analyze current state and define next steps, optimize for the next 1–2 weeks, must add tests, solo maintainer.

### Interview Summary (decisions)
- **Primary goal**: dev-first setup + agent guardrails + MVP.
- **MVP UI**: HTMX dashboard + `/read`.
- **Auth for UI**: Django session login (allauth).
- **Social login**: Google + GitHub.
- **Username/password**: deferred.
- **Mentor selection**: required.
- **Reading types**: single-card only (MVP).
- **Rate limit**: 20 readings/hour/user.
- **Cost guardrails**: both per-reading cap and daily per-user budget.
- **Token economy**: keep fixed-cost in-app tokens (MIN_TOKEN_COST pattern) for MVP.
- **Telegram**: long polling bot.
- **Telegram integration**: bot calls existing `/api/tg/*` endpoints (API remains the source of truth).
- **Server**: docker-compose already exists; target PostgreSQL in compose.
- **Docs**: update existing `ROADMAP.md` with near-term MVP checklist.

### Repo Reality Check (from scan)
- Tests are effectively absent (`users/tests.py`, `mentors/tests.py` empty; no `tarot/tests.py`).
- CI runs `ruff check` only (`.github/workflows/ci.yml`).
- `celestial_insight/settings.py` contains hardcoded `SECRET_KEY` and `DEBUG=True`.
- `.env.example` lacks Telegram variables.
- No templates/HTMX exist yet (project is API-only today).
- Telegram APIs already exist: `UsersTGController` and `AsyncTarotTGController` registered in `celestial_insight/api.py`.

### Metis Review (gaps surfaced)
Metis highlighted (and this plan addresses):
- Need an explicit decision for web auth UI because settings include `HEADLESS_ONLY = True` (blocks rendered allauth views).
- Define concrete acceptance criteria (no “manual check”).
- Lock down scope to prevent CSS/framework and bot UX creep.
- Confirm rate limiting wiring (Ninja Extra throttle config may not apply unless wired/decorated).

### Defaults Applied (override if you disagree)
- **Allauth headless**: set `HEADLESS_ONLY = False` to enable session login UI for HTMX pages.
- **CSS**: PicoCSS via CDN (no build step).
- **PostgreSQL image**: use a current stable major (e.g., 16) unless your server standardizes another.
- **Telegram mentor requirement**: require a mentor selection once, then persist as a per-user preference (simple field on profile), defaulting only if none exist.

---

## Work Objectives

### Core Objective
Deliver a dev-ready, test-verified MVP that allows authenticated users to create tarot readings via HTMX and Telegram, with safety guardrails around AI usage and cost.

### Concrete Deliverables
- Updated `.env.example` (includes web + Telegram + DB env vars)
- PostgreSQL docker-compose setup + Django settings that read env vars
- CI updated to run pytest
- Guardrail implementation + tests
- HTMX templates + views + URLs + tests
- Telegram long-polling bot runner + tests (mocked Telegram + mocked AI)
- `ROADMAP.md` updated with an “MVP (Next 1–2 weeks)” checklist

### Definition of Done
- [ ] `uv run ruff check` passes
- [ ] `uv run pytest` passes
- [ ] `docker compose up -d` starts app + db successfully
- [ ] Playwright (or equivalent automated browser check) can log in and create a reading via HTMX
- [ ] Telegram bot management command starts and can process a mocked update end-to-end without hitting external networks (tests)

### Must NOT Have (guardrails)
- No Redis/Celery/background infra (keep it simple for solo maintainer)
- No “favorites”, “journals”, or rich dashboard analytics
- No Telegram webhook mode (long polling only)
- No CSS build pipeline (use minimal CSS: classless or CDN)
- No real OpenAI or Telegram API calls in CI/tests

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (pytest configured), but test coverage is near-zero
- **User wants tests**: YES (TDD for core flows)
- **Framework**: pytest (+ pytest-django patterns)

### TDD Workflow for This Plan
Each feature task includes:
1) RED: failing test for the behavior
2) GREEN: minimal implementation
3) REFACTOR: cleanups with tests still green

### Automated Verification Tools
- **Backend/API**: pytest + Django test client / httpx (as appropriate)
- **HTMX UI**: Playwright automated browser run (headless) OR Django template response assertions (minimum)
- **Telegram**: pytest with mocked httpx + golden update payloads

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (Foundations)
├─ Task 1: Env + settings hardening
├─ Task 2: docker-compose PostgreSQL
├─ Task 3: CI runs pytest
└─ Task 4: Create core test scaffolding (pytest-django baseline)

Wave 2 (Guardrails + Core flows)
├─ Task 5: Rate limiting wiring (20/hour/user)
├─ Task 6: Input validation + prompt-injection hardening
└─ Task 7: Cost guardrails (per-reading + daily budget)

Wave 3 (User-facing MVP)
├─ Task 8–11: HTMX UI (dashboard + /read) + tests
└─ Task 12–14: Telegram bot (polling) + tests

Final (Docs)
└─ Task 15: Update ROADMAP.md MVP checklist

---

## TODOs

> Notes on references: file paths reflect the repo scan; the executor should open these files to follow established patterns.

### 1) Dev settings & env hygiene (SECRET_KEY/DEBUG/ALLOWED_HOSTS)

- [ ] 1. Move sensitive settings to env and make dev defaults explicit

  **What to do**:
  - Update `celestial_insight/settings.py` to read `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` from env.
  - Ensure dev defaults are safe-ish but convenient (explicit `.env` required for real deploy).
  - Decide web auth UI: switch allauth `HEADLESS_ONLY` to allow session login pages for HTMX.

  **Recommended Agent Profile**:
  - Category: `unspecified-high` (touches core settings + impacts auth)
  - Skills: (none required)

  **Parallelization**: Can run in parallel with Tasks 2–4.

  **References**:
  - `celestial_insight/settings.py` — current hardcoded `SECRET_KEY`, `DEBUG=True`, and allauth config
  - `.env.example` — currently missing several vars

  **Acceptance Criteria**:
  - [ ] `uv run python -c "import os; assert os.getenv('SECRET_KEY') is None"` is not required; instead verify via tests/settings import:
  - [ ] `uv run python manage.py check` exits 0 using a dev `.env` (executor to create local `.env` as needed)
  - [ ] No secrets are hardcoded in `settings.py` (grep check in executor)

### 2) Docker-compose: PostgreSQL + app wiring

- [ ] 2. Update `docker-compose.yml` to include PostgreSQL and app env wiring

  **What to do**:
  - Add `db` service (PostgreSQL) with volume.
  - Add app env vars for DB connection.
  - Add basic healthcheck/wait strategy (minimal).

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: (none)

  **Parallelization**: Parallel with Tasks 1, 3, 4.

  **References**:
  - `docker-compose.yml` — current baseline
  - `Dockerfile` — check for fixture references that may fail container start

  **Acceptance Criteria**:
  - [ ] `docker compose up -d` exits 0
  - [ ] `docker compose ps` shows app + db running
  - [ ] `docker compose exec app python manage.py migrate --check` exits 0

### 3) CI: run pytest in GitHub Actions

- [ ] 3. Update CI workflow to run tests (not just ruff)

  **What to do**:
  - Add `uv run pytest` to `.github/workflows/ci.yml`.
  - Ensure test env provides minimal required env vars (dummy secrets).

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: (none)

  **Parallelization**: Parallel with Tasks 1, 2, 4.

  **References**:
  - `.github/workflows/ci.yml`
  - `pyproject.toml` (pytest config)

  **Acceptance Criteria**:
  - [ ] CI has a step that runs `uv run pytest -q` (or similar)
  - [ ] Local: `uv run pytest` passes

### 4) Test scaffolding baseline (pytest-django conventions)

- [ ] 4. Establish a minimal pytest baseline and first “core flow” tests

  **What to do**:
  - Create a `tarot/tests.py` (or `tarot/tests/test_*.py`) with first tests for:
    - token deduction behavior
    - create reading behavior (mock AI)
  - Add fixtures for users/mentors and tarot fixture loading as needed.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: (none)

  **Parallelization**: Parallel with Tasks 1–3.

  **References**:
  - `tarot/services/reading_service.py` — create/generate insight flows
  - `tarot/utils.py` — `deduct_tokens()`
  - `users/models.py` — `UserProfile.available_tokens`
  - `tarot/fixtures/tarot_data.json` — seed data

  **Acceptance Criteria**:
  - [ ] `uv run pytest -q` passes
  - [ ] At least 5 tests exist covering token deduction + reading creation with mocked agent

### 5) Rate limiting wiring (20 readings/hour/user)

- [ ] 5. Implement per-user throttling that matches “20 readings/hour/user”

  **What to do**:
  - Update `celestial_insight/settings.py` throttling rates to include an hourly rate.
  - Apply throttling to the endpoints that create/compute readings (web API and TG API).
  - Ensure rate-limit responses are consistent (HTTP 429 + useful message).

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: Depends on Tasks 1–4.

  **References**:
  - `celestial_insight/settings.py` — existing `NINJA_EXTRA["THROTTLE_RATES"]`
  - `tarot/api.py` — create reading endpoints for normal and TG controllers

  **Acceptance Criteria**:
  - [ ] Unit/API test demonstrates 21st request within an hour returns 429
  - [ ] `uv run pytest -q` passes

### 6) Input validation + prompt-injection defense

- [ ] 6. Add strict validation for user prompts/questions and harden system prompts

  **What to do**:
  - Enforce minimum/maximum question length and reject obviously malicious “ignore instructions” style inputs.
  - Ensure Pydantic result parsing failures return safe error messages.
  - Strengthen agent system prompts to explicitly refuse instruction-following that conflicts with system rules.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 4; can parallelize with Task 5.

  **References**:
  - `tarot/services/reading_service.py` — where question is processed + errors returned
  - `tarot/agents/celestial_agent.py` — system prompt / agent config
  - `tarot/agents/tarot_support_agent.py` — validation agent patterns

  **Acceptance Criteria**:
  - [ ] Tests: empty question rejected
  - [ ] Tests: injection-like prompt rejected/sanitized (expected safe error)
  - [ ] Tests: malformed AI output handled gracefully

### 7) Cost guardrails (per-reading cap + daily per-user budget)

- [ ] 7. Enforce “Balanced” cost limits

  **Spec**:
  - Per reading cap: **2,500 total tokens max**
  - Daily per user budget: **10,000 tokens/day**
  - In-app token economy remains fixed-cost (keep `MIN_TOKEN_COST` approach)

  **What to do**:
  - Add per-reading cap by constraining agent call token limits and/or aborting if usage exceeds cap.
  - Track daily usage per user (date-bucketed) and deny once budget exceeded.
  - Ensure failures do not leak secrets and return consistent errors.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 4; can parallelize with Tasks 5–6.

  **References**:
  - `tarot/services/reading_service.py` — already computes “actual token usage” and extra deductions
  - `users/models.py` — where to store per-user counters (may require new model/migration)

  **Acceptance Criteria**:
  - [ ] Tests: per-reading cap enforced (mock usage > 2500 returns safe error)
  - [ ] Tests: daily budget enforced (mock usage accumulating to > 10000 denies)

### 8) Add HTMX dependency + base template skeleton

- [ ] 8. Add HTMX support and minimal templates

  **What to do**:
  - Add `django-htmx` dependency (and enable in `INSTALLED_APPS`).
  - Add a minimal templates structure (`templates/base.html`, etc.).
  - Use minimal CSS (no build): recommend PicoCSS via CDN.

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: `frontend-ui-ux`

  **Parallelization**: After Task 1 (settings) and Task 4 (tests baseline).

  **References**:
  - `celestial_insight/settings.py` — templates configuration (DIRS currently empty)
  - `celestial_insight/urls.py` — add routes for HTML pages

  **Acceptance Criteria**:
  - [ ] `uv run python manage.py check` passes
  - [ ] Template response tests pass for dashboard route

### 9) HTMX Dashboard: reading list + token balance

- [ ] 9. Implement authenticated dashboard page

  **What to do**:
  - Add `/dashboard` page requiring session auth.
  - Show: token balance + recent readings list (minimal fields).
  - Provide “Create reading” CTA to `/read`.

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: `frontend-ui-ux`

  **Parallelization**: After Task 8.

  **References**:
  - `tarot/api.py` endpoints for listing readings (`/api/tarot/readings/my`)
  - `users/models.py` token balance

  **Acceptance Criteria**:
  - [ ] pytest: authenticated user gets 200 and HTML contains reading list container
  - [ ] pytest: anonymous user redirected to login

### 10) HTMX `/read`: form + mentor required + partial rendering

- [ ] 10. Implement `/read` HTMX flow (create reading + generate insight)

  **What to do**:
  - Provide mentor selection (required; “few options” — show a small curated list).
  - Submit question via HTMX POST; swap in result partial.
  - Use service layer directly (avoid extra HTTP hops) but keep the same guardrails.

  **Recommended Agent Profile**:
  - Category: `visual-engineering`
  - Skills: `frontend-ui-ux`

  **Parallelization**: After Task 8; can overlap with Task 9.

  **References**:
  - `mentors/api.py` and/or mentors models for mentor list
  - `tarot/services/reading_service.py` for create+insight

  **Acceptance Criteria**:
  - [ ] pytest: posting valid question + mentor returns HTML including insight text
  - [ ] pytest: missing mentor returns form error
  - [ ] pytest: injection prompt rejected
  - [ ] pytest: HTMX POST includes CSRF and succeeds; missing/invalid CSRF returns 403

### 11) Allauth/session auth wiring for UI

- [ ] 11. Ensure session login works for HTMX pages

  **What to do**:
  - Confirm/adjust allauth headless setting to allow web login.
  - Enable social providers (Google + GitHub) for session login.
  - Defer password login (explicitly out of MVP).

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 1.

  **References**:
  - `celestial_insight/settings.py` — allauth config, providers, headless mode
  - `.env.example` — add provider keys as documented

  **Acceptance Criteria**:
  - [ ] Automated browser test can reach login and establish a session (dev config)
  - [ ] pytest confirms dashboard redirects to login when unauthenticated
  - [ ] `HEADLESS_ONLY` is set so that rendered login views work for session auth

### 12) Telegram Bot service wrapper (httpx)

- [ ] 12. Implement Telegram Bot API client wrapper

  **What to do**:
  - Add `TELEGRAM_BOT_TOKEN` to env example.
  - Implement a small service module for Telegram Bot API calls and polling.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 1 and Task 2.

  **References**:
  - `ROADMAP.md` — contains planned `send_reading_to_telegram()` pattern

  **Acceptance Criteria**:
  - [ ] Unit tests mock httpx and validate request/response handling

### 13) Telegram bot runner (management command, long polling)

- [ ] 13. Add `manage.py` command to run long-polling bot

  **What to do**:
  - Create a Django management command to poll for updates.
  - Implement minimal command set:
    - `/start` and `/help`
    - `/mentors` (list few mentors)
    - `/mentor <id>` (set preferred mentor)
    - `/read <question>` (requires preferred mentor; prompts user to run `/mentors` if missing)
  - No complex conversation state in MVP.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 12.

  **References**:
  - `users/api.py` — `UsersTGController` `/api/tg/users/auth`
  - `users/schemas.py` — `TelegramAuthSchema`
  - `tarot/api.py` — `AsyncTarotTGController` `/api/tg/tarot/*`
  - `celestial_insight/api.py` — controller registration

  **Acceptance Criteria**:
  - [ ] Tests simulate one update → bot calls mocked `/api/tg/users/auth` → gets JWT → calls mocked create/insight endpoints
  - [ ] Bot runner handles network errors with backoff (unit tested)

### 14) Telegram auth bootstrap behavior (create user/profile)

- [ ] 14. Ensure Telegram user bootstrap is deterministic

  **What to do**:
  - Ensure `/api/tg/users/auth` reliably creates/links a user profile given `telegram_id` + `username`.
  - Ensure token balance exists for TG users.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**: After Task 4; can overlap with Tasks 12–13.

  **References**:
  - `users/api.py` — TG auth controller
  - `users/models.py` — profile creation expectations

  **Acceptance Criteria**:
  - [ ] pytest: TG auth creates a user and returns JWT tokens
  - [ ] pytest: subsequent TG tarot call with JWT succeeds

### 15) Update existing ROADMAP.md with MVP checklist

- [ ] 15. Add an “MVP (Next 1–2 weeks)” section to `ROADMAP.md`

  **What to do**:
  - Add a short, top-of-file (or clearly-linked) MVP checklist with status boxes.
  - Include: dev setup, guardrails, HTMX dashboard + /read, TG bot, tests/CI.
  - Link to key commands (`uv sync`, `uv run pytest`, `docker compose up`).

  **Recommended Agent Profile**:
  - Category: `writing`

  **Parallelization**: Can run in parallel once scope is stable.

  **References**:
  - `ROADMAP.md`
  - `AGENTS.md` (canonical commands)

  **Acceptance Criteria**:
  - [ ] `ROADMAP.md` contains MVP checklist and “Definition of Done” for MVP

---

## Commit Strategy

Solo-maintainer friendly, keep commits atomic:

1. `chore(config): env-based settings and postgres compose`
2. `ci(test): run pytest in CI`
3. `test(core): add token + reading service tests`
4. `feat(guardrails): throttle + validation + cost caps`
5. `feat(ui): add htmx dashboard and read flow`
6. `feat(tg): add long polling bot runner`
7. `docs(roadmap): add mvp checklist`

Each commit must keep `uv run pytest` green.

---

## Success Criteria

### Verification Commands
```bash
uv sync
uv run ruff check
uv run pytest
docker compose up -d
```

### Final Checklist
- [ ] Dev setup documented and repeatable
- [ ] CI runs ruff + pytest
- [ ] Guardrails enforced and covered by tests
- [ ] HTMX UI works end-to-end (automated)
- [ ] Telegram bot runs via management command and is testable (mocked)
- [ ] ROADMAP.md updated with MVP section
