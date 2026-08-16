# Review Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | ReviewReport-{F-XX}-{S-XX}-attempt-{NN}.md |
| Output | `review-feature-01-slice-01-attempt-01.md` at `.forgeflow/artifacts/` |
| Required inputs | TDDRecord; Implementation evidence |

## Sample Output: review-report

```markdown
# Review Report F-01 S-01 Attempt 01

Metadata
---
| Artifact Type | ReviewReport |
| Feature ID | F-01 |
| Slice ID | S-01 |
| Attempt | 01 |
| Decision | FAIL |
| Blocking Findings | 2 |
| Non-blocking Findings | 1 |
| Version | 1.0 |
| Status | READY |

## Findings Table

| # | Severity | Owner Workflow | Affected Scope | Evidence | Violated Contract |
|---|----------|---------------|----------------|----------|-------------------|
| 1 | BLOCKING P0 | TDD | Slice S-01 | Test assertion uses hardcoded DB connection string | Auth config should use env var |
| 2 | BLOCKING P1 | Solution | Feature F-01 | No rate limiting on login endpoint | Security policy requires brute-force protection |
| 3 | NON-BLOCKING P2 | TDD | Slice S-01 | Missing docstring in `verify_password()` | PEP8 docstring requirement |

## Detailed Findings

### Finding 1 (P0 — BLOCKING)
**Location:** `tests/test_auth.py:15`
```python
engine = create_engine("postgresql://localhost/mydb")  # Hardcoded!
```
**Expected:** Use `os.environ.get('DATABASE_URL')`  
**Fix:** Replace with environment variable reference

### Finding 2 (P1 — BLOCKING)
**Location:** `auth/main.py:8-15`
No rate limiter decorator on `/auth/login` endpoint.  
**Expected:** Implement slow_lock with max 5 attempts/min/IP  
**Fix:** Add `@slow_lock(max_requests=5, window=60)`

---
*Review Decision: FAIL (2 blocking findings require TDD rework)*
