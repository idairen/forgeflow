# Slice Workflow

Version: 2.9

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Slice Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | current READY Planning, Requirement, and Solution Plan; Feature Target Scope |

Slice decomposes exactly one approved Feature into the smallest useful ordered
delivery increments while preserving the project engineering baseline.
The Feature Target Scope is the complete authorization boundary for this execution.
Other planned Features are future execution scopes and MUST NOT be decomposed or
written during this execution. The resulting Slice Plan may declare multiple
Slices, but it does not authorize executing any of them.

## READY quality gate

Before marking a Slice Plan READY, Slice MUST trace every applicable Requirement
behavior and Solution Plan constraint for the targeted Feature to one or more
Slices. The decomposition MUST have no uncovered obligation, contradictory or
overlapping ownership, invalid dependency, or completion gap. Every Slice MUST
define observable acceptance evidence, required checks, dependencies, and risks
sufficient for TDD and Review to apply the shared quality gate.

Missing business policy returns to Grill. A missing or invalid engineering
decision returns to Solution at Project scope. Slice MUST NOT compensate for an
upstream contract gap by inventing behavior or engineering policy.

## Required process

1. On Handoff Entry, execute the Unified Entry Validation Procedure defined in the
   Handoff Protocol. Without an incoming handoff, proceed only through Recovery Entry
   when a fresh Rule 3 result selects Slice at the exact Feature Target Scope from a
   current SLICE_VIOLATION. Validate that Target Scope identifies exactly one planned
   Feature and freeze it as the only productive scope for this execution.
2. Validate the Feature's Requirement and the current Solution Plan. Resolve this
   Feature's Feature Engineering Version from the Solution Plan.
3. Inspect existing implementation boundaries relevant to the Feature.
4. Define ordered `S-XX` Slices that are independently implementable, testable,
   reviewable, and valuable.
5. For each Slice record intent, acceptance evidence, dependencies, expected
   components/files, tests, risks, completion conditions, applicable engineering
   decision references, and shared components or utilities it reuses or changes.
   Add the Artifact Protocol's Planned File Placement rows for every production and
   test responsibility the Slice creates, moves, or materially changes. Paths or
   directory patterns MUST resolve to the current Implementation Structure and Test
   Structure and must distinguish responsibilities when Solution does.
6. Validate dependency order and reject cycles.
7. Perform the READY quality gate and record Requirement-and-Solution-to-Slice
   traceability in the Slice Plan. Every referenced shared component or engineering
   decision MUST resolve in the current Solution Plan and in that Feature's
   structured component or decision mapping. Slice MUST NOT infer a relationship
   omitted from the current Solution impact metadata.
8. Persist an immutable Slice Plan version at its Canonical Artifact Path with
   Feature ID and Based On Solution equal to this Feature's current Feature
   Engineering Version.
9. Confirm that no Slice Plan other than the targeted Feature's Slice Plan was
   created or modified during this execution.
10. Apply the Transition Resolution Procedure. If it requires a handoff, validate
   and render exactly one Canonical Handoff Block from the Handoff Protocol as the
   final content of the response, then stop without consuming its Target Scope.

Slice Plans MUST NOT store dynamic execution state. They contain no mutable cursor,
PENDING/IN_PROGRESS/BLOCKED/COMPLETE field, or review result. Runtime state is
derived from TDD and Review evidence.

Slice MUST NOT change business behavior, redesign the Solution Plan, write code,
or select an execution target independently. All planned Features require current
READY Slice Plans before the procedure may target the first TDD Slice.

If the Solution does not decide a required package/module or test-layout strategy,
Slice returns `ENGINEERING_GAP` to Solution. If the strategy exists but the current
Slice cannot map its responsibilities to it without overlapping or incomplete file
ownership, Slice persists `SLICE_VIOLATION` rather than leaving placement for TDD.

Completing one Feature's Slice Plan does not continue the Slice loop inside this
execution. A FORWARD to another Feature starts a new Slice execution. A FORWARD to
TDD authorizes a later TDD execution for exactly one Slice; Slice MUST NOT begin
implementation or create TDD evidence in the current execution.

## Emit conditions after Slice completes a Feature

After producing a current Slice Plan:

- **FORWARD to Slice**: When Rule 7 selects another Feature lacking a usable current Slice Plan, forward to Slice at that different Feature scope.
- **FORWARD to TDD**: When every planned Feature has a usable current Slice Plan and Rule 10 selects the first incomplete Slice, forward to TDD at that Slice scope.
- **RETURN**: When Rule 3 selects a persisted blocker, return to its resolved owner and scope.

## Change impact

A decomposition change creates a new Slice Plan version for that Feature. TDD and
Review evidence tied to older versions remains history but is stale.
