# Slice Workflow

Version: 2.2

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Slice Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | current READY Planning, Requirement, and Solution Plan; Feature Target Scope |

Slice decomposes exactly one approved Feature into the smallest useful ordered
delivery increments while preserving the project engineering baseline.

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

1. Before accepting any handoff, execute the Unified Entry Validation Procedure
   defined in the Handoff Protocol. Validate that Target Scope identifies one planned Feature.
2. Validate the Feature's Requirement and the project Solution Plan versions.
3. Inspect existing implementation boundaries relevant to the Feature.
4. Define ordered `S-XX` Slices that are independently implementable, testable,
   reviewable, and valuable.
5. For each Slice record intent, acceptance evidence, dependencies, expected
   components/files, tests, risks, and completion conditions.
6. Validate dependency order and reject cycles.
7. Perform the READY quality gate and record Requirement-and-Solution-to-Slice
   traceability in the Slice Plan.
8. Persist an immutable Slice Plan version at its Canonical Artifact Path with
   Feature ID and Based On Solution.
9. Apply the Transition Resolution Procedure. If it requires a handoff, validate
   and render exactly one Canonical Handoff Block from the Handoff Protocol as the
   final content of the response.

Slice Plans MUST NOT store dynamic execution state. They contain no mutable cursor,
PENDING/IN_PROGRESS/BLOCKED/COMPLETE field, or review result. Runtime state is
derived from TDD and Review evidence.

Slice MUST NOT change business behavior, redesign the Solution Plan, write code,
or select an execution target independently. All planned Features require current
READY Slice Plans before the procedure may target the first TDD Slice.

## Emit conditions after Slice completes a Feature

After producing a current Slice Plan:

- **FORWARD to Slice**: When Rule 5 matches (another Feature in Slice Plan order still lacks a current READY Slice Plan) — forward to Slice at that Feature's Target Scope.
- **RETURN**: When Rule 2 or Rule 5 matches (a blocker exists or slice plan is stale) — return per the Blocker Routing Rules table, with Return Workflow determined by Blocker Category.

## Change impact

A decomposition change creates a new Slice Plan version for that Feature. TDD and
Review evidence tied to older versions remains history but is stale.
