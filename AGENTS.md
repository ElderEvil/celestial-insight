# AGENTS.md - Celestial Insight

Guidelines for AI agents working in this Django + PydanticAI tarot reading application.

## Quick Reference

| Action | Command |
|--------|---------|
| Install deps | `uv sync` |
| Run server | `uv run python manage.py runserver` |
| Run migrations | `uv run python manage.py migrate` |
| Make migrations | `uv run python manage.py makemigrations` |
| Run all tests | `uv run pytest` |
| Run single test | `uv run pytest path/to/test.py::TestClass::test_method -v` |
| Lint check | `uv run ruff check` |
| Lint fix | `uv run ruff check --fix` |
| Format code | `uv run ruff format` |
| Pre-commit all | `uv run pre-commit run --all-files` |

## Project Structure

```
celestial_insight/     # Django project config (settings, urls, api router)
tarot/                 # Core tarot app (cards, readings, spreads)
  agents/              # PydanticAI agents (celestial_agent, tarot_support_agent)
  services/            # Business logic (card_service, reading_service)
mentors/               # Mentor entities for readings
users/                 # User auth and profiles
```

## Tech Stack

- **Python**: 3.12+
- **Framework**: Django 5.x with Django Ninja (REST API)
- **AI**: PydanticAI with OpenAI GPT-4
- **Auth**: Django AllAuth + ninja-jwt
- **Package Manager**: uv (Astral)

## Code Style

### Formatting (Ruff)

- **Line length**: 120 characters
- **Indent**: 4 spaces
- **Quotes**: Double quotes (`"`)
- **Trailing commas**: Preserved

### Imports

Order (enforced by Ruff `I` rules):
1. Standard library
2. Third-party packages
3. Local imports (relative for same app)

```python
# Standard library
import logging
from datetime import datetime
from typing import Literal

# Third-party
from django.db import models
from ninja import Schema
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# Local (relative imports within same app)
from .enums import ReadingTypeEnum
from .models import Card, Reading
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `reading_service.py` |
| Classes | PascalCase | `ReadingCard`, `CelestialInsightResponse` |
| Functions | snake_case | `create_reading`, `generate_insight` |
| Constants | UPPER_SNAKE | `MIN_TOKEN_COST = 250` |
| Variables | snake_case | `card_objects`, `reading_type` |
| Django models | PascalCase singular | `Card`, `Reading`, `Mentor` |
| Schemas (Ninja) | PascalCase + `Schema` suffix | `CardSchema`, `ReadingSchemaShort` |

### Type Annotations

Always use modern Python 3.12+ syntax:

```python
# Use | instead of Union
def create_reading(user, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None):

# Use list[] instead of List[]
cards: list[CardResponse] = Field(description="List of cards")

# Use dict[] instead of Dict[]
preferences: dict[str, str] = {}
```

### Django Models

```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class Card(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    slug = AutoSlugField(populate_from="name")
    description = models.TextField(_("Description"))

    # ForeignKey with explicit related_name and verbose_name
    suit = models.ForeignKey(
        Suit,
        on_delete=models.CASCADE,
        related_name="cards",
        verbose_name=_("Suit"),
        db_index=True,
    )

    class Meta:
        ordering = ["suit", "number"]
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self):
        return f"{self.name} ({self.suit.name})"
```

### Django Ninja API Controllers

```python
from ninja_extra import api_controller, http_get, http_post, permissions


@api_controller("/tarot", tags=["Tarot"], permissions=[permissions.IsAuthenticatedOrReadOnly])
class AsyncTarotController:
    @http_get("/cards", response=list[CardSchemaShort])
    async def list_tarot_cards(self, filters: CardFilterSchema = Query(...)):
        return await list_cards(filters)

    @http_post("/readings", response=ReadingSchema | str)
    async def create_tarot_reading(
        self, request, question: str, mentor_id: int, reading_type: ReadingTypeEnum | None = None
    ):
        return await create_reading(request.user, question, mentor_id, reading_type)
```

### PydanticAI Agents

```python
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class CelestialInsightResponse(BaseModel):
    text: str = Field(description="The mystical guidance text.")
    cards: list[CardResponse] = Field(description="List of cards with details.")


celestial_agent = Agent(
    "openai:gpt-4o",
    deps_type=ReadingDependencies,
    result_type=CelestialInsightResponse,
    system_prompt="You are a wise and mystical guide...",
)
```

### Error Handling

```python
# Service layer - return error messages as strings
async def create_reading(user, question: str, ...):
    has_tokens = await deduct_tokens(user, MIN_TOKEN_COST)
    if not has_tokens:
        return "Insufficient tokens to create a reading."
    
    try:
        result = await agent.run(question, deps=deps)
        if not result or not result.data.is_valid:
            return f"Invalid question: {result.data.reason}"
    except AttributeError as e:
        return f"Data validation error: Missing attribute - {e}"
    except ValidationError as e:
        return f"Validation error: {e}"
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info level for operational messages
logger.info(f"Actual token usage: {actual_usage}")
```

### Choices and Enums

Use Django-style choices tuples in `choices.py`:

```python
from django.utils.translation import gettext_lazy as _

READING_TYPE_CHOICES = [
    ("single_card", _("Single Card")),
    ("three_card_spread", _("Three-Card Spread")),
]
```

Use Python Enum in `enums.py` for type safety:

```python
from enum import Enum


class ReadingTypeEnum(str, Enum):
    SINGLE_CARD = "single_card"
    THREE_CARD_SPREAD = "three_card_spread"
```

## Testing

- Framework: pytest
- Test files: `tests.py` or `test_*.py` in app directories
- Run single test: `uv run pytest tarot/tests.py::TestClassName::test_method -v`

## Linting Rules (Ruff)

Key enabled rule sets:
- `F`, `E`, `W`: Pyflakes, pycodestyle errors/warnings
- `I`: isort (import sorting)
- `N`: pep8-naming
- `UP`: pyupgrade (modern Python syntax)
- `S`: bandit (security) - `S101` (assert) ignored
- `B`: bugbear
- `C4`: comprehensions
- `PT`: pytest style
- `RUF`: Ruff-specific rules

Migrations are excluded from linting.

## Pre-commit Hooks

Runs automatically on commit:
1. `ruff` - lint with auto-fix
2. `ruff-format` - code formatting
3. `djlint` - Django template linting
4. `django-upgrade` - Django 5.0 compatibility

## CI Pipeline

On PR to `master`:
- Runs `uv run ruff check`

## Key Patterns

1. **Async by default**: API endpoints and services use `async/await`
2. **Service layer**: Business logic in `services/` not in views
3. **Schema separation**: Input/output schemas in `schemas.py`
4. **Filters**: Query filtering via Django Ninja `FilterSchema`
5. **Translation ready**: All user-facing strings use `gettext_lazy`
