# Celestial Insight - Project Roadmap

## Project Overview

**Celestial Insight** is a Django-powered mystical tarot reading application that combines traditional tarot wisdom with AI-generated insights using OpenAI's GPT-4o through PydanticAI.

---

## Technology Stack

### Core Technologies
- **Backend Framework**: Django 5.1.4
- **API Framework**: Django Ninja (fast, type-safe REST APIs)
- **AI Integration**: PydanticAI with OpenAI GPT-4o
- **Authentication**: Django Allauth + JWT tokens
- **Database**: SQLite (development), Docker-ready for production
- **Python Version**: 3.12
- **Package Manager**: `uv` (fast Python package installer)

### Development Tools
- **Code Quality**: Ruff linter with comprehensive rule sets
- **Pre-commit Hooks**: Automated code validation
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions workflows

### Key Dependencies
- `django-ninja` - Fast API framework
- `django-ninja-extra` - Enhanced Django Ninja with controllers
- `pydantic-ai` - Type-safe AI agent framework
- `django-allauth` - Social authentication (Google, GitHub, Telegram)
- `django-ninja-jwt` - JWT authentication
- `django-cors-headers` - Cross-origin resource sharing
- `whitenoise` - Static file serving
- `uvicorn` - ASGI server
- `beautifulsoup4` - HTML parsing for web scraping
- `httpx` - Async HTTP client (planned) for external API integrations

---

## Architecture

### Application Structure

```
celestial-insight/
├── celestial_insight/          # Django project configuration
│   ├── settings.py            # Project settings
│   ├── urls.py                # URL routing
│   ├── api.py                 # API initialization
│   └── wsgi.py/asgi.py        # Server interfaces
│
├── tarot/                     # Main tarot application
│   ├── agents/               # PydanticAI agent implementations
│   │   ├── celestial_agent.py       # Mystical insight generation
│   │   ├── tarot_support_agent.py   # Question validation
│   │   └── common.py                # Shared dependencies
│   ├── services/             # Business logic layer
│   │   ├── reading_service.py       # Reading CRUD + AI integration
│   │   └── card_service.py          # Card retrieval logic
│   ├── models.py             # Database models
│   ├── api.py                # API controllers
│   ├── schemas.py            # Pydantic schemas
│   ├── filters.py            # Query filters
│   └── fixtures/             # Seed data
│
├── mentors/                   # Mentor management
│   ├── models.py             # Mentor model
│   └── api.py                # Mentor endpoints
│
└── users/                     # User profile system
    ├── models.py             # UserProfile with token tracking
    ├── api.py                # User-related endpoints
    └── signals.py            # User creation signals
```

### Design Patterns

- **Async-First Architecture**: All API controllers and services use `async/await` patterns for optimal performance
- **Service Layer Pattern**: Business logic separated from API layer
- **Agent Pattern**: AI logic encapsulated in dedicated PydanticAI agents
- **Repository Pattern**: Database access abstracted through Django ORM
- **Dependency Injection**: PydanticAI agents use typed dependencies

---

## Core Features

### 1. Tarot Card Management

**Database Models:**
- `Suit` - Organizes cards (Major Arcana, Cups, Wands, Swords, Pentacles)
- `Card` - Individual tarot cards with full metadata

**Card Attributes:**
- Name and slug (URL-friendly identifier)
- Card number (for ordering)
- Description and keywords
- Upright and reversed meanings
- Image upload support
- Suit association

**API Endpoints:**
- `GET /tarot/cards` - List all cards with filtering
- `GET /tarot/cards/{slug}` - Get single card details

### 2. Reading System

**Database Models:**
- `Reading` - User's tarot reading session
- `ReadingCard` - Individual cards within a reading

**Reading Types:**
- Single Card
- Three Card Spread
- Celtic Cross
- Custom spreads (AI-generated)

**Reading Workflow:**
1. User poses a question
2. Selects a mentor for guidance
3. AI validates question and extracts theme
4. Reading created with spread type
5. Celestial insight generated with card interpretations

