# Review Workflow

Version: 2.9

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | Review Report |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Incoming Handoff; current Requirement, Solution Plan, Slice Plan, TDD Record, and implementation evidence |

Review independently evaluates exactly one resolver-authorized Slice attempt. It
is read-only with respect to code, tests, upstream plans, and the TDD Record.
The incoming Slice Target Scope and attempt are the complete authorization boundary
for this execution. A PASS or FAIL may select a future execution scope, but Review
MUST only emit that Handoff and stop; it MUST NOT fix, implement, review, or create
evidence for the selected target in this execution.

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
the Affected Scope of one blocking finding owned by it as Return Scope. Review
does not rely on the Transition Protocol to infer or replace this disposition.
Before writing the report, every Feature or Slice identifier in every finding and
Return Scope MUST resolve in active Planning and the applicable Canonical Slice
Plan. Findings and conversation text cannot create a new routing identifier.

The Review Report is the final aggregate decision artifact. It MUST contain exactly
one canonical Findings table using the exact structure defined by the Artifact
Protocol. Build that table first, then derive Blocking Findings, Non-blocking
Findings, Decision, Return Workflow, and Return Scope from its rows. A zero-finding
report retains the header-only table. Plugin reports are supplemental evidence and
never replace or independently determine the core Review Report fields.

## Required process

1. Read the positive `attempt` from the current READY_FOR_REVIEW TDD Record and
   reject an attempt already used by another Review Report.
2. Trace every Slice condition to tests, implementation, and recorded evidence.
3. Run all enabled plugin-based automated checks (security, coding-standard,
   architecture, performance) defined in `.forgeflow/rules/reviews/_index.md`.
   Follow each plugin's `rules.md` checklist for structured checking. Before writing
   any supplemental report path that already exists, archive its exact prior content
   through the Reports History Root procedure.
4. Inspect correctness, regressions, scope discipline, security, maintainability,
   conformance with the Solution Plan, and consistency of the complete knowledge
   trace from Feature Contract through implementation evidence.
5. For every finding, record severity, Owner Workflow, Affected Scope, observable
   Evidence details (code snippets, test output excerpts, log lines), and
   Violated Contract. These finding records must be written into the Review Report
   artifact as the findings table so downstream workflows can inspect the full
   evidence chain.
6. Decide PASS or FAIL using the shared gate. For FAIL, select Return Workflow by
   upstream owner precedence and use that owner's canonical Return Scope.
7. Persist a new immutable Review Report at its Canonical Artifact Path. Write the
   exact canonical Findings table first, derive its counts and disposition, and
   include return metadata only when applicable.
8. Confirm that cited current decisions and versions resolve to canonical Artifacts;
   historical evidence may explain evolution but MUST NOT satisfy a current gate.
   When the current Solution contains structured impact metadata, also confirm that
   implemented dependencies, shared-component use, and decision references agree
   with the targeted Feature's mappings and that every current impact entry resolves.
9. Compare every created or moved production/test path with the Solution
   Implementation/Test Structure, Slice Planned File Placement, and TDD File
   Placement Conformance table. A concrete violation of an explicit structure
   contract is blocking according to the architecture plugin; a mere preference
   not established by repository evidence or Solution remains non-blocking.
10. Apply the Transition Resolution Procedure. If it requires a handoff, validate
   and render exactly one Canonical Handoff Block from the Handoff Protocol as the
   final content of the response, then stop without consuming its Target Scope.



## Emit conditions after Review completes a Slice

After producing a Review Report:

- **FORWARD (PASS)**: When all findings are non-blocking and Rule 10 selects another
  incomplete Slice, forward to TDD at that Slice scope.
- **TERMINAL / COMPLETE (PASS)**: When Rule 11 matches after this PASS, emit the
  successful terminal variant with Completed Scope `Project`.
- **RETURN per findings table (FAIL)**: When one or more blocking findings exist — emit
  a RETURN per the Review Report Findings Table, which determines the Return Workflow and
  canonical Return Scope. The RETURN Handoff uses Blocker Category `REVIEW_BLOCKER`.
  The Transition Resolution Procedure uses Rule 8 to route this.

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

