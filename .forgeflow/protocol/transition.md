# Transition Protocol

Version: 1.8

## Purpose

This protocol alone authorizes ForgeFlow entry, derives active and runtime state,
routes blockers, selects the next Scope, and determines terminal status. The same
repository evidence and entry authorization MUST produce the same result.

## Active Artifact Graph

Build the graph only from valid Canonical Artifact Paths under the Artifact Root.
History, backups, logs, runtime steps, and supplemental reports never join the graph.
The Artifact Protocol permits bounded history reads for lineage, archival, and
counter validation only; those reads supply no readiness or completion evidence.
A contract Artifact is usable only with READY Status (READY_FOR_REVIEW for Implement),
matching active upstream versions, Feature/Slice identifiers resolved through current
Planning/Slice Plan, and no duplicate active Artifact or Review attempt.

Check an Artifact's own structure before currentness. Apply Artifact Protocol
Solution baseline validity and currentness to distinguish a valid-but-stale Solution
after authorized Planning changes from malformed or unexplained references. Such a
Solution remains a comparison/update baseline only. It cannot make downstream
evidence usable, route a current blocker, or establish completion.

A stale READY_FOR_REVIEW record is ignored and Implement reruns at that Scope. A PASS
without a matching current Implement Record is ignored. A lower FAIL remains immutable
history after Implement advances Attempt but cannot route the newer attempt.

When resolving a current Implement's Review state, check only its exact Attempt's
invalid Review history pair under Artifact Protocol. A valid pair makes that
Attempt ineligible for Review or completion, even if READY_FOR_REVIEW; Rule 10 may
select it for a new Implement Attempt after the ordinary earlier barriers. An
occupied Attempt never becomes reviewable again. Invalid pairs or a canonical
Review coexisting with its pair trigger Rule 2 `artifact_invalid`; project the
affected canonical Implement as evidence and identify the history paths in Reason.
Unrelated recovery history does not join graph discovery or Handoff projections.

Implement Record usability includes its verification selection, evidence, and
READY_FOR_REVIEW gate under the Artifact Protocol. Required checks cannot be
deferred merely to obtain Rule 9. Legacy implementation evidence is history only;
old active TDD paths or routing require the explicit migration described there.

All ordering comes from Feature position in Planning and Slice position in its Slice
Plan—not identifiers, filenames, filesystem order, timestamps, or conversation.

### Persisted blocker currentness

A structurally valid BLOCKED Artifact is actionable only with this complete usable
upstream chain:

| BLOCKED Artifact | Required chain |
| --- | --- |
| Planning | None |
| Requirement | READY Planning containing its Feature; matching Feature Contract Version; matching current Feature Lane Record when one exists |
| Solution Plan | READY Planning and all READY Requirements; exact Requirement map |
| Slice Plan | Current Planning and Requirements; READY Solution; matching Feature Engineering Version |
| Implement Record | Current Planning, Requirements, Solution, and Slice Plan; matching engineering and Slice Plan versions |

A direct version match cannot repair an earlier unusable barrier. A stale blocker
cannot authorize RETURN or Recovery. A current blocker persists until its owner
replaces the canonical Artifact with a higher valid version or attempt whose Status
is no longer BLOCKED.

A BLOCKED Requirement whose Lane was transactionally released remains actionable
when its Planning and Feature Contract Version are current. No canonical Lane is
required after release; historical Lane evidence neither reserves the Feature nor
supplies a new execution authorization.

## Feature Lane model

Feature Lane applies only to Grill. Its Record is current coordination evidence, not
a contract, exactly when Feature, Feature Contract Version, and every transitive
`Dependency Requirement Version` match Planning and usable Requirements. ACTIVE
reserves that Feature; COMPLETE also requires its matching usable Requirement. A
stale COMPLETE is ignored until archived for a later claim. A stale ACTIVE, malformed
dependency map, or matching COMPLETE without its Requirement is contradictory.

