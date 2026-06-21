# ADR-001: Pull-Based Sync Model for Requirements

**Status:** Accepted  
**Date:** 2026-06-21  
**Deciders:** V-Model team

## Context

The testing-validation-platform needs to synchronize requirements from the investing-platform project files (FUNCTIONAL_REQUIREMENTS.md, NONFUNCTIONAL_REQUIREMENTS.md) to a central Tracker service.

Two main approaches were available:
1. **Push model**: investing-platform pushes requirements to Tracker when they change
2. **Pull model**: testing-validation-platform periodically pulls requirements from investing-platform files

**Constraints:**
- Investing-platform is the source of truth, but doesn't own the sync process
- Tracker needs real-time awareness of requirement changes
- testing-validation-platform is already a separate service
- We want to minimize coupling between projects

## Decision

We chose a **pull-based sync model** running every 5 minutes on a periodic timer.

**Implementation:**
- `backend/core/vmodel_sync.py` reads FUNCTIONAL_REQUIREMENTS.md and NONFUNCTIONAL_REQUIREMENTS.md
- Extracts structured requirement metadata (ID, description, status)
- POST to Tracker API to upsert requirements
- Inverse sync: pull gaps/bugs from Tracker and write V_MODEL_BOARD.md

## Consequences

### Benefits
- **Loose coupling**: investing-platform doesn't need to know about sync mechanism
- **Resilient**: No dependency on webhooks; failed syncs retry on next cycle
- **Auditable**: Clear record of what was synced and when (via git history + V_MODEL_BOARD.md)
- **Simple**: No need to instrument every requirements change in investing-platform

### Trade-offs
- **Latency**: 5-minute delay between requirements update and Tracker awareness (acceptable for non-real-time use)
- **Duplicates**: Syncing same requirements multiple times (mitigated by Tracker idempotency)
- **Bandwidth**: Periodic full reads instead of event-driven updates

## Alternatives Considered

### 1. Push Model (Webhooks)
**Rejected because:**
- Requires investing-platform to implement webhook calls on every requirements change
- Adds coupling and maintenance burden to investing-platform
- More fragile (failed webhooks need retry logic)

### 2. Real-Time Streaming (Event Bus)
**Rejected because:**
- Over-engineered for current scale (N requirements per project)
- Requires shared infrastructure (Kafka, RabbitMQ)
- Increases operational complexity

### 3. Git-Based Sync (Read Git History)
**Rejected because:**
- Already doing this for secrets scanning (see: auto_check.py limitations)
- Git blame/log fragile across rebases and squashes
- Doesn't capture partial updates (e.g., status change without description)

## Related Decisions

- ADR-002: Centralized V-Model Tracker architecture (upstream consumer)
- ADR-003: FastAPI REST API (how dashboard accesses synced data)
