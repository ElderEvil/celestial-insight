## Purpose

Make every saved reading reproducible and auditable by selecting its cards and orientations in application code before interpretation begins.

## ADDED Requirements

### Requirement: Server owns spread construction
The system SHALL define supported spreads as ordered position roles and descriptions. It SHALL reject, with a client validation error rather than a server error, any request whose spread has no supported position definition or whose spread is defined but not active.

#### Scenario: Supported spread has ordered positions
- **WHEN** a visitor creates a three-card reading
- **THEN** the saved reading has Past, Present, and Future positions in that order

#### Scenario: Unsupported or inactive spread is rejected
- **WHEN** a client requests a reading with a spread that has no position definition, or with a defined spread that is not active
- **THEN** the request is rejected with a 4xx validation error and no reading is created

### Requirement: Draw is persisted before interpretation
The system SHALL select distinct cards and upright or reversed orientations server-side and persist them with their roles before an interpretation request is started. The selection SHALL not depend on an AI response.

#### Scenario: Draw survives interpretation failure
- **WHEN** interpretation cannot be generated after cards are selected
- **THEN** the reading retains its original cards, orientations, and roles and exposes an interpretation-pending or failed state

#### Scenario: No duplicated card in a spread
- **WHEN** the system creates a multi-card reading
- **THEN** no card appears more than once in that reading

### Requirement: Draw has an audit seed
The system SHALL persist an opaque draw seed or equivalent immutable audit value with each reading so the original draw can be verified without relying on model-provider output.

#### Scenario: Existing reading is reloaded
- **WHEN** a saved reading is reopened
- **THEN** it displays the persisted draw rather than selecting cards again
