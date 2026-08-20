# Handoff and Transition Protocol

Version: 2.9

## Purpose

A handoff records the result of a workflow's execution — the decision, artifacts produced, and what happens next in the ForgeFlow pipeline. It captures both the forward progress and any blockers that require re-work by an upstream owner. A handoff does not transfer artifact ownership and does not replace artifact evidence. The receiving workflow must still read current artifacts from the Artifact Root to validate the decision before acting on it.

## Active Artifact Graph

Build the active artifact graph exclusively from the Artifact Root defined by the Artifact Protocol. Only files at valid Canonical Artifact Paths participate in resolution. Review Report attempt files coexist as immutable history; archived or replaced contract versions do not participate in the active graph.

An artifact is usable for forward progress only when all of these hold:

1. Its status is READY, or READY_FOR_REVIEW for a TDD Record.
2. Every required upstream version equals the active upstream artifact version.
3. Its Feature and Slice identifiers exist in the active Planning and Slice Plan.
4. No duplicate active artifact or duplicate Review attempt exists.

If any of these conditions fails, the artifact cannot satisfy a barrier, authorize work, or prove completion. A canonical artifact with Status `BLOCKED` is not usable for forward progress, but it remains active blocker evidence when its required blocker metadata is valid and every preceding upstream barrier has a usable current artifact. This upstream requirement is transitive: matching only the immediately referenced version is insufficient when an earlier Planning, Requirement, Solution Plan, or Slice Plan is missing, stale, or not READY. A stale downstream blocker remains evidence but cannot authorize RETURN or Recovery Entry. A valid current blocker remains unresolved until its owner replaces it with a higher valid version or attempt whose Status is no longer `BLOCKED`. A Review Report is valid only when its single canonical Findings table is structurally valid, its metadata counts and decision match its rows, and its FAIL disposition matches the highest-precedence blocking finding owner and one of that owner's blocking scopes. A READY_FOR_REVIEW TDD Record with stale upstream versions is ignored and TDD reruns at that scope. A PASS Review Report without a corresponding current TDD Record is also ignored and cannot complete the Slice.

### Determinism Rule

Ordering comes exclusively from declared positions in Planning and the current Slice Plans. Identifier numbers, canonical filenames, filesystem enumeration order, artifact creation time, and conversation order never define Feature or Slice priority. If the graph is contradictory — duplicate active contracts, duplicate Review attempts, invalid Feature or Slice identifiers, missing required metadata, invalid FAIL disposition, or Review Report counts that differ from its finding body — resolution stops at INVALID GRAPH and does not guess a next workflow.

## Transition Resolution Procedure

Evaluate these rules in order and stop at the first match. A transition between different Workflow/Scope authorizations produces the stated Canonical Handoff variant. Bootstrap Entry, Plan's Subsequent Plan Entry, and Recovery Entry authorize a fresh invocation without synthesizing a handoff. The receiving workflow applies the rules fresh from the active artifact graph and never relies on remembered conversation state.

### Rule 1 — Bootstrap Without Planning

No Planning artifact exists and the Artifact Root is absent or empty. **Action**: authorize Plan at `Project` scope through Bootstrap Entry. No incoming handoff exists and no synthetic handoff is created. A non-empty Artifact Root without Planning is evaluated by Rule 2 rather than treated as a safe bootstrap.

### Rule 2 — Graph Contradiction

The artifact graph is contradictory: a non-empty Artifact Root without Planning, duplicate active contracts, duplicate Review attempts, invalid identifiers, invalid empty-Feature approval metadata, any downstream artifact beside a `NONE` Planning, a BLOCKED Affected Scope or any Review Finding or FAIL Return Scope that does not resolve to declared identifiers, missing required metadata, a missing or malformed canonical Findings table, Review count/decision/disposition mismatch, or conflicting version references. **Action**: emit the `TERMINAL / HALTED` template with Blocker Category `GRAPH_CONTRADICTION`, Affected Scope `Project`, and an evidence-based Reason. No productive workflow runs until the contradiction is corrected outside the invalid transition.