**API Endpoints:**
- `POST /tarot/readings` - Create new reading
- `GET /tarot/readings/my` - List user's readings
- `GET /tarot/readings/{id}` - Get reading details
- `POST /tarot/readings/{id}/insight` - Generate AI insight

### 3. AI-Powered Insights

**PydanticAI Agents:**

**Tarot Support Agent** (`tarot_support_agent.py`)
- Validates user questions
- Extracts thematic elements
- Suggests appropriate spread types
- Returns structured validation response

**Celestial Agent** (`celestial_agent.py`)
- Generates mystical guidance text
- Creates card spreads aligned with question
- Provides card-specific interpretations
- Considers orientation (upright/reversed)
- Returns structured `CelestialInsightResponse`

**Token Management:**
- Users start with 1,000 tokens
- Minimum 250 tokens upfront per operation
- Dynamic adjustment based on actual API usage
- Token costs tracked in reading notes

### 4. Mentor System

**Mentor Model:**
- Name and slug
- Mystical level (0-10 scale)
  - 0 = Skeptical/Rational
  - 10 = Fortune Teller/Mystical
- Specialization field
- Avatar URL
- Active/inactive status

**Integration:**
- Users select mentor for each reading
- Mentor influences interpretation style
- Preferred mentor saved in user profile

### 5. User Profile System

**UserProfile Model:**
- One-to-one with Django User
- Token balance tracking
- Preferred mentor
- JSON preferences field for extensibility

**Token System:**
- Deducted before AI operations
- Prevents operations if insufficient
- Usage tracked per reading

### 6. Authentication & Authorization

**Supported Authentication:**
- Traditional email/password
- Google OAuth
- GitHub OAuth
- Telegram authentication
- JWT tokens for API access

**Permission Levels:**
- Public: Browse tarot cards
- Authenticated: Create readings, generate insights
- Per-endpoint permissions via Django Ninja Extra

**API Variants:**
- `/tarot/*` - Standard API with session auth
- `/tg/tarot/*` - Telegram-specific with JWT

### 7. Multi-Channel API

**Standard REST API** (`AsyncTarotController`)
- Session-based authentication
- IsAuthenticatedOrReadOnly permissions
- Full CRUD operations

**Telegram API** (`AsyncTarotTGController`)
- JWT authentication via `AsyncJWTAuth()`
- Designed for bot integration
- User lookup by username

---

## Current Implementation Status

### ✅ Completed Features

- [x] Complete tarot card database schema
- [x] Major and Minor Arcana support
- [x] Card filtering and search
- [x] Reading creation and management
- [x] Multiple spread types
- [x] AI question validation
- [x] AI-powered celestial insights
- [x] Token-based usage tracking
- [x] Mentor system with mystical levels
- [x] User profile management
- [x] Social authentication (Google, GitHub, Telegram)
- [x] JWT authentication
- [x] Async API architecture
- [x] Docker containerization
- [x] CORS configuration for frontend
- [x] Internationalization (i18n) support
- [x] Admin interface customization
- [x] Custom spread generation based on user input

### 🚧 Planned Features

#### Enhanced Spread Logic
- [x] Support for more tarot spreads
- [ ] **Visual representation of card layouts**
  - SVG/Canvas-based spread diagrams
  - Interactive card positioning
  - Responsive design for mobile
  - Export spread images

#### User Personalization
- [ ] **Save favorite readings**
  - Star/bookmark readings
  - Quick access to favorites
  - Share favorite readings
- [ ] **Insights tailored to user history**
  - Pattern recognition across readings
  - Recurring card analysis
  - Personal growth tracking
  - Historical theme analysis

#### Advanced AI Integrations
- [ ] **Deeper GPT-4 interpretative insights**
  - Context-aware interpretations
  - Historical reading context
  - Personality-based guidance
  - Follow-up question suggestions
- [x] Generate custom spreads based on user input

#### Deck Customization
- [ ] **Users can create and manage custom tarot decks**
  - Upload custom card images
  - Define custom meanings
  - Share decks with community
  - Import/export deck data

