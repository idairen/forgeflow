# Architecture Review Rules

**Plugin:** architecture  
**Version:** 1.1

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

Apply Registry verdict, evidence, and threshold rules only to the authorized Slice
and declared architecture. Absent architectural surfaces are N/A. ARC-003/009 apply
when current Solution/Slice defines structure; a pre-2.10 Solution's omission alone
is not a violation, so use repository evidence and UNKNOWN/N/A unless another current
contract requires RETURN. Judge the current contract, never a universal Java/Spring,
layer, or Feature packaging preference.
