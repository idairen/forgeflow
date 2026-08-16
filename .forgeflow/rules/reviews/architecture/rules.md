# Architecture Review Rules

**Plugin:** architecture  
**Version:** 1.0  
**Severity Guide:** P0=Critical(blocking), P1=High(blocking), P2=Medium(non-blocking), P3=Info(suggestion)

## Checklist

| # | Rule ID | Description | Severity | Check Criteria | Expected Result |
|---|---------|-------------|----------|----------------|-----------------|
| 1 | ARC-001 | Layer Separation — No Cross-Layer Violations | P1 | Verify that architectural layers (e.g., presentation → business logic → data access) are strictly separated | No layer imports from non-adjacent layers; e.g., view layer must not directly access database models |
| 2 | ARC-002 | Dependency Injection / Loose Coupling | P1 | Check that components are loosely coupled using interfaces, abstract base classes, or DI patterns | Classes depend on abstractions rather than concrete implementations; no tightly-coupled direct instantiation chains |
| 3 | ARC-003 | Package Structure — Coherent Module Boundaries | P2 | Audit package directory structure for logical grouping of related code | Related functionality is co-located; no mixed responsibilities within a single module/package |
| 4 | ARC-004 | API Design — RESTful Conventions and Consistency | P2 | Verify endpoint naming conventions, HTTP method usage (GET/POST/PUT/DELETE), response format consistency | Endpoints follow REST conventions; responses use consistent JSON structure with proper status codes |
| 5 | ARC-005 | Database Schema — Proper Indexing and Normalization | P1 | Review database schema for missing indexes on frequently queried columns, over-normalization or under-normalization | Tables have appropriate primary/foreign keys; indexes exist on high-selectivity filter columns; no excessive JOIN depth (>3) |
| 6 | ARC-006 | Error Handling Architecture — Centralized Strategy | P2 | Check that error handling follows a centralized pattern (e.g., global exception handler, middleware) | No scattered try/except blocks without a top-level handler; errors bubble up to a central resolver |
| 7 | ARC-007 | Scalability Assessment — Horizontal Readiness | P2 | Evaluate whether architecture supports horizontal scaling (statelessness, caching strategy, DB sharding considerations) | Stateless services where possible; cache layer defined; no session-local state that prevents distribution |

## Execution Notes

- Apply each rule against the design documents, code structure, and any architectural decision records.
- Mark `[x]` if compliant, `[!]` if violated, `[~]` if unclear or partially implemented.
- P1 violations are structural — fix them before adding more features.
- Some rules require reading multiple files; ensure all source directories are scanned.
