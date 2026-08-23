# ForgeFlow Framework

Version: 2.20

ForgeFlow is an artifact-driven delivery framework for humans and AI agents. The
versioned artifact graph is the sole persistent source of truth. Conversations,
adapter prompts, and derived dashboards are never authoritative state.

## Project index

| Contract | Version | Path |
|---|---|---|
| Framework | 2.20 | `forgeflow.md` |
| Artifact Protocol | 2.17 | `protocol/artifact.md` |
| Handoff and Transition Protocol | 2.14 | `protocol/handoff.md` |

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
- Subsequent Plan changes preserve unaffected Feature evidence through explicit
  Feature-scoped compatibility versions.
- Existing system behavior is inspected before a solution is proposed.
- Delivery advances only from immutable evidence, never an agent's claim.
- Independent Feature Lanes may advance concurrently only when canonical dependency
  and shared-component contracts prove them parallel-safe.
- The Project Knowledge View is derived from canonical Artifacts and immutable
  history; it is never a second source of truth.

ForgeFlow core consists entirely of Markdown files. No Python package, schema engine,
plugin, model API, or platform-specific state store is part of the framework.

## Platform compatibility

Adapters are optional Markdown launchers. They add no framework rule and cannot
override the precedence defined above.

| Participant | Status | Launcher path |
| --- | --- | --- |
| Generic Markdown participant | Supported through the core specifications | `.forgeflow/forgeflow.md` |
| Codex | Dedicated launcher supplied | `.forgeflow/adapter/codex/` |
| Copilot | Dedicated launcher supplied | `.forgeflow/adapter/copilot/` |
| Claude | Supported generically; no dedicated launcher supplied | — |
| Gemini | Supported generically; no dedicated launcher supplied | — |

Every launcher path is workspace-root-relative and begins with `.forgeflow/`.
A new platform becomes compatible by supplying launchers that reference the canonical
Framework, Artifact Protocol, Handoff Protocol, and one Workflow specification in
that order. A launcher MUST NOT copy, redefine, or override their rules.

### Authoritative loading and workspace boundary

Before productive work, a participant MUST read the four authoritative files
completely and in this exact order: Framework, Artifact Protocol, Handoff Protocol,
then the single Workflow specification selected for the current invocation. Reading
the selected Workflow before either protocol is non-conforming even if all four are
eventually read.

#### Authoritative Read Completion Procedure

For each authoritative file, the participant MUST complete this procedure before
opening the next file:

1. Establish the file's current physical end using a line count, an explicit EOF
   indication, or an equivalent host capability.
2. Read from the first line through that physical end in contiguous ranges. A host
   preview, a successful partial read, or a model-generated summary is not evidence
   that the file was read completely.
3. Verify that the final non-blank line is the path-specific marker
   `<!-- forgeflow-eof: <canonical-path> -->`, where `<canonical-path>` is the
   repository-relative path of the file being read.
4. Retain an internal read receipt containing the canonical path, observed physical
   end, and verified EOF marker. Productive work may begin only after receipts exist
   for all four files in the required order.

If a read is truncated, the participant MUST continue from the next unread line. If
a range is skipped, the EOF marker is absent or mismatched, the file changes while
being read, or physical EOF cannot be established, the participant MUST restart that
file's read or stop without inspecting project implementation, changing artifacts,
or emitting a Handoff. It MUST NOT infer unread rules from prior conversations,
adapter text, summaries, or model memory.

The participant MUST NOT load another Workflow specification, adapter, or launcher
as preparation for a future transition. The Handoff Protocol contains the complete
transition procedure needed by the current Workflow. A future Workflow may be read
only by the distinct invocation authorized to execute it.

Once an IDE launcher has been invoked and its four authoritative paths are readable,
the participant MUST NOT inspect user-level agent configuration, global command
registries, home-directory prompt stores, or unrelated host-discovery paths. Project
inspection remains limited to repository evidence relevant to the authorized
Workflow. Host troubleshooting is a separate user-requested diagnostic operation,
not part of normal workflow execution.

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

