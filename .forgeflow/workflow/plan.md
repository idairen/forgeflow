# Plan Workflow

Version: 2.4

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

1. Classify entry before changing artifacts:
   - Bootstrap Entry with an absent or empty Artifact Root creates the root if needed
     and starts Planning without rotation.
   - An explicit user request to start a new project or reset the active project
     executes the Artifact Root Rotation Procedure before Planning.
   - A RETURN or Recovery Entry preserves the active Artifact Root and creates a new
     Planning version in place; it MUST NOT rotate the current graph. Recovery Entry
     is valid only when Rule 3 selects Plan at Project scope from a current PLAN_GAP.
   - A non-empty Artifact Root without Planning is not Bootstrap Entry; Rule 2
     produces `TERMINAL / HALTED`. Do not rotate or repair it unless the user starts
     a separate explicit new-project/reset operation.
2. Inspect existing project context and constraints.
3. Define project goals, exclusions, assumptions, and success measures.
4. Identify all independently valuable Features in dependency-aware order. If no
   delivery objective exists, ask and wait for explicit user approval; do not infer
   an empty project from silence, ambiguity, missing context, or exclusions alone.
5. Give every Feature a stable `F-XX` identifier and concise boundary. Only after
   explicit empty-project approval, instead record `Feature IDs` as `NONE` and
   persist `Empty Feature Approval` as `APPROVED: <approval evidence>`.
6. Confirm that the Feature set covers the approved project intent without overlap.
7. Persist a new Planning version at its Canonical Artifact Path and mark it READY
   only when the list is complete.
8. For Bootstrap Entry, validate that Rule 1 authorizes Plan. For Handoff Entry,
   execute the Unified Entry Validation Procedure defined in the Handoff Protocol.
   For Recovery Entry, execute its persisted-blocker checks before changing Planning.
   Apply the Transition Resolution Procedure.
   If it requires a handoff, validate and render exactly one Canonical Handoff Block
   from the Handoff Protocol as the final content of the response.

Plan MUST NOT specify detailed acceptance criteria, architecture, Slices, tests, or
implementation. Missing stakeholder scope is a blocker and MUST NOT be guessed.

## Completion

Planning is READY when every approved delivery objective maps to at least one
Feature, dependencies and exclusions are explicit, and no unresolved scope decision
changes the Feature list. An empty Feature list is READY only when the user
explicitly approves that the project has no delivery objective. It uses the exact
`NONE` representation and approval metadata defined by the Artifact Protocol; a
blank Feature IDs value is invalid.

### Emit conditions after Plan completes

After producing a current Planning artifact:

- **FORWARD to Grill**: When Rule 5 matches, forward to Grill for the first Feature lacking a usable current Requirement.
- **TERMINAL / COMPLETE**: Only when Rule 11 matches, including an explicitly approved empty Feature list. Planning readiness alone never completes a non-empty project.
