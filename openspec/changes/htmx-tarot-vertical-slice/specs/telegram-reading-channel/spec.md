## Purpose

Let Telegram act as a constrained, verified channel for the same backend-owned readings without duplicating tarot logic or exposing private records.

## ADDED Requirements

### Requirement: Telegram identity is verified by the backend
The system SHALL authenticate Telegram requests using verified Telegram identity data and backend-issued credentials. It SHALL not create or authenticate an account from a username, query parameter, or shared/generated password.

#### Scenario: Valid Telegram identity
- **WHEN** Telegram supplies a valid backend-verifiable identity payload
- **THEN** the backend issues or recognizes credentials for that Telegram identity

#### Scenario: Forged username
- **WHEN** a request supplies only a Telegram username or user identifier without valid verification
- **THEN** the backend rejects the request and does not disclose or create a reading

### Requirement: Telegram reads backend-owned content
The Telegram client SHALL call documented backend endpoints and SHALL not draw cards, store an alternative reading history, or invoke AI interpretation directly.

#### Scenario: Telegram views a reading
- **WHEN** an authenticated Telegram user requests one of their readings
- **THEN** the client presents the backend's persisted cards, positions, and interpretation status

### Requirement: Launch bot scope is read-only
The Telegram client SHALL limit the initial release to browsing the public catalogue and retrieving the authenticated user's existing readings. It SHALL not offer reading creation until the web journey and verified identity handoff are operational.

#### Scenario: Telegram user requests a new reading during launch
- **WHEN** an authenticated user asks the launch bot to create a reading
- **THEN** the bot directs them to the web journey rather than creating an independent reading