Planning's `Dependencies` column is the sole Lane dependency source. A Feature is
eligible when Planning is READY, it lacks a usable current Requirement, every
transitive dependency has one, no current BUSINESS_GAP closes it, and no current
ACTIVE Record reserves it. The eligible set preserves Planning order. A BUSINESS_GAP
closes its Feature and transitive dependents only, so independent eligible Features
may run concurrently in executions that each claim and mutate one Feature.

An accepted Grill Handoff or Lane Entry MUST atomically create the target ACTIVE Record
before work; a failed claim authorizes none. When no Feature is eligible but a current
ACTIVE Record remains, resolution is join-pending and the current Lane stops without
a Handoff, including during incomplete completion recovery. The last transactional
completion that makes every Requirement usable continues to Rule 6.

The ordinary claim and join rules do not reclaim an interrupted ACTIVE Record.
Only a valid Blocker Recovery or interrupted Lane Recovery below may replace it.
All Lane mutations follow
the Artifact Protocol's ownership checks and protected transactions. A released
claim supplies no reservation; a later valid Entry allocates the next Lane Attempt
from canonical and standard historical counter evidence.

Every Plan Entry checks for ACTIVE Lanes again before persistence and MUST wait
without writing Planning while any remains. A Project blocker stops each running
Lane at its next checkpoint; each execution releases its own claim before stopping.
Plan cannot release another execution's claim. An inactive claim requires the exact
interrupted Lane Recovery below. The check and Planning write must exclude a racing
claim; if the host cannot protect that boundary, report the limitation and stop.

## Transition Resolution Procedure

Evaluate in order and stop at the first match.

After an upstream Artifact is persisted, resolve from the saved versions and
recompute downstream currentness and the completion prefix. Do not reuse the
pre-revision completion decision or default to the Slice that requested the change.
Retain old Implement/Review evidence unchanged; only matching current evidence
can establish completion. The existing Rule 1–11 precedence still applies.

### Rule 1 — Bootstrap without Planning

When Planning is absent and Artifact Root is absent or empty, authorize Plan at
`Project` through Bootstrap Entry without a Handoff. Before productive Planning,
Plan also validates Reports Root. If it is non-empty, Plan only asks and waits for
explicit reset authorization; it neither rotates reports nor creates Planning.

### Rule 2 — Graph contradiction

HALT on any Artifact Protocol root, schema, reference, or routing contradiction,
including an invalid root, a non-empty root without Planning, duplicate contract or
Review attempt, invalid Artifact content, or downstream evidence beside `NONE`
Planning. Emit TERMINAL / HALTED with `GRAPH_CONTRADICTION` at Project.

An authorized Planning membership/order/version change explained by the Artifact
Protocol's baseline validation is staleness, not a Rule 2 contradiction. Validate
the relevant lineage before applying this exception. Never-declared identifiers,
unexplained differences, malformed maps, cycles, or absent required lineage evidence
receive no exception. NONE Planning still forbids every downstream active Artifact.

Reject new TDD Workflow/Owner declarations and retired active TDD filenames under
the Artifact Protocol's canonical and legacy rules. Report `artifact_invalid` using
the offending persisted path as terminal evidence; do not silently omit a retired
active path because it is no longer canonical. Only for this Rule 2 diagnostic,
the exact retired `tdd-feature-<FeatureNumber>-slice-<SliceNumber>.md` filename may
appear in the sorted terminal projection with its readable Version or INVALID_VERSION.
It never becomes an active node or a non-terminal Input Artifact. A new Implement
Record with missing or invalid strategies/rationales or an overall Review Decision
is invalid. Malformed
record structure is Rule 2; a valid IN_PROGRESS/BLOCKED record with pending or failed
verification follows ordinary progress/blocker rules, never automatic Review PASS.

Select one primary contradiction deterministically: validate filenames and Artifact
structure in canonical order, then graph references in procedure order. Project only
its sorted canonical evidence; relational errors include Planning, the offender, and
the applicable Slice Plan when membership matters, while a root-only error has none.

