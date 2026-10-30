## Purpose

Provide a fast, private browser journey for completing and reopening a reflective tarot reading without requiring an account before the first draw.

## ADDED Requirements

### Requirement: Visitor can complete a browser reading journey
The system SHALL let a visitor select an active mentor, submit a non-empty question, select a supported spread, and request a reading through a server-rendered web journey. The journey SHALL work without JavaScript and SHALL progressively replace the relevant page region when HTMX is available.

#### Scenario: Successful three-card reading
- **WHEN** a visitor selects a mentor, enters a question, and selects the three-card spread
- **THEN** the system displays the saved positions, cards, orientations, and interpretation state for the created reading

#### Scenario: Invalid journey submission
- **WHEN** a visitor submits a missing question, inactive mentor, or unsupported spread
- **THEN** the system preserves the visitor's valid selections and displays a field-level error without creating a reading

### Requirement: Anonymous visitor owns new readings
The system SHALL associate each anonymous reading with an opaque signed session identity. A visitor SHALL be able to reopen only readings associated with the current session and SHALL not need a third-party OAuth account to create a first reading.

#### Scenario: Visitor reopens own reading
- **WHEN** the original browser session requests a reading it created
- **THEN** the system displays that reading

#### Scenario: Different visitor requests a reading
- **WHEN** a browser without the owning session requests an anonymous reading URL or identifier
- **THEN** the system does not disclose the reading content

### Requirement: Account claiming has a stable ownership seam
The system SHALL retain enough anonymous ownership information to attach readings to a verified account in a later change without changing existing reading identifiers or card records.

#### Scenario: Anonymous reading remains valid before account claiming exists
- **WHEN** a visitor creates a reading without signing in
- **THEN** the reading persists and remains available through the visitor's session