Feature Lane concurrency consists of distinct Workflow executions. Each execution
still obeys the one-session command policy. Parallel lanes MUST have dependency-safe,
non-conflicting write responsibilities established by Solution; concurrency never
authorizes two executions for the same lane action or a shared write that Solution
has not ordered.

### Workflow persistence boundary

The canonical Artifacts and supplemental Reports explicitly defined by this
framework are the only persistent stores for workflow decisions, progress, and
evidence. A participant MUST NOT create a database table, SQL record, sidecar file,
host memory entry, task-tracking store, or other shadow state to retain ForgeFlow
questions, answers, decisions, cursors, summaries, or execution progress. Temporary
reasoning may remain in the current conversation, but it grants no future authority.

Each Workflow may mutate only the project surfaces authorized by its ownership and
required process. Tool availability does not grant mutation authority. In
particular, reading a repository database for relevant evidence does not authorize
writing to it, and a host-provided planning, memory, SQL, or agent-management tool
does not become part of ForgeFlow merely because it is available.

This exception applies only when the selected Workflow is TDD; it never authorizes
Plan, Grill, Solution, Slice, or Review to create application persistence. The
shadow-state prohibition does not forbid application persistence implemented by TDD.
When the current TDD Slice and its valid Solution/Slice contracts authorize it,
TDD MAY create or change application database schemas, migrations, tables, indexes,
seed or fixture data, and SQL records required by that Slice. Those mutations are
implementation work, must remain inside the authorized project/test/development
surface, and must be tested and recorded in the TDD Record. They MUST NOT target an
undeclared external or production datastore. Review MAY execute approved verification
that creates disposable test data, but it does not author new application persistence
outside the implementation already produced by TDD.

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
findings remain. Every finding MUST be one row in the Review Report's single
canonical Findings table and record severity, owner workflow, affected scope,
finding, observable evidence, and violated contract. Review derives its metadata
counts, decision, and FAIL disposition from those rows. Plugin reports are
supplemental evidence; they do not replace this core aggregate artifact.

When a FAIL contains blocking findings owned by multiple workflows, its single
RETURN destination is the most upstream owner in this precedence order:

```text
Plan > Grill > Solution > Slice > TDD
```

The RETURN Target Scope MUST equal the scope of a blocking finding owned by the
selected workflow: Project for Plan and Solution, affected Feature for Grill and
Slice, and affected Slice for TDD. Findings retain their individual affected scopes
even when the selected RETURN owner has a broader canonical scope. After the
upstream issue is resolved, version invalidation and transition resolution expose
any remaining downstream failing evidence.

## Canonical workflows

ForgeFlow defines exactly six canonical workflows, each owning one artifact type:

- **Plan** — decomposes project intent into an ordered Feature set (Project scope).
- **Grill** — produces Feature-level Requirements by establishing business decisions (Feature scope).
- **Solution** — analyzes all READY Requirements and establishes the Engineering Baseline (Project scope).
- **Slice** — decomposes one approved Feature into independently deliverable Slices (Feature scope).
- **TDD** — implements and tests one Slice against its Requirement and Solution Plan (Slice scope).
- **Review** — independently verifies one Slice's evidence against all contracts (Slice scope).

Source and test placement are engineering contracts, not local TDD preferences.
Solution owns the organization strategy and dependency direction; Slice maps its
authorized work to concrete or pattern-resolved production and test paths; TDD
creates or moves files only within those approved boundaries; Review verifies the
result. ForgeFlow does not prescribe one universal package-by-layer,
package-by-Feature, or language-specific directory convention.

These workflows communicate through handoffs. The Transition Resolution Procedure
determines which workflow runs next; the Handoff Protocol carries the decision.

