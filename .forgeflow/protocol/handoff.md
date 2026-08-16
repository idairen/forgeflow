# Handoff and Transition Protocol

Version: 2.3

## Purpose

A handoff records the result of a workflow's execution — the decision, artifacts produced, and what happens next in the ForgeFlow pipeline. It captures both the forward progress and any blockers that require re-work by an upstream owner. A handoff does not transfer artifact ownership and does not replace artifact evidence. The receiving workflow must still read current artifacts from the Artifact Root to validate the decision before acting on it.

## Active Artifact Graph

Build the active artifact graph exclusively from the Artifact Root defined by the Artifact Protocol. Only files at valid Canonical Artifact Paths participate in resolution. Review Report attempt files coexist as immutable history; archived or replaced contract versions do not participate in the active graph.

An artifact is current only when all of these hold:

1. Its status is READY, or READY_FOR_REVIEW for a TDD Record.
2. Every required upstream version equals the active upstream artifact version.
3. Its Feature and Slice identifiers exist in the active Planning and Slice Plan.
4. No duplicate active artifact or duplicate Review attempt exists.

If any of these conditions fails, the artifact cannot satisfy a barrier, authorize work, or prove completion. This directly governs C-13: if a READY_FOR_REVIEW TDD references stale upstream versions, it must be ignored and TDD re-run at that scope. It also governs C-14: a PASS Review Report without a corresponding current TDD record is ignored — the Slice is incomplete.

### Determinism Rule

Ordering comes exclusively from Planning order and Slice Plan order. If the graph is contradictory — duplicate active contracts, duplicate Review attempts, invalid Feature or Slice identifiers, missing required metadata — resolution stops at INVALID GRAPH and does not guess a next workflow (C-15: two Review Reports for the same Feature, Slice, and attempt make the graph invalid; C-38: a FAIL Review Report without valid blocking counts, Return Workflow, or Return Scope is invalid; C-42: Review Report metadata finding counts that differ from its finding body are invalid).

## Transition Resolution Procedure

Evaluate these rules in order. Stop at the first match and produce the corresponding handoff type. Each rule's matching condition and resulting action are described naturally — no enumeration of every possible scenario is required or expected. The receiving workflow applies these rules fresh each time it receives a handoff, without relying on remembered conversation state.

### Rule 1 — No Planning Yet

No Planning artifact exists, or the existing Planning artifact is not yet READY. **Action**: FORWARD to Plan at Project scope. When Planning is READY but only the first Feature's Requirement is current, forward to Grill at that Feature's Target Scope — evaluate per Feature rather than assuming all Features are complete just because Planning itself is ready.

### Rule 2 — Blocker Exists (Upstream Defect)

An upstream workflow has identified a blocker in a predecessor artifact. A Blocker Category encodes which workflow owns the fix, and a Return Workflow identifies the specific owner to receive it. See the **Blocker Routing Rules** section for how categories map to owners. **Action**: RETURN with the appropriate Blocker Category and Target Scope per the routing table.

### Rule 3 — Missing or Stale Requirement

The first Feature in Planning order lacks a current READY Requirement, or a stale Requirement from an older Planning version causes downstream invalidation and Plan re-hands off the affected Feature. **Action**: FORWARD to Grill at that Feature's Target Scope.

### Rule 4 — Missing, Stale, or Incomplete Solution Plan

The Solution Plan is absent, not yet READY, incomplete, or stale (its referenced Requirement versions have been superseded by newer Planning versions). **Action**: FORWARD to Solution at Project scope. If the Solution Plan has advanced but some Slice Plans still reference an older version, those stale Slices must be addressed by Slice before TDD proceeds for any Feature with outdated upstream contracts.

### Rule 5 — Missing or Stale Slice Plan

The first Slice in Slice Plan order lacks a current READY Slice Plan, or a stale Slice Plan references a Solution Plan version that is no longer active. **Action**: FORWARD to Slice at the affected Feature's Target Scope. TDD is forbidden for any Feature whose upstream contracts are stale.

### Rule 6 — Review Failure with Blocker

