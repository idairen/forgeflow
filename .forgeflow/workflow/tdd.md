# TDD Workflow

Version: 2.8

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | TDD Record |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Valid Handoff Entry or Recovery Entry; current Requirement, Solution Plan, and Slice Plan |

Target Scope is the only authoritative execution scope. It MUST identify exactly
one Feature ID and Slice ID, and it MUST equal a fresh Transition Resolution
Procedure result.
Conversation text, filenames, or a previously remembered cursor cannot widen or
replace it.
Completion of the targeted Slice does not authorize Review or the next Slice in
this execution. A different Workflow or Slice selected afterward is a future
execution scope and may only be reported through a Canonical Handoff.

## Entry validation

Before changing tests or production code, TDD MUST validate its entry. On Handoff
Entry it executes the Unified Entry Validation Procedure. Without an incoming
handoff, it may proceed only through Recovery Entry when a fresh Rule 3 result
selects TDD at the exact Slice Target Scope from a current IMPLEMENTATION_GAP. It
then:

1. validate the typed handoff and confirm Next Workflow is TDD, or validate every
   Recovery Entry condition without inferring a handoff;
2. validate `DELIVERY_READY` and the complete Requirement, Solution Plan, and
   Slice Plan version chain, including Solution Version equal to the targeted
   Feature's current Feature Engineering Version;
3. locate the exact Slice in the targeted current Slice Plan;
4. reject stale inputs, a mismatched target, or work outside the Slice boundary;
5. inspect the existing implementation and applicable repository instructions;
6. resolve every planned production and test responsibility through the Slice Plan's
   Planned File Placement and the Solution's Implementation/Test Structure before
   creating, moving, or editing files. TDD may resolve concrete filenames from an
   approved directory pattern and established naming conventions, but it MUST NOT
   choose a new package, module, layer, or test-topology strategy.

## Command execution

Every TDD command MUST follow the Framework Command execution policy. RED, GREEN,
refactor, and verification commands are sequential unless the targeted Slice
explicitly requires simultaneous processes. TDD MUST reuse the same terminal tab
or equivalent session when supported, use bounded one-shot commands by default,
record any required concurrency, and terminate every process it starts before its
handoff.

## Review readiness self-check

Before declaring READY_FOR_REVIEW, TDD MUST apply the Framework Review readiness
and decision policy as a self-check. It MUST:

- trace every applicable Requirement behavior and Slice condition through the
  Solution Plan to implementation, tests, and recorded evidence;
- inspect the complete Slice change for scope discipline, regressions, security,
  concrete maintainability risk, and repository-required checks;
- correct every local implementation, test, or evidence blocker before handoff;
- RETURN an upstream blocking gap to its owner before READY_FOR_REVIEW, using
  Grill for missing business policy, Solution for missing engineering policy, or
  Slice for invalid decomposition;
- record the self-check coverage, commands, results, and residual non-blocking
  risks in the TDD Record.

This self-check is preparation evidence, not an independent Review decision.

## Required process

1. Build a file-placement checklist for the authorized Slice. Confirm that every
   new or moved production class/module and every test maps to one approved
   responsibility, source/test root, package/module pattern, and governing decision.
   Distinct architectural responsibilities MUST NOT be collapsed into one package
   or module when the Solution separates them. Tests MUST follow the approved Test
   Structure, including production-package mirroring where specified.
2. Translate the Slice's acceptance evidence into observable test cases.
3. Run the smallest relevant test and record the failing RED evidence.
4. Implement the minimum behavior needed for GREEN in the approved locations.
5. Run relevant tests and record exact commands and results.
6. Refactor without changing approved behavior and rerun verification.
7. Repeat until every Slice condition is evidenced.
8. Record changed files and the File Placement Conformance table. Record
   implemented engineering decisions, shared components or utilities touched,
   deviations, and residual risks. Each deviation MUST identify
   whether it is locally resolvable or requires RETURN to its owning Workflow.
9. Perform and record the Review readiness self-check; do not proceed while a
   blocking finding remains in TDD's authority or requires an upstream RETURN.
10. Set Attempt to 1 for first review, or one greater than the latest FAIL attempt
   after correction.
11. Persist the TDD Record at its Canonical Artifact Path with Status
    READY_FOR_REVIEW and apply the Transition Resolution Procedure. If it requires
    a handoff, validate and render exactly one Canonical Handoff Block from the
    Handoff Protocol as the final content of the response, then stop without
    consuming its Target Scope.

The TDD Record MUST reference the exact Solution Plan and Slice Plan versions.
Review findings are addressed in the same Slice scope with new TDD evidence; Review
does not edit the TDD Record.

TDD MUST NOT invent business policy, redesign engineering contracts, change Slice
boundaries, implement a future Slice, issue PASS or FAIL, create a Review Report,
or declare Feature or Project completion.

If the required Solution structure is absent or materially ambiguous, TDD returns
`ENGINEERING_GAP` to Solution. If Solution defines the structure but Planned File
Placement is absent, overlapping, or inconsistent, TDD returns `SLICE_VIOLATION` to
Slice. A local wrong-path implementation is TDD-owned and MUST be corrected before
READY_FOR_REVIEW; passing tests do not excuse it.

## Emit conditions after TDD completes a Slice

After marking the TDD Record as READY_FOR_REVIEW:

- **FORWARD to Review**: When Rule 9 matches the current READY_FOR_REVIEW attempt, forward to Review for the same Slice.
- **RETURN**: When Rule 3 selects a persisted blocker before completing the Slice, return per the Blocker Routing Rules table:
   - BUSINESS_GAP → Grill for the affected Feature
   - ENGINEERING_GAP → Solution at Project scope
   - SLICE_VIOLATION → Slice for the affected Feature
   - IMPLEMENTATION_GAP → TDD for the affected Slice; while the same invocation is active, remain in TDD without a handoff

TDD never emits project-complete TERMINAL because completion requires a matching PASS Review Report under Rule 11.

## Blockers

- Missing business behavior: RETURN to Grill for the affected Feature.
- Missing engineering decision: RETURN to Solution with the affected scope.
- Invalid decomposition: RETURN to Slice for the affected Feature.
- Local implementation/test defect: persist `IMPLEMENTATION_GAP` when blocked across
  invocations; otherwise remain in TDD for the same Slice without a handoff.
