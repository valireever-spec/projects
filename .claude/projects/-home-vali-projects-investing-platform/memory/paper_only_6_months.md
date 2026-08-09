---
name: paper-only-6-months
description: Hard constraint — bot must run paper-only for >=6 months; live go-live is date-locked until 2027-01-19
metadata:
  type: project
---

The trading bot **must run paper-only for at least 6 months** from the paper
trial restart (2026-07-19). User directive, 2026-07-20.

Enforced in code (not just convention):
- `backend/core/config.py`: `LIVE_TRADING_NOT_BEFORE` (default `2027-01-19`,
  env-overridable).
- `backend/api/routers/paper_trading_analytics.py` `_compute_paper_go_live()`:
  hard date lock checked BEFORE trade-journal readiness criteria and before
  `confirmed=true` — no combination of stats can flip `ALPACA_MODE=live` until
  the date passes. Fails closed if the date is misconfigured.

**Why:** the signal has no proven edge yet (see [[us-alpaca-correctness-gaps]] /
signal-edge verdict TRADEABLE=False), and the prior go-live switch was gated
only on trade stats with no time lock — someone could have flipped to live
prematurely.

**How to apply:** keep `ALPACA_MODE=paper`. Do not lift the lock before
2027-01-19. To lift later, update `LIVE_TRADING_NOT_BEFORE` AND require the
signal-edge validator to return TRADEABLE=True first. Priorities during the
paper window: (1) "bot inert" alert when cycles qualify signals but open 0
positions due to mock fundamentals; (2) paper-accounting store unification
(deferred in Gap 4). Related: [[phase-b-trial-active]].
