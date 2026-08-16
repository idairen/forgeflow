# ForgeFlow Framework

Version: 2.2

ForgeFlow is an artifact-driven delivery framework for humans and AI agents. The
versioned artifact graph is the sole persistent source of truth. Conversations,
adapter prompts, and derived dashboards are never authoritative state.

## Project index

| Contract | Version | Path |
|---|---|---|
| Framework | 2.2 | `forgeflow.md` |
| Artifact Protocol | 2.2 | `protocol/artifact.md` |
| Handoff and Transition Protocol | 2.2 | `protocol/handoff.md` |

| Workflow | Artifact Type | Scope | Spec Path |
|---|---|---|---|
| Plan | Planning | Project | `workflow/plan.md` |
| Grill | Requirement | Feature | `workflow/grill.md` |
| Solution | Solution Plan | Project | `workflow/solution.md` |
| Slice | Slice Plan | Feature | `workflow/slice.md` |
| TDD | TDD Record | Slice | `workflow/tdd.md` |
| Review | Review Report | Slice | `workflow/review.md` |

## Normative language and precedence

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative.

When instructions conflict, precedence is:

1. this framework;
2. protocols;
3. workflow specifications;
4. platform adapters;
5. conversation context.

An implementation MUST stop and report a contract conflict rather than silently
choosing a lower-precedence instruction.

## Principles

- Artifacts before conversations.
- Business decisions are created only by Plan and Grill.
- Engineering decisions are created only by Solution and Slice.
- Execution work is confined to one resolver-authorized Slice.
- Upstream contracts are frozen before execution and versioned when changed.
- Existing system behavior is inspected before a solution is proposed.
- Delivery advances only from immutable evidence, never an agent's claim.

ForgeFlow core consists entirely of Markdown files. No Python package, schema engine,
plugin, model API, or platform-specific state store is part of the framework. A new
platform becomes compatible by supplying Markdown launchers that reference these
canonical specifications. Supported launchers include: Codex (`adapter/codex/`),
Copilot (`adapter/copilot/`). Generic participants and other platforms (Claude, Gemini)
remain usable through the core specifications without a dedicated launcher.

## Command execution policy

A command-execution session is the terminal, shell, or equivalent process channel
used by a participant. Unless the current authorized work genuinely requires
simultaneous processes, command execution MUST be sequential and the participant
MUST maintain at most one active command-execution session.

- When the platform supports session reuse, the participant MUST reuse the same
  terminal tab or equivalent session for consecutive commands. It MUST NOT create
  a new session merely because the next command is different.
- Before starting a command, the participant MUST confirm that an equivalent prior
  command is not still running. Duplicate test, build, server, or watcher processes
  MUST NOT be started.
- Commands MUST use bounded, one-shot mode by default. Watch, background, daemon,
  development-server, or other long-running modes MAY be used only when required
  for current acceptance evidence.
- Required concurrency MUST be explicit in the current Slice or verification need,
  use the minimum number of sessions, and be recorded with its reason. Convenience
  or independent review alone does not authorize concurrency.
- The workflow MUST track every long-running process it starts and terminate all of
  them before emitting a handoff. No background or watch process may be transferred
  implicitly to the next workflow.
- If a platform cannot reuse a session, commands MUST still run sequentially. The
  participant MUST ensure the previous process has exited, release its session when
  possible, and report the platform limitation instead of overlapping commands.

Review independence means a fresh evaluation and rerun of relevant checks. It does
not require a separate terminal tab, a separate command-execution session, or
concurrent execution.

## Review readiness and decision policy

TDD and Review MUST apply the same quality gate to the same current Requirement,
Solution Plan, Slice Plan, implementation, tests, and evidence. A finding is
blocking when evidence shows any of the following:

- required observable behavior, acceptance criteria, or business constraints in
  the Requirement are not satisfied;
- a required Solution Plan engineering contract is absent or violated, including
  interfaces, data, security, error handling, operations, or verification;
- the Slice Plan has an invalid boundary, dependency, scope, or completion gap;
- implementation, test, or regression behavior is incorrect;
- evidence required to establish compliance is missing or unreliable;
- a concrete maintainability defect creates a correctness or material change risk.

A preference without a demonstrated correctness, compliance, or material
maintainability consequence is non-blocking.

Before setting a TDD Record to READY_FOR_REVIEW, TDD MUST inspect its own change
and evidence against this gate. TDD may correct findings within its authority, but
it MUST NOT issue a Review decision or create a Review Report. Review independently
reapplies the same gate.

Review decides PASS exactly when zero blocking findings remain. PASS may include
non-blocking findings. Review decides FAIL exactly when one or more blocking
findings remain. Every finding MUST record severity, owner workflow, affected
scope, observable evidence, and violated contract.

When a FAIL contains blocking findings owned by multiple workflows, its single
RETURN destination is the most upstream owner in this precedence order:

```text
Grill > Solution > Slice > TDD
```

The RETURN Target Scope MUST equal that owner's canonical scope: affected Feature
for Grill, Project for Solution, affected Feature for Slice, and affected Slice
for TDD. Findings retain their individual affected scopes even when the selected
RETURN owner has a broader canonical scope. After the upstream issue is resolved,
version invalidation and transition resolution expose any remaining downstream
failing evidence.

