# TDD Workflow

Version: 2.11

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | TDD Record |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Valid Handoff Entry or Recovery Entry; current Requirement, Solution Plan, and Slice Plan |

Target Scope MUST identify exactly one Feature and Slice and equal a fresh
Transition Resolution result. Conversation text, filenames, or remembered state
cannot widen it. Completing the Slice does not authorize Review or the next Slice
in this execution; a later scope is reported only through a Canonical Handoff.

## Entry validation

Before changing tests or code, TDD MUST:

1. run Unified Entry Validation for Handoff Entry or Feature Lane Entry and confirm
   this exact TDD/Slice action, or accept only Recovery selected by fresh Rule 3 for
   this Slice from a current `IMPLEMENTATION_GAP`;
2. validate `LANE_DELIVERY_READY` for the Feature, including completed effective
   dependencies, and the complete Requirement/Solution/Slice version chain,
   and Solution Version against the Feature's current Feature Engineering Version;
3. locate the exact Slice, reject stale or mismatched evidence and out-of-scope work,
   then inspect applicable implementation and repository instructions; and
4. resolve every production and test responsibility through Planned File Placement
   and the Solution Implementation/Test Structure before editing files. Concrete
   filenames may follow an approved pattern and established convention, but TDD MUST NOT
   choose a new package, module, layer, or test-topology strategy.

## Command execution

All commands follow the Framework Command execution policy. RED, GREEN, refactor,
and verification run sequentially unless the Slice requires concurrency. Reuse one
session when supported, prefer bounded one-shot commands, record required
concurrency, and terminate every started process before Handoff.

When authorized by the current Solution and Slice, TDD may implement
application database schemas, migrations, tables, indexes, seed or fixture data, and
SQL records required by the targeted Slice. Keep them within approved
project/test/development surfaces, test them, record migration evidence, and include
them in the TDD Record. TDD MUST NOT use an
application database or SQL tool to persist ForgeFlow decisions, questions, cursors,
session plans, or workflow progress.

## Review readiness self-check

Before `READY_FOR_REVIEW`, TDD MUST:

- trace every applicable Requirement behavior and Slice condition through Solution
  to implementation, tests, and evidence;
- inspect the complete Slice change for scope, regressions, security, concrete
  maintainability risk, and repository-required checks;
- correct every local implementation, test, placement, or evidence blocker;
- apply the Blockers section to every upstream gap before handoff; and
- record coverage, commands, results, and residual non-blocking risks.

This self-check is preparation evidence, never a Review decision.

## Required process

1. Build a placement checklist mapping every new or moved production and test file
   to an approved responsibility, root, package/module pattern, and decision.
   Responsibilities separated by Solution MUST remain separated; tests follow the
   approved Test Structure, including production-package mirroring when required.
2. Translate Slice acceptance evidence into observable tests and record the smallest
   relevant failing RED result.
3. Implement only enough approved behavior for GREEN, run relevant tests, and record
   exact commands and results.
4. Refactor without changing approved behavior, rerun verification, and repeat until
   every Slice condition is evidenced.
5. Record changed files, File Placement Conformance, and implemented engineering decisions.
   Record affected shared components or utilities, deviations and their owning
   Workflow, and residual risks. Resolve local deviations; RETURN upstream-owned
   deviations.
6. Perform and record the Review readiness self-check. Do not continue while a
   blocking finding remains locally unresolved or requires RETURN.
7. Re-read Planning, Solution, and the selected Lane immediately before persistence.
   If its engineering version, dependencies, shared access, Slice Plan, or upstream
   completion changed, do not publish stale evidence; stop and resolve fresh.
   Set Attempt to `1`, or one greater than the latest FAIL attempt after correction.
   Persist the TDD Record at its Canonical Artifact Path with exact Solution/Slice
   Plan versions and Status `READY_FOR_REVIEW`. Review may not edit this record;
   later corrections create new TDD evidence in the same Slice scope.
8. Apply the Transition Resolution Procedure. If it selects a transition, validate
   and render exactly one Canonical Handoff Block as final response content, then
   stop without consuming its Target Scope.

TDD MUST NOT invent business policy, redesign engineering contracts, change Slice
boundaries, implement a future Slice, issue PASS or FAIL, create a Review Report, or
declare Feature or Project completion. Passing tests do not excuse wrong placement.

## Emit conditions after TDD completes a Slice

- **FORWARD to Review**: Rule 9 matches the selected Lane's current `READY_FOR_REVIEW` attempt; forward to Review for the same Slice.
- **RETURN**: Rule 3 selects a persisted blocker; use the routes below.

TDD never emits project-complete TERMINAL; Rule 11 requires a matching PASS Review.

## Blockers

| Condition | Route |
| --- | --- |
| Missing business behavior | `BUSINESS_GAP` → Grill at the affected Feature |
| Missing or invalid engineering decision or structure | `ENGINEERING_GAP` → Solution at Project |
| Missing, overlapping, or inconsistent Planned File Placement or decomposition | `SLICE_VIOLATION` → Slice at the affected Feature |
| Local implementation, test, placement, or evidence defect | Correct locally; if blocked across invocations, persist `IMPLEMENTATION_GAP`; while this invocation remains active, stay in TDD without Handoff |

<!-- forgeflow-eof: .forgeflow/workflow/tdd.md -->