#### Community Features
- [ ] **Reading journals**
  - Personal notes on readings
  - Reflection prompts
  - Progress tracking
- [ ] **Reading sharing**
  - Share readings with friends
  - Community interpretations
  - Discussion threads
- [ ] **Mentor marketplace**
  - User-created mentors
  - Rating system
  - Featured mentors

#### Technical Enhancements
- [ ] **HTTPX integration for external APIs**
  - Async HTTP client for third-party integrations
  - Telegram Bot API calls
  - External tarot card repositories/APIs
  - Webhook notifications (Discord, Slack)
  - Social media sharing integrations
  - Payment gateway webhooks
  - Analytics event tracking
  - Custom retry/timeout logic for OpenAI
- [ ] **PostgreSQL migration**
  - Production-ready database
  - Advanced indexing
  - Full-text search
- [ ] **Redis caching**
  - API response caching
  - Session management
  - Rate limiting
- [ ] **WebSocket support**
  - Real-time reading updates
  - Live AI generation streaming
  - Collaborative readings
- [ ] **Mobile app**
  - React Native or Flutter
  - Push notifications
  - Offline reading access
- [ ] **Analytics dashboard**
  - Usage statistics
  - Popular cards/spreads
  - User engagement metrics

---

## HTTPX Integration Strategy

### Why HTTPX?

The project uses async-first architecture throughout the API layer, making HTTPX the ideal HTTP client for external integrations. Unlike the synchronous `requests` library, HTTPX provides native async/await support that aligns with Django Ninja's async controllers.

### Recommended Use Cases

#### 1. Telegram Bot Integration
```python
# tarot/services/telegram_service.py
import httpx
from django.conf import settings

async def send_reading_to_telegram(user_id: int, reading: Reading):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": user_id,
                "text": reading.celestial_insight,
                "parse_mode": "Markdown"
            }
        )
```

#### 2. External Tarot Card APIs
```python
# tarot/services/external_card_service.py
async def fetch_card_imagery(card_name: str) -> dict:
    """Fetch high-res card images from external tarot repositories."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"https://tarot-api.example.com/cards/{card_name}",
            headers={"Authorization": f"Bearer {settings.EXTERNAL_API_KEY}"}
        )
        response.raise_for_status()
        return response.json()
```

#### 3. Webhook Notifications
```python
# tarot/services/webhook_service.py
async def notify_reading_complete(reading_id: int, webhook_url: str):
    """Send webhook notification when reading insight is generated."""
    async with httpx.AsyncClient() as client:
        await client.post(
            webhook_url,
            json={
                "event": "reading.completed",
                "reading_id": reading_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            timeout=5.0
        )
```

#### 4. Social Media Sharing
```python
# tarot/services/sharing_service.py
async def generate_reading_preview(reading: Reading) -> str:
    """Generate OpenGraph image for social sharing."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://og-image-service.example.com/generate",
            json={
                "title": f"Tarot Reading: {reading.question[:50]}",
                "cards": [card.card.name for card in reading.cards.all()[:3]],
                "insight": reading.celestial_insight[:200]
            }
        )
        return response.json()["image_url"]
```

#### 5. Payment Gateway Integration
```python
# users/services/payment_service.py
async def purchase_tokens(user: User, amount: int) -> dict:
    """Process token purchase via payment gateway."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://payment-gateway.example.com/api/v1/charge",
            json={
                "user_id": user.id,
                "amount": amount,
                "currency": "USD",
                "description": f"Purchase {amount} tokens"
            },
            headers={"Authorization": f"Bearer {settings.PAYMENT_API_KEY}"}
        )
        return response.json()
```

### Implementation Pattern

#### Singleton Client Pattern
```python
# celestial_insight/clients.py
import httpx
from django.conf import settings

class HTTPXClient:
    """Shared HTTPX client with connection pooling."""
    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                limits=httpx.Limits(max_keepalive_connections=20),
                headers={"User-Agent": "CelestialInsight/0.1.0"}
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.aclose()
            cls._client = None
```

