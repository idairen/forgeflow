# Plan Workflow

Version: 2.12

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owns | Planning; project and cross-Feature business scope |
| Inputs | User Intent; existing system context when present |

Plan does not own Feature-level rules, engineering design, Slices, tests, or
implementation.

## Entry and clarification

Validate Bootstrap, Subsequent Plan, Handoff, or Recovery Entry through the
Transition Protocol and freeze Project Scope. Bootstrap creates absent roots without
rotation. Subsequent Plan and rework preserve and version current evidence. Project
Evidence Rotation requires an explicit reset/archive request and the Artifact
Protocol transaction; semantic similarity never implies rotation or another project.
Rule 2 contradictions are halted, not repaired implicitly.

### Clarification Gate

Before Planning, classify every material decision by owner and state.

A decision is Plan-owned only when different answers change:

- Project Intent, Goals, Measures, Constraints, Assumptions, or Exclusions;
- Feature set, boundary, Outcome, order, or dependency; or
- a project-wide or cross-Feature business contract recorded as a Feature Outcome
  or Project Constraint.

Before asking, identify the exact Planning field affected. No exact field means
Plan MUST NOT ask.

Feature-local actors, triggers, permissions, rules, validation, states, failures,
edge cases, and acceptance criteria are Grill-owned when Feature topology and
cross-Feature contracts remain unchanged.

Architecture, APIs, protocols, algorithms, schemas, storage, synchronization,
security mechanisms, migrations, deployment, and implementation are
Solution-owned. Cost, complexity, or technical impact never changes ownership.

For a mixed decision, ask only the Plan-owned portion. Options and explanations
MUST NOT contain or imply Grill-owned or Solution-owned choices.

A Plan-owned decision is resolved only by current User Intent, unchanged approved
Planning, or an explicit user answer. Repository evidence proves current facts,
not approval. Silence, convention, convenience, and likely intent are not approval.
Two compatible but materially different Planning outcomes mean the decision is open.

Complete ownership and coverage classification before asking. Ask every currently
discoverable open Plan-owned question and wait at Project Scope. While waiting,
MUST NOT create or modify Planning, emit a Handoff, or encode an open answer as an
Assumption, Exclusion, Measure, or Outcome. Reapply this gate after every answer.

### Project Decision Gate

Before defining or revising Planning, Plan MUST classify every currently
discoverable material Plan-owned decision as resolved or open. This classification
is invocation-local and does not create an Artifact status. A decision is open when
two or more materially different Planning outcomes remain compatible with current
User Intent and approved Planning, even if one outcome appears conventional or more
likely.

The gate covers decisions that could change:

- project or cross-Feature behavior;
- Feature set, boundary, dependency, order, or exclusion;
- project-wide roles, access, visibility, journey, or user experience;
- shared data meaning, identity, ownership, lifecycle, or reporting; or
- goals, success measures, constraints, or evidence-backed assumptions.

A decision is resolved only by explicit current User Intent, an unchanged decision
in current approved Planning, or an explicit user answer to a Plan clarification.
Repository evidence may establish current-state facts and support clarification
options, but MUST NOT authorize new or changed project scope, Feature topology,
cross-Feature behavior, shared-data policy, roles, access, constraints, exclusions,
or success measures. Convention, likely intent, implementation convenience, and
silence are not approval.

If any decision is open, Plan MUST ask every currently discoverable open question
under the Framework clarification policy and wait at Project Scope. It MUST NOT
create or modify Planning, emit a Handoff, or encode an open answer as an Assumption,
Exclusion, Success Measure, or Outcome. A user answer resolves only the decisions it
explicitly addresses; reapply the gate before continuing.

Feature-local rules, validation, states, edge cases, and acceptance criteria remain
Grill-owned. For mixed uncertainty, Plan applies the gate only to the project or
cross-Feature portion and leaves the detailed portion to Grill.

## Process

1. Validate entry. For Subsequent Plan, classify non-empty intent as additions,
   modifications, reorderings, retirements, and project-constraint effects.
2. Inspect approved evidence, classify candidate decisions through the
   Clarification Gate, and ask, wait, and stop if any Plan-owned decision is open.
3. Define approved goals, constraints, exclusions, evidence-backed assumptions, and
   success measures. Silence supports neither assumption nor exclusion.
4. Identify independently valuable Features in dependency-aware order. With no
   delivery objective, ask for explicit empty-project approval.
5. Assign stable `F-<FeatureNumber>` IDs using the Artifact Protocol's canonical
   Sequence Number; never change an existing ID or reuse a retired one.
   Empty Planning uses `NONE` and persisted approval.
6. Build Feature Contract Versions and Change Set. Retain unchanged versions; advance
   added and business-affected Features.
7. Record Intent Evolution without creating another current contract.
8. Trace every approved objective and cross-Feature constraint to an Outcome or
   Project Constraint; validate dependency consistency, coverage, and non-overlap.
9. Render the full Artifact Protocol 2.11 Planning structure with
   `Artifact Protocol Version = 2.11` and explicit `NONE` where required.
10. For every Entry, recheck that no ACTIVE Lane remains before persistence; wait
    without writing while one exists. Running Grill executions release their own
    claims on a Project blocker; inactive claims require interrupted Lane Recovery.
    Plan never removes another execution's claim. Protect the check and write from
    racing claims as required by Transition. Archive prior Planning and complete
    the retirement transaction when applicable. Partial retirement retains a
    validated old Solution as stale; retiring all Features also archives the exact
    old Solution and requires Empty Feature Approval. Persist canonical Planning
    only when ready, rolling back the entire transaction on failure.
11. Resolve Transition. If it selects another Scope or terminal result, emit the
    exact Handoff as final content and stop.

## Ready

Planning is READY only when every approved objective maps to a Feature; dependencies,
exclusions, constraints, Change Set, and Feature Contract Versions are exact; and
every material Plan-owned decision covered by the Project Decision Gate has explicit
resolution evidence. Absence of a detected uncertainty is not resolution evidence.

Empty Planning requires exact `NONE` metadata and approval. Reordering preserves
versions unless it changes a dependency or contract. Retirement requires explicit
authorization and completed archival; omission never retires a Feature.

Every clarification asked by Plan has an exact Planning projection. Planning
contains no Feature-local rule or engineering decision, and no Grill-owned or
Solution-owned answer is required for Planning readiness.
