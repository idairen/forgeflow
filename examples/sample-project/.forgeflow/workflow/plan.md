# Plan Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Planning |
| Output | Planning.md at `.forgeflow/artifacts/planning.md` |
| Required inputs | User Intent; existing system context |

## Sample Output: planning.md

This shows what the Plan workflow produces. The real LLM-generated artifact will contain project-specific content.

```markdown
# Planning

Metadata
---
| Artifact Type | Planning |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Plan |

## Project Intent

Build a RESTful API for a task management application using FastAPI and PostgreSQL.

## Features (Ordered List)

| Feature ID | Title | Description |
|------------|-------|-------------|
| F-01 | User Authentication | Login, logout, token refresh |
| F-02 | Task CRUD | Create, read, update, delete tasks |
| F-03 | Task Assignment | Assign tasks to users |

## Exclusions

- Mobile app (out of scope for v1)
- Payment processing (future release)
```
