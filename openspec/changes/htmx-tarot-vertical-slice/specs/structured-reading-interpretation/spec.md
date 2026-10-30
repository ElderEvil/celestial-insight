## Purpose

Generate a bounded reflective interpretation for a persisted draw while preventing the model from inventing or changing cards, positions, and certainty claims.

## ADDED Requirements

### Requirement: Interpreter receives a fixed draw
The system SHALL supply the interpreter with the reading question, language, mentor style, each persisted card, orientation, and position. The interpreter output SHALL map to those positions and SHALL not add, remove, or rename drawn cards.

#### Scenario: Model names an unselected card
- **WHEN** an interpretation response references a card not in the persisted draw
- **THEN** the system rejects the response and leaves the saved draw unchanged

### Requirement: Interpretation is reflective guidance
The system SHALL present tarot output as reflective guidance, use calibrated language for outcomes, and avoid deterministic claims about health, legal matters, financial outcomes, or another person's hidden intent.

#### Scenario: High-stakes question
- **WHEN** a visitor asks a health, legal, or financial question
- **THEN** the interpretation frames the result as reflection and does not give a definitive outcome or professional instruction

### Requirement: Interpretation status is visible
The system SHALL distinguish pending, completed, and failed interpretation states. A failure SHALL preserve the reading draw and provide a retry path that does not redraw cards.

#### Scenario: Retry after provider failure
- **WHEN** a completed draw has a failed interpretation and the visitor retries it
- **THEN** the system requests interpretation for the same persisted cards and positions
