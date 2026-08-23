# Architecture Review Rules

**Plugin:** architecture  
**Version:** 1.1
**Severity Guide:** P0=Critical, P1=High, P2=Medium, P3=Info; blocking disposition is determined exclusively by the registry threshold

## Checklist

| # | Rule ID | Description | Severity | Check Criteria | Expected Result |
|---|---------|-------------|----------|----------------|-----------------|
| 1 | ARC-001 | Layer Separation — No Cross-Layer Violations | P1 | Verify that architectural layers (e.g., presentation → business logic → data access) are strictly separated | No layer imports from non-adjacent layers; e.g., view layer must not directly access database models |
| 2 | ARC-002 | Dependency Injection / Loose Coupling | P1 | Check that components are loosely coupled using interfaces, abstract base classes, or DI patterns | Classes depend on abstractions rather than concrete implementations; no tightly-coupled direct instantiation chains |
| 3 | ARC-003 | Contracted Source Structure Conformance | P1 | Compare every created or moved production path with the current Solution Implementation Structure and Slice Planned File Placement | Source roots, packages/modules, responsibilities, and dependency direction conform; roles separated by the contract are not collapsed into one package/module |
| 4 | ARC-004 | API Design — RESTful Conventions and Consistency | P2 | Verify endpoint naming conventions, HTTP method usage (GET/POST/PUT/DELETE), response format consistency | Endpoints follow REST conventions; responses use consistent JSON structure with proper status codes |
| 5 | ARC-005 | Database Schema — Proper Indexing and Normalization | P1 | Review database schema for missing indexes on frequently queried columns, over-normalization or under-normalization | Tables have appropriate primary/foreign keys; indexes exist on high-selectivity filter columns; no excessive JOIN depth (>3) |
| 6 | ARC-006 | Error Handling Architecture — Centralized Strategy | P2 | Check that error handling follows a centralized pattern (e.g., global exception handler, middleware) | No scattered try/except blocks without a top-level handler; errors bubble up to a central resolver |
| 7 | ARC-007 | Scalability Assessment — Horizontal Readiness | P2 | Evaluate whether architecture supports horizontal scaling (statelessness, caching strategy, DB sharding considerations) | Stateless services where possible; cache layer defined; no session-local state that prevents distribution |
| 8 | ARC-008 | General Package/Module Cohesion | P2 | Evaluate organization concerns not already established as explicit Solution/Slice contracts | Related functionality is co-located, catch-all utility areas are avoided, and recommendations remain non-blocking unless concrete material risk is shown |
| 9 | ARC-009 | Contracted Test Structure Conformance | P1 | Compare created or moved test paths with the Solution Test Structure, Slice placement, and production relationship | Unit/component tests mirror production packages/modules when required; integration/contract/e2e tests use their declared roots and patterns |

## Execution Notes

- Evaluate applicability before compliance. Layering, dependency injection, REST,
  database, centralized error handling, and horizontal scaling rules are N/A when
  the authorized Slice and Solution Plan do not contain that architectural surface.
- Record PASS, VIOLATION, UNKNOWN, or N/A with observable evidence.
- Apply the registry Blocking Threshold to each VIOLATION. Review only files and
  documents needed for the authorized Slice and its declared architectural context.
- ARC-003 and ARC-009 are applicable when the current Solution/Slice establishes a
  structure contract. A legacy Solution with no such contract is not by
  itself a violation; use observable repository conventions and report missing
  evidence as UNKNOWN or N/A unless another current contract requires RETURN.
- Do not prescribe Java/Spring package names, package-by-layer, or package-by-Feature
  as a universal rule. Judge conformance to the current engineering contract.
