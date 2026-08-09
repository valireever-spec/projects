---
name: yfinance-removal-plan
description: yfinance is fully dead (news/options/prices all returning errors); planned for removal in a future phase
metadata:
  type: project
---

yfinance provides nothing to the platform — all endpoints return errors or empty results (429s, JSON parse failures, empty DataFrames). Already replaced the one critical usage (live quotes in `live.py`) with Alpaca IEX.

**Why:** Yahoo Finance blocked/rate-limited the library. No features depend on it working.

**How to apply:** Treat any remaining yfinance call as dead code. Don't add new yfinance calls. Schedule removal as a dedicated cleanup phase.

**Scope when ready:**
- 27 files actually import yfinance
- 100 files mention it in comments/strings
- Key deletions: `yfinance_interceptor.py`, `yfinance_safe.py`, `yfinance_health.py`
- Key stubs: news.py → return [], options_data.py → return None, ingest Tier 4 fallback → drop
- Uninstall: remove from requirements.txt

**Composite signal impact:** News factor (10 pts) and IV/options factor (10 pts) already return 0 — no behavior change on removal, score just runs on 80 pts.
