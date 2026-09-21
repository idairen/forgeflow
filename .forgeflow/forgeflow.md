# ForgeFlow Framework

Version: 3.8

ForgeFlow is an Artifact-driven delivery framework for humans and AI agents. The
versioned Artifact Graph is the sole persistent source of truth; conversation,
launchers, logs, and derived views are never authoritative.

## Project index

| Contract | Version | Path |
| --- | --- | --- |
| Framework | 3.8 | `forgeflow.md` |
| Artifact Protocol | 2.19 | `protocol/artifact.md` |
| Transition Protocol | 1.8 | `protocol/transition.md` |
| Handoff Protocol | 2.15 | `protocol/handoff.md` |

| Workflow | Artifact | Scope | Specification |
| --- | --- | --- | --- |
| Plan | Planning | Project | `workflow/plan.md` |
| Grill | Requirement; Feature Lane Record | Feature | `workflow/grill.md` |
| Solution | Solution Plan | Project | `workflow/solution.md` |
| Slice | Slice Plan | Feature | `workflow/slice.md` |
| Implement | Implement Record | Slice | `workflow/implement.md` |
| Review | Review Report | Slice | `workflow/review.md` |

## Normative model

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative. Conflicts resolve by:
Framework → Artifact Protocol → Transition Protocol → Handoff Protocol → Workflow →
adapter → conversation. Stop and report a conflict rather than follow lower
precedence.

ForgeFlow follows these invariants:

- Artifacts before conversations; progress requires evidence, not claims.
- Plan and Grill alone create business decisions; Solution and Slice alone create
  engineering decisions.
- Existing behavior is inspected before engineering design.
- Upstream contracts are frozen before execution and versioned when changed.
- Compatible changes preserve unaffected Feature evidence.
- One invocation executes one resolver-authorized Workflow and Scope.
- Independent Grill Feature Lanes may execute concurrently while remaining isolated.
- Knowledge and impact views are disposable projections without authority.

ForgeFlow core is Markdown. Executable tooling, schema engines, plugins, model APIs,
and platform state may automate it but are not part of or superior to the core.

## Ownership

| Workflow | Owns | Must not own |
| --- | --- | --- |
| Plan | Approved intent, Feature topology, project constraints | Feature rules or engineering design |
| Grill | Feature Lane Record; observable Feature behavior and Requirement | Architecture, APIs, technical errors, implementation |
| Solution | Architecture, interfaces, data, security, operations, verification | Business outcomes, Slices, code |
| Slice | Delivery decomposition, dependencies, planned file placement | Business or project-wide engineering policy |
| Implement | One Slice's authorized changes, verification execution, and Implement Record | Upstream contracts or Review decisions |
| Review | One attempt's independent findings and disposition | Repairs or upstream changes |

Source and test placement are engineering contracts: Solution defines organization
and dependency direction, Slice resolves placement, Implement implements within it, and
Review verifies it. No language-specific layout is universal.

Implement is the sole implementation Workflow; TDD is a verification strategy, never
a peer Workflow or separate state machine. Solution owns verification obligations,
mandatory checks, and passing criteria. Slice maps them to each Slice's verification
plan. Implement selects and refines strategies within that plan, executes them, and
records evidence; a rationale cannot weaken or replace mandatory verification.
Review independently evaluates coverage, execution evidence, and correctness.

One Slice may require multiple strategies. A successful check does not discharge
another required check. Routine test cases, commands, and parameters within approved
constraints are Implement decisions; changes to those constraints return to their
owner. Plan and Grill do not acquire engineering verification responsibilities.

## Clarification

Plan, Grill, and Solution ask only within their ownership. When an owned material
decision cannot be inferred from approved Artifacts and observable repository
evidence, they ask and wait rather than invent policy, assumptions, exclusions, or
downstream work.

Offer only evidence-supported or established domain options, explain the relevant
effect, use no more than three to five without filler, and end with `Other`. Do not
offer conflicting choices or steer the user. Waiting remains in the same
Workflow/Scope, emits no Handoff, and grants no future authority.

## Platform and loading boundary

Generic Markdown participants use the core. Dedicated launchers exist under
`.forgeflow/adapter/codex/` and `.forgeflow/adapter/copilot/`; Claude and Gemini are
supported generically. Adapters add no rule.

Only when explicitly requested to recover an invalid Review, additionally read
`protocol/review-recovery.md` after the four core contracts. This bounded maintenance
operation is not Review execution or a seventh Workflow. It requires authorization
for the concrete file disposition; ordinary Workflow commands never authorize it.
Normal Workflows do not load this optional procedure.

A new dedicated adapter is compatible only when each workspace-root-relative
launcher reads the five canonical files below in order without copying or overriding
their rules.

Before productive work, read completely and in order: Framework, Artifact Protocol,
Transition Protocol, Handoff Protocol, then exactly one authorized Workflow. Do not
load another Workflow or launcher for a future transition.

After a direct IDE launcher resolves those files, do not inspect user-level agent
configuration, global command registries, home-directory prompt stores, or unrelated
host-discovery paths. Host troubleshooting requires a separate user request.

## Execution policies

### Invocation boundary

An entry authorizes exactly one Workflow and Target Scope. Clarification continues
only at that same authorization. A later Workflow, Feature, Slice, or attempt is a
future Scope.