Project an active version when valid; an invalid Artifact uses its single readable
valid `major.minor` Version or `INVALID_VERSION`. Only Rule 2 may render an empty
projection as `NONE`. HALTED Reason begins `<code>: ` using:

| Code | Primary contradiction |
| --- | --- |
| `artifact_root_invalid` | Artifact Root is not a usable directory |
| `planning_missing` | Non-empty root or active graph has no valid Planning |
| `artifact_invalid` | Canonical Artifact, list, version, or structure is invalid |
| `empty_project_contradiction` | `NONE` Planning has downstream evidence |
| `identifier_reference_invalid` | Artifact references an undeclared Feature or Slice |
| `routing_scope_invalid` | Blocker or Review routing Scope does not resolve |

For an invalid Review format, the diagnostic may identify the optional
`protocol/review-recovery.md` procedure before the terminal Handoff. HALTED itself
grants no disposition authority; only a separate explicit recovery request loads
that procedure. Ordinary Entry and read-only correction never move the report.

### Rule 3 — Persisted blocker exists

After Rule 2 validates routing references, discard stale blockers and apply Feature
Lane isolation: defer a BUSINESS_GAP while an independent eligible or ACTIVE Lane can
progress, and ignore blockers outside the executing Lane's dependency closure. Exact
blocked-Feature Recovery does not defer its blocker. Select the remainder by owner
order
`Plan > Grill > Solution > Slice > Implement`, then Planning Feature position, then Slice
Plan position. Same-owner/same-Scope blockers authorize one result; canonical path
only stabilizes an evidence tie.

RETURN to the selected owner and Scope when it differs from current authorization.
The same Workflow/Scope waits without Handoff. A fresh blocker-recovery invocation
requires Rule 3 to select its exact Workflow/Scope; interrupted Lane Recovery is the
separate limited branch under Entry authorization. Never emit same-authorization
RETURN.

### Rule 4 — Planning not ready

If Planning exists but is unusable and Rule 3 did not select a blocker, FORWARD to
Plan at `Project`.

### Rule 5 — Requirement Feature Lane

When the eligible set is non-empty, ordinary resolution FORWARDs to Grill for its
first `Feature: F-<FeatureNumber>`; Lane Entry may select any one member of the same
frozen set. When it is empty with a current ACTIVE Record, return join-pending without
a Handoff. Eligibility, atomic claim, dependency exclusion, and concurrency follow
the Feature Lane model.

### Rule 6 — Solution required

If at least one Feature exists, every Requirement is usable, and no current ACTIVE
Lane remains, FORWARD to Solution at `Project` when Solution is absent, not READY,
incomplete, valid-but-stale after authorized Planning changes, or does not reference
every current Requirement version. Updating a stale Solution never bypasses the
all-Requirement join. Its existing canonical version remains in Rule 6's projection
as an update input, not as an engineering-ready baseline.

### Rule 7 — Slice Plan required

If at least one Feature exists, FORWARD to Slice for the first Planning-ordered
Feature without a usable Slice Plan matching its Feature Engineering Version and
the Artifact Protocol's actionable Verification Plan requirement. Implement
remains forbidden until every Feature has a usable Slice Plan. Target Scope is
`Feature: F-<FeatureNumber>`.

### Rule 8 — Current Review failure

When at least one Feature exists, RETURN the first current Implement attempt with a valid
matching FAIL as `REVIEW_BLOCKER` to that report's valid recorded Workflow and Scope.

### Rule 9 — Review required

When at least one Feature exists, FORWARD the first incomplete Slice in declared
Feature/Slice order to Review when its current Implement Record is READY_FOR_REVIEW and no
valid Review exists for that attempt and current upstream versions. Target Scope is
`Slice: F-<FeatureNumber>/S-<SliceNumber>`.

### Rule 10 — Implement required

