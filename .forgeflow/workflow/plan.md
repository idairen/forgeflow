# Plan Workflow

Version: 2.2

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Planning |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | User Intent; existing system context when present |

Plan transforms approved intent into the complete ordered Feature set for one
project version. It owns business scope decomposition, not detailed Feature
behavior or engineering design.

## Required process

1. Before reading or creating any project artifact, execute the Artifact Root
   Rotation Procedure defined by the Artifact Protocol. This ensures no stale
   artifacts from prior projects or earlier Plan runs interfere with new planning:
   if `.forgeflow/artifacts/` exists and is non-empty, it is renamed to
    `artifacts.YYYYMMDDHHMMSS` and a fresh empty directory replaces it.
2. Inspect existing project context and constraints.
3. Define project goals, exclusions, assumptions, and success measures.
4. Identify all independently valuable Features in dependency-aware order.
5. Give every Feature a stable `F-XX` identifier and concise boundary.
6. Confirm that the Feature set covers the approved project intent without overlap.
7. Persist a new Planning version at its Canonical Artifact Path and mark it READY
   only when the list is complete.
8. Before accepting any handoff, execute the Unified Entry Validation Procedure
   defined in the Handoff Protocol. Apply the Transition Resolution Procedure.
   If it requires a handoff, validate and render exactly one Canonical Handoff Block
   from the Handoff Protocol as the final content of the response.

Plan MUST NOT specify detailed acceptance criteria, architecture, Slices, tests, or
implementation. Missing stakeholder scope is a blocker and MUST NOT be guessed.

## Completion

Planning is READY when every approved objective maps to at least one Feature,
dependencies and exclusions are explicit, and no unresolved scope decision changes
the Feature list.

### Emit conditions after Plan completes

After producing a current Planning artifact:

- **FORWARD to Grill**: When Rule 3 matches (first Feature in Planning order lacks a READY Requirement) — forward to Grill at that Feature's Target Scope.
- **TERMINAL**: When the project scope is fully planned and no further decomposition is needed.