Rule 2 derives one deterministic primary contradiction and a terminal evidence
projection before HALTED is rendered. Artifact validation follows canonical filename
order and each artifact's validation order; graph-reference validation follows the
Transition Resolution Procedure. The projection contains exactly the canonical
artifacts needed to demonstrate that primary contradiction, sorted by filename.
Relational contradictions include Planning, the offending artifact, and the
applicable Slice Plan when Slice membership is material. A root-level contradiction
with no canonical artifact has an empty projection.

Each projected artifact uses its active version when valid. An invalid artifact
still uses its readable version when the file contains exactly one valid
`major.minor` Version value. It uses `INVALID_VERSION` only when Version is absent,
duplicated, unreadable, or malformed. A HALTED handoff MUST reproduce the projection
exactly: no omitted, additional, reordered, nonexistent, or differently versioned
entry is allowed. An empty projection is rendered as the exact value `NONE`, which
is forbidden by every other handoff variant.

HALTED Reason begins with the graph error code, the exact delimiter `: `, and a
non-empty human-readable explanation. The graph error codes are:

| Graph Error Code | Primary contradiction |
| --- | --- |
| `artifact_root_invalid` | Artifact Root is not a usable directory |
| `planning_missing` | A non-empty root or active graph has no valid Planning |
| `artifact_invalid` | A canonical artifact, identifier list, version, or required structure is invalid |
| `empty_project_contradiction` | `NONE` Planning coexists with a downstream artifact |
| `identifier_reference_invalid` | An artifact references an undeclared Feature or Slice |
| `routing_scope_invalid` | Blocker, Review Return, or Review Finding scope does not resolve |

### Rule 3 — Persisted Blocker Exists

After Rule 2 has validated every blocker scope reference, one or more canonical artifacts have Status `BLOCKED` with valid blocker metadata and a complete transitive chain of usable current upstream artifacts. Filter out stale downstream blockers before selection. Select deterministically by this tuple: Blocker Owner position in `Plan > Grill > Solution > Slice > TDD`; Affected Scope Feature position in Planning when applicable; and Affected Scope Slice position in that Feature's current Slice Plan when applicable. Compare declared positions, never identifier numbers. Blockers with the same owner and exact scope authorize the same transition; a canonical-path tie-breaker may be used only to keep internal evidence selection stable. **Action**: when another Workflow or Scope is currently authorized, RETURN to the selected Blocker Owner and Affected Scope using its Blocker Category. A blocker owned by the currently active workflow at the same scope remains in that workflow without a handoff while it waits for required user input. A fresh invocation with no incoming handoff uses Recovery Entry only when this rule selects that exact owner and scope; it never creates or emits a same-authorization RETURN.

### Rule 4 — Planning Not Ready

A Planning artifact exists but is DRAFT, stale, or otherwise not usable and is not a valid persisted blocker selected by Rule 3. **Action**: FORWARD to Plan at `Project` scope.

### Rule 5 — Missing or Stale Requirement

At least one Feature is declared, and the first Feature in Planning order lacks a usable current Requirement whose Planning Version matches that Feature's current Feature Contract Version. **Action**: FORWARD to Grill at `Feature: F-XX` for that Feature.

### Rule 6 — Missing, Stale, or Incomplete Solution Plan

At least one Feature is declared and every planned Feature has a usable current Requirement, but the Solution Plan is absent, not READY, incomplete, or does not reference every current Requirement version. **Action**: FORWARD to Solution at `Project` scope.

### Rule 7 — Missing or Stale Slice Plan

At least one Feature is declared, and the first Feature in Planning order lacks a usable current Slice Plan, or its Slice Plan does not reference that Feature's current Feature Engineering Version from the current Solution Plan. **Action**: FORWARD to Slice at `Feature: F-XX` for that Feature. TDD is forbidden until every planned Feature has a usable current Slice Plan.

### Rule 8 — Current Review Failure

At least one Feature is declared, and the current TDD Record attempt for a Slice has a valid matching FAIL Review Report. Its canonical Findings table has at least one blocking row, the recorded Return Workflow is the highest-precedence blocking finding owner, and Return Scope equals one blocking finding scope for that owner after Rule 2 identifier resolution. **Action**: RETURN to that recorded Return Workflow and Return Scope. A FAIL for an older TDD attempt remains history and does not match this rule after TDD advances the attempt.

