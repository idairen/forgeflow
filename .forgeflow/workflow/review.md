# Review Workflow

Version: 2.2

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | Review Report |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Incoming Handoff; current Requirement, Solution Plan, Slice Plan, TDD Record, and implementation evidence |

Review independently evaluates exactly one resolver-authorized Slice attempt. It
is read-only with respect to code, tests, upstream plans, and the TDD Record.

## Entry validation

Review MUST first execute the Unified Entry Validation Procedure defined in the
Handoff Protocol before accepting any handoff block. It then validates its typed
handoff, exact Target Scope, artifact readiness, and the complete upstream version
chain. Stale or mismatched evidence cannot be reviewed as current work.

## Command execution

Every Review command MUST follow the Framework Command execution policy. An
independent rerun is fresh evidence, not a reason to create another terminal tab or
run concurrently. Review MUST reuse the same terminal tab or equivalent session
when supported, MUST NOT start a duplicate check while an equivalent process is
active, and MUST terminate every process it starts before its handoff.

## Decision and disposition

Review MUST independently apply the Framework Review readiness and decision
policy. It decides PASS with zero blocking findings, including when non-blocking
findings remain, and decides FAIL with one or more blocking findings. Preferences
without a demonstrated correctness, compliance, or material maintainability
consequence MUST NOT cause FAIL.

For FAIL, Review selects exactly one Return Workflow from all blocking finding
owners using the Framework's upstream precedence and records that workflow and
its canonical Return Scope in Review Report metadata. Review does not rely on the
Transition Protocol to infer or replace this disposition.

## Required process

1. Read the positive `attempt` from the current READY_FOR_REVIEW TDD Record and
   reject an attempt already used by another Review Report.
2. Trace every Slice condition to tests, implementation, and recorded evidence.
3. Run all enabled plugin-based automated checks (security, coding-standard,
   architecture, performance) defined in `.forgeflow/rules/reviews/_index.md`.
   Follow each plugin's `rules.md` checklist for structured checking.
4. Inspect correctness, regressions, scope discipline, security, maintainability,
   and conformance with the Solution Plan.
5. For every finding, record severity, Owner Workflow, Affected Scope, observable
   Evidence details (code snippets, test output excerpts, log lines), and
   Violated Contract. These finding records must be written into the Review Report
   artifact as the findings table so downstream workflows can inspect the full
   evidence chain.
6. Decide PASS or FAIL using the shared gate. For FAIL, select Return Workflow by
   upstream owner precedence and use that owner's canonical Return Scope.
7. Persist a new immutable Review Report at its Canonical Artifact Path. The report
   MUST include the attempt number, PASS/FAIL decision, total finding counts broken
   down by blocking vs non-blocking severity, the complete findings table (each entry
   containing severity, Owner Workflow, Affected Scope, full evidence details, and
   Violated Contract), and return metadata when applicable.
8. Apply the Transition Resolution Procedure. If it requires a handoff, validate
   and render exactly one Canonical Handoff Block from the Handoff Protocol as the
   final content of the response.



## Emit conditions after Review completes a Slice

After producing a Review Report:

- **FORWARD (PASS)**: When all findings are non-blocking — forward to the next workflow
  in the pipeline (typically TDD for the next Slice, or Plan/TERMINAL if all slices complete).
- **RETURN per findings table (FAIL)**: When one or more blocking findings exist — emit
  a RETURN per the Review Report Findings Table, which determines the Return Workflow and
  canonical Return Scope. The Transition Resolution Procedure uses Rule 6 to route this.

## Findings and returns

- Implementation, test, regression, or local evidence defect: TDD, same Slice
  Target Scope.
- Invalid Slice boundary, dependency, or completion gap: Slice, affected Feature
  Target Scope.
- Missing or invalid engineering decision: Solution, Project Target Scope; record
  the affected Feature and Slice on the finding.
- Missing business policy: Grill, affected Feature Target Scope.

Every finding MUST cite observable evidence and the violated contract. Preferences
without a correctness or maintainability consequence are non-blocking.

---

# Plugin-Based Review Extensions

This section defines how custom review plugins integrate into the workflow.
The core decision logic, entry validation, and disposition policy remain unchanged.

## Plugin Registry

All enabled plugins are registered in `.forgeflow/rules/reviews/_index.md`.
Each plugin lives in its own subdirectory with a `rules.md` file containing
a structured checklist of rules to apply against project artifacts.

