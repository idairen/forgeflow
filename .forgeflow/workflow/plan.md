# Plan Workflow

Version: 2.15

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Planning |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | User Intent; existing system context when present |

Plan transforms approved User Intent into the complete ordered Feature set for one
project version. This decomposition is its only product-definition responsibility.
It does not define detailed Feature behavior or engineering design.

## Execution boundary

From invocation start, Plan MAY read authoritative files and relevant repository
evidence, ask Plan-owned questions, and perform only the canonical mutations in this
Workflow. It MUST NOT invoke an SQL or database tool, execute SQL DDL or DML, create
a table or record, or use a task, memory, planning, agent-management, or session-state
tool to track questions, answers, decisions, or progress. This includes temporary,
host-provided, out-of-repository, and internal-bookkeeping tools.

Protocol words such as “table” or “record” mean Markdown structures unless the
selected Workflow is TDD and its current Slice authorizes application persistence.
Plan has no such exception. It MUST NOT call host actions such as `Execute SQL`,
`Create Table`, or `Insert Row`.

## Planning clarification

A question is Plan-owned only when different plausible answers can change:

- the approved project scope or project-level inclusion/exclusion boundary;
- the Feature set, boundary, dependency, or dependency-aware order; or
- a project-wide or cross-Feature actor, identity, ownership, lifecycle, or shared
  data meaning, including a contract between two or more Features.

For each material uncertainty, Plan MUST compare at least two plausible answers by
their effect on those outcomes. Topic names do not determine ownership. Exact state,
reopen, assignment and collaboration rules are Grill-owned only when every plausible
answer remains inside exactly one stable Feature and changes neither another Feature
nor the Planning graph. If an uncertainty mixes local and cross-Feature effects, Plan
asks only the cross-Feature portion and leaves the local portion to Grill.

Plan MUST ask the user during this invocation for every unresolved Plan-owned answer
and wait before marking Planning READY. Every other business question is forbidden in Plan:
Plan MUST NOT ask it, silently answer it, or encode a proposed answer as an
Assumption, Exclusion, Success Measure, Constraint, or Feature Outcome. Confidence,
common practice, repository technology, and a plausible default are not approval.

Plan asks only the minimum question needed to stabilize project scope, Feature
topology, or a cross-Feature contract. It MUST NOT repeat an already approved
project-level decision or ask extra questions merely to make Planning detailed,
realistic, or implementation-ready.

## Decomposition readiness gate

Before asking questions or writing Planning, Plan MUST apply this domain-independent procedure:

1. Derive candidate independently valuable Features only from approved User Intent
   and user-confirmed Plan answers; plausible implications are not approved scope.
2. Inspect the five universal dimensions: project boundary; cross-Feature actors and
   identity; shared entities and ownership; cross-Feature lifecycle transfer; and
   shared data or measurement semantics.
3. Apply the impact test above to classify every material uncertainty as Plan-owned,
   Grill-owned, or mixed.
4. Ask the smallest set of questions that resolves every Plan-owned uncertainty.
5. If any remains, wait without READY Planning or Handoff. Do not ask, answer, or
   persist Grill-owned details.
6. Continue only when every material dimension is explicitly resolved or irrelevant.

This gate is an execution check, not authority for a separate checklist, database
table, decision store, or Planning section. Zero Plan questions is valid only after
the gate proves all five dimensions resolved or irrelevant. The same procedure
applies identically to every domain and User Intent.

For each Plan-owned question, present no more than three to five evidence-supported
options, use fewer when enough, end with `Other`, and briefly explain the scope or
observable behavior impact. Do not recommend an option merely to avoid asking.

While waiting, Plan remains at Project scope, creates no READY Planning, emits no
Handoff, and does not read or begin Grill.

## Required process

1. Classify entry before mutation:
   - Bootstrap Entry conditions are defined only by the Handoff Protocol. When Rule 1
     authorizes Bootstrap, create missing roots without rotation. Do not redefine or
     weaken its Artifact Root and supplemental Reports Root checks locally.
   - Non-empty User Intent after READY Planning is a **Subsequent Plan Entry**. Merge
     it into a higher Planning version while preserving both evidence roots; users
     need not label the intent incremental or restate project identity.
   - Semantic similarity to current Planning MUST NOT be used to infer a different
     project, request project confirmation, or rotate evidence. Later Plan intent is
     a change to the current software project.
   - Rotate project evidence only through explicit reset or archive maintenance.
   - RETURN or valid Rule 3 `PLAN_GAP` Recovery preserves roots and creates a new
     Planning version in place.
   - Non-empty Artifact Root without Planning is Rule 2 `TERMINAL / HALTED`; repair
     requires a separate explicit reset or archive maintenance operation.