When at least one Feature exists and all delivery barriers hold, FORWARD to Implement for
the first incomplete Slice not awaiting Review. This includes missing or stale Implement
evidence and a correction required after Rule 8 returned to Implement. Target Scope is
`Slice: F-<FeatureNumber>/S-<SliceNumber>`.

### Rule 11 — Project complete

Emit TERMINAL / COMPLETE for Project when every Slice has a current READY_FOR_REVIEW
record and matching current PASS, with no blocker. READY `NONE` Planning also
completes when its approval is valid and it is the sole active Artifact.

## Handoff Input Artifact projections

This protocol alone selects the exact ordered `Input Artifacts` projection. The
Handoff Protocol only renders and validates that selection. A projection contains
the active `major.minor` Version of every listed Canonical Artifact and no other
Artifact, except Rule 2's explicit retired-path diagnostic. Absence required by a
Rule is represented by omission, never by `NONE`;
`NONE` and `INVALID_VERSION` remain exclusive to Rule 2.

Use these ordered building blocks:

- **Project chain**: Planning, every usable Requirement in Planning order, then the
  current Solution when the matching Rule requires it.
- **Delivery baseline**: Project chain followed by every usable Slice Plan in
  Planning order.
- **Completion prefix**: for every Slice before a target Slice in declared
  Feature/Slice order, its current Implement Record followed by its matching current PASS.
  Rules 9 and 10 can select that target only when this prefix is complete.
- **Artifact currentness chain**: the selected Artifact and exactly the usable
  upstream Artifacts required by the Persisted blocker currentness table, rendered
  in dependency order with the selected Artifact last.
- **Lane completion evidence**: every matching current COMPLETE Feature Lane Record
  that exists, in Planning order. A legacy usable Requirement needs no synthetic
  Lane Record.

Except for Rule 2's explicit filename sort, declared order replaces filename or
identifier order within each group. Apply the groups from left to right and list an
Artifact only once.

| Rule | Exact ordered projection |
| --- | --- |
| Rule 1 | None; Bootstrap emits no Handoff |
| Rule 2 | The exact sorted terminal evidence projection defined by Rule 2 |
| Rule 3 | Selected BLOCKED Artifact's Artifact currentness chain; used only when RETURN is emitted |
| Rule 4 | Current Planning |
| Rule 5 | Planning; every usable transitive dependency Requirement in Planning order; target Feature Lane Record when a canonical one exists; target Requirement when a canonical one exists |
| Rule 6 | Planning; every current Requirement in Planning order; Lane completion evidence; current Solution when a canonical one exists |
| Rule 7 | Project chain; every usable Slice Plan before the target Feature; the target Slice Plan when a canonical one exists |
| Rule 8 | Delivery baseline; selected Slice's current Implement Record; its matching current FAIL Review Report |
| Rule 9 | Delivery baseline; Completion prefix; target Slice's current Implement Record |
| Rule 10 | Delivery baseline; Completion prefix; target Slice's current Implement Record when a canonical one exists |
| Rule 11 | Empty project: Planning only. Otherwise Delivery baseline followed, in declared Slice order, by every current Implement Record and its matching current PASS Review Report |

For Rule 8, if more than one current matching FAIL exists, the selected Slice is the
first one in declared Feature/Slice order. A Rule 3 same-authorization wait, a Rule 5
join-pending result, and every no-Handoff Entry have no rendered projection.
Canonical Artifacts not named by the selected row—including lower Review attempts
and Lane Records outside Lane completion evidence—are forbidden in the Handoff even
when they remain valid evidence. A receiver rebuilds the full graph before comparing
this projection; the Handoff never substitutes for fresh resolution.

## Runtime Slice state

Runtime Slice state is derived and MUST NOT be persisted in Slice Plans: PENDING means no
current Implement evidence; IN_PROGRESS means current Implement without valid PASS; BLOCKED means
a current BLOCKED Artifact or FAIL targets the Slice; COMPLETE means its latest valid
Review is PASS.

## Entry authorization

There are exactly five modes:

