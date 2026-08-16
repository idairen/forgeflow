# Grill Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Requirement-{F-XX}.md |
| Output | `requirement-feature-01.md` at `.forgeflow/artifacts/` |
| Required inputs | Planning.md; user intent |

## Sample Output: requirement-feature-01.md

```markdown
# Requirement F-01 — User Authentication

Metadata
---
| Artifact Type | Requirement |
| Feature ID | F-01 |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Grill |

## Behavior

- User MUST be able to login with email/password combination
- Token MUST expire after 3600 seconds (1 hour)
- Refresh token MUST rotate on each use

## Acceptance Criteria

1. `POST /auth/login` returns 200 with access_token and refresh_token
2. `POST /auth/logout` invalidates the current session
3. Invalid credentials return 401 Unauthorized

## Edge Cases

- Rate limiting: max 5 login attempts per minute per IP
- Token blacklisting: previously revoked tokens must fail validation