#### Service-Specific Clients
```python
# tarot/clients/tarot_api_client.py
class TarotAPIClient:
    """Client for external tarot card APIs."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://tarot-api.example.com",
            headers={"Authorization": f"Bearer {settings.TAROT_API_KEY}"},
            timeout=15.0
        )

    async def get_card(self, slug: str) -> dict:
        response = await self.client.get(f"/cards/{slug}")
        response.raise_for_status()
        return response.json()

    async def search_cards(self, query: str) -> list[dict]:
        response = await self.client.get("/cards/search", params={"q": query})
        response.raise_for_status()
        return response.json()["results"]

    async def close(self):
        await self.client.aclose()
```

### Error Handling Best Practices

```python
import httpx
from typing import TypeVar, Callable
import logging

logger = logging.getLogger(__name__)
T = TypeVar('T')

async def with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    backoff_factor: float = 1.0
) -> T:
    """Retry logic for external API calls."""
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPStatusError as e:
            if e.response.status_code < 500 or attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(backoff_factor * (2 ** attempt))
        except httpx.TimeoutException as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Timeout on attempt {attempt + 1}")
            await asyncio.sleep(backoff_factor * (2 ** attempt))
```

### Configuration

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "httpx>=0.27.0",
]
```

Add to `.env.example`:
```bash
# External API Keys
EXTERNAL_TAROT_API_KEY=your-key-here
TELEGRAM_BOT_TOKEN=your-bot-token
WEBHOOK_SECRET=your-webhook-secret
PAYMENT_API_KEY=your-payment-key
```

### Testing with HTTPX

```python
# tarot/tests/test_external_services.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_external_card():
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"name": "The Fool", "number": 0}
        )

        result = await fetch_card_imagery("the-fool")
        assert result["name"] == "The Fool"
```

### Performance Considerations

- **Connection Pooling**: Reuse client instances to avoid connection overhead
- **Timeouts**: Always set appropriate timeouts (default 10s recommended)
- **Limits**: Configure max connections based on external API rate limits
- **Retries**: Implement exponential backoff for transient failures
- **Monitoring**: Log external API latency and error rates

---

## API Documentation

### Authentication

**Session-based (Web):**
```
POST /accounts/login
POST /accounts/logout
POST /accounts/signup
```

**JWT-based (Telegram/Mobile):**
```
POST /api/token/
POST /api/token/refresh/
POST /api/token/verify/
```

### Tarot Endpoints

**Cards:**
```
GET  /tarot/cards                    # List cards (public)
GET  /tarot/cards/{slug}             # Get card details (public)
```

**Readings:**
```
POST /tarot/readings                 # Create reading (authenticated)
     Body: { question, mentor_id, reading_type? }

GET  /tarot/readings/my              # List user readings (authenticated)
     Query: filters (date, type, etc.)

GET  /tarot/readings/{id}            # Get reading (authenticated)

