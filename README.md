# Tarot Reading API
<!-- Badges -->
<a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</a>
<a href="https://github.com/charliermarsh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json" alt="Ruff">
</a>

## A mystical tarot reading application powered by Django Ninja and PydanticAI. This project allows users to explore tarot cards, create readings, and generate AI-powered celestial insights for guidance.

---

<p align="center">
  <!-- Django Ninja Logo -->
  <a href="https://django-ninja.dev/">
    <img src="https://django-ninja.dev/img/logo-big.png" alt="Django Ninja Logo">
  </a>
</p>

<p align="center">
    <em>Fast to learn, fast to code, fast to run</em>
</p>

---

<div align="center">
  <!-- Pydantic AI Logo -->
  <a href="https://ai.pydantic.dev/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://ai.pydantic.dev/img/pydantic-ai-dark.svg">
      <img src="https://ai.pydantic.dev/img/pydantic-ai-light.svg" alt="PydanticAI">
    </picture>
  </a>
</div>

---

## Features ✨

- Manage tarot suits and cards (Major and Minor Arcana).
- Create readings and add cards with positions, orientations, and interpretations.
- Generate AI-powered celestial insights using GPT-4 for tarot readings.

---

## Installation Instructions 🔌

### Prerequisites

- Python 3.12
- SQLite (default)
- [uv](https://github.com/astral-sh/uv) package manager

---

### 1. Clone the Repository

```bash
git clone https://github.com/ElderEvil/celestial-insight.git
cd celestial-insight
```

---

### 2. Install requirements

```bash
uv virtualenv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Run Database Migrations
```bash
uv run python manage.py migrate
```

### 5. Start the Development Server
```bash
uv run python manage.py runserver
```

---

## Roadmap 🚀

#### Current Features
- Manage tarot suits and cards.
- AI-powered celestial insights for readings.
- Localization for multi-language support.
- Filter cards and readings via API.

#### Planned Features

**Enhanced Spread Logic:**
- [x] Support for more tarot spreads.
- [ ] Visual representation of card layouts.

**User Personalization:**
- [ ] Save favorite readings.
- [ ] Insights tailored to user history.

**Advanced AI Integrations:**
- [ ] Deeper GPT-4 interpretative insights.
- [ ] Generate custom spreads based on user input.

**Deck Customization:**
- [ ] Users can create and manage custom tarot decks.
