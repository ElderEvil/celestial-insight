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

### Requirement: Full roster is stored with a curated active set
The catalogue SHALL store all seven authored personas with a stable primary key, unique slug, both locales, and a local managed image, and SHALL expose exactly three as active at launch: `neutral-reader`, `milo-starwhisk`, and `lolly-kiddie`. Inactive personas SHALL remain complete content and SHALL not be selectable through any surface.

#### Scenario: Inactive persona is not selectable
- **WHEN** a visitor or an authenticated API caller requests an inactive mentor by slug or identifier
- **THEN** the mentor is not listed, is not returned by detail lookup, and cannot be assigned to a reading or saved as a preferred mentor

#### Scenario: Activation follows the fixture
- **WHEN** the catalogue is seeded twice from the fixture
- **THEN** the active set is derived from each row's `is_active` value and no separate launch list overrides it
