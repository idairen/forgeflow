# Review Workflow

Version: 2.12

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owns | Review Report; immutable independent disposition |
| Inputs | valid Handoff; current Requirement, Solution, Slice Plan, Implement, and implementation |

Review is read-only for code, tests, upstream plans, and Implement.
Accept only Handoff Entry—never Recovery—then validate Transition/Handoff, freeze
the exact Slice and positive current Attempt, and verify the complete upstream chain.
Stale or mismatched evidence is not current review work.

## Decision

Independently apply the Framework review gate; unsupported preferences are non-blocking.
Build one canonical Findings table, then derive counts, Decision, Return Workflow,
and Return Scope:

- PASS has zero blocking rows and no return metadata.
- FAIL has blocking rows and one disposition: the Framework's highest-precedence
  blocking owner and one of that owner's blocking Scopes.

Resolve every finding and return identifier in the active graph; supplemental plugin
reports never determine or replace the canonical Review Report.

## Process

All commands follow the Framework command lifecycle.

1. Read and freeze Attempt and exact upstream versions from current READY_FOR_REVIEW
   Implement. Reject Attempts occupied by a PASS or FAIL Review even with stale upstream versions;
   only Implement allocates the next Attempt, and Review never changes counters or
   overwrites old reports.
2. Trace every Slice condition to tests, implementation, and evidence.
   Independently check the Verification Plan against Solution obligations and the
   selected strategies/rationales against that plan. Verify all required checks,
   current target/environment, passing criteria, and evidence references.
   Tool success must be relevant and sufficient; model
   assessment cannot substitute for required execution, and required human acceptance
   needs the actual acceptor's result.
   Assess missing, invented, inconclusive, or unreliable required evidence under the
   shared blocking gate; RED/GREEN/refactor applies only when TDD was selected; other
   strategies follow their own evidence requirements.
   Report unauthorized strategy substitution to its responsible owner; never rewrite
   the Implement Record or upstream plan.
3. Execute every enabled plugin from `.forgeflow/rules/reviews/_index.md`, including
   dependency order, applicability, rules, thresholds, archival, and report formats.
4. Inspect correctness, regression, Scope, security, maintainability, Solution
   conformance, and the current knowledge trace.
5. Compare every created/moved production/test path with Solution structure, Slice
   placement, and Implement conformance. Explicit structure violations follow architecture
   plugin severity; unsupported preferences do not block.
6. Validate structured Feature dependencies, shared components, decision references,
   and impact metadata when present.
7. Record each finding with Severity, Owner, Affected Scope, Finding, observable
   Evidence, and Violated Contract; derive Decision and disposition from the rows.
8. Validate the complete candidate Review locally before any canonical write:
   title followed by exactly one Metadata section and its two-column table; all
   common and Review-specific fields, labels, values and filename/identity matches;
   exactly one Findings table with required columns, sequential rows, valid owners
   and scopes; counts, Decision and Return disposition derived from those rows.
   Check Solution Version against the frozen Feature Engineering Version, and Slice
   Plan Version against the frozen Slice Plan. Use the already loaded Artifact
   schema and frozen direct inputs, not another full-graph scan or test/plugin run.
   Correct candidate formatting within this Review execution before publication;
   do not change findings, evidence or Decision merely to pass a format check.
   Missing substantive evidence follows the existing review gate, not a fabricated
   PASS. An occupied Attempt, changed baseline or unresolved reference is not a
   formatting correction and follows the existing stop/routing rules.
9. Recheck that current Implement still matches the frozen Attempt and exact upstream
   versions, and that no Review occupies the target path. Persist one immutable
   attempt-specific Review Report with those same values; never overwrite an
   attempt. A changed baseline ends this review without a report for the new attempt.
10. Resolve Transition, emit its exact Handoff as final content, and stop.

Supplemental report replacement follows Reports History; historical evidence may explain
evolution, never satisfy current gates.
Review never repairs implementation, edits tests/Implement, changes upstream Artifacts,
or begins returned work.
