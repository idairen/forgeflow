# Review Plugin Index (Registry)

This file is the single authoritative plugin registry for the ForgeFlow Review
workflow. Each enabled plugin lives under `.forgeflow/rules/reviews/<name>/`.

## Plugin Table

| Name | Directory | Rules File | Enabled? | Priority | Depends On | Scope | Applicability | Report Format | Blocking Threshold | Description |
|------|-----------|-----------|----------|----------|------------|-------|---------------|---------------|-------------------|-------------|
| security | `security/` | `security/rules.md` | true | 1 | — | code, docs | Projects containing executable code or security-relevant configuration; individual rules may be N/A | md, csv | P0–P1 | Security vulnerability detection and compliance |
| coding-standard | `coding-standard/` | `coding-standard/rules.md` | true | 2 | security | code | Python source files only | md, csv | P0–P1 | Python coding style, naming, documentation, and typing conventions |
| architecture | `architecture/` | `architecture/rules.md` | true | 3 | — | code, docs | Implemented architectural surfaces only; API, database, scaling, and explicit source/test layout rules may be N/A | md, html, csv | P0–P1 | Design boundaries, coupling, source/test structure, and modularity assessment |
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

### Canonical Report Serialization

Every configured report represents the same ordered rule-result set. Include one
result for every rule in Rules File checklist order, including `N/A` results. Copy
Rule ID, Description, and Severity from the Rules File without reinterpretation.
`Verdict` is exactly `PASS`, `VIOLATION`, `UNKNOWN`, or `N/A`. `Disposition` is
`BLOCKING` or `NON_BLOCKING` only for `VIOLATION`; every other verdict uses `NONE`.
Evidence is non-empty and observable for every result.

Derive `Overall Verdict` in this order: `VIOLATION` when any result is
`VIOLATION`; otherwise `UNKNOWN` when any result is `UNKNOWN`; otherwise `PASS`
when any result is `PASS`; otherwise `N/A`. This supplemental verdict does not
replace the Review decision: only `BLOCKING` results contribute canonical Findings
and cause Review FAIL.

Angle-bracketed values in the templates below are metavariables and MUST be replaced.

#### Markdown Template

An `md` report MUST use exactly this structure and field order:

```markdown
# <registry Name> Review Report

## Metadata

| Field | Value |
| --- | --- |
| Plugin | <registry Name> |
| Rules Version | <Rules File Version> |
| Feature ID | <F-XX> |
| Slice ID | <S-XX> |
| Attempt | <positive integer> |
| Overall Verdict | <PASS, VIOLATION, UNKNOWN, or N/A> |
| PASS Count | <non-negative integer> |
| VIOLATION Count | <non-negative integer> |
| UNKNOWN Count | <non-negative integer> |
| N/A Count | <non-negative integer> |
| BLOCKING Count | <non-negative integer> |
| NON_BLOCKING Count | <non-negative integer> |

## Results

| Rule ID | Description | Severity | Verdict | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| <Rule ID> | <exact description> | <P0, P1, P2, or P3> | <PASS, VIOLATION, UNKNOWN, or N/A> | <BLOCKING, NON_BLOCKING, or NONE> | <observable evidence> |
```

Metadata counts MUST equal the Results rows. Escape a literal `|` inside a table
cell as `\|` and render an embedded line break as `<br>`. Do not add another
heading, summary table, findings section, or explanatory text.

#### CSV Template

A `csv` report MUST be UTF-8 RFC 4180 data with exactly this header:

```csv
Plugin,Rules Version,Feature ID,Slice ID,Attempt,Overall Verdict,PASS Count,VIOLATION Count,UNKNOWN Count,N/A Count,BLOCKING Count,NON_BLOCKING Count,Rule ID,Description,Severity,Verdict,Disposition,Evidence
```

Write exactly one record per rule in Rules File checklist order and no comment,
summary, or blank records. Repeat identical metadata and count values on every
record. Quote a field containing a comma, quote, CR, or LF and double embedded
quotes. Normalize an Evidence line break to the two literal characters `\n` before
CSV escaping. The CSV rows MUST contain the same rules, verdicts, dispositions,
evidence, and counts as the Markdown report for the same plugin attempt.

An `html` report MUST contain the same metadata and ordered results, but its markup
is not a canonical serialization format.

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
7. Before replacing an existing configured report path, archive its exact prior file
   under `.forgeflow/reports/history/<name>/` using the Artifact Protocol's next
   revision suffix.
8. Generate configured reports at `.forgeflow/reports/<name>/report-feature-XX-slice-XX-attempt-NN.<format>`.
9. Decide Review FAIL only when one or more BLOCKING findings remain.

UNKNOWN is non-blocking unless separate observable evidence independently satisfies
the Framework definition of a blocking finding.

## Adding a Plugin

1. Create `.forgeflow/rules/reviews/<new-plugin>/rules.md`.
2. Add one complete registry row with an unused Priority.
3. Invoke Review for a concrete Slice attempt.

## Report Evidence

Plugin reports are supplemental evidence outside the active artifact graph. They
are attempt-scoped and MUST NOT overwrite another Feature, Slice, or attempt. The
Reports History Root is immutable and never participates in the current report set.
Replacing the same Feature, Slice, attempt, plugin, and format requires archival;
silent overwrite is forbidden. The
immutable Review Report under the Artifact Root MUST contain the complete findings
needed for PASS/FAIL and transition resolution.