POST /tarot/readings/{id}/insight    # Generate AI insight (authenticated)
```

### Telegram Endpoints

```
GET  /tg/tarot/cards                 # List cards
GET  /tg/tarot/cards/{slug}          # Get card
POST /tg/tarot/readings              # Create reading
GET  /tg/tarot/readings/my           # List readings
GET  /tg/tarot/readings/{id}         # Get reading
POST /tg/tarot/readings/{id}/insight # Generate insight
```

All `/tg/tarot/*` endpoints require JWT authentication header:
```
Authorization: Bearer <jwt_token>
```

---

## Database Schema

### Core Models

**Suit**
```python
- id: Integer (PK)
- name: String(50)
- description: Text
- arcana: String(10) [major, minor]
```

**Card**
```python
- id: Integer (PK)
- name: String(100)
- slug: String (auto-generated)
- description: Text
- number: Integer (nullable)
- image: ImageField
- upright_meaning: Text
- reversed_meaning: Text
- keywords: String(255)
- suit_id: ForeignKey(Suit)
```

**Reading**
```python
- id: Integer (PK)
- reading_type: String(20) [single_card, three_card, celtic_cross, etc.]
- date: DateTime (auto_now_add)
- question: Text
- notes: Text
- celestial_insight: Text
- mentor_id: ForeignKey(Mentor)
- user_id: ForeignKey(User)
```

**ReadingCard**
```python
- id: Integer (PK)
- position: Integer
- orientation: String(10) [upright, reversed]
- interpretation: Text
- role: String(50) [Outcome, Advice, Significator, etc.]
- reading_id: ForeignKey(Reading)
- card_id: ForeignKey(Card)
```

**Mentor**
```python
- id: Integer (PK)
- name: String(100)
- slug: String (auto-generated)
- mystical_level: Integer(0-10)
- avatar_url: URLField(500)
- specialization: String(255)
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime
```

**UserProfile**
```python
- id: Integer (PK)
- user_id: OneToOneField(User)
- available_tokens: Integer (default: 1000)
- preferences: JSONField
- preferred_mentor_id: ForeignKey(Mentor, nullable)
```

---

## Configuration

### Environment Variables

Required in `.env` file:

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Social Authentication
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-secret

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

TELEGRAM_BOT_ID=your-telegram-bot-id
TELEGRAM_BOT_SECRET=your-telegram-secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3002

# Database (optional, defaults to SQLite)
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Django Settings Highlights

```python
# API Throttling
NINJA_EXTRA = {
    "THROTTLE_RATES": {
        "burst": "6/min",
        "sustained": "100/day"
    }
}

# Authentication
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True

# Internationalization
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True
```

---

## Development Setup

### Prerequisites
- Python 3.12+
- `uv` package manager ([installation](https://github.com/astral-sh/uv))
- SQLite (included with Python)
- OpenAI API key

### Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/ElderEvil/celestial-insight.git
   cd celestial-insight
   ```

2. **Create virtual environment:**
   ```bash
   uv virtualenv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run migrations:**
   ```bash
   uv run python manage.py migrate
   ```

6. **Load fixtures (optional):**
   ```bash
   uv run python manage.py loaddata tarot/fixtures/initial_data.json
   ```

7. **Start development server:**
   ```bash
   uv run python manage.py runserver
   ```

8. **Access application:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - API Docs: http://localhost:8000/api/docs

### Docker Setup

```bash
# Build and run
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

---

## Testing Strategy

### Current Coverage
- Model tests for core functionality
- API endpoint tests (basic)

### Planned Testing
- [ ] Comprehensive API integration tests
- [ ] AI agent unit tests with mocked responses
- [ ] Token deduction logic tests
- [ ] Authentication flow tests
- [ ] Performance/load testing
- [ ] Frontend E2E tests (when frontend built)

### Test Configuration
```toml
[tool.pytest.ini_options]
python_files = ["tests.py", "test_*.py"]
```

---

## Deployment Considerations

### Production Checklist
- [ ] Switch to PostgreSQL
- [ ] Set `DEBUG = False`
- [ ] Configure secure `SECRET_KEY`
- [ ] Set up proper `ALLOWED_HOSTS`
- [ ] Configure Redis for caching/sessions
- [ ] Set up Celery for background tasks
- [ ] Configure static file serving (S3/CDN)
- [ ] Set up monitoring (Sentry, New Relic)
- [ ] Configure backup strategy
- [ ] Set up SSL/HTTPS
- [ ] Configure logging
- [ ] Set up CI/CD pipeline

### Recommended Stack
- **Hosting**: Railway, Render, or AWS
- **Database**: PostgreSQL (managed)
- **Cache/Queue**: Redis (managed)
- **Storage**: S3 or Cloudinary
- **CDN**: CloudFlare
- **Monitoring**: Sentry + DataDog

---

## Code Quality Standards

### Linting Configuration (Ruff)
- Line length: 120 characters
- Target: Python 3.12
- Comprehensive rule set (see `pyproject.toml`)
- Pre-commit hooks enabled

### Key Rules
- Type hints required
- Security checks enabled
- Import sorting enforced
- Code complexity limits
- Docstring requirements

---

## Contributing Guidelines

### Development Workflow
1. Fork repository
2. Create feature branch (`feature/amazing-feature`)
3. Make changes with tests
4. Run linters: `ruff check .`
5. Format code: `ruff format .`
6. Run tests: `pytest`
7. Commit with conventional commits
8. Push and create PR

### Commit Convention
```
feat: Add new feature
fix: Bug fix
docs: Documentation update
style: Code style changes
refactor: Code refactoring
test: Test additions/changes
chore: Build/tooling changes
```

---

## Future Vision

## Revival Plan (August 2026)

### Product Direction

Revive **Celestial Insight** as the canonical tarot product: a Django/Ninja backend with a Next.js web client. Treat the other repositories as supporting material rather than equal product implementations:

- `celestial-ui`: retain and modernize as the web client.
- `celestial-neutral`: reuse useful mentor, card, localization, and prompt assets only.
- `celestial-tg`: rebuild later as a channel integration after the web product is stable.

### Core Design Decision

The backend must be the source of truth for tarot cards. It should deterministically select or draw the cards for a reading, then provide those exact cards, orientations, spread positions, question, and mentor context to the AI for interpretation. Do not ask the model to invent card names and fuzzy-match them back to the database.

This makes readings testable and auditable while letting the model focus on its strengths: nuanced, structured interpretation; tone; localization; and personalization.

### Phased Work

1. **Security preflight**
   - [ ] Revoke and rotate the Telegram bot credential currently present in `celestial-tg` source history.
   - [ ] Remove credentials from tracked files, including any `.env` files; replace them with documented environment variables and `.env.example` templates.
   - [ ] Review the repository history and deployed environments for exposed credentials.

2. **Backend health audit**
   - [ ] Create a clean local environment and verify dependency installation, migrations, fixtures, tests, linting, and Docker startup.
   - [ ] Inventory API routes, authentication behavior, data fixtures, and the existing Next.js client contract.
   - [ ] Add missing regression tests before changing behavior.

3. **AI and reading workflow modernization**
   - [ ] Upgrade and validate the PydanticAI/OpenAI integration using typed, structured responses.
   - [ ] Move card selection and spread construction to deterministic backend services.
   - [ ] Supply the selected cards to the AI and store only its interpretation, with model/usage metadata.
   - [ ] Redesign usage limits around a clear product budget instead of treating raw model-token counts as user currency.
   - [ ] Add mocked agent tests and end-to-end tests for a complete reading.

4. **Web client restoration**
   - [ ] Update Next.js dependencies and build tooling.
   - [ ] Replace the hard-coded local API URL with environment-based configuration.
   - [ ] Reconcile UI calls, CORS, authentication, error states, and reading flows with the backend contract.
   - [ ] Build visual spread layouts and mobile-friendly reading history.

5. **Deployment and channels**
   - [ ] Deploy the secure web flow with PostgreSQL, production settings, monitoring, backups, and CI.
   - [ ] Reintroduce Telegram as an authenticated client of the stable API.

### Model-Assisted Development

Use a high-capability coding/reasoning model for the initial codebase audit, dependency migration, and architecture decisions. Use a balanced model for routine refactors and test-writing, and reserve a low-cost model for high-volume mechanical tasks. Evaluate changes against tests and the written API contract rather than relying on generated code alone.

### Short Term (3-6 months)
- Complete visual spread layouts
- Implement user favorites
- Add reading journals
- Enhanced AI context awareness

### Medium Term (6-12 months)
- Custom deck creation
- Community features
- Mobile app MVP
- Advanced analytics

### Long Term (12+ months)
- Mentor marketplace
- Live collaborative readings
- Video/audio readings
- Integration with wearables
- Multi-language support expansion

---

## License

[Insert License Information]

---

## Contact & Support

- **GitHub**: https://github.com/ElderEvil/celestial-insight
- **Issues**: https://github.com/ElderEvil/celestial-insight/issues
- **Documentation**: [Link to full docs when available]

---

**Last Updated**: August 2026