Together, the current canonical Artifacts form the active project knowledge
baseline. Their version references create one traceability chain from approved
intent through business contracts, engineering decisions, delivery decomposition,
implementation evidence, and Review outcomes. Historical Artifacts and reports
preserve superseded evidence without participating in current authorization. The
Artifact Protocol defines the read-only Project Knowledge View over both layers.
Implementations MAY provide filtered JSON or Markdown renderings of that view. A
filter narrows navigation only; it never changes declared order, active state, or
the Workflow/Scope authorization derived from the complete graph.

A derived Project Impact View MAY resolve Feature dependencies, reverse
dependencies, shared-component relationships, and current change classifications
from structured Solution metadata. It is advisory evidence for navigation and
planning only. Transition Resolution reads canonical Solution dependency and access
metadata, never the derived view. The view MUST NOT authorize a Workflow, select a
Target Scope, advance a Gate, or make invalid or historical evidence current.

## Execution scope isolation

A workflow execution is one authorized invocation of exactly one Workflow at exactly
one Target Scope. A workflow execution MUST NOT consume a future execution scope
unless that scope is explicitly provided by the incoming Canonical Handoff or a
validated Feature Lane Entry. Bootstrap Entry, Subsequent Plan Entry, Feature Lane
Entry, and Recovery Entry authorize only their exact scope and never future progression.

A future execution scope is any Workflow or Target Scope other than the invocation's
validated authorization, including a different Feature owned by the same Workflow
or a later Slice selected after the current Slice completes. Once the Transition
Resolution Procedure selects such a scope, the current execution MUST only emit the
required Canonical Handoff and stop. It MUST NOT analyze, question, create or modify
artifacts, run commands, implement, or review work for that future scope.

Therefore:

- one Grill execution processes at most one Feature and writes at most that
  Feature's Requirement;
- one Slice execution processes at most one Feature and writes at most that
  Feature's Slice Plan, although that plan may declare multiple future Slices;
- one TDD execution implements at most one Slice; and
- one Review execution evaluates at most one Slice attempt.

Clarification turns may continue without a Handoff only while the Workflow and
Target Scope remain identical. A same-Workflow transition to another Feature or
Slice is a new execution, not an in-invocation loop.

### Invocation termination barrier

A direct IDE launcher invocation is manual and authorizes exactly one Workflow
execution. When that execution emits a Canonical Handoff, the Handoff is an output
for a future invocation, not an instruction the emitting agent may consume. The
agent MUST end the response at the Handoff and MUST NOT invoke, simulate, delegate,
or begin the Next Workflow or Target Scope in the same invocation.

Only an external orchestrator may consume a completed Handoff and start a distinct
workflow execution automatically. That orchestrator MUST validate the Handoff and
fresh Artifact Graph before every new execution. A repository configuration value,
IDE agent mode, model capability, tool delegation feature, or conversational request
to "continue" does not turn one workflow execution into an orchestrator.

The optional Python CLI Runner is such an external orchestrator only while executing
its explicit auto pipeline. Its `forgeflow.json` mode is CLI configuration and has
no authority over direct IDE launchers or the Markdown framework itself.

## Canonical flow

```text
Plan all currently approved Features
   -> Grill every Feature
   -> Solution analyzes every READY Requirement
   -> derive dependency-ready Feature Lanes
      -> each ready Feature: Slice -> TDD -> Review -> next Slice
      -> independent ready Features may run as parallel invocations
      -> dependent Features wait for all dependency lanes to PASS
   -> Project Complete
```

The barriers are strict:

- `BUSINESS_READY`: every planned Feature has a READY Requirement matching its
  current Feature Contract Version.
- `ENGINEERING_READY`: a current READY Solution Plan references all Requirement
  versions, declares one Feature Engineering Version per active Feature, and has a
  valid combined dependency/shared-access contract.
- `LANE_READY(F)`: Feature F is incomplete, every effective dependency is complete,
  and no Project or F-scoped blocker prevents its next derived action.
