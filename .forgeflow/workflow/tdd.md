# TDD Workflow

Version: 2.2

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owned artifact | TDD Record |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | Incoming Handoff (required); current Requirement, Solution Plan, and Slice Plan |

Target Scope is the only authoritative execution scope. It MUST identify exactly
one Feature ID and Slice ID, and it MUST equal a fresh Transition Resolution
Procedure result.
Conversation text, filenames, or a previously remembered cursor cannot widen or
replace it.

## Entry validation

Before changing tests or production code, TDD MUST first execute the Unified Entry
Validation Procedure defined in the Handoff Protocol for every incoming handoff. It
then:

1. validate the typed handoff and confirm Next Workflow is TDD;
2. validate `DELIVERY_READY` and the complete Requirement, Solution Plan, and
   Slice Plan version chain;
3. locate the exact Slice in the targeted current Slice Plan;
4. reject stale inputs, a mismatched target, or work outside the Slice boundary;
5. inspect the existing implementation and applicable repository instructions.

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

1. Translate the Slice's acceptance evidence into observable test cases.
2. Run the smallest relevant test and record the failing RED evidence.
3. Implement the minimum behavior needed for GREEN.
4. Run relevant tests and record exact commands and results.
5. Refactor without changing approved behavior and rerun verification.
6. Repeat until every Slice condition is evidenced.
7. Record changed files, decisions, deviations, and residual risks.
8. Perform and record the Review readiness self-check; do not proceed while a
   blocking finding remains in TDD's authority or requires an upstream RETURN.
9. Set Attempt to 1 for first review, or one greater than the latest FAIL attempt
   after correction.
10. Persist the TDD Record at its Canonical Artifact Path with Status
    READY_FOR_REVIEW and apply the Transition Resolution Procedure. If it requires
    a handoff, validate and render exactly one Canonical Handoff Block from the
    Handoff Protocol as the final content of the response.

The TDD Record MUST reference the exact Solution Plan and Slice Plan versions.
Review findings are addressed in the same Slice scope with new TDD evidence; Review
does not edit the TDD Record.

TDD MUST NOT invent business policy, redesign engineering contracts, change Slice
boundaries, implement a future Slice, issue PASS or FAIL, create a Review Report,
or declare Feature or Project completion.

## Emit conditions after TDD completes a Slice

After marking the TDD Record as READY_FOR_REVIEW:

- **FORWARD to Review**: When the Slice's implementation is complete (all tests pass, all evidence recorded) and no blockers prevent review — forward execution to Review for that Slice.
- **RETURN**: When Rule 2 matches before completing the Slice (a blocker exists in upstream artifacts or during self-check) — return per the Blocker Routing Rules table, with Return Workflow determined by Blocker Category:
   - BUSINESS_GAP → Grill for the affected Feature
   - ENGINEERING_GAP → Solution at Project scope
   - SLICE_VIOLATION → Slice for the affected Feature
   - Local implementation defect → remain in TDD (no handoff needed)
- **TERMINAL**: When all planned Slices have completed successfully — not typically emitted by TDD alone but may occur as part of a terminal pipeline state.

## Blockers

- Missing business behavior: RETURN to Grill for the affected Feature.
- Missing engineering decision: RETURN to Solution with the affected scope.
- Invalid decomposition: RETURN to Slice for the affected Feature.
- Local implementation/test defect: remain in TDD for the same Slice.
