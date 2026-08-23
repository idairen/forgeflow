# Review Workflow

Version: 2.12

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | Review Report |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Handoff Entry or Feature Lane Entry; current Requirement, Solution Plan, Slice Plan, TDD Record, and implementation evidence |

Review independently evaluates exactly one resolver-authorized Slice attempt. It is
read-only for code, tests, upstream plans, and the TDD Record. Target Scope and
attempt are the complete authorization boundary. When PASS or FAIL selects a future
scope, Review MUST only emit that Handoff and stop; it cannot fix, implement, review,
or create evidence for that target in this execution.

## Entry validation

Run Unified Entry Validation for Handoff Entry or Feature Lane Entry. Validate the
exact Target Scope, selected Lane action, artifact readiness, positive unused attempt,
completed effective dependencies, and complete upstream version chain. Reject stale,
mismatched, or duplicate-attempt evidence.

## Command execution

All commands follow the Framework Command execution policy. Independent reruns are
fresh evidence, not permission for another terminal or concurrent duplicate check.
Review MUST NOT start a duplicate check while an equivalent process is active. Reuse
one session when supported and terminate every started process before Handoff.

## Decision and disposition

Apply the Framework Review readiness and decision policy independently:

- PASS requires zero blocking findings and may retain non-blocking findings.
- FAIL requires one or more blocking findings.
- A preference without demonstrated correctness, compliance, or material
  maintainability impact cannot cause FAIL.

For FAIL, choose exactly one Return Workflow from all blocking finding owners using
Framework upstream precedence. Return Scope is the Affected Scope of one blocking
finding owned by that Workflow. Resolve every Feature/Slice identifier against
active Planning and the applicable Slice Plan before writing; findings cannot create
routing identifiers. Review records this disposition; Transition Resolution MUST NOT
infer or replace it.

The Review Report is the final aggregate decision artifact. Build exactly one
canonical Findings table first, then derive `Blocking Findings`, `Non-blocking
Findings`, `Decision`, `Return Workflow`, and `Return Scope`. A zero-finding report
keeps the header-only table. Plugin reports are supplemental and never replace or
independently determine the canonical decision.

## Required process

1. Read the positive `attempt` from the current `READY_FOR_REVIEW` TDD Record and
   reject an attempt already used by another Review Report.
2. Trace every Slice condition through tests, implementation, and recorded evidence.
3. Execute all enabled plugins through the authoritative Plugin Registry procedure.
   Before replacing a configured report path, archive its exact prior content using
   the Reports History Root procedure.
4. Inspect correctness, regressions, scope, security, maintainability, Solution
   conformance, and the complete knowledge trace from Feature Contract through
   implementation evidence.
5. Record each finding's severity, Owner Workflow, canonical Affected Scope,
   observable evidence, and violated contract in the canonical Findings table.
6. Decide PASS or FAIL. For FAIL, derive Return Workflow by upstream owner
   precedence and Return Scope from that owner's blocking finding.
7. Re-read Planning, Solution, Slice Plan, and TDD Record immediately before
   persistence. If Lane readiness, dependencies, shared access, or any version
   changed, do not publish a stale decision. Otherwise persist one immutable Review
   Report at its Canonical Artifact Path. Derive counts
   and disposition from the Findings rows and include return metadata only for FAIL.
8. Resolve every cited current decision and version to canonical Artifacts; history
   may explain evolution but cannot satisfy a current gate. Validate implemented
   dependencies, shared components, decision references, and current impact entries
   against structured Solution mappings when present.
9. Compare every created or moved production/test path with Solution
   Implementation/Test Structure, Slice Planned File Placement, and TDD File
   Placement Conformance. An explicit structure-contract violation is blocking under
   the architecture plugin; an unsupported organization preference is non-blocking.
10. Apply the Transition Resolution Procedure. If it selects a transition, validate
    and render exactly one Canonical Handoff Block as final response content, then
    stop without consuming its Target Scope.

## Emit conditions after Review completes a Slice

- **FORWARD (PASS)**: Rule 10 selects the next incomplete Slice in the same Lane, or the default next dependency-ready Lane after this Feature completes.
- **TERMINAL / COMPLETE (PASS)**: Rule 11 matches; emit Completed Scope `Project`.
- **RETURN (FAIL)**: Use the Review Report's selected Return Workflow and canonical Return Scope with Blocker Category `REVIEW_BLOCKER`; Rule 8 routes it.

## Findings and returns

| Finding owner | Canonical route |
| --- | --- |
| Local implementation, test, regression, or evidence defect | TDD, same Slice |
| Invalid Slice boundary, dependency, or completion gap | Slice, affected Feature |
| Missing or invalid engineering decision | Solution, Project; finding identifies affected Feature and Slice |
| Missing business policy | Grill, affected Feature |

Every finding cites observable evidence and the violated contract. Preferences with
no correctness or material maintainability consequence are non-blocking.

## Plugin Registry

`.forgeflow/rules/reviews/_index.md` is the sole registry and execution contract.
Review MUST NOT duplicate, infer, reorder, or locally redefine registry fields,
execution steps, thresholds, paths, or report schemas. Execute the registry contract
exactly, then aggregate each resulting `BLOCKING` row into canonical Findings.
Plugin reports remain attempt-scoped supplemental evidence outside the active
Artifact Graph; the Framework decision gate alone determines Review PASS or FAIL.

<!-- forgeflow-eof: .forgeflow/workflow/review.md -->
