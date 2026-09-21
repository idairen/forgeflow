# Performance Review Rules

**Plugin:** performance  
**Version:** 1.0  

## Checklist

| # | Rule ID | Description | Severity | Check Criteria | Expected Result |
|---|---------|-------------|----------|----------------|-----------------|
| 1 | PERF-001 | N+1 Query Detection — No Loop Queries Without Batching | P0 | Scan for loops that issue individual database queries; check for `select_related`/`prefetch_related` or batch operations | No unbatched queries inside loops; use bulk_create, select_related, prefetch_related, or JOIN where appropriate |
| 2 | PERF-002 | Missing Cache on Repeated Reads | P1 | Verify that frequently accessed data (user profiles, configurations, lookups) uses caching (Redis, Memcached, LRU cache) | Hot reads are cached with TTL; no repeated expensive computations without memoization |
| 3 | PERF-003 | Blocking Synchronous Calls to External Services | P1 | Check for synchronous HTTP calls in request-handling code paths that could block the thread pool | External service calls use async/await, background tasks, or at least non-blocking patterns; timeouts are set |
| 4 | PERF-004 | Unbounded Data Structures and Memory Leaks | P2 | Audit for unbounded caches, infinite lists growing in memory, unclosed file handles, missing cleanup in finally blocks | All caches have size limits with eviction; file/stream resources closed properly; no global mutable state leaks |
| 5 | PERF-005 | Excessive Computation in Hot Paths — O(n²) or Worse | P2 | Identify patterns like nested loops over large datasets, redundant sorting, unnecessary deep copies | Critical paths use efficient algorithms (O(n log n) or better); avoid re-sorting inside inner loops |
| 6 | PERF-006 | Database Index Absence on Filter/Join Columns | P1 | Check that columns used in WHERE, ORDER BY, and JOIN conditions have appropriate indexes | Tables have indexes on foreign keys and frequently filtered columns; explain plans show index usage |
| 7 | PERF-007 | Large Payload Transfers — No Pagination | P2 | Verify that APIs returning lists paginate results with cursor-based or offset-based pagination | List endpoints return paginated responses (limit/offset or cursor); default page size is reasonable (≤100) |
| 8 | PERF-008 | Image/File Processing — No Synchronous Heavy Operations | P3 | Check for synchronous image resizing, PDF generation, or file encoding in request handlers | Heavy operations run asynchronously or via background workers; response does not block on processing |

## Execution Notes

Apply Registry verdict, evidence, and threshold rules within the authorized Slice and
demonstrated runtime paths. Absent technology is N/A; missing profiling is UNKNOWN
unless a current contract requires that evidence.