| Entry | Conditions and authority |
| --- | --- |
| Bootstrap | No Handoff; Rule 1 authorizes only Plan/Project |
| Subsequent Plan | No Handoff; non-empty changed User Intent after READY Planning; valid graph with no actionable blocker or current FAIL; authorizes only Plan/Project |
| Handoff | One canonical Handoff passes the Handoff Protocol and fresh resolution |
| Lane | No Handoff; Grill claims exactly one Feature from the current eligible set |
| Recovery | No Handoff; exact blocker recovery selected by Rule 3, or the narrowly authorized interrupted Grill Lane recovery below |

Only Plan uses Bootstrap or Subsequent Plan; only Grill uses Lane. Plan, Grill,
Solution, Slice, and Implement may recover only their own blocker; Grill may additionally
recover one interrupted Lane under the conditions below. Review cannot recover.
Without one valid mode, no productive work is authorized.

### Read-only routing correction

For an invocation requiring Handoff, if the Handoff is missing or fails receiving
validation and no other valid Entry applies, perform read-only routing correction.
This is not a sixth Entry, a new Workflow, or authority to repair Artifacts.
Reject the old Handoff as execution authority; resolve the complete active graph
under Rule 1–11 before application inspection, tests, plugins, or any mutation.
The requested Workflow/Scope and old Handoff cannot override the result.

Reuse this invocation's fresh graph validation and resolution when the graph has
not changed; correction adds no unconditional second full-graph scan. Do not reuse
pre-revision currentness or an unverified result from a previous invocation. If
graph changes are observed before rendering, revalidate and resolve the new graph.

For a Handoff-producing result, emit exactly its existing variant and ordered
projection with Source Scope `Project`, then stop. This also applies when the
selected target equals the requested Workflow/Scope: execution requires a later
invocation with valid Entry. Rule 2 emits HALTED rather than a guessed forward
target. Correction has no authorized Workflow; for Rule 3 it applies global
blocker selection without an executing Lane and does not invent a same-owner wait.

Preserve valid Bootstrap, Subsequent Plan, Lane, Recovery, and same-authorization
waiting behavior; they are not replaced by correction. A Rule 1 no-Handoff result
or Rule 5 join-pending result only reports the existing entry or wait condition
and stops, without a synthetic Handoff or a Lane claim. Correction never consumes
its own output, allocates an Attempt, or performs target-scope work.

### Subsequent Plan and Lane validation

Subsequent Plan confirms no inferred Handoff, one current READY Planning, non-empty
intent, and Plan-only authority through persistence and fresh resolution. It may add,
modify, reorder, or explicitly retire Features while preserving IDs and evidence.
Semantic similarity neither creates another project nor triggers identity confirmation
or Rotation, which requires an explicit reset/archive request; the user need not label
intent incremental or reconfirm identity. Any current ACTIVE Lane forbids this Entry.

Lane Entry follows the Feature Lane model and additionally confirms no inferred
Handoff and one requested member of the frozen eligible set. It authorizes no other
Feature; an older COMPLETE is archived before the new atomic claim.

### Blocker Recovery

Blocker Recovery confirms Rule 3 is first, blocker metadata and the entire upstream
chain are current, and context does not widen Scope. CLI entry context is a projection
to validate, not authority. Recovering a claimed Grill Lane also requires explicit
user confirmation that its prior execution is inactive, archives the prior Lane
Record, and advances Lane Attempt before work under the Artifact Protocol transaction.
If the claim was already released, a fresh atomic claim uses the next Lane Attempt.

### Interrupted Lane Recovery

This Recovery branch does not require or invent a BLOCKED Requirement. It authorizes
only Grill at one explicitly requested `Feature: F-<FeatureNumber>` when:

1. Rule 2 validation passes and the canonical Lane is structurally valid ACTIVE,
   with current Feature Contract Version and dependency Requirement versions.
2. The user explicitly confirms that the prior execution for this exact claim has
   stopped. Timeout, silence, missing output, or a model's inference is insufficient.