### Rule 9 — Review Required

At least one Feature is declared, and the first incomplete Slice in Planning Feature order and Slice Plan order has a current READY_FOR_REVIEW TDD Record, and no valid Review Report exists for that same attempt and current upstream versions. **Action**: FORWARD to Review at `Slice: F-XX/S-XX`.

### Rule 10 — TDD Required

At least one Feature is declared, all delivery barriers are satisfied, and the first incomplete Slice in Planning Feature order and Slice Plan order has no current READY_FOR_REVIEW TDD Record awaiting Review. This includes a Slice with no TDD Record, stale TDD evidence, or a corrected attempt required after Rule 8 returned to TDD. **Action**: FORWARD to TDD at `Slice: F-XX/S-XX`.

### Rule 11 — Project Complete

Every planned Slice has a current READY_FOR_REVIEW TDD Record and a valid matching PASS Review Report for the same attempt and current upstream versions, and no unresolved blocker exists. A READY Planning artifact with `Feature IDs = NONE`, valid Empty Feature Approval evidence, and no other active artifact also satisfies completion. Rules 5 through 10 require at least one declared Feature and therefore do not match that graph. **Action**: emit the `TERMINAL / COMPLETE` template with Completed Scope `Project`.

## Entry Modes and Unified Entry Validation Procedure

There are exactly four entry modes:

- **Bootstrap Entry**: no incoming handoff exists. It is valid only for Plan at `Project` scope when Rule 1 matches.
- **Subsequent Plan Entry**: no incoming handoff exists, a non-empty new or changed User Intent is supplied after current READY Planning, and the current graph has no graph contradiction, actionable persisted blocker, or current FAIL Review. It temporarily authorizes only Plan at `Project` scope to merge that intent into a higher Planning version. The user does not need to label the intent incremental or confirm that it belongs to the current software project. It never rotates project evidence or synthesizes a handoff.
- **Handoff Entry**: an incoming Canonical Handoff Block exists. Every workflow, including Plan rework, MUST execute this unified validation before accepting or acting on it.
- **Recovery Entry**: no incoming handoff exists, and a fresh Rule 3 result selects the exact current Workflow and Target Scope from a valid persisted blocker. Recovery re-authorizes only that blocker owner and scope; it does not create a synthetic handoff or authorize unrelated work.

No workflow other than Plan may use Bootstrap or Subsequent Plan Entry. Plan,
Grill, Solution, Slice, and TDD may use Recovery Entry only for a persisted blocker
they own. Review owns no persisted BLOCKED artifact and cannot use Recovery Entry.
Any direct invocation without a valid Bootstrap, Subsequent Plan, Handoff, or
Recovery Entry performs no productive work.

### Invocation-scoped authorization

Entry validation authorizes exactly one Workflow and one Target Scope for the
current execution. A workflow execution MUST NOT consume a future execution scope
unless that scope is explicitly provided by the incoming Canonical Handoff. The
current execution cannot treat a fresh Transition Resolution Procedure result as
permission to begin the selected future scope.

When resolution selects a different Workflow or a different Target Scope owned by
the same Workflow, the current execution MUST render the applicable Canonical
Handoff as its final content and stop. Only a subsequent execution that accepts
that Handoff may perform productive work at the new scope. It is forbidden for the
current execution to ask questions, inspect scope-specific implementation, create
or modify artifacts, run commands, implement, or review on behalf of that future
scope. Recovery Entry remains limited to its exact persisted-blocker scope and
cannot be used to skip this boundary for normal forward progression.

For Subsequent Plan Entry, Plan MUST verify before productive work that:

1. no incoming Handoff Block is being accepted or inferred;
2. the active Artifact Graph is structurally valid and contains one current READY Planning artifact;
3. no valid current blocker or FAIL Review is awaiting its canonical owner;
4. the User Intent is non-empty;
5. semantic similarity is not used to infer another project, request project-identity confirmation, or authorize evidence rotation; and
6. only Plan is authorized until the new Planning version is persisted and the Transition Resolution Procedure is applied fresh.

