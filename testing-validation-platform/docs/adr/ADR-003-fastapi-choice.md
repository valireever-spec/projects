# ADR-003: FastAPI for Dashboard REST API

**Status:** Accepted  
**Date:** 2026-06-21  
**Deciders:** V-Model team

## Context

The testing-validation-platform needs a REST API to serve the V-Model dashboard. The API must:
- Return JSON data about project requirements, gaps, and health metrics
- Support filtering and searching by requirement ID, status, severity
- Auto-refresh on the frontend every 30 seconds (low-latency requirement)
- Validate request payloads and enforce type safety

We evaluated three Python web frameworks:

## Decision

We chose **FastAPI** for the REST API server (`backend/api_server.py`).

**Key features used:**
- Automatic OpenAPI documentation (helps with Tracker integration debugging)
- Built-in request/response validation via Pydantic models
- Async/await support for concurrent dashboard refreshes
- Type hints throughout (aligns with project's mypy strict mode)
- Fast startup and low memory footprint

**Endpoints:**
- `GET /api/vmodel/board` — Returns full V-Model status (JSON)
- `GET /api/vmodel/requirements` — Filter requirements by status/type
- `GET /api/vmodel/gaps` — Filter gaps/bugs by severity

## Consequences

### Benefits
- **Type safety**: Pydantic models enforce schema; catches bugs at request time
- **Developer experience**: Automatic OpenAPI docs at `/docs` (self-documenting)
- **Performance**: Async allows high throughput for dashboard refreshes
- **Maintainability**: Minimal boilerplate compared to Django
- **Python 3.10+**: Leverages modern Python features (pattern matching, unions)

### Trade-offs
- **Ecosystem**: Smaller than Django (fewer packages for common tasks)
- **Learning curve**: Async/await adds complexity vs. synchronous frameworks
- **Maturity**: Newer than Django (less StackOverflow questions)

### Mitigations
- Well-documented API via `/docs` (OpenAPI/Swagger)
- Test coverage via `tests/test_api_server.py`
- Sync wrapper around async functions for simpler code paths

## Alternatives Considered

### 1. Django + Django REST Framework
**Pros:** Mature, large ecosystem, built-in admin panel  
**Cons:** Heavy for a simple read-only API; slow startup; over-engineered for our needs

### 2. Flask
**Pros:** Lightweight, minimal boilerplate  
**Cons:** No built-in type validation; requires separate JSON schema library; less mature ecosystem

### 3. Starlette (ASGI framework)
**Pros:** Very lightweight, async-first  
**Cons:** No validation layer; would need to add Pydantic manually anyway

## Implementation Notes

- Server runs on `http://localhost:8004` (development)
- Configured in `backend/api_server.py`
- Uses Pydantic models from `backend/models.py` for type safety
- All endpoints tested via pytest with coverage tracking

## Related Decisions

- ADR-002: Centralized Tracker (what the API queries)
- ADR-001: Pull-based sync (keeps data current for API responses)