When required Handoff authorization is missing or invalid and no other valid Entry
applies, Transition permits read-only routing correction before productive work.
This is not a Workflow Entry: it writes no Artifacts, runs no application tests or
plugins, and never starts the target Workflow. It emits the fresh routing result
and stops under Transition/Handoff rules. Valid Entries proceed normally without
an additional correction step.

When Transition selects a future Scope, emit one Canonical Handoff and stop. A direct
IDE invocation cannot consume its own Handoff. Only an external orchestrator may
start a distinct execution after revalidating the Handoff and fresh graph. The
no-Handoff parallel exceptions are an eligible Grill Lane Entry and a valid Grill
Lane Recovery under the Transition Protocol, each isolated to one Feature with an
atomic claim. Release-only Recovery authorizes no business work. CLI mode, model
capability, delegation, or a request to continue does not widen authorization.

### Command lifecycle

Unless authorized work genuinely requires simultaneous processes, keep at most one
active command session and run sequentially.

Feature Lane concurrency consists of isolated Workflow executions for distinct
Features. It never means multiple Feature mutations or command sessions inside one
Grill execution.

- Reuse the session when supported and never duplicate an active equivalent command.
- Within one invocation, prefer bounded one-shot commands. Command concurrency
  requires a current Slice or verification need, the minimum sessions, and a
  recorded reason.
- Track and terminate every long-running process before Handoff.
- Without session reuse, confirm exit, release when possible, and report the
  limitation.

Independent Review means fresh evaluation and checks, not another terminal.

## Shared review gate

Implement and Review evaluate the same current Requirement, Solution, Slice Plan,
implementation, tests, and evidence. A finding is blocking only when evidence shows:

- required behavior, acceptance criteria, or business constraints fail;
- required engineering contracts are absent or violated;
- Slice boundaries, dependencies, placement, or completion are invalid;
- implementation, tests, or regressions are incorrect;
- required compliance evidence is missing or unreliable; or
- a maintainability defect creates correctness or material change risk.

Unsupported preference is non-blocking. Implement self-checks and repairs within its
authority but never decides Review. Review independently PASSes with zero blocking
findings and FAILs with one or more. Its canonical Findings table is the aggregate
decision; plugin reports are supplemental.

Implement reaches READY_FOR_REVIEW only after every required verification obligation
has current, adequate evidence meeting its passing criteria and no blocking issue
remains. Pending checks keep work IN_PROGRESS or BLOCKED as appropriate. Tool
execution, human acceptance, and model assessment are distinct evidence sources;
neither an unsupported assertion nor a successful irrelevant command proves a gate.
Review is the normal next Workflow after readiness, not an unconditional exit that
bypasses upstream RETURN, blocker, or graph-contradiction handling.

For multiple FAIL owners, choose the most upstream:
`Plan > Grill > Solution > Slice > Implement`. Return Scope is Project for Plan/Solution,
the affected Feature for Grill/Slice, and the affected Slice for Implement.

## Flow and barriers

```text
Plan
  -> Grill dependency-ready Features in isolated parallel Lanes
  -> join when every Requirement is READY
  -> Solution over every READY Requirement
  -> Slice every Feature
  -> each Feature and Slice in declared order: Implement -> Review -> PASS
  -> Project Complete
```

| Barrier | Condition |
| --- | --- |
| BUSINESS_READY | every Feature has a READY Requirement matching its Feature Contract Version |
| ENGINEERING_READY | current READY Solution references all Requirements and declares every Feature Engineering Version |
| DELIVERY_READY | every Feature has a READY Slice Plan matching its Feature Engineering Version |
| PROJECT_COMPLETE | every Slice has a latest valid matching PASS |

An approved no-delivery project uses `Feature IDs = NONE`, persisted Empty Feature
Approval, and Planning as the sole active Artifact.

## Artifact compatibility

The Artifact Protocol owns paths, metadata, versions, history, and views. The active
chain is:

```text
Planning
  -> Requirement[Feature Contract Version]
  -> Solution[Requirement map, Feature Engineering Version map]
  -> Slice Plan[Feature Engineering Version]
  -> Implement[engineering version, Slice Plan Version, Attempt]
  -> Review[matching versions and Attempt]
```

Feature Lane Records coordinate parallel Requirement creation but do not become a
business or engineering contract link in this chain.

Planning advances only added or business-affected Feature Contract Versions;
Solution advances only new or engineering-affected Feature Engineering Versions.
Invalidation is transitive within each affected Feature. A valid-but-stale Solution
may remain at its canonical path for comparison and update under the Artifact
Protocol; it cannot satisfy an engineering or delivery barrier. History never joins
the active graph, but bounded lineage, archival, and counter checks may read it.
Other stale evidence cannot authorize work or completion. No mutable Project State,
phase, or cursor is authoritative.

## Conformance

A conforming implementation recognizes exactly the six Workflows; enforces
ownership, paths, metadata, versions, barriers, entry, transition, and typed
Handoffs; preserves immutable attempts and required history; isolates each
invocation; atomically claims each Feature Lane; releases claims before upstream
RETURN; recovers interrupted claims only under the Transition Protocol and fences
superseded executions; prevents duplicate or dependent Lane execution; joins all
READY Requirements before Solution; retains compatible Feature evidence; excludes
history, backups, logs, and supplemental reports from
progression; and derives views without creating authority.