- `LANE_DELIVERY_READY(F)`: F is `LANE_READY` and has a current READY Slice Plan
  referencing its Feature Engineering Version.
- `PROJECT_COMPLETE`: every planned Slice has a latest valid PASS Review Report.

An explicitly approved project with no delivery objective uses `Feature IDs = NONE`
and persisted `Empty Feature Approval` evidence in its READY Planning artifact.
That Planning file MUST be the sole active artifact. It bypasses no applicable
barrier: Feature- and Slice-dependent barriers have no subject, so Rule 11 derives
`PROJECT_COMPLETE` after graph validity, blocker, and Planning readiness checks.
Blank Feature metadata or an empty graph with downstream artifacts is invalid.

TDD for Feature F MUST NOT start before `LANE_DELIVERY_READY(F)`. Planning order is
not an execution dependency. A Feature waits only for its effective dependencies;
independent Features may progress through separate validated invocations.

## Artifact graph

Artifact location and Canonical Artifact Paths are governed exclusively by the
Artifact Protocol.

Edges between artifacts carry explicit versions. At minimum:

```text
Planning
   -> Requirement[Feature Contract Version]
   -> Solution Plan[Requirement version map, Feature Engineering Version map]
   -> Slice Plan[Feature, Feature Engineering Version]
   -> TDD Record[Feature Engineering Version, Slice Plan Version]
   -> Review Report[Feature Engineering Version, Slice Plan Version, Attempt]
```

A new Planning or Solution Plan artifact version does not by itself invalidate every
Feature. Planning advances the Feature Contract Version only for an added or
business-affected Feature. Solution advances the Feature Engineering Version only
for a new or engineering-affected Feature. Evidence is stale when its applicable
Feature-scoped version or a directly referenced Slice Plan version no longer matches.
Stale evidence remains history but MUST NOT authorize downstream execution or
completion. Invalidation remains transitive within each affected Feature chain: a
downstream BLOCKED artifact cannot authorize RETURN or Recovery merely because its
direct version reference matches when an earlier barrier in that chain is unusable.

No mutable "Project State" artifact is authoritative. Phase, Feature cursor,
Slice cursor, and runtime Slice state are disposable projections produced from
the graph by the Transition Resolution Procedure.

## Transition Resolution Procedure

The Transition Resolution Procedure is a normative Markdown decision procedure
performed by the active workflow before every handoff. It:

- validates barrier and version conditions;
- derives project phase, Feature Lane readiness, and runtime Slice states;
- preserves the current lane or selects a dependency-ready lane and its next action;
- selects the next workflow;
- emits one typed handoff.

For Rule 2 it also derives a deterministic primary graph error code and an exact
terminal evidence projection. HALTED is authorized only when its Reason code and
sorted Input Artifacts reproduce that projection. Invalid artifacts remain eligible
as terminal evidence: they use a single readable valid Version when available and
`INVALID_VERSION` only when no such Version exists. A root-level contradiction with
no canonical artifact uses the HALTED-only value `NONE`.

Every use of "first Feature" or "first Slice" is a deterministic tie-breaker among
otherwise eligible candidates using Planning or Slice Plan position. It never makes
an unrelated Feature a dependency and never means the numerically smallest identifier
or filename.

It owns no artifact, requires no executable runtime, and makes no business or
engineering decision. Given the same valid graph and the same validated entry or
current-scope context, every conforming participant MUST derive the same result by
following the ordered rules in the Handoff Protocol.

### Handoff emission rule

Every workflow that reaches a handoff-producing end MUST validate and render
exactly one Canonical Handoff Block from the Handoff Protocol. The block MUST use
the selected variant's exact heading, fields, row order, and value rendering, and
MUST be the final content of the response. A workflow or adapter MUST NOT create a
local handoff format, omit required rows, add explanatory rows, or place content
after the block.