## Canonical workflows

ForgeFlow defines exactly six canonical workflows, each owning one artifact type:

- **Plan** — decomposes project intent into an ordered Feature set (Project scope).
- **Grill** — produces Feature-level Requirements by establishing business decisions (Feature scope).
- **Solution** — analyzes all READY Requirements and establishes the Engineering Baseline (Project scope).
- **Slice** — decomposes one approved Feature into independently deliverable Slices (Feature scope).
- **TDD** — implements and tests one Slice against its Requirement and Solution Plan (Slice scope).
- **Review** — independently verifies one Slice's evidence against all contracts (Slice scope).

These workflows communicate through handoffs. The Transition Resolution Procedure
determines which workflow runs next; the Handoff Protocol carries the decision.

## Canonical flow

```text
Plan all Features
   -> Grill every Feature
   -> Solution analyzes every READY Requirement
   -> Slice every Feature
   -> for each Feature in Planning order
       for each Slice in Slice Plan order
         TDD -> Review -> PASS
   -> Project Complete
```

The barriers are strict:

- `BUSINESS_READY`: every planned Feature has a current READY Requirement.
- `ENGINEERING_READY`: a current READY Solution Plan references all Requirement
  versions.
- `DELIVERY_READY`: every planned Feature has a current READY Slice Plan that
  references the Solution Plan version.
- `PROJECT_COMPLETE`: every planned Slice has a latest valid PASS Review Report.

TDD MUST NOT start before `DELIVERY_READY`. A later Feature's Slice MUST NOT start
until every Slice of all earlier Features is complete.

## Artifact graph

Artifact location and Canonical Artifact Paths are governed exclusively by the
Artifact Protocol.

Edges between artifacts carry explicit versions. At minimum:

```text
Planning
   -> Requirement[Feature]
   -> Solution Plan[Requirement version map]
   -> Slice Plan[Feature, Solution Version]
   -> TDD Record[Solution Version, Slice Plan Version]
   -> Review Report[Solution Version, Slice Plan Version, Attempt]
```

If an upstream artifact gets a new version, dependent artifacts referencing an
older version are stale. Stale artifacts remain historical evidence but MUST NOT
authorize downstream execution or completion.

No mutable "Project State" artifact is authoritative. Phase, Feature cursor,
Slice cursor, and runtime Slice state are disposable projections produced from
the graph by the Transition Resolution Procedure.

## Transition Resolution Procedure

The Transition Resolution Procedure is a normative Markdown decision procedure
performed by the active workflow before every handoff. It:

- validates barrier and version conditions;
- derives project phase and runtime Slice states;
- selects the first incomplete Feature and Slice in declared order;
- selects the next workflow;
- emits one typed handoff.

It owns no artifact, requires no executable runtime, and makes no business or
engineering decision. Given the same valid graph, every conforming participant
MUST derive the same result by following the ordered rules in the Handoff Protocol.

### Handoff emission rule

Every workflow that reaches a handoff-producing end MUST validate and render
exactly one Canonical Handoff Block from the Handoff Protocol. The block MUST use
the selected variant's exact heading, fields, row order, and value rendering, and
MUST be the final content of the response. A workflow or adapter MUST NOT create a
local handoff format, omit required rows, add explanatory rows, or place content
after the block.

The emitting workflow is responsible for format validity before output. The target
workflow MUST reject a malformed handoff rather than infer or normalize it. An
authorized same-Workflow/same-Scope continuation or a wait for required user input
emits no handoff.

Runtime Slice state is derived as follows:

| State | Evidence |
|---|---|
| PENDING | Current Slice Plan exists; no current TDD evidence exists |
| IN_PROGRESS | Current TDD evidence exists; no valid PASS review exists |
| BLOCKED | An unresolved blocker targets this Slice |
| COMPLETE | Latest valid Review Report is PASS |

Slice Plans MUST NOT contain those dynamic runtime states.

## Blockers, returns, and recovery

A workflow MUST stop when required input is missing, contradictory, stale, or
outside its authority. A blocker identifies its owner and exact affected scope.

- Missing business policy returns to Grill for the affected Feature.
- Missing or invalid engineering policy returns to Solution.
- Invalid decomposition returns to Slice for the affected Feature.
- Implementation or test defects remain with TDD for the affected Slice.

After an upstream change, the procedure recomputes the whole graph. A Solution Plan
change invalidates old Slice Plans before TDD may resume. A Requirement change
requires Solution validation and then Slice validation. Recovery resumes at the
first incomplete valid Slice, not at a cursor saved in conversation history.

## Conformance

A conforming implementation MUST:

1. recognize exactly the six canonical workflows;
2. enforce the scope and ownership table above;
3. validate artifact metadata and version references;
4. enforce all four barriers;
5. use typed handoffs and the deterministic Transition Resolution Procedure;
6. preserve immutable review attempts;
7. reject execution whose Target Scope differs from a fresh procedure result;
8. construct the active artifact graph only from valid Canonical Artifact Paths;
9. satisfy every Markdown conformance scenario.

The framework relies solely on Markdown files and a participant capable of reading,
writing, and updating them in the order defined here. No executable parser, external
schema engine, or platform service is required to operate the core.
