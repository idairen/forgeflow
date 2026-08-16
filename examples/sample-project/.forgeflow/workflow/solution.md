# Solution Workflow — Sample

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | SolutionPlan.md |
| Output | `solution-plan.md` at `.forgeflow/artifacts/` |
| Required inputs | All READY Requirements; Planning.md |

## Sample Output: solution-plan.md

```markdown
# Solution Plan F-01/F-02/F-03

Metadata
---
| Artifact Type | SolutionPlan |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Solution |

## Architecture

The project uses a **layered architecture**:
- API Layer: FastAPI with OpenAPI docs at `/docs`
- Service Layer: Business logic modules per domain (auth, task, assign)
- Data Layer: PostgreSQL via SQLAlchemy ORM

## Technology Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Web Framework | FastAPI 0.104+ | Auto OpenAPI docs, async support |
| Database | PostgreSQL 15 | Relational integrity, JSON support |
| ORM | SQLAlchemy 2.0 | Type hints, migration tools |

## Key Decisions

1. Use JWT for stateless auth; refresh tokens stored in HTTP-only cookies
2. Implement request validation with Pydantic models
3. Add logging middleware for audit trails
4. No caching layer in v1 (add Redis if P95 > 200ms)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database migration failure | High | Use Alembic with rollback scripts |
| JWT token theft | Medium | Enforce HTTPS only; short expiry |