2. For Subsequent Plan Entry, run all Handoff Protocol subsequent-entry checks, read
   current Planning, and classify changes as added, modified, removed, reordered, or
   project-constraint impact.
3. Inspect relevant project context, then apply the Decomposition readiness gate.
4. Define goals, exclusions, evidence-backed assumptions, and success measures.
   Silence does not authorize an exclusion or assumption.
5. Identify all independently valuable Features in dependency-aware order. If no
   delivery objective exists, ask for explicit empty-project approval and wait.
6. Assign stable `F-XX` identifiers. Preserve existing IDs, never reuse retired IDs,
   and allocate unused IDs to new Features. An approved empty project uses `NONE`
   plus `Empty Feature Approval: APPROVED: <approval evidence>`.
7. Build Feature Contract Versions and Change Set per the Artifact Protocol.
   Unchanged Features retain versions; added or business-affected Features use the
   new Planning Version.
8. Record an intent-evolution summary distinguishing retained, added, modified,
   reordered, and explicitly retired Features without duplicating historical Planning.
9. Map every approved objective and cross-Feature constraint to Feature Outcomes or
   Project Constraints; validate exhaustive, acyclic dependencies and remove overlap.
10. Render every required Planning section and canonical table. Use protocol `NONE`
    rather than omitting an empty applicable section.
11. Archive prior Planning exactly before replacement. Complete the Feature retirement
    transaction for explicit removal, then persist READY Planning only when complete.
12. Validate entry authorization: Rule 1 for Bootstrap, Plan-only authorization for
    Subsequent Plan Entry, Unified Entry Validation for Handoff Entry, and persisted
    blocker checks for Recovery. Apply Transition Resolution. If authorized, render
    exactly one Canonical Handoff Block as final response content and stop; do not start Grill,
    even when the IDE can continue or CLI mode is auto.

Plan MUST NOT specify detailed acceptance criteria, architecture, Slices, tests, or
implementation. Missing stakeholder scope is a blocker and MUST NOT be guessed.

Its only permitted persistent mutations are root creation when required,
`planning.md` creation or replacement, required Planning/history/retirement archival,
and explicitly authorized project evidence rotation. Plan MUST NOT execute SQL DDL or DML,
change an application database, source, tests, build/runtime configuration, or
persist a separate decision, question, session-plan, cursor, or progress store.
Approved answers appear only in canonical Planning content they govern; pending
answers remain only in the conversation.

Repository technology is evidence, not design authority. Plan may record an existing
hard platform constraint or explicitly approved product constraint, but libraries,
databases, rendering, authentication, deployment, scaling, backup, packages, and
infrastructure remain Solution-owned unless the user explicitly makes them product
constraints.

## Planning conformance gate

Before READY, run the Artifact Protocol Planning serialization validation against
persisted `planning.md`, then confirm:

- every Feature is an independently valuable business outcome, not scaffolding,
  implementation layers, shared components, or architecture;
- repeated permissions and business rules agree, approved decisions are not hidden
  as Assumptions, role cardinality is unambiguous, and dependencies are exhaustive;
- only project and cross-Feature detail appears; local behavior remains for Grill.

Only then run Transition Resolution from the reparsed persisted artifact, never the
draft, conversation summary, or intended Feature list. Invalid Planning cannot
satisfy Rule 5 and Plan MUST NOT emit FORWARD while correcting it or awaiting a
Plan-owned decision.

An authorized transition uses the exact Handoff Protocol Markdown template.
`Source Scope` is always `Project`. Never emit an XML/HTML `<transition>` wrapper, substitute
`Plan` for `Project`, use plain key-value lines, or expose an incomplete block.

## Completion

Planning is READY when all approved objectives map to Features, dependencies and
exclusions are explicit, and no unresolved Plan-owned decision can change project
scope, Feature topology, a cross-Feature contract, or product experience. An empty
Feature list additionally requires explicit approval and the exact `NONE` metadata.

For later versions, READY requires an exact Change Set and contract version for every
active Feature. Additive intent normally appends without changing earlier versions;
modification advances only affected versions; reorder preserves versions unless a
dependency or contract changes; removal requires explicit authorization and a
completed retirement transaction.

### Emit conditions after Plan completes

- **FORWARD to Grill**: Rule 5 selects the first Feature lacking a usable current Requirement.
- **TERMINAL / COMPLETE**: Rule 11 only, including an explicitly approved empty Feature list. READY Planning alone never completes a non-empty project.

<!-- forgeflow-eof: .forgeflow/workflow/plan.md -->