A FAIL Review Report exists for an active attempt on a TDD record or Slice, with valid blocking counts and a declared Return Workflow in its findings table. **Action**: RETURN per the Review Report Findings Table — the Target Scope is determined by the specific finding type (Solution_CONFORMANCE_DEFECT → Solution at Project scope; Requirement_GAP → Grill at Feature scope; etc.). The Rule's matching condition requires reading the Review Report's own findings table to determine the exact owner and scope.

### Rule 7 — Graph Contradiction

The artifact graph is contradictory (duplicate active contracts, invalid identifiers, missing required metadata). **Action**: TERMINAL with Blocker Category GRAPH_CONTRADICTION and a Reason describing the specific inconsistency. This halts all forward progress until the contradiction is resolved by Plan or an upstream rework.

### Rule 8 — All Slices Complete

All planned Slices have passed Review successfully, all TDD records are current and PASS, and no blockers exist. **Action**: TERMINAL at Project scope with Completed Scope covering all Slices and Features.

## Unified Entry Validation Procedure

Every workflow MUST execute this unified entry validation before accepting or acting on a handoff. This procedure is defined once here and referenced by all workflows — no workflow defines its own ad-hoc entry check.

When a workflow receives a handoff block, it must verify:

1. **Exactly one variant applies**: The `Transition` field is exactly one of `FORWARD`, `RETURN`, or `TERMINAL`. No other values are valid.
2. **All required fields present, all forbidden fields absent**: Each template variant defines its fixed set of required and forbidden fields (see Template Variants section). A handoff with a missing required field or an extra forbidden field is invalid — the receiving workflow performs no work and must reject it back to the source.
3. **Workflow names are canonical**: The `Next Workflow` field matches one of the known workflow identifiers (Plan, Grill, Solution, Slice, TDD, Review). Unknown workflow names are invalid.
4. **Input Artifacts resolve**: Every entry in `Input Artifacts` is a valid Canonical Artifact Filename (not a directory path), resolves under the Artifact Root, uses `; ` as separator between multiple entries, and states the current artifact version — no unreplaced metavariables or blank values.
5. **Scope identifiers are valid**: The `Target Scope` field identifies an existing, active Feature or Slice identifier that matches what the Transition Resolution Procedure would resolve at this point.
6. **Blocker Category is valid (FORWARD/RETURN only)**: When `Transition` is FORWARD with a Blocker Category, the category must be one of the known values in the Blocker Routing Rules table. Unknown categories cause rejection — but this situation should not occur in well-formed systems; if it arises, the system framework must expand its routing rules rather than reject downstream work.
7. **No scope widening from context**: The receiving workflow's Target Scope must not be widened by conversation text or prior context beyond what is explicitly stated in the handoff block.

If any check fails, the handoff is invalid. The receiving workflow performs no productive work until the source workflow corrects and re-emits a complete, valid handoff block. The receiving workflow must not infer missing fields or normalize a malformed block.

## Template Variants and Exit Rules

### FORWARD — Advance to next workflow

A FORWARD handoff advances execution from one workflow to the next. It is emitted when a workflow determines that the next step requires a different workflow's capability.

**When to emit FORWARD:**
- The current workflow has completed its scope but determined the next operation belongs to another workflow.
- A blocker in the current artifact graph requires an upstream workflow to fix before proceeding.
- After applying the Transition Resolution Procedure, Rule 1, Rule 3–Rule 5 match and direct forward progress is needed.

**Required fields:** `Transition`, `Next Workflow`, `Source Scope`, `Target Scope`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Blocker Category`, `Completed Scope`

### RETURN — Route back to upstream owner

A RETURN handoff routes execution back to the workflow whose artifact caused a failure. It is emitted when a downstream workflow discovers that an upstream artifact requires rework.

**When to emit RETURN:**
- A Review Report found a blocker and declared a specific Return Workflow (Rule 6).
- An upstream workflow identified a defect in another upstream's artifact (Rule 2).
- The Blocker Routing Rules table maps the failure type to a specific owner that is not the current workflow.

**Required fields:** `Transition`, `Next Workflow`, `Source Scope`, `Target Scope`, `Blocker Category`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Completed Scope`

### TERMINAL — Record completion or halt

