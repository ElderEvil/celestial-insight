## Why

Celestial currently has a Django API, an incomplete Next.js client, and a Telegram prototype whose reading flow does not match the backend. The smallest compelling product is a private, reflective tarot-reading journey that can be completed in the browser and later viewed through Telegram, rather than another disconnected client or an AI chat wrapper.

The existing `celestial-neutral` prototype already contains reusable mentor personas, spread positions, localization, and structured interpretation concepts. This change turns the proven material into one canonical Django experience while making card selection auditable and deterministic.

## What Changes

- Add a server-rendered Django + HTMX web journey for an anonymous visitor to select a mentor, pose a question, select a supported spread, draw cards, and view a saved reading.
- Define deterministic server-owned card selection and orientation. The selected spread, roles, cards, and orientations are persisted before any AI request.
- Change AI from card chooser to structured interpreter of the persisted selection; interpretations are bounded to reflective guidance and retain the selected positions.
- Introduce a curated mentor-content model and import path, using selected personas, local assets, styles, and English/Ukrainian copy from `celestial-neutral` instead of external hotlinked images.
- Add an anonymous reading identity backed by a signed session, plus a later account-claiming seam; do not make third-party OAuth a prerequisite for the first reading.
- Define a backend-authenticated Telegram contract for browsing and retrieving a visitor's own readings. The bot remains read-only until the web reading flow and Telegram identity verification are complete.
- Retire the Next.js client as a required runtime path for the first vertical slice. It may remain a reference project, but it is not part of the launch dependency graph.

## Capabilities

### New Capabilities

- `web-tarot-journey`: Server-rendered, progressively enhanced tarot-reading journey and anonymous reading ownership.
- `deterministic-reading-draw`: Persisted spread selection, positions, unique cards, and orientations owned by the Django domain layer.
- `structured-reading-interpretation`: AI interpretation contract for a previously selected reading, including safety and failure behavior.
- `mentor-content-catalog`: Curated, localized mentor personas and locally managed visual assets.
- `telegram-reading-channel`: Verified Telegram identity boundary and read-only access to the caller's backend-owned readings.

### Modified Capabilities

None; OpenSpec was initialized for this product as part of this planning change.

## Impact

- **Backend:** `tarot`, `mentors`, `users`, templates/static assets, migrations, Django settings and URLs.
- **AI:** PydanticAI schemas and prompts; model output can no longer create or alter the card draw.
- **Clients:** `celestial-tg` consumes documented authenticated endpoints; `celestial-ui` is removed from the first-release critical path.
- **Data:** selected content from `celestial-neutral/src/data`, `assets/mentors`, and localization resources is normalized into the canonical Django product.
- **Security:** Telegram credentials must be rotated, signed identity must be verified server-side, and no channel receives another user's reading by username or query parameter.
