## Purpose

Provide a curated, localized mentor catalogue whose personas and images are product-owned content rather than unverified remote dependencies.

## ADDED Requirements

### Requirement: Active mentor catalogue is curated
The system SHALL expose only active mentors with a stable slug, localized display content, interpretation style, and product-managed image or image fallback. A mentor's public profile SHALL not depend on a third-party hotlinked avatar.

#### Scenario: Visitor views mentors
- **WHEN** a visitor opens mentor selection
- **THEN** they see active curated mentors with usable names, descriptions, and images or intentional fallbacks

### Requirement: Mentor style affects interpretation only
The selected mentor SHALL influence presentation and interpretation style but SHALL not alter the server-selected cards, positions, orientations, ownership, or safety rules.

#### Scenario: Same draw with different mentors
- **WHEN** two readings have the same selected spread and cards but different mentors
- **THEN** their card selections remain unchanged while their interpretation style can differ

### Requirement: Launch content supports English and Ukrainian
The system SHALL provide English and Ukrainian mentor-facing and reading-journey text for the launch mentor catalogue.

#### Scenario: Ukrainian journey
- **WHEN** a visitor selects Ukrainian as the active language
- **THEN** mentor-facing journey copy and interpretation request context use Ukrainian