A Subsequent Plan Entry may add, modify, reorder, or explicitly retire Features.
It preserves stable identifiers, archives replaced evidence through the Artifact
Protocol, and records an exact Planning Change Set. User intent cannot authorize a
different workflow directly or make stale downstream evidence current.

Project Evidence Rotation is an explicit reset or archive maintenance operation,
not an entry mode and not an outcome inferred by Plan. It MUST NOT be triggered by
semantic distance between a later User Intent and current Planning.

For Recovery Entry, the workflow MUST verify before productive work that:

1. no incoming Handoff Block is being accepted or inferred;
2. the active Artifact Graph is valid and Rule 3 is the first matching rule;
3. Rule 3 selects the current Workflow and exact Target Scope;
4. the selected blocker metadata and every required upstream version are current; and
5. conversation text or launcher context does not widen the recovered authorization.

If any recovery check fails, the workflow performs no productive work. CLI-provided entry context is a projection to validate, not authority that can override the active Artifact Graph.

When a workflow receives a handoff block, it must verify:

1. **Exactly one variant applies**: The `Transition` field is exactly one of `FORWARD`, `RETURN`, or `TERMINAL`. A TERMINAL block also has exactly one `Terminal Status`: `COMPLETE` or `HALTED`.
2. **All required fields present, all forbidden fields absent**: Each template variant defines its fixed set of required and forbidden fields (see Template Variants section). A handoff with a missing required field or an extra forbidden field is invalid — the receiving workflow performs no work and must reject it back to the source.
3. **Workflow names are canonical**: When present, `Next Workflow` matches one of Plan, Grill, Solution, Slice, TDD, or Review. Unknown workflow names are invalid.
4. **Input Artifacts resolve**: Every entry in `Input Artifacts` uses the exact rendering `<canonical filename> = <version>` and resolves under the Artifact Root. Multiple entries use exactly `; ` as their separator. FORWARD, RETURN, and `TERMINAL / COMPLETE` state the active `major.minor` version of every entry. `TERMINAL / HALTED` exactly matches the Rule 2 terminal evidence projection and may use `NONE` only for an empty projection or `INVALID_VERSION` only under its version rule. No directory path, unreplaced metavariable, duplicate filename, blank value, unrelated evidence, or evidence omission is allowed.
5. **Scope values are canonical and resolvable**: Every scope field uses exactly one of `Project`, `Feature: F-XX`, or `Slice: F-XX/S-XX`. `Source Scope` matches the emitting workflow's authorized scope. `Target Scope` matches the canonical scope of `Next Workflow`: Project for Plan and Solution, Feature for Grill and Slice, and Slice for TDD and Review. Every Feature identifier resolves in active Planning, and every Slice identifier resolves in the Canonical Slice Plan for that Feature, except when Plan is repairing Planning itself. A BLOCKED Affected Scope or FAIL Review Return Scope that does not resolve is a Rule 2 contradiction, not a scope to ignore, sort last, or infer. `TERMINAL / HALTED` uses Affected Scope `Project` because an invalid graph cannot authorize a narrower identifier.
6. **Blocker Category is valid where required**: RETURN and `TERMINAL / HALTED` require a category from the Blocker Routing Rules; FORWARD and `TERMINAL / COMPLETE` forbid it.
7. **No scope widening or pre-consumption**: The receiving workflow's Target Scope must not be widened by conversation text or prior context beyond what is explicitly stated in the handoff block. Completion of that scope does not authorize the same execution to consume the next resolved Workflow or Target Scope.

If any check fails, the handoff is invalid. The receiving workflow performs no productive work until the source workflow corrects and re-emits a complete, valid handoff block. The receiving workflow must not infer missing fields or normalize a malformed block.

## Template Variants and Exit Rules

### FORWARD — Advance to next workflow

A FORWARD handoff advances execution from one workflow to the next. It is emitted when a workflow determines that the next step requires a different workflow's capability.

