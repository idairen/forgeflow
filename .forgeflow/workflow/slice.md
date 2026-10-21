# Slice Workflow

Version: 2.12

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owns | Slice Plan; delivery decomposition and placement |
| Inputs | current READY Planning, Requirement, and Solution; one Feature Target Scope |

Accept only a valid Handoff or Recovery selected from current `SLICE_VIOLATION`.
Validate Transition and Handoff; resolve and freeze one planned Feature as the sole
productive and Slice Plan mutation Scope; another Feature requires another execution.
Declaring Slices does not authorize their execution.

## Ready gate

Trace every applicable Requirement behavior and Solution constraint to one or more
Slices without uncovered obligations, overlap, contradictory ownership, invalid
dependency, or completion gap. Each Slice supplies observable acceptance evidence,
checks, dependencies, risks, and completion conditions sufficient for Implement and
Review. Return missing business policy to Grill and engineering policy to Solution;
never invent either.

Each Slice requires an actionable Verification Plan covering all its acceptance conditions
and applicable Solution verification obligations, with one or more strategies,
rationale, required checks, passing criteria, and evidence requirements under Artifact Protocol.
Strategies may combine; none cancels other obligations.
Implement may select only explicitly permitted alternatives or refine execution details;
missing engineering criteria return to Solution, never to Implement discretion.

## Process

1. Validate entry, the Feature's Requirement, and its current Engineering Version.
2. Inspect relevant implementation boundaries.
3. Define dependency-ordered `S-<SliceNumber>` Slices with Artifact Protocol canonical
   Sequence Numbers; each must be independently implementable, testable, reviewable,
   and valuable; reject cycles.
4. For each Slice record intent, acceptance evidence, dependencies, components/files,
   tests, risks, completion, engineering decisions, and shared components.
   Add Verification Plan rows with justified strategies and checks mapped to current
   Solution requirements; preserve mandatory checks and thresholds and state conditions
   for any Solution-permitted alternative. TDD is a candidate for behavioral changes,
   not a requirement for configuration, migration, documentation, or every other Slice.
   Implement may refine routine commands.
5. Add every Planned File Placement row with paths/patterns resolving to current
   Implementation and Test Structures, preserving distinct responsibilities.
   Include authorized configuration, migration, and documentation changes and their
   verification placement when applicable; a strategy grants no additional path scope.
6. Trace Requirement and Solution obligations; resolve every component and decision
   in Solution and the Feature's structured mappings without inferring omitted links.
7. Persist one immutable Slice Plan whose Feature matches Target Scope and whose
   Based On Solution matches its Engineering Version; change no other Slice Plan.
8. Resolve Transition from the saved Slice Plan version under its upstream-persistence
   rule, recomputing this Feature's Slice evidence currentness. Do not return directly
   to the requesting Slice or retain an old completion prefix after a plan revision.
   Transition alone selects the next target under the complete Rule order; emit any
   exact Handoff as final content, and stop.

Slice Plans store no runtime cursor, state, blocker projection, or Review result.
Slice does not alter business behavior, redesign Solution, write code, or select an
execution target. Missing source/test structure is `ENGINEERING_GAP`; a complete
structure that cannot support non-overlapping placement is `SLICE_VIOLATION`.

## Change impact

Decomposition change creates a new Feature Slice Plan version. Evidence tied to the
older version remains immutable history but is stale.
