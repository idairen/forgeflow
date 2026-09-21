# Security Review Rules

**Plugin:** security  
**Version:** 1.0  

## Checklist

| # | Rule ID | Description | Severity | Check Criteria | Expected Result |
|---|---------|-------------|----------|----------------|-----------------|
| 1 | SEC-001 | No hardcoded passwords or API keys | P0 | Scan all source files for literal string assignments to variables named `password`, `passwd`, `api_key`, `secret`, `token`, `credential` | All credentials must come from environment variables or a secrets manager (e.g., Vault, AWS Secrets Manager) |
| 2 | SEC-002 | SQL Injection Prevention | P0 | Verify that all database query constructions use parameterized queries or ORM methods | No raw SQL interpolation with user input; only `?` placeholders, `%s` parameters, or ORM calls |
| 3 | SEC-003 | Authentication before Authorization | P1 | Check that protected API endpoints and routes have auth middleware/guards applied | Every protected route has an auth control; intentionally public routes are documented and expose no protected data |
| 4 | SEC-004 | Input Validation on All Entry Points | P1 | Verify that all user-provided inputs (forms, APIs, file uploads) are validated and sanitized before use | Input is type-checked, length-limited, and escaped/sanitized before processing or storage |
| 5 | SEC-005 | Secure Logging — No Sensitive Data Leakage | P2 | Audit log statements for raw tokens, PII, passwords, or secrets being written to logs | Logs contain masked/redacted values; no plaintext credentials or tokens |
| 6 | SEC-006 | Dependency Security — Known Vulnerabilities | P2 | Check `requirements.txt` / `pyproject.toml` against known CVE databases (e.g., OSV, Snyk) | No dependencies with high/critical severity CVEs in the installed version range |
| 7 | SEC-007 | Rate Limiting on Public APIs | P2 | Verify that public-facing endpoints have rate limiting or throttling configured | All public API routes include a rate limiter; responses return 429 when exceeded |
| 8 | SEC-008 | Error Handling — No Stack Traces to Clients | P3 | Check error handlers for exposure of stack traces, internal paths, or database errors to end users | Errors return generic messages; stack traces logged server-side only |

## Execution Notes

Apply Registry verdict, evidence, and threshold rules. Database, API, dependency,
logging, and rate-limit checks are N/A when that surface is absent from the Slice.
