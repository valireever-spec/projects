# Architecture Decision Records (ADRs)

This directory documents major architectural and technical decisions made for the testing-validation-platform.

## Index

- [ADR-001: Pull-Based Sync Model for Requirements](ADR-001-pull-sync.md) — Why we use a pull model instead of webhooks for syncing requirements from investing-platform
- [ADR-002: Centralized V-Model Tracker Architecture](ADR-002-vmodel-tracker.md) — Design rationale for the tracker-centric architecture
- [ADR-003: FastAPI for REST API Server](ADR-003-fastapi-choice.md) — Why FastAPI over Django/Flask for the dashboard API

## Format

Each ADR follows the [Lightweight Architecture Decision Record](https://adr.github.io/) format:

- **Title**: Short descriptive name
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: Problem and constraints
- **Decision**: What we decided and why
- **Consequences**: Benefits and trade-offs
- **Alternatives Considered**: Other options and why we didn't choose them

## Contributing

When proposing a new ADR:
1. Create a new file: `ADR-NNN-short-name.md`
2. Use the format below as a template
3. Mark as `Proposed` initially
4. After review, update to `Accepted` or `Deprecated`
5. Update this README with an entry
