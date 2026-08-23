# Slice Workflow

Version: 2.11

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Slice Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | current READY Planning, Requirement, and Solution Plan; Feature Target Scope |

Slice decomposes exactly one approved Feature into the smallest useful ordered
delivery increments. The Target Scope is the complete authorization boundary. Other
Features are future execution scopes and MUST NOT be analyzed, decomposed, or
modified. A Slice Plan may declare multiple Slices but authorizes none for execution.

## READY quality gate

A READY Slice Plan MUST:

- trace every applicable Requirement behavior and Solution constraint to at least
  one Slice, with no uncovered obligation or completion gap;
- contain independently implementable, testable, reviewable, and valuable Slices
  with non-overlapping ownership and acyclic dependencies;
- define each Slice's observable acceptance evidence, checks, dependencies, risks,
  and completion conditions; and
- map every production and test responsibility to Planned File Placement consistent
  with the Solution's Implementation Structure and Test Structure.

Missing business policy returns to Grill. A missing or invalid engineering decision,
including an absent package/module or test-layout strategy, returns
`ENGINEERING_GAP` to Solution at Project scope. If the strategy exists but file
responsibilities cannot be mapped without overlap or omission, persist
`SLICE_VIOLATION`. Slice MUST NOT invent or redesign upstream contracts.

## Required process

1. Run Unified Entry Validation for Handoff Entry, Feature Lane Entry, or Recovery.
   Without a handoff, Feature Lane Entry requires this exact Slice/Feature action in
   the current Ready Set; Recovery requires fresh Rule 3 at this Feature from a
   current `SLICE_VIOLATION`. Validate and freeze exactly one planned Feature.
2. Validate its current Requirement and Solution Plan, resolve its Feature
   Engineering Version, and inspect relevant existing implementation boundaries.
3. Define ordered `S-XX` Slices. For each, record intent, acceptance evidence,
   dependencies, expected components/files, tests, risks, completion conditions,
   engineering-decision references, and reused or changed shared components or utilities.
4. Add Planned File Placement rows for every created, moved, or materially changed
   production and test responsibility. Every path or pattern MUST resolve to the
   current Implementation/Test Structure and preserve its responsibility boundaries.
5. Validate dependency order, reject cycles, perform the READY quality gate, and
   record Requirement-and-Solution-to-Slice traceability. Every referenced decision
   or shared component MUST resolve through the current Solution Plan and the
   targeted Feature's structured mappings; omitted relationships MUST NOT be inferred.
6. Re-read Planning and Solution immediately before persistence. If the Feature
   Engineering Version, effective dependencies, or shared-component access changed,
   stop and resolve from the fresh graph instead of publishing stale lane evidence.
   Persist an immutable Slice Plan version at its Canonical Artifact Path with the
   Feature ID and `Based On Solution` equal to that Feature's current Feature
   Engineering Version.
7. Confirm that no other Feature's Slice Plan was created or modified. Slice Plans
   contain no dynamic cursor, `PENDING`, `IN_PROGRESS`, `BLOCKED`, `COMPLETE`, or
   review-result state; runtime state is derived from TDD and Review evidence.
8. Apply the Transition Resolution Procedure. If it selects a transition, validate
   and render exactly one Canonical Handoff Block as the final response content,
   then stop without consuming its Target Scope.

Slice MUST NOT change business behavior, redesign Solution, write code or TDD
evidence, or independently choose an execution target. Completing one Feature's
Slice Plan does not continue work inside this execution or begin TDD. Its Handoff
may continue the same Lane; independent ready Features may use separate Feature Lane
Entries without waiting for every Feature to have a Slice Plan.

## Emit conditions after Slice completes a Feature

- **FORWARD to Slice**: Rule 7 selects another dependency-ready Feature Lane lacking a usable current Slice Plan.
- **FORWARD to TDD**: Rule 10 selects the first incomplete Slice in the selected Lane once that Feature is lane-delivery-ready.
- **RETURN**: Rule 3 selects a persisted blocker; return to its resolved owner and scope.

## Change impact

A decomposition change creates a new Slice Plan version for that Feature. TDD and
Review evidence tied to older versions remains history but is stale.

<!-- forgeflow-eof: .forgeflow/workflow/slice.md -->