3. Planning is READY and, ignoring only this claim's own reservation, the target
   satisfies Lane eligibility. It has no usable current Requirement; an apparently
   half-completed Requirement/COMPLETE transaction is not ordinary interruption.
4. No current Project blocker or blocker in this Feature's dependency closure must
   be handled first. A current Feature blocker uses Blocker Recovery instead.
5. The host can perform the Artifact Protocol's protected archival and conditional
   replacement; a changed claim or failed transaction authorizes no work.

Freeze the old claim, archive it unchanged, and atomically replace it with a new
ACTIVE claim at the next Lane Attempt. Persist the recovery evidence and recheck
Planning, dependencies, blockers, and the new claim before business work. The prior
execution is superseded and cannot persist or archive the new claim. One recovery
never authorizes another Feature or a second Attempt in the same execution.

When a current Project blocker exists, an otherwise valid, explicitly confirmed
inactive claim may be recovered for release only. Apply checks 1, 2, and 5; require
READY Planning and no usable current target Requirement. Archive and remove only
that claim, create no replacement, and do no business work. Re-resolve the committed
graph and emit the selected blocker Handoff when required, then stop. This does not
authorize Plan to release the claim or a recovery participant to repair the blocker.
Stale ACTIVE, malformed, or half-completed evidence remains outside this exception.

## Invocation boundary

Every Entry obeys the Framework Invocation Boundary and freezes one Workflow/Target
Scope: one Project for Plan, at most one Feature for Grill/Slice, or one Slice attempt
for Implement/Review. Distinct concurrent Grill Lanes share no command session or mutable
Artifact. Declared future work grants no authority.

Implement entry may allocate this execution's Attempt under the Artifact Protocol after
validating authorization. Freeze and persist IN_PROGRESS before code changes; a
selection gap instead persists the same frozen Attempt as BLOCKED and returns to
its upstream owner without implementation. A later upstream change or another
required Attempt ends this authorization rather
than advancing it again. Review always consumes the frozen current Implement Attempt.

When resolution selects another Workflow or Scope, emit its Handoff and stop without
analyzing, questioning, inspecting, changing, commanding, implementing, reviewing, or
delegating in that future Scope. A join-pending Lane likewise stops after its
transaction, without Handoff, polling, or another Lane; only fresh resolution after
a graph change can authorize more Lanes or Solution.

## Blocker routing

| Category | Owner | Scope | Meaning |
| --- | --- | --- | --- |
| `PLAN_GAP` | Plan | `Project` | Planning scope, overlap, or compatibility |
| `BUSINESS_GAP` | Grill | `Feature: F-<FeatureNumber>` | Missing, stale, or contradictory business contract |
| `ENGINEERING_GAP` | Solution | `Project` | Missing, stale, incomplete, or conflicting engineering contract |
| `SLICE_VIOLATION` | Slice | `Feature: F-<FeatureNumber>` | Invalid decomposition, dependency, placement, or completion |
| `IMPLEMENTATION_GAP` | Implement | `Slice: F-<FeatureNumber>/S-<SliceNumber>` | Implementation, test, or local evidence |
| `REVIEW_BLOCKER` | Finding owner | Owner's canonical Scope | Current FAIL disposition |
| `GRAPH_CONTRADICTION` | None | `Project` | Invalid graph; terminal halt |

Every routed identifier exists in the active graph. Before RETURN or invocation end,
a non-Review Workflow persists its blocker and upstream owner without editing that
owner's Artifact; Review uses its immutable FAIL, and conversation is never blocker
state. Grill returning PLAN_GAP to Plan first commits its BLOCKED Requirement and
releases its own Lane in the Artifact Protocol transaction, then resolves again and
renders the Handoff from persisted facts. It cannot leave ACTIVE behind on this
RETURN or mark an unfinished Requirement COMPLETE. Feature Lane isolation follows
its model, while Project blockers and graph contradictions stop every Lane. The
table is exhaustive; new failure kinds require a
protocol revision.