A TERMINAL handoff records that all planned Slices have completed successfully (success terminal) or that the pipeline has been halted due to an unresolvable contradiction (halt terminal).

**When to emit TERMINAL:**
- All planned Slices have passed Review and all artifacts are current (Rule 8 — success terminal).
- The artifact graph is contradictory and no forward progress is possible (Rule 7 — halt terminal).

**Required fields:** `Transition`, `Source Scope`, `Completed Scope`, `Input Artifacts`, `Reason`

**Forbidden fields:** `Next Workflow`, `Target Scope`, `Blocker Category`

## Canonical Handoff Block Rendering Rules

A handoff-producing workflow must render exactly one Canonical Handoff Block using the template for its selected variant. The rendered block:

1. Begins with the exact heading `### Handoff`;
2. Uses the exact field names, capitalization, row order, and delimiter row shown;
3. Replaces every metavariable with a non-empty value — no unreplaced `{{metavariable}}` allowed;
4. Omits every field not present in that variant's template — no extra rows added;
5. Is not enclosed in a code fence;
6. Is the final non-whitespace content of the workflow response — no prose, list, note, or second handoff after it.

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

### TERMINAL Template

| Field | Requirement |
|---|---|
| Transition | `TERMINAL` |
| Source Scope | Required |
| Completed Scope | Required |
| Input Artifacts | Required canonical artifact filenames and versions |
| Reason | Required |

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Source Scope | {{Source Scope}} |
| Completed Scope | {{Completed Scope}} |
| Input Artifacts | {{Input Artifacts}} |
| Reason | {{Reason}} |
```

## Blocker Routing Rules

When a blocker exists (Rule 2) or a Review Report FAIL needs routing (Rule 6), the following table determines ownership. This table is semantically exhaustive — every possible blocker maps to exactly one category and owner. There is no "unknown" rejection path: if a new type of failure arises, it means the framework's routing rules need expansion rather than that downstream work should be rejected.

| `Blocker Category` | Owner Workflow | Return Scope | Meaning |
|---|---|---|---|
| `PLAN_GAP` | Plan | Project | Planning missing features, overlapping scope, or incompatible versions |
| `BUSINESS_GAP` | Grill | Feature ID (F-XX) | Requirement missing, outdated (Planning upgraded), or internally contradictory |
| `ENGINEERING_GAP` | Solution | Project | Solution Plan missing, outdated (Requirement upgraded), incomplete, or conflicting across Requirements |
| `SLICE_VIOLATION` | Slice | Feature ID (F-XX) | Slice Plan boundary wrong, dependency invalid, content missing, or misaligned with Solution Plan |
| `REVIEW_BLOCKER` | Determined by Review Report Findings Table | Determined by Review Report findings | A review finding triggers routing. Read the Review Report Findings Table to determine owner and scope |

This routing table applies when a blocker has no FAIL Review Report encoding it. When an existing FAIL Review Report with Blocker Category `REVIEW_BLOCKER` exists, follow Rule 6 to read the Findings Table instead. The findings table maps each finding type (e.g., `Requirement_GAP`, `Solution_CONFORMANCE_DEFECT`) to its specific owner and scope.

## Validation Checklist for Receiving Workflows

Before accepting a handoff, the target workflow must confirm:

1. Exactly one typed variant applies (`FORWARD`, `RETURN`, or `TERMINAL`);
2. Every required field is present and every forbidden field is absent;
3. Workflow names and identifiers are canonical (match known workflow list);
4. Every Input Artifacts entry uses only a Canonical Artifact Filename, resolves under the Artifact Root, and states the current artifact version (no unreplaced metavariables or blank values);
5. TDD and Review Target Scope identify exactly one Feature and Slice;
6. The Target Scope equals a fresh run of the Transition Resolution Procedure (not inferred from conversation context);
7. The block exactly matches its variant template and value-rendering rules;
8. Exactly one handoff block is present and it is the response's final content.

Failure of any check makes the handoff invalid. The target workflow performs no work until the source workflow corrects and re-emits the complete Canonical Handoff Block. The target must not infer missing fields or normalize a malformed block.