Artifact and Handoff Markdown structures are protocol data, not presentational
suggestions. A participant or host MUST NOT translate them into XML, HTML, YAML,
plain key-value text, a native planning format, or another visually similar
representation. Workflow names and scopes are distinct values: a Workflow name such
as `Plan` MUST NOT be rendered where the canonical scope is `Project`.

Handoff emission completes the current workflow execution. Emission and consumption
MUST be separate executions even when Next Workflow equals the current Workflow.
The Handoff is also the final action of the emitting execution: no tool call,
command, state update, progress event, or additional response content may follow it.

The emitting workflow is responsible for format validity before output. The target
workflow MUST reject a malformed handoff rather than infer or normalize it. An
authorized same-Workflow/same-Scope continuation or a wait for required user input
emits no handoff. A transition to the same Workflow at a different Target Scope is
not a continuation and MUST emit a FORWARD handoff for the newly authorized scope.
A fresh invocation may proceed without an incoming handoff only through Bootstrap,
Plan's Subsequent Plan, Feature Lane, or persisted-blocker Recovery Entry. A
non-empty later Plan intent is a change to the current software
project without requiring an incremental label or project-identity confirmation.
Semantic similarity never identifies another project or rotates evidence. Recovery
authority comes from a fresh Rule 3 result and never permits a synthetic or
same-authorization RETURN.

Runtime Slice state is derived as follows:

| State | Evidence |
|---|---|
| PENDING | Current Slice Plan exists; no current TDD evidence exists |
| IN_PROGRESS | Current TDD evidence exists; no valid PASS review exists |
| BLOCKED | A valid current BLOCKED artifact or FAIL Review Report targets this Slice |
| COMPLETE | Latest valid Review Report is PASS |

Slice Plans MUST NOT contain those dynamic runtime states.

## Blockers, returns, and recovery

A workflow MUST stop when required input is missing, contradictory, stale, or
outside its authority. A blocker identifies its owner and exact affected scope.
Every Feature or Slice in that scope must already be declared by the active Artifact
Graph. A blocker, Review finding, launcher, or conversation cannot create a narrower
authorization by naming an undeclared identifier; such a reference is a graph
contradiction.
Before a non-Review workflow returns or ends an invocation with an unresolved
blocker, it MUST persist that blocker in its own owned artifact using the Artifact
Protocol's BLOCKED metadata. Review persists blocking findings in its immutable FAIL
Review Report. Conversation text alone is never sufficient blocker state.

- Missing business policy returns to Grill for the affected Feature.
- Missing or invalid engineering policy returns to Solution.
- Invalid decomposition returns to Slice for the affected Feature.
- Implementation or test defects remain with TDD for the affected Slice.

After an upstream change, the procedure recomputes the whole graph. A Requirement
change requires Solution validation. Solution then advances Feature Engineering
Versions only for Features with demonstrated engineering impact; Slice, TDD, and
Review evidence remains usable for every unaffected Feature. Recovery resumes at
the selected lane's next valid action, not at a cursor saved in conversation history.

## Conformance

A conforming implementation MUST:

1. recognize exactly the six canonical workflows;
2. enforce the scope and ownership table above;
3. validate artifact metadata and version references;
4. enforce the project and Feature Lane barriers;
5. use typed handoffs and the deterministic Transition Resolution Procedure;
6. preserve immutable review attempts;
7. reject execution whose Target Scope differs from a fresh procedure result and
   prevent an execution from consuming any subsequently selected future scope;
8. construct the active artifact graph only from valid Canonical Artifact Paths;
9. preserve unaffected Feature evidence across valid Subsequent Plan changes; and
10. exclude both Artifact History and Reports History from current progression;
11. derive any Project Knowledge View without creating new authority or replacing
    canonical Artifact validation.

The framework relies solely on Markdown files and a participant capable of reading,
writing, and updating them in the order defined here. No executable parser, external
schema engine, or platform service is required to operate the core.

<!-- forgeflow-eof: .forgeflow/forgeflow.md -->
