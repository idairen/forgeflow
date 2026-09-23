# Review Plugin Registry

This is the single authority for Review plugins, their execution, severity mapping,
and supplemental reports. Each plugin lives under
`.forgeflow/rules/reviews/<name>/`.

## Plugins

| Name | Directory | Rules File | Enabled? | Priority | Depends On | Scope | Applicability | Formats | Blocking Threshold | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| security | `security/` | `security/rules.md` | true | 1 | — | code, docs | Executable code or security configuration; individual rules may be N/A | md, csv | P0–P1 | Security and compliance |
| coding-standard | `coding-standard/` | `coding-standard/rules.md` | true | 2 | security | code | Python source only | md, csv | P0–P1 | Python style, naming, documentation, typing |
| architecture | `architecture/` | `architecture/rules.md` | true | 3 | — | code, docs | Implemented architecture; absent API, database, scaling, or layout surfaces may be N/A | md, html, csv | P0–P1 | Boundaries, coupling, layout, modularity |
| performance | `performance/` | `performance/rules.md` | true | 4 | architecture | code | Implemented runtime/data surfaces; absent technologies are N/A | md, csv | P0–P1 | Efficiency and performance risks |

## Registry fields

| Field | Rule |
| --- | --- |
| Name | unique lowercase identifier using hyphens |
| Directory | unique plugin directory under this registry's directory |
| Rules File | exact unique path relative to this directory; never prepend Directory again |
| Enabled? | `true` evaluates; `false` skips |
| Priority | lower first; equal values sort by Name |
| Depends On | evaluate dependencies first; missing/disabled dependency skips dependent; a cycle invalidates Review |
| Scope | `code`, `docs`, or `code, docs` |
| Applicability | evidence required before compliance evaluation |
| Formats | comma-separated `md`, `html`, and/or `csv`; generate all, first is primary |
| Blocking Threshold | severities that turn VIOLATION into BLOCKING |

An inapplicable plugin or rule is N/A, never PASS or VIOLATION. Absence of optional
technology is not failure. Record observable evidence for N/A and UNKNOWN. UNKNOWN
is non-blocking unless separate evidence independently meets the Framework blocking
definition.

## Severity and disposition

| Severity | Meaning | Typical impact |
| --- | --- | --- |
| P0 | Critical | Security breach, data loss, severe regression |
| P1 | High | Material reliability, security, architecture, or scalability defect |
| P2 | Medium | Concrete maintainability or performance risk |
| P3 | Information | Suggestion without demonstrated material impact |

| Threshold | Blocking severities |
| --- | --- |
| `P0` | P0 |
| `P0–P1` | P0, P1 |
| `P0–P2` | P0, P1, P2 |
| `P0–P3` | P0, P1, P2, P3 |

Only an applicable VIOLATION receives BLOCKING or NON_BLOCKING from the registered
threshold. PASS, UNKNOWN, and N/A use disposition NONE. Review FAILs only when at
least one BLOCKING finding remains.

## Execution

1. Validate unique Names, Directories, and Rules Files, plus all field values and the
   dependency graph.
2. Sort enabled plugins by dependency, Priority, then Name.
3. Evaluate plugin applicability, then each rule's applicability.
4. Record PASS, VIOLATION, UNKNOWN, or N/A with required evidence.
5. Map VIOLATION through Blocking Threshold.
6. Archive any replaced report through the Artifact Protocol Reports History.
7. Generate every configured format.
8. Supply plugin findings to the canonical Review Report aggregate decision.

## Supplemental report contract

Write reports to:

```text
.forgeflow/reports/<name>/report-feature-<FeatureNumber>-slice-<SliceNumber>-attempt-<AttemptNumber>.<format>
```

Markdown and HTML contain rules version, Review date, aggregate status/counts, a
summary table, and details for VIOLATION/UNKNOWN. CSV carries equivalent structured
fields. The canonical summary is:

```markdown
| # | Rule ID | Description | Severity | Verdict | Disposition | Finding |
| --- | --- | --- | --- | --- | --- | --- |
```

Detailed entries identify rule, location/evidence source, expected result, and
remediation guidance.

Reports are attempt-scoped supplemental evidence outside the active Artifact Graph.
Never overwrite another Feature, Slice, attempt, or existing report. Replacing the
same canonical report requires immutable revision archival. The canonical Review
Report alone contains all findings needed for PASS/FAIL and transition.

## Adding a plugin

Create `<name>/rules.md`, add one complete registry row, then invoke Review for a
specific Slice attempt.
