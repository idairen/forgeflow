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

## Acceptance Criteria

1. `POST /auth/login` returns 200 with access_token and refresh_token
2. Invalid credentials return 401 Unauthorized
