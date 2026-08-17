# Review Plugin Index (Registry)

This file is the single authoritative plugin registry for the ForgeFlow Review
workflow. Each enabled plugin lives under `.forgeflow/rules/reviews/<name>/`.

## Plugin Table

| Name | Directory | Rules File | Enabled? | Priority | Depends On | Scope | Applicability | Report Format | Blocking Threshold | Description |
|------|-----------|-----------|----------|----------|------------|-------|---------------|---------------|-------------------|-------------|
| security | `security/` | `security/rules.md` | true | 1 | — | code, docs | Projects containing executable code or security-relevant configuration; individual rules may be N/A | md, csv | P0–P1 | Security vulnerability detection and compliance |
| coding-standard | `coding-standard/` | `coding-standard/rules.md` | true | 2 | security | code | Python source files only | md, csv | P0–P1 | Python coding style, naming, documentation, and typing conventions |
| architecture | `architecture/` | `architecture/rules.md` | true | 3 | — | code, docs | Implemented architectural surfaces only; API, database, and scaling rules may be N/A | md, html, csv | P0–P1 | Design boundaries, coupling, and modularity assessment |
| performance | `performance/` | `performance/rules.md` | true | 4 | architecture | code | Implemented runtime and data-processing surfaces only; absent technologies are N/A | md, csv | P0–P1 | Performance anti-patterns and efficiency analysis |

## Field Definitions

### Name

Lowercase plugin identifier using hyphens only.

### Directory

Plugin subdirectory under `.forgeflow/rules/reviews/`.

### Rules File

Exact rules path relative to `.forgeflow/rules/reviews/`. Review MUST resolve this
field directly and MUST NOT prepend `Directory` a second time.

### Enabled?

- `true` — evaluate the plugin when its dependencies and applicability allow it.
- `false` — skip the plugin.

### Priority

Lower numbers run first. Equal priorities run in alphabetical Name order.

### Depends On

Comma-separated plugin names that must be evaluated first. A dependent plugin is
skipped when any dependency is disabled or missing. Dependency cycles make the
registry invalid and block Review before checks run.

### Scope

- `code` — source code only.
- `docs` — design and artifact documentation only.
- `code, docs` — both.

### Applicability

Applicability determines whether relevant project evidence exists before compliance
is evaluated:

- an inapplicable plugin or rule is `N/A`, never PASS or VIOLATION;
- absence of an optional technology is not evidence of failure;
- Review records an observable reason for every `N/A` or `UNKNOWN` result;
- only applicable rules can produce blocking or non-blocking findings.

### Report Format

Comma-separated output formats. Supported values are `md`, `csv`, and `html`. Review
generates every configured format; the first is primary.

### Blocking Threshold

Severity range converted to BLOCKING when an applicable rule has verdict VIOLATION:

| Threshold | Blocking severities |
|-----------|---------------------|
| `P0` | P0 |
| `P0–P1` | P0 and P1 |
| `P0–P2` | P0, P1, and P2 |
| `P0–P3` | P0, P1, P2, and P3 |

Threshold controls disposition; the presence of a VIOLATION alone does not imply
Review FAIL.

## Execution Contract

Review performs these steps in order:

1. Read this registry and validate unique Names, Directories, Rules Files, and Priorities.
2. Resolve dependencies and sort enabled plugins deterministically.
3. Evaluate plugin applicability.
4. Resolve each applicable Rules File relative to `.forgeflow/rules/reviews/`.
5. Evaluate rule applicability, then record PASS, VIOLATION, UNKNOWN, or N/A.
6. Convert each VIOLATION to BLOCKING or NON_BLOCKING using its plugin threshold.
7. Generate configured reports at `.forgeflow/reports/<name>/report-feature-XX-slice-XX-attempt-NN.<format>`.
8. Decide Review FAIL only when one or more BLOCKING findings remain.

UNKNOWN is non-blocking unless separate observable evidence independently satisfies
the Framework definition of a blocking finding.

## Adding a Plugin

1. Create `.forgeflow/rules/reviews/<new-plugin>/rules.md`.
2. Add one complete registry row with an unused Priority.
3. Invoke Review for a concrete Slice attempt.

## Report Evidence

Plugin reports are supplemental evidence outside the active artifact graph. They
are attempt-scoped and MUST NOT overwrite another Feature, Slice, or attempt. The
immutable Review Report under the Artifact Root MUST contain the complete findings
needed for PASS/FAIL and transition resolution.
