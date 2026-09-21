# Review Workflow

Version: 2.12

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owns | Review Report; immutable independent disposition |
| Inputs | valid Handoff; current Requirement, Solution, Slice Plan, Implement, and implementation |

Review is read-only for code, tests, upstream plans, and Implement. It accepts only Handoff
Entry—never Recovery—then validates Transition/Handoff, freezes the exact Slice and
positive current Attempt, and verifies the complete upstream chain. Stale or
mismatched evidence is not current review work.

## Decision

Independently apply the Framework review gate. Unsupported preference is
non-blocking. Build the one canonical Findings table first, then derive counts,
Decision, Return Workflow, and Return Scope:

- PASS has zero blocking rows and no return metadata.
- FAIL has blocking rows and one disposition: the Framework's highest-precedence
  blocking owner and one of that owner's blocking Scopes.

Every finding and return identifier resolves in the active graph. Plugin reports are
supplemental and never determine or replace the canonical Review Report.

## Process

All commands follow the Framework command lifecycle.

1. Read and freeze Attempt and exact upstream versions from current READY_FOR_REVIEW
   Implement. Reject an Attempt already occupied by a PASS or FAIL Review, even if its
   upstream versions are stale. Only Implement allocates the next Attempt; Review never
   changes the counter or overwrites an old report.
2. Trace every Slice condition to tests, implementation, and evidence.
   Independently check the Verification Plan against Solution obligations and the
   selected strategies/rationales against that plan. Verify all required checks,
   current target/environment, passing criteria, and evidence references. Review
   source distinctions: tool success must be relevant and sufficient, model
   assessment cannot substitute for required execution, and required human acceptance
   needs the actual acceptor's result. Missing, invented, inconclusive, or unreliable
   required evidence is evaluated under the shared blocking gate. TDD-specific
   RED/GREEN/refactor applies only when TDD was selected; other strategies have their
   own evidence requirements. Report unauthorized strategy substitution to the
   responsible owner without rewriting the Implement Record or upstream plan.
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

Supplemental replacement follows Reports History. Historical evidence may explain
evolution but cannot satisfy a current gate. Review never repairs implementation,
edits tests/Implement, changes upstream Artifacts, or begins returned work.
