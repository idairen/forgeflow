# TDD Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | TDDRecord-{F-XX}-{S-XX}.md |
| Output | `tdd-feature-01-slice-01.md` at `.forgeflow/artifacts/` |
| Required inputs | SlicePlan; Implementation evidence |

## Sample Output: tdd-feature-01-slice-01.md

```markdown
# TDD Record F-01 S-01 — Login Endpoint

Metadata
---
| Artifact Type | TDDRecord |
| Feature ID | F-01 |
| Slice ID | S-01 |
| Attempt | 1 |
| Version | 1.0 |
| Status | READY_FOR_REVIEW |
| Owner Workflow | TDD |

## Red Phase (Tests Fail)

```python
# tests/test_auth.py
def test_login_returns_401_with_wrong_password():
    response = client.post("/auth/login", json={"email": "user@test.com", "password": "wrong"})
    assert response.status_code == 401
```
Result: FAILED (expected) — No test data exists yet.

## Green Phase (Tests Pass)

Implemented `auth.py` with basic password hashing via `passlib`.
- Tests run green after adding mock user in database fixture.

## Refactor Notes

- Consider moving password logic to a separate module for reusability
