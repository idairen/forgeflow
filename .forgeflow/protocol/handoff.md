# Handoff Protocol

Version: 2.15

## Purpose

A Handoff is the canonical message between two distinct ForgeFlow Workflow
executions. It records a resolved transition, its evidence, and the exact next or
terminal scope. It transfers no artifact ownership and never replaces the Artifact
Graph. The Transition Protocol determines the result and its exact ordered Input
Artifact projection; this protocol only defines how they are represented and
validated.

Transition's read-only routing correction may also emit a Handoff without executing
a Workflow. It follows the same variants, projection, rendering, and stop rules.

## Canonical variants

Exactly one variant applies:

| Variant | Required fields | Forbidden fields |
| --- | --- | --- |
| FORWARD | Transition, Next Workflow, Source Scope, Target Scope, Input Artifacts, Reason | Blocker Category, Completed Scope, Affected Scope, Terminal Status |
| RETURN | Transition, Next Workflow, Source Scope, Target Scope, Blocker Category, Input Artifacts, Reason | Completed Scope, Affected Scope, Terminal Status |
| TERMINAL / COMPLETE | Transition, Terminal Status, Source Scope, Completed Scope, Input Artifacts, Reason | Next Workflow, Target Scope, Affected Scope, Blocker Category |
| TERMINAL / HALTED | Transition, Terminal Status, Source Scope, Affected Scope, Blocker Category, Input Artifacts, Reason | Next Workflow, Target Scope, Completed Scope |

FORWARD carries a Rule 4–7, Rule 9, or Rule 10 result from the Transition Protocol.
RETURN carries a Rule 3 or Rule 8 result and MUST NOT target the emitting Workflow at
the same Scope. TERMINAL / COMPLETE carries Rule 11. TERMINAL / HALTED carries Rule 2.

## Canonical rendering

A Handoff-producing Workflow MUST render exactly one block that:

1. begins with the exact heading `### Handoff`;
2. uses the selected template's exact field names, capitalization, row order, and
   delimiter row;
3. replaces every metavariable with a non-empty value;
4. contains no fields outside the selected variant;
5. is not enclosed in a code fence;
6. is the final non-whitespace content of the response; and
7. contains no duplicate Input Artifact filename.

For read-only routing correction, Source Scope is exactly `Project`, identifying
the routing operation rather than impersonating a prior Workflow. The operation
has no emitting Workflow, so RETURN's same-Workflow prohibition does not turn a
Project-scoped target into a same-authorization wait. Ordinary emitters retain
their authorized Source Scope.

`Input Artifacts` MUST reproduce the selected Transition Rule's exact ordered
projection without choosing, omitting, adding, or reordering evidence. Render each
entry as `<canonical filename> = <major.minor version>` and separate multiple
entries with the exact delimiter `; `. Only Rule 2 HALTED may render `NONE` for an
empty projection or `INVALID_VERSION` under that Rule's version requirement.
Rule 2's explicit legacy-path diagnostic may name the exact retired TDD filename
selected by Transition; it is never a non-terminal input or implementation authority.

Rendering the block terminates the current Workflow execution. The emitter MUST NOT
consume its own Handoff, start the target Workflow, perform target-scope work, or
create target-owned evidence. An external orchestrator may start a distinct
execution after validating the completed Handoff and fresh Artifact Graph, or start
one eligible Grill Feature through Transition Lane Entry and its atomic claim.

Lane Entry, Rule 5 join-pending, and same-authorization waiting emit no Handoff and
MUST NOT synthesize an empty block. Feature Lane changes authorization, not the four
canonical Handoff variants or their rendering.

## FORWARD template

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

## RETURN template

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

## TERMINAL / COMPLETE template

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

## TERMINAL / HALTED template

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

HALTED `Reason` MUST use
`<Graph Error Code>: <non-empty human-readable explanation>`, with the exact code
selected by Transition Rule 2.

## Receiving validation

Every Handoff Entry MUST reject the block without productive work unless all of the
following are true:

1. Exactly one canonical variant applies and its Transition and Terminal Status,
   when present, use canonical values.
2. Every required field is present once and every forbidden or extra field is absent.
3. `Next Workflow`, when present, is Plan, Grill, Solution, Slice, Implement, or Review.
   TDD is a verification strategy, not a valid Next Workflow. Reject an old TDD
   Handoff rather than silently normalizing it to Implement; fresh resolution and
   the canonical Artifact Protocol govern the next execution.
4. Input Artifacts exactly equal the fresh Transition result's ordered projection.
   Every entry uses the canonical rendering, exists at a Canonical Artifact Path,
   has the stated active version, and contains no duplicate, omitted, additional,
   reordered, placeholder, directory, or blank value.
   The only retired-path exception is the Rule 2 HALTED diagnostic defined by
   Transition; its exact filename/version must match that fresh diagnostic.
5. Scope fields use `Project` or the canonical form `Feature: F-<FeatureNumber>` or
   `Slice: F-<FeatureNumber>/S-<SliceNumber>`. Angle-bracket terms are schema
   metavariables, never literal output; their numbers are rendered by the Artifact
   Protocol. Source Scope matches the emitter. Target Scope matches the canonical
   scope of Next Workflow and resolves in current Planning and the applicable Slice Plan.
   HALTED uses Affected Scope `Project`.
6. RETURN and HALTED contain the exact Blocker Category selected by the Transition
   Protocol; FORWARD and COMPLETE contain none.
7. Target Workflow and Scope equal a fresh Transition Protocol result and are not
   widened by conversation or launcher context.
8. Exactly one Handoff block exists and it is the response's final content.

An invalid Handoff grants no execution authority. The receiver MUST NOT infer its
missing fields, normalize malformed content, or replace version values to make it
appear valid. When no other valid Entry applies, use Transition's read-only routing
correction to generate a new result solely from the current graph, rather than
requiring the user to restart the prior emitter. Validate the new block against
that result and stop; even a matching requested target grants no same-invocation
execution. Missing Handoffs follow the same correction rule. Existing no-Handoff
entries and waiting results remain unchanged.
