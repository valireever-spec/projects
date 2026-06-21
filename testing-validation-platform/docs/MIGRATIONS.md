# Database Migrations

## Why No Local Migrations?

This project **does not manage its own database schema**. Here's why:

### Architecture Decision
The central Tracker service (external infrastructure at `http://127.0.0.1:8001`) owns the database and all schema evolution. This testing-validation-platform is a **client** that:
- Reads requirements from project markdown files
- **Pushes** data to Tracker API (HTTP POST)
- **Pulls** gaps/bugs from Tracker API (HTTP GET)
- Writes results to V_MODEL_BOARD.md

See [ADR-002](docs/adr/ADR-002-vmodel-tracker.md) for architectural rationale.

### Local Data Storage
This project stores only:
- **In-memory**: Metrics, SLOs (MetricsCollector in `backend/metrics.py`)
- **File-based**: V_MODEL_BOARD.md, vmodel-status.html (auto-generated)
- **Config**: .env, settings from `backend/config.py`

No persistent local database = no migrations needed.

### If Tracker Schema Changes
- Tracker team manages migrations in their own alembic/ directory
- We update `backend/models.py` Pydantic validators
- We update `tracker_client.py` API call signatures
- No local migration needed

## Implications

✅ **Simpler**: No schema versioning overhead  
✅ **Decoupled**: Tracker and platform can evolve independently  
❌ **Trade-off**: Dependency on Tracker availability (see `backend/utils/retry.py`)

## If We Ever Need Local Storage

Should we decide to cache Tracker data locally (e.g., for offline mode), we would:
1. Create `db/migrations/` directory
2. Add SQLAlchemy models in `backend/db/models.py`
3. Use Alembic for schema evolution: `pip install alembic`
4. Initialize: `alembic init alembic`
5. Document in RUNBOOKS.md

For now, this is intentionally absent.
