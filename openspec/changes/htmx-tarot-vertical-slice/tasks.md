## 1. Foundation and safety

- [ ] 1.1 Rotate the previously exposed Telegram credential, document the replacement environment variables, and verify no credential or generated-password auth flow remains in tracked source.
- [x] 1.2 Add Django test settings and test coverage for anonymous reading ownership, deterministic draws, interpreter validation, and Telegram authorization; verify `uv run pytest` collects and passes the new tests.
- [x] 1.3 Add HTMX and the minimal Django template/static configuration, with a normal POST/redirect/GET fallback; verify a browser can load the journey without JavaScript.

## 2. Reading domain and deterministic draw

- [x] 2.1 Add migrations for anonymous session ownership, immutable draw seed/audit value, spread content version, and interpretation status/error metadata; verify migrations apply to a fresh SQLite database.
- [x] 2.2 Define the editorially approved launch spread catalogue with ordered position roles and versioning; verify unit tests cover all launch position counts and reject unsupported spreads.
- [x] 2.3 Implement an atomic backend draw service that persists distinct cards, orientations, and roles before interpretation; verify a failed interpretation retry retains the exact saved draw.
- [x] 2.4 Update reading API/service behavior so AI cannot select or remap cards; verify existing and new API tests assert persisted card IDs and roles are authoritative.

## 3. Structured interpretation

- [x] 3.1 Replace card-generating AI result schemas and prompts with a per-persisted-position interpretation schema, including mentor, locale, and reflection-only safety context; verify schema tests reject missing, duplicate, and unknown positions.
- [x] 3.2 Persist pending, completed, and failed interpretation states and add a same-draw retry operation; verify provider failure leaves cards visible and retry does not create new `ReadingCard` rows.
- [x] 3.3 Add high-stakes prompt and response validation rules for health, legal, financial, and third-party-intent questions; verify representative tests produce calibrated reflective copy rather than definitive advice.

## 4. Mentor catalogue and localization

- [x] 4.1 Select and editorially review the launch mentor subset from `celestial-neutral`, recording content provenance and excluding unsuitable or incomplete personas; verify the selected fixture contains English and Ukrainian content for every active mentor.
- [x] 4.2 Add mentor content fields or related localized records for biography, style instruction, and managed image metadata; verify migrations and model/API serialization tests pass.
- [x] 4.3 Copy approved mentor assets into product-managed storage and replace remote avatar dependencies with local media or deliberate fallbacks; verify rendered mentor pages do not request third-party avatar URLs.
- [x] 4.4 Extend demo seeding to load the curated mentor catalogue and both locales idempotently; verify `uv run python manage.py seed_demo` succeeds twice on a fresh database.

## 5. HTMX web journey

- [x] 5.1 Build the mentor-selection and reading-request templates, form validation, and session ownership guard; verify integration tests cover valid creation, invalid input, and cross-session denial.
- [x] 5.2 Add normal-page and HTMX partial responses for draw reveal and interpretation status; verify an HTMX request replaces only the journey region and a non-HTMX request redirects to the persisted reading.
- [x] 5.3 Build the saved-reading view with ordered cards, roles, orientations, status, retry action, locale-aware copy, and an explicit reflective-guidance notice; verify an owner can reopen it while another session cannot.
- [x] 5.4 Add a deferred account-claiming interface seam without making account creation part of the initial journey; verify anonymous readings remain usable before an account exists.

## 6. Telegram adapter

- [x] 6.1 Design and implement backend verification of Telegram Web App init data or an equivalent signed Bot API identity flow; verify invalid hashes, expired payloads, and username-only requests are rejected.
- [x] 6.2 Add scoped read-only endpoints for public catalogue browsing and the verified caller's reading list/detail; verify authorization tests prevent cross-user reading access.
- [ ] 6.3 Simplify `celestial-tg` to consume only the documented read-only endpoints and direct new-reading requests to the web journey; verify bot handler tests/mock HTTP assertions show no local draw or AI request.

## 7. Release and verification

- [x] 7.1 Add production configuration checks for stable Django secret, trusted origins, local media, AI provider settings, and Telegram credential presence; verify unsafe production startup fails clearly.
- [x] 7.2 Run migrations and curated demo seeding in a clean environment, then execute the full browser journey manually in English and Ukrainian; record expected screenshots or a concise release checklist.
- [x] 7.3 Run `uv run ruff check .`, `uv run pytest`, `openspec validate htmx-tarot-vertical-slice --strict`, and Django deployment checks; verify all commands pass before enabling the journey feature flag.
