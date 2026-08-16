# Slice Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | SlicePlan-{F-XX}.md |
| Output | `slice-plan-feature-01.md` at `.forgeflow/artifacts/` |
| Required inputs | SolutionPlan.md; Requirement F-01 |

## Sample Output: slice-plan-feature-01.md

```markdown
# Slice Plan F-01 — User Authentication

Metadata
---
| Artifact Type | SlicePlan |
| Feature ID | F-01 |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Slice |

## Slices (Ordered List)

| Slice ID | Title | Description | Dependency |
|----------|-------|-------------|------------|
| S-01 | Login endpoint | POST /auth/login with JWT issuance | None |
| S-02 | Logout endpoint | POST /auth/logout with session invalidation | S-01 |
| S-03 | Token refresh | POST /auth/refresh with token rotation | S-01 |

## Execution Order

```text
S-01 → S-02 → S-03 (sequential; each depends on previous)
```
