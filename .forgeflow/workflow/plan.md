# Plan Workflow

Version: 2.7

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
   - Bootstrap Entry requires both an absent or empty Artifact Root and an absent or
     empty supplemental Reports Root. It creates either root if needed and starts
     Planning without rotation.
   - A non-empty User Intent received after current READY Planning uses Subsequent
     Plan Entry, preserves both evidence roots, and merges the intent into a higher
     Planning version. The user does not need to label it incremental or restate
     that it belongs to the current software project.
   - Semantic similarity to current Planning MUST NOT be used to infer a different
     project, request confirmation of project identity, or rotate evidence. Every
     later Plan intent is a change to the current software project.
   - Project Evidence Rotation occurs only through an explicit reset or archive
     maintenance operation. Rotation is not a Plan classification outcome.
   - An empty Artifact Root with a non-empty Reports Root is not a clean Bootstrap
     Entry. Ask and wait for explicit reset authorization before rotating the
     residual reports or creating Planning.
   - A RETURN or Recovery Entry preserves the active Artifact Root and creates a new
     Planning version in place; it MUST NOT rotate the current graph. Recovery Entry
     is valid only when Rule 3 selects Plan at Project scope from a current PLAN_GAP.
   - A non-empty Artifact Root without Planning is not Bootstrap Entry; Rule 2
     produces `TERMINAL / HALTED`. Do not rotate or repair it unless the user starts
     a separate explicit reset or archive maintenance operation.
2. On Subsequent Plan Entry, execute every subsequent-entry validation check in the
   Handoff Protocol. Read current Planning and classify the requested change as added,
   modified, removed, reordered, or project-constraint impact before changing files.
3. Inspect existing project context and constraints.
4. Define project goals, exclusions, assumptions, and success measures.
5. Identify all independently valuable Features in dependency-aware order. If no
   delivery objective exists, ask and wait for explicit user approval; do not infer
   an empty project from silence, ambiguity, missing context, or exclusions alone.
6. Give every Feature a stable `F-XX` identifier and concise boundary. Preserve every
   existing identifier; assign new Features previously unused identifiers and never
   reuse a retired identifier. Only after explicit empty-project approval, instead
   record `Feature IDs` as `NONE` and persist `Empty Feature Approval` as
   `APPROVED: <approval evidence>`.
7. Build Feature Contract Versions and the Change Set according to the Artifact
   Protocol. Unchanged Features retain their prior contract versions. Added and
   business-affected Features use the new Planning Version.
8. Record an intent-evolution summary that explains how the current Change Set
   changes the complete approved scope. It MUST distinguish retained, added,
   modified, reordered, and explicitly retired Features without copying historical
   Planning into a second current contract.
9. Confirm that the Feature set covers the currently approved project intent without
   overlap. A later module may extend that approved scope through another Subsequent
   Plan Entry.
10. Before replacement, archive the prior Planning exactly. For explicit Feature
   removal, complete the Artifact Protocol's Feature retirement transaction. Persist
   the new Planning at its Canonical Artifact Path and mark it READY only when the
   current approved scope and Change Set are complete.
11. For Bootstrap Entry, validate that Rule 1 authorizes Plan. For Subsequent Plan
   Entry, retain its Plan-only authorization until the new Planning is persisted.
   For Handoff Entry, execute the Unified Entry Validation Procedure defined in the
   Handoff Protocol.
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

For a subsequent version, READY also requires an exact Change Set and one Feature
Contract Version for every active Feature. Additive intent normally appends Features
without changing earlier Feature versions or evidence. Modification advances only
the affected Feature versions. Reordering alone preserves versions unless it changes
a Feature dependency or contract. Removal requires explicit user authorization and
the completed retirement transaction; omission alone never retires a Feature.

### Emit conditions after Plan completes

After producing a current Planning artifact:

- **FORWARD to Grill**: When Rule 5 matches, forward to Grill for the first Feature lacking a usable current Requirement.
- **TERMINAL / COMPLETE**: Only when Rule 11 matches, including an explicitly approved empty Feature list. Planning readiness alone never completes a non-empty project.