**When to emit FORWARD:**
- The Transition Resolution Procedure selects a different workflow or a different Target Scope owned by the same workflow.
- Rules 4–Rule 7, Rule 9, or Rule 10 match.

Emission ends the current execution. The emitter MUST NOT begin the target
Workflow or Target Scope after rendering, deciding, or preparing this handoff.

**Required fields:** `Transition`, `Next Workflow`, `Source Scope`, `Target Scope`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Blocker Category`, `Completed Scope`

### RETURN — Route back to upstream owner

A RETURN handoff routes execution back to a different Workflow/Scope authorization whose artifact caused a failure. It is emitted when a downstream workflow discovers that an upstream artifact requires rework. It MUST NOT return to the emitting workflow at the same Source Scope; same-authorization continuation or waiting emits no handoff.

**When to emit RETURN:**
- A persisted blocker selects an owner or scope different from the current authorization under Rule 3.
- A current FAIL Review Report selects its recorded owner under Rule 8.

**Required fields:** `Transition`, `Next Workflow`, `Source Scope`, `Target Scope`, `Blocker Category`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Completed Scope`

### TERMINAL / COMPLETE — Record project completion

This variant records successful completion under Rule 11.

**Required fields:** `Transition`, `Terminal Status`, `Source Scope`, `Completed Scope`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Next Workflow`, `Target Scope`, `Affected Scope`, `Blocker Category`

### TERMINAL / HALTED — Record an invalid graph

This variant records a graph contradiction under Rule 2. It does not claim completion
and is valid only when its evidence and Reason code exactly match the Rule 2
projection.

**Required fields:** `Transition`, `Terminal Status`, `Source Scope`, `Affected Scope`, `Blocker Category`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Next Workflow`, `Target Scope`, `Completed Scope`

## Canonical Handoff Block Rendering Rules

A handoff-producing workflow must render exactly one Canonical Handoff Block using the template for its selected variant. The rendered block:

1. Begins with the exact heading `### Handoff`;
2. Uses the exact field names, capitalization, row order, and delimiter row shown;
3. Replaces every metavariable with a non-empty value — no unreplaced `{{metavariable}}` allowed;
4. Omits every field not present in that variant's template — no extra rows added;
5. Is not enclosed in a code fence;
6. Is the final non-whitespace content of the workflow response — no prose, list, note, or second handoff after it;
7. Renders `Input Artifacts` as one or more `<canonical filename> = <version>` entries separated by the exact delimiter `; `, with no duplicate filename. HALTED instead renders `NONE` only for an empty terminal evidence projection. `INVALID_VERSION` is permitted only by HALTED and only when its projected artifact has no single readable valid Version.

A concise human-readable result summary may precede the block. A workflow must not emit more than one `### Handoff` heading in a response. Empty, `None`, and placeholder handoffs are forbidden.

### FORWARD Template

| Field | Requirement |
|---|---|
| Transition | `FORWARD` |
| Next Workflow | Required; one canonical workflow name |
| Source Scope | Required |
| Target Scope | Required; must match the resolved operation |
| Input Artifacts | Required canonical artifact filenames and versions |
| Reason | Required |

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | FORWARD |
| Next Workflow | {{Next Workflow}} |
| Source Scope | {{Source Scope}} |
| Target Scope | {{Target Scope}} |
| Input Artifacts | {{Input Artifacts}} |
| Reason | {{Reason}} |
```

### RETURN Template

| Field | Requirement |
|---|---|
| Transition | `RETURN` |
| Next Workflow | Required; the authorized owner |
| Source Scope | Required |
| Target Scope | Required; the authorized owner's canonical operating scope |
| Blocker Category | Required; one valid category from routing table |
| Input Artifacts | Required canonical artifact filenames and versions |
| Reason | Required and evidence-based |

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | RETURN |
| Next Workflow | {{Next Workflow}} |
| Source Scope | {{Source Scope}} |
| Target Scope | {{Target Scope}} |
| Blocker Category | {{Blocker Category}} |
| Input Artifacts | {{Input Artifacts}} |
| Reason | {{Reason}} |
```

### TERMINAL / COMPLETE Template