| Plugin | Directory | Rules File | Enabled? | Report Dir |
|--------|-----------|-----------|----------|------------|
| security | `security/` | `rules/security/rules.md` | true | `reports/security/` |
| coding-standard | `coding-standard/` | `rules/coding-standard/rules.md` | true | `reports/coding-standard/` |
| architecture | `architecture/` | `rules/architecture/rules.md` | true | `reports/architecture/` |
| performance | `performance/` | `rules/performance/rules.md` | true | `reports/performance/` |

## Plugin Execution Flow

For each **enabled** plugin in the registry:

1. Read `.forgeflow/rules/reviews/<plugin-name>/rules.md` to load the checklist
2. For each rule row in the checklist table:
    a. Apply the check criteria against relevant artifacts  
    b. Record verdict: `[x] PASS` / `[!] FAIL` / `[~] WARN/N/A`
    c. Capture evidence for any FAIL or WARN result
3. Compile results into a structured report
4. Save report to `.forgeflow/reports/<plugin-name>/report.md`

After all plugins complete, aggregate verdicts:
- **ALL PASS** → `PASS` (proceed to next workflow)
- **ANY `[!] FAIL`** → `FAIL` (block until critical/high issues resolved)
- **All `[~]` only** → `PASS with warnings` (non-blocking)

## Report Generation

Each plugin generates a standalone report at `.forgeflow/reports/<plugin-name>/report.md`:

### Report Structure

```markdown
# <Plugin Name> Review Report

**Version:** <rules.md version>
**Review Date:** YYYY-MM-DD
**Status:** PASS / FAIL / WARN (with counts by severity)

## Summary Table

| # | Rule ID | Description | Severity | Status | Finding |
|---|---------|-------------|----------|--------|---------|
| 1 | SEC-001 | No hardcoded passwords | P0 | [!] FAIL | Password found in config.py:15 |
| 2 | SEC-002 | SQL Injection Prevention | P0 | [x] PASS | All queries parameterized |

## Detailed Findings (FAIL/WARN items only)

### SEC-001 — No hardcoded passwords [P0] [!]

**Location:** `config.py`, line 15
```python
db_password = "admin123"   # Should use env var or Vault
```

**Expected:** Credentials from environment variables or secrets manager.
**Fix:** Replace with `os.environ.get('DB_PASSWORD')` or vault reference.

---
```

### Report Outputs Per Format

| Format | Location | Use Case |
|--------|----------|----------|
| MD (default) | `.forgeflow/reports/<name>/report.md` | Git-tracked, auditable |
| HTML | `.forgeflow/reports/<name>/report.html` | Dashboard / Wiki display |
| CSV/Excel | `.forgeflow/reports/<name>/report.csv` | CI/CD dashboards, data filtering |

For now, the default output is **MD**. HTML and CSV exports can be added later.

## Severity Classification Standard

Use this unified severity scale across all plugins:

| Level | Name | Impact | Block? | Example |
|-------|------|--------|--------|---------|
| P0 | Critical | System security breach, data loss risk, or severe regression | **Yes** (always blocks) | Hardcoded password, SQL injection, test failure on main branch |
| P1 | High | Architectural flaw that degrades reliability or scalability | **Yes** (should block) | Missing auth on endpoint, N+1 query on hot path, no error handling |
| P2 | Medium | Maintainability issue or technical debt accumulation | No (warn only) | Naming convention violation, missing docstring, unbatched cache key |
| P3 | Info | Best-practice suggestion with no material impact | No (info only) | Code style preference, naming alternative, optional refactor |

## Adding a New Plugin

To extend the review engine with a new custom check:

1. Create `.forgeflow/rules/reviews/<new-plugin>/rules.md`
2. Write rule checks in checklist table format (see existing plugins as template)
3. Add an entry to the Plugin Registry table above with `Enabled? = true`
4. Run review — all enabled plugins execute automatically

## Backward Compatibility

The following existing behavior is **not changed** by plugin-based extensions:

- Entry validation and handoff protocol remain identical
- Decision and disposition policy (PASS/FAIL) unchanged
- Output format for handoff block unchanged
- Findings table structure in Review Report artifact unchanged
- Return workflow selection logic unchanged

Plugins only add **more structured checking** on top of existing review steps.
They do not alter the decision gate or routing behavior.