`.forgeflow/rules/reviews/_index.md` is the single authoritative registry. Review
MUST NOT duplicate or infer registry fields locally. Each Rules File is resolved
relative to `.forgeflow/rules/reviews/` using the exact registered path.

## Plugin Execution Flow

For each **enabled** plugin in the registry:

1. Resolve dependencies and the registered Rules File.
2. Evaluate plugin applicability; if inapplicable, record plugin N/A with evidence.
3. For each rule in an applicable plugin:
    a. Evaluate rule applicability before compliance.  
    b. Record PASS, VIOLATION, UNKNOWN, or N/A.  
    c. Capture evidence for VIOLATION, UNKNOWN, and N/A.  
    d. Map each VIOLATION through the registered Blocking Threshold to BLOCKING or
       NON_BLOCKING.
4. Compile every configured report format.
5. Save reports to `.forgeflow/reports/<plugin-name>/report-feature-XX-slice-XX-attempt-NN.<format>`.
   Existing files at that exact path are archived first under
   `.forgeflow/reports/history/<plugin-name>/` with the next revision suffix.

After all plugins complete, aggregate verdicts:
- one or more BLOCKING findings → Review FAIL;
- zero BLOCKING findings → Review PASS, including NON_BLOCKING, UNKNOWN, and N/A;
- UNKNOWN remains non-blocking unless separate observable evidence independently
  satisfies the Framework definition of a blocking finding.

## Report Generation

Each plugin generates attempt-scoped supplemental reports under
`.forgeflow/reports/<plugin-name>/`:

### Report Structure

```markdown
# <Plugin Name> Review Report

**Version:** <rules.md version>
**Review Date:** YYYY-MM-DD
**Status:** PASS / VIOLATION / UNKNOWN / N/A (with counts by disposition)

## Summary Table

| # | Rule ID | Description | Severity | Verdict | Disposition | Finding |
|---|---------|-------------|----------|---------|-------------|---------|
| 1 | SEC-001 | No hardcoded passwords | P0 | VIOLATION | BLOCKING | Password found in config.py:15 |
| 2 | SEC-002 | SQL Injection Prevention | P0 | PASS | NONE | All queries parameterized |

## Detailed Findings (VIOLATION/UNKNOWN items only)

### SEC-001 — No hardcoded passwords [P0] [BLOCKING]

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
| MD (default) | `.forgeflow/reports/<name>/report-feature-XX-slice-XX-attempt-NN.md` | Git-tracked, auditable |
| HTML | `.forgeflow/reports/<name>/report-feature-XX-slice-XX-attempt-NN.html` | Dashboard / Wiki display |
| CSV/Excel | `.forgeflow/reports/<name>/report-feature-XX-slice-XX-attempt-NN.csv` | CI/CD dashboards, data filtering |

Review generates every format configured by the authoritative registry.

## Severity Classification Standard

Use this unified severity scale across all plugins:

| Level | Name | Impact | Block? | Example |
|-------|------|--------|--------|---------|
| P0 | Critical | Security breach, data loss risk, or severe regression | When included by registered threshold; normally always included | Hardcoded password, SQL injection, required test failure |
| P1 | High | Material reliability, security, or scalability defect | When included by registered threshold | Missing auth on a protected endpoint, evidenced N+1 query on a hot path |
| P2 | Medium | Concrete maintainability or performance risk | Only when registered threshold includes P2 | Repeated risky duplication or evidenced inefficient processing |
| P3 | Info | Best-practice suggestion with no material impact | Only when registered threshold includes P3 | Naming alternative or optional refactor |

## Adding a New Plugin

To extend the review engine with a new custom check:

1. Create `.forgeflow/rules/reviews/<new-plugin>/rules.md`
2. Write rule checks in checklist table format (see existing plugins as template)
3. Add an entry to `.forgeflow/rules/reviews/_index.md` with `Enabled? = true`
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