| Field | Requirement |
|---|---|
| Transition | `TERMINAL` |
| Terminal Status | `COMPLETE` |
| Source Scope | Required |
| Completed Scope | `Project` |
| Input Artifacts | Required canonical artifact filenames and versions |
| Reason | Required |

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Terminal Status | COMPLETE |
| Source Scope | {{Source Scope}} |
| Completed Scope | Project |
| Input Artifacts | {{Input Artifacts}} |
| Reason | {{Reason}} |
```

### TERMINAL / HALTED Template

| Field | Requirement |
|---|---|
| Transition | `TERMINAL` |
| Terminal Status | `HALTED` |
| Source Scope | Required canonical scope |
| Affected Scope | `Project` |
| Blocker Category | `GRAPH_CONTRADICTION` |
| Input Artifacts | Exact sorted Rule 2 evidence projection, or `NONE` when empty |
| Reason | `<Graph Error Code>: <non-empty human-readable explanation>` |

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Terminal Status | HALTED |
| Source Scope | {{Source Scope}} |
| Affected Scope | Project |
| Blocker Category | GRAPH_CONTRADICTION |
| Input Artifacts | {{Input Artifacts}} |
| Reason | {{Reason}} |
```

## Blocker Routing Rules

When a persisted blocker exists (Rule 3) or a current Review Report FAIL needs routing (Rule 8), the following table determines ownership. This table is semantically exhaustive — every possible blocker maps to exactly one category and owner. There is no "unknown" rejection path: if a new type of failure arises, it means the framework's routing rules need expansion rather than that downstream work should be rejected.

| `Blocker Category` | Owner Workflow | Return Scope | Meaning |
|---|---|---|---|
| `PLAN_GAP` | Plan | `Project` | Planning missing features, overlapping scope, or incompatible versions |
| `BUSINESS_GAP` | Grill | `Feature: F-XX` | Requirement missing, outdated (Planning upgraded), or internally contradictory |
| `ENGINEERING_GAP` | Solution | `Project` | Solution Plan missing, outdated (Requirement upgraded), incomplete, or conflicting across Requirements |
| `SLICE_VIOLATION` | Slice | `Feature: F-XX` | Slice Plan boundary wrong, dependency invalid, content missing, or misaligned with Solution Plan |
| `IMPLEMENTATION_GAP` | TDD | `Slice: F-XX/S-XX` | Implementation, test, or local execution evidence is blocked or invalid |
| `REVIEW_BLOCKER` | Determined by Review Report Findings Table | Determined by Review Report findings | A review finding triggers routing. Read the Review Report Findings Table to determine owner and scope |
| `GRAPH_CONTRADICTION` | None; terminal halt | `Project` | The active artifact graph is structurally invalid and cannot authorize a workflow |

The five non-terminal owner categories above route persisted BLOCKED artifacts.
`REVIEW_BLOCKER` is used by the RETURN handoff produced from a valid FAIL Review
Report; Rule 8 reads the canonical Findings table's Owner Workflow and Affected
Scope rather than inferring a route from prose or a finding-type label.

## Validation Checklist for Receiving Workflows

Before accepting a handoff, the target workflow must confirm:

1. Exactly one rendered template applies (`FORWARD`, `RETURN`, `TERMINAL / COMPLETE`, or `TERMINAL / HALTED`);
2. Every required field is present and every forbidden field is absent;
3. Workflow names, identifiers, and scope rendering are canonical;
4. Every Input Artifacts entry follows the variant-specific version rule and contains no unreplaced metavariables or blank values;
5. Target Scope matches the target workflow's canonical scope; TDD and Review identify exactly one Feature and Slice;
6. The Target Scope equals a fresh run of the Transition Resolution Procedure (not inferred from conversation context);
7. The block exactly matches its variant template and value-rendering rules;
8. Exactly one handoff block is present and it is the response's final content.
9. The execution performed productive work only for the Workflow and Target Scope
   authorized by this handoff's receiving entry; it did not pre-consume the next
   resolved scope.

Failure of any check makes the handoff invalid. The target workflow performs no work until the source workflow corrects and re-emits the complete Canonical Handoff Block. The target must not infer missing fields or normalize a malformed block.
