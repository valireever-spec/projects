# Non-Functional Requirements: nas

Specification of system qualities: performance, reliability, security, maintainability.

---

## Overview

**Project:** nas
**Tech Stack:** Linux Docker

---

## How to Complete This Document

For each system quality, create NFR-001, NFR-002, etc.:

```
## NFR-001: [Quality Category - Specific Metric]

**ID:** NFR-001
**Category:** [Performance / Reliability / Security / Maintainability / Correctness]
**Related Requirement:** [FR-001, FR-002, etc. that this enables]

### Specification

**Requirement:** [What the system must achieve]

**Measurement Method:**
```bash
# How to measure this in production
[Command or code snippet]
```

**Target:**
- [Acceptable range / SLO]

**Alert Threshold:**
- Warning: [When to investigate]
- Critical: [When to escalate]

**Test Case:**
```python
# How to validate this requirement
def test_requirement():
    ...
    assert result <= target
```

### Rationale

[Why does this metric matter?]

### Related Pillar

- **[8-Pillar Name]**: How this supports that pillar
```

---

## Common Categories

### Performance
- Response time (latency)
- Throughput (requests/sec)
- Batch job duration
- Memory usage
- Query execution time

**Example:**
```
NFR-001: API response < 500ms (p99)
Target: p99 < 500ms
Measurement: Monitor journalctl for latency_ms metric
```

### Reliability
- Availability % (uptime)
- MTTR (mean time to recovery)
- Crash frequency
- Data loss incidents

**Example:**
```
NFR-002: 99.5% availability
Target: <= 216 min downtime/month
Measurement: Health check endpoint success rate
```

### Security
- No secrets in code/logs
- Encryption at rest & transit
- Authentication & authorization
- Input validation
- CVE scanning

**Example:**
```
NFR-003: No secrets in code
Target: 0 API keys, passwords in git
Measurement: pip-audit, git-secrets scan
```

### Maintainability
- Type hints coverage
- Code complexity (cyclomatic)
- Test coverage
- Code duplication
- Documentation

**Example:**
```
NFR-004: Type hints >= 90%
Target: >= 90% of functions typed
Measurement: mypy strict mode
```

### Correctness
- Accuracy (±% error)
- Completeness (all records processed)
- Consistency (A matches B)

**Example:**
```
NFR-005: Results match validation ±0.1%
Target: ±0.1% error
Measurement: Compare against ground truth
```

---

## Template Qualities (Customize Per Project)

### NFR-001: [Performance Metric]

**Category:** Performance
**Target:** [Measurable target]
**Current:** [Status - TBD]

Measure via: [journalctl / prometheus / custom script]
Alert when: [threshold exceeds]

---

### NFR-002: [Reliability Metric]

**Category:** Reliability
**Target:** [Uptime % / MTTR / etc.]
**Current:** [Status - TBD]

Health check: [URL or command]
Alert when: [SLO breached]

---

### NFR-003: [Security Metric]

**Category:** Security
**Target:** [0 vulnerabilities / 0 secrets / etc.]
**Current:** [Status - TBD]

Scan: [pip-audit / git-secrets / SAST / etc.]
Alert when: [Issues found]

---

## Instructions for Project Owner

1. **Performance**: What latency/throughput is acceptable?
   - API responses
   - Batch jobs
   - Database queries
   - File operations

2. **Reliability**: What uptime/recovery is required?
   - Service availability (99.5%, 99.9%, etc.)
   - MTTR target
   - Data durability

3. **Security**: What security properties are critical?
   - No secrets in code
   - Encryption requirements
   - CVE scanning
   - Input validation

4. **Maintainability**: How maintainable must the code be?
   - Type hints
   - Test coverage
   - Complexity limits
   - Documentation

5. **Correctness**: What accuracy/completeness is required?
   - ±% error bounds
   - All records processed
   - Consistency checks

---

## Summary

| ID | Category | Title | Target | Current | Status |
|----|----------|-------|--------|---------|--------|
| NFR-001 | [Category] | [Metric] | [Target] | [TBD] | TBD |
| NFR-002 | [Category] | [Metric] | [Target] | [TBD] | TBD |

**Total Non-Functional Requirements: [TBD]**
**Met: [TBD]**
**Partial: [TBD]**
**Gap: [TBD]**
