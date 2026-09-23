# Artifact Protocol

Version: 2.19

## Purpose

Canonical Markdown Artifacts and their version references are ForgeFlow's sole
persistent source of truth. This protocol owns their paths, schemas, versions,
history, and read-only projections. It requires no executable parser, external
schema, YAML front matter, or platform service.

## Roots and lifecycle

### Artifact Root

The canonical Artifact Root is `.forgeflow/artifacts/`, relative to the repository
root. Active Artifacts MUST be created, read, and updated only at the Canonical
Artifact Paths in this protocol. Files outside those paths never join the active
Artifact Graph. The first Artifact owner creates an absent root before writing.

### Artifact History

The immutable History Root is `.forgeflow/artifacts/history/`. History never joins
the active Artifact Graph or satisfies readiness or completion. Bounded reads are
permitted only to verify version lineage, archival consistency, and counter
continuity under this protocol. Read only the versions or Feature/Slice counter
paths involved in the check; backups, other projects, and supplemental reports
cannot supply that evidence.

Before replacing a current contract Artifact with a higher version, its owner copies
the exact prior file to:

| Artifact Type | Historical filename |
| --- | --- |
| Planning | `planning-v<Version>.md` |
| Feature Lane Record | `lane-feature-<FeatureNumber>-attempt-<AttemptNumber>.md` |
| Requirement | `requirement-feature-<FeatureNumber>-v<Version>.md` |
| Solution Plan | `solution-plan-v<Version>.md` |
| Slice Plan | `slice-plan-feature-<FeatureNumber>-v<Version>.md` |
| Implement Record | `implement-feature-<FeatureNumber>-slice-<SliceNumber>-attempt-<AttemptNumber>.md` |

Review Reports are immutable attempt files and are not copied by ordinary Workflows;
the narrowly authorized Invalid Review history disposition below preserves invalid
originals unchanged. An IN_PROGRESS Implement
Record may change within its Attempt; Implement archives the exact current record before
advancing Attempt or replacing READY_FOR_REVIEW or BLOCKED evidence. Grill archives
before advancing Lane Attempt or replacing its Record for a new Feature Contract
Version. Historical files are immutable. Identical content at a required history
path satisfies archival; different content blocks replacement.

### Invalid Review history

Only the explicitly authorized procedure in `protocol/review-recovery.md` may move
an invalid Review unchanged to `history/invalid-review/<original-review-filename>`.
Its immutable companion replaces `.md` with `.receipt.md` and contains a title,
then a two-column `Field | Value` table with exactly: Source Filename, SHA256,
Feature ID, Slice ID, Attempt, Implement Version, Authorization, Reason.
Source Filename is the canonical Review basename; SHA256 is the lowercase hex
digest of the original bytes. Identity and positive Attempt match that filename
and the structurally valid canonical Implement at disposition; Implement Version
records that Implement's version. Authorization names the explicit user-approved
disposition, and Reason describes the observed format defect; both are non-empty.
The original/receipt pair is immutable maintenance history, not an active Artifact
or a Review decision. Never infer PASS, FAIL, readiness or completion from it.

Read only the exact current Implement Attempt's pair when checking its Review
state, and matching Feature/Slice pairs when collecting UsedAttempts. Validate
both files, digest, identity and receipt schema. A pair permanently occupies its
Attempt and requires reimplementation if it is still the current Implement Attempt.
A missing half, malformed receipt, digest mismatch, or canonical Review at that
same occupied Attempt is a contradiction, not permission to reuse the number.
Do not scan unrelated recovery history. This is an additional bounded counter and
disposition check, not a general historical readiness source.

### Reports History

Supplemental Review reports live under `.forgeflow/reports/<plugin-name>/`. Before
replacing the same Feature, Slice, attempt, plugin, and format, move the exact report
to `.forgeflow/reports/history/<plugin-name>/` at the first unused
`-revision-<RevisionNumber>` filename, beginning with `01`; different content there
blocks replacement. Neither current nor historical supplemental reports are active
Artifact evidence; a subsequent Plan archives only evidence it replaces.

## Project Evidence Rotation

Rotation is explicit reset or archive maintenance, never a classification inferred
from User Intent. The participant applies this Markdown procedure:

1. Resolve `.forgeflow/artifacts/` and `.forgeflow/reports/` without reading or
   changing contents; neither may be a symbolic link or non-directory path. An absent
   root is empty.
2. If both roots are empty, create any absent root and finish without a backup.
3. Otherwise capture UTC once as `yyyyMMddHHmmss`; any entry, hidden or nested,
   makes a root non-empty. Map each non-empty root to its sibling
   `artifacts.<timestamp>` or `reports.<timestamp>`.
4. Before mutation, require every backup path to be absent and not a symbolic link;
   never overwrite, merge, or delete a current or backup root.
5. As one transaction, move each non-empty root in full and create new empty roots
   before Plan reads or writes evidence. On failure restore every move; if rollback
   also fails, report all retained paths for manual recovery.

Backup paths never participate in transition resolution.

## Project Knowledge View

The Project Knowledge View is a disposable read-only projection with no Artifact
Type, owner, path, or transition authority. From a valid current graph it exposes,
in declared Feature/Slice order, the canonical metadata and references in this chain:

```text
Planning[Change Set, Feature Contract Version]
  -> Feature Lane Record[dependency Requirement versions, Attempt, Status]
  -> Requirement[Planning Version]
  -> Solution[Requirement map, Feature Engineering Version]
  -> Slice Plan[Based On Solution]
  -> Implement Record[Solution Version, Slice Plan Version, Attempt]
  -> Review Report[matching versions, Attempt, Decision]
```

Missing optional nodes are omitted. If the current graph is invalid, current
knowledge is unavailable; a renderer MUST NOT combine a valid subset into an apparent
baseline. An explicit history option MAY index Artifact and Reports History, current
supplemental reports, rotated roots, and a Planning/Solution timeline without making
them current contracts. Invalid historical metadata is a warning, not a current graph
contradiction.

A query accepts one active `F-<FeatureNumber>` or
`F-<FeatureNumber>/S-<SliceNumber>`, rejects malformed or inactive identifiers, and
returns only that subtree in declared order; current knowledge is the default. JSON
and Markdown SHOULD render to standard output. Any persisted cache remains disposable
and every rendering links to canonical filenames and versions without inventing a
relationship.

A Project Impact View MAY derive dependencies, reverse dependencies, shared-component
relationships, and current impact classifications from structured Solution metadata.
It is advisory and cannot select a Workflow, Scope, Gate, or current Artifact.

## Common Artifact schema

### Required metadata

Every Artifact begins with its title followed immediately by one `## Metadata`
section and a two-column table:

```markdown
| Field | Value |
| --- | --- |
| Artifact Type | Planning |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Plan |
```

Labels are case-sensitive. Missing, duplicated, malformed, or contradictory required
metadata makes the file invalid. Version uses `major.minor`; Attempt is a positive
integer.

The canonical Workflow values are Plan, Grill, Solution, Slice, Implement, and
Review. Newly written Artifacts cannot use TDD as Owner Workflow, Blocker Owner,
Return Workflow, or a Findings owner. `Workflow: Implement` alone is not the
Metadata schema; validate Artifact Type, Owner Workflow, all required fields,
references, and content together. TDD is valid only as a verification strategy or
an explicitly historical reference under Legacy implementation evidence below.
An extra `Workflow` declaration cannot override Owner Workflow; declaring it as
TDD in a new active Artifact is likewise invalid.

### Canonical sequence numbers and identifiers

`<SequenceNumber>` is the unique filename and identifier rendering of a positive
integer. Values 1 through 9 use exactly one leading zero; values 10 and greater use
ordinary decimal notation without a leading zero. Its grammar is
`0[1-9] | [1-9][0-9]+`: `01`, `09`, `10`, `99`, and `100` are valid, while `00`,
`1`, `001`, and `010` are invalid. Sequence numbers have no maximum width.

`<FeatureNumber>`, `<SliceNumber>`, `<SharedComponentNumber>`, and
`<EngineeringDecisionNumber>` are Sequence Numbers. Their canonical identifiers
are respectively `F-<FeatureNumber>`, `S-<SliceNumber>`,
`SC-<SharedComponentNumber>`, and `ED-<EngineeringDecisionNumber>`.
`<AttemptNumber>` and `<RevisionNumber>` are the Sequence Number renderings of
their positive integer counter values. Attempt metadata remains an ordinary
positive integer; for example, Attempt `1` maps to filename portion `attempt-01`,
and Attempt `100` maps to `attempt-100`.

Every Feature, Slice, Shared Component, and Engineering Decision identifier, plus
every Artifact or supplemental-report counter filename portion defined here, MUST
use this canonical rendering. For these identifiers, the prefix and number are
indivisible: alternate padding, truncation, and normalization by a reader are
invalid. Numeric comparison may validate or advance a counter, but declared
Planning and Slice Plan order alone determines workflow ordering.

### Ownership and Canonical Artifact Paths

| Artifact Type | Owner | Scope | Filename under Artifact Root |
| --- | --- | --- | --- |
| Planning | Plan | Project | `planning.md` |
| Feature Lane Record | Grill | Feature | `lane-feature-<FeatureNumber>.md` |
| Requirement | Grill | Feature | `requirement-feature-<FeatureNumber>.md` |
| Solution Plan | Solution | Project | `solution-plan.md` |
| Slice Plan | Slice | Feature | `slice-plan-feature-<FeatureNumber>.md` |
| Implement Record | Implement | Slice | `implement-feature-<FeatureNumber>-slice-<SliceNumber>.md` |
| Review Report | Review | Slice attempt | `review-feature-<FeatureNumber>-slice-<SliceNumber>-attempt-<AttemptNumber>.md` |

Only Planning declares `F-<FeatureNumber>` identifiers; only that Feature's Slice
Plan declares `S-<SliceNumber>`. A filename's Feature and Slice numbers MUST exactly
equal their canonical Metadata, Planning, and Slice Plan identifier numbers. Its
Attempt number MUST equal the canonical Sequence Number rendering of Attempt metadata.
A Slice ID may repeat under different Features and is always resolved with its
Feature.
A Feature or Slice used in blocker or Review routing is a graph reference, not a
declaration, and must resolve in current Planning and the applicable Slice Plan.

### Type-specific metadata

| Artifact Type | Additional required fields |
| --- | --- |
| Planning | Feature IDs in order; Feature Contract Versions; Change Set; Artifact Protocol Version when created or revised under 2.11; Empty Feature Approval only for `NONE` |
| Feature Lane Record | Feature ID; Feature Contract Version; Attempt; Dependency Requirement Versions; Claim Evidence |
| Requirement | Feature ID; Planning Version |
| Solution Plan | Based On Requirements; Feature Engineering Versions; Artifact Protocol Version when created or revised under 2.11; structured impact metadata |
| Slice Plan | Feature ID; Based On Solution; Slice IDs in order |
| Implement Record | Feature ID; Slice ID; Attempt; Solution Version; Slice Plan Version; Verification Strategies |
| Review Report | Feature ID; Slice ID; Attempt; Decision; Solution Version; Slice Plan Version; Blocking Findings; Non-blocking Findings; Return Workflow and Return Scope only for FAIL |

Multiple values use canonical entries separated by `; `. Declared order is
significant; identifier numbers and filesystem order never replace it.

### Feature-scoped versions

Planning `Feature Contract Versions` contains exactly every active Feature. New or
business-affected Features use the current Planning Version; unchanged Features
retain theirs. Intent, boundary, dependency, exclusion, success-condition, or
applicable project-constraint changes are affecting. Requirement `Planning Version`
refers to that Feature-scoped value.

Planning `Change Set` is initially `BASELINE`; later it records every added, modified,
removed, or reordered Feature and project-constraint effect. IDs remain stable and
retired IDs are never reused. A constraint advances each affected Feature, not all
Features automatically.

At creation or normative revision, Solution `Feature Engineering Versions` contains
exactly every active Feature. This is also required for current usability. New or
engineering-affected Features use the current Solution Plan Version; unaffected ones
retain theirs. Feature- and Slice-scoped `Based On Solution` or `Solution Version`
fields use this value.

#### Solution baseline validity and currentness

Validate a Solution's own structure separately from its current usability. An
authorized Planning revision may change Feature membership, order, or contract
versions and leave the existing Solution valid-but-stale at its canonical path.
This classification is derived, not a new persisted Status. The old Solution is
available for comparison and update only; it satisfies no engineering, delivery,
blocker-currentness, or completion barrier.

For a membership or order difference, verify the old Solution's maps against an
approved prior Planning baseline and the Requirement versions it references. Use
the current Planning Change Set and the intervening standard Planning history to
account for every addition, retirement, reordering, and affected contract version,
including changes across multiple revisions. Read referenced Requirement versions
only at their canonical or standard history paths, including the exact retired
Feature directory when applicable. Every map must have been complete and consistent
for that prior baseline. Missing evidence or an unexplained difference receives no
staleness exemption. A never-declared Feature, malformed map, unresolved component
or decision reference, or cycle remains invalid; staleness cannot repair it.

A version mismatch in an otherwise valid reference makes the old baseline stale,
not usable. A new or revised Solution must again satisfy every current map,
reference, and impact requirement before READY. No historical Requirement becomes
an active input to engineering decisions by virtue of this lineage check.

### Structured Solution impact metadata

A Solution created or normatively revised under Artifact Protocol 2.9 includes the
entire set below. A pre-2.9 Solution may omit all of it, making Project Impact
unavailable; a partial set is invalid.

| Field | Canonical value |
| --- | --- |
| Shared Component IDs | `NONE` or ordered unique `SC-<SharedComponentNumber>` values |
| Feature Dependencies | one entry per Feature: `F-<FeatureNumber> = NONE` or dependency IDs |
| Feature Shared Components | one entry per Feature: `F-<FeatureNumber> = NONE` or component IDs |
| Feature Decision References | one entry per Feature: `F-<FeatureNumber> = NONE` or `ED-<EngineeringDecisionNumber>` IDs |
| Cross-Feature Impact | one entry per Feature: `F-<FeatureNumber> = DIRECT`, `INDIRECT`, or `UNAFFECTED` |

At creation or normative revision and for current usability, every map contains
exactly the active Features in Planning order. Existing Solutions follow Solution
baseline validity and currentness for authorized upstream differences. Dependencies
target other Features of the validated baseline and are acyclic. Component IDs
resolve through Shared Component IDs; Decision IDs resolve in the current Engineering
Decision Register. `NONE`
cannot accompany another value. Dependency means consuming another Feature's
engineering contract; shared-component membership means co-usage, not direction.
Cross-Feature Impact classifies the current Solution revision.

### Empty project

An explicitly approved empty Planning uses exact `Feature IDs = NONE`, exact
`Feature Contract Versions = NONE`, and
`Empty Feature Approval = APPROVED: <non-empty approval evidence>`. That field is
forbidden when a Feature exists, and `NONE` cannot accompany a Feature identifier.
A READY empty Planning is valid only as the sole active Artifact; any downstream
Artifact is a graph contradiction.

### Status and blockers

| Artifact Type | Allowed Status |
| --- | --- |
| Planning, Requirement, Solution Plan, Slice Plan | DRAFT, BLOCKED, READY |
| Feature Lane Record | ACTIVE, COMPLETE |
| Implement Record | IN_PROGRESS, BLOCKED, READY_FOR_REVIEW |
| Review Report | READY |

Review Decision is PASS or FAIL. Finding counts are non-negative integers.

A BLOCKED Planning, Requirement, Solution Plan, Slice Plan, or Implement Record adds:

| Field | Requirement |
| --- | --- |
| Blocker Category | non-terminal category from the Transition Protocol |
| Blocker Owner | canonical Workflow |
| Affected Scope | category's canonical Project, declared Feature, or declared Slice |
| Blocker Reason | non-empty unresolved condition |
| Blocker Evidence | observable artifact, code, command, or user-decision evidence |

Only `PLAN_GAP`, `BUSINESS_GAP`, `ENGINEERING_GAP`, `SLICE_VIOLATION`, and
`IMPLEMENTATION_GAP` are persisted BLOCKED categories. `REVIEW_BLOCKER` exists only
in FAIL Review routing and `GRAPH_CONTRADICTION` only in HALTED Handoffs. Owner,
scope, currentness, and selection follow the Transition Protocol. Conversation and
Handoff text never replace blocker metadata.

## Type contracts

### Planning

Planning contains approved intent, constraints, exclusions, success measures, and
the complete ordered Feature list. A Planning created or revised under Artifact
Protocol 2.11 records `Artifact Protocol Version = 2.11` and contains exactly:

1. `## Project Intent`
2. `## Project Goals`
3. `## Success Measures`
4. `## Project Constraints`
5. `## Assumptions`
6. `## Exclusions`
7. `## Features`
8. `## Change Set`
9. `## Intent Evolution`

Each section has a non-placeholder value. When no constraint, assumption, or
exclusion applies, record `NONE` with a reason.

`Features` uses:

```markdown
| Feature ID | Title | Outcome | Dependencies |
| --- | --- | --- | --- |
```

Dependencies are `NONE` or comma-separated active Feature IDs. Empty Planning keeps
one `NONE` row whose Outcome cites approval.

`Change Set` uses:

```markdown
| Feature ID | Change | Previous Contract Version | Current Contract Version | Rationale |
| --- | --- | --- | --- | --- |
```

Change is `BASELINE`, `RETAINED`, `ADDED`, `MODIFIED`, `REORDERED`, or
`RETIRED`; a nonexistent version is `NONE`. Baseline has one row per Feature.
Later versions include every active Feature and each Feature retired by that change.
Intent Evolution explains the complete effect without becoming another contract.

A pre-2.11 Planning without Artifact Protocol Version remains readable; its next
normative revision adds the full 2.11 structure. Partial migration is invalid.

Planning is approved evidence, not a scratchpad. Assumptions need User Intent or
observable current-project evidence and cannot answer an open business question,
create identity policy, choose shared-data semantics, or remove scope. Exclusions
need explicit intent or current approved Planning; silence is not evidence. Success
Measures and Outcomes cannot invent mandatory behavior. Every project-wide or
cross-Feature behavior traces to an Outcome or Project Constraint, every business
dependency appears in Features, and Intent Evolution cannot claim complete coverage
or non-overlap when those mappings are absent or contradictory.

### Requirement

A Requirement is Feature-level business behavior, rules, acceptance criteria, edge
cases, dependencies, and exclusions. READY means no unresolved business decision can
change observable behavior.

### Feature Lane Record

A Feature Lane Record is Grill-owned coordination evidence for one Feature Contract
Version; it grants no other authority and contains no business decision. Transition
alone determines Lane currentness, eligibility, Entry, Recovery, and join behavior.
After Handoff or Lane Entry authorization and before work, Grill claims the canonical
path with atomic create-if-absent. Recovery uses the conditional transaction below.
A failed claim authorizes no mutation or productive work.

Immediately after creation, at each work checkpoint, and before any Requirement
write or Lane transaction, Grill rereads Planning, dependency Requirements, current
Project blockers, and the claim. Compare Feature, Attempt, Version, Feature Contract
Version, dependency versions, and Claim Evidence with the frozen claim. If the claim
was replaced or removed, stop without writing or archiving any canonical file. If
it still belongs to this execution but a frozen version or eligibility fact changed,
archive and release only this claim and stop. Conversation or an earlier read cannot
bridge these checks. Each check and its conditional mutation must be protected
against concurrent replacement; a stale execution cannot archive its successor.
When rechecking eligibility after a successful claim, ignore only this execution's
own reservation; the expected creation of that reservation is not an eligibility loss.

`Dependency Requirement Versions` is exact `NONE` or one
`F-<FeatureNumber> = <major.minor>` entry for every transitive Planning dependency
in Planning order. Each resolves to a usable current Requirement. `Claim Evidence`
identifies the accepted Entry and exact Feature Scope without treating conversation
as authority. A new claim uses one greater than the maximum Attempt in this Feature's
canonical Lane and standard Lane history, or 1 when none exists; releasing a claim
or changing its Feature Contract Version never resets the counter. Conflicting or
unreadable relevant counter evidence blocks allocation. Within an Attempt, Claim
Evidence, dependency versions, and Feature Contract Version are immutable.

`ACTIVE` reserves that Feature/version; `COMPLETE` also requires its matching usable
Requirement. ACTIVE-to-COMPLETE is an unarchived coordination update at the same
Version. Every other replacement advances Version or Attempt and follows Artifact
History. Recovery additionally archives the inactive prior claim and atomically
advances Attempt; its superseded execution becomes stale and cannot persist.

#### Lane release and Recovery transactions

Before returning a PLAN_GAP to Plan, Grill verifies ownership of its current claim
and performs one transaction: archive any replaced Requirement as required, persist
the BLOCKED Requirement with the exact blocker owner, Scope, reason, and evidence,
and archive the exact Lane Record at its standard history path while removing it
from the canonical path. Failure restores the prior Requirement and claim. Release
does not set COMPLETE and introduces no new Lane Status. The BLOCKED Requirement
remains canonical evidence after claim release. Resolve the committed graph before
emitting the RETURN; an archived claim is not an Input Artifact.

On a current Project blocker, each running Grill execution stops business work at
its next checkpoint and releases only its own claim using the same ownership and
archival checks; it does not replace another Lane's Requirement or invent another
blocker. Plan waits for these releases. Only the narrowly authorized interrupted
Lane Recovery may release a confirmed inactive execution's claim.

For a Transition-authorized interrupted Lane Recovery, verify that the old claim
has not changed, archive its exact bytes, and atomically replace it with a new ACTIVE
Record using the next Lane Attempt and a higher Version. Record the exact Feature,
replaced Attempt, and explicit confirmation of inactivity in Claim Evidence. Reread
Planning, dependencies, blockers, and the new claim before work. Under a Project
blocker, Recovery is release-only: archive and remove the old claim, create no new
claim, do no business work, then resolve and stop.

Archival and conditional replacement or release are one protected transaction. Only
one competing claimant may succeed. History conflicts or failures restore the old
claim and authorize no work. Existing identical history satisfies archival without
being rewritten; rollback never overwrites another execution's files. If the host
cannot provide exclusion and conditional mutation, stop and report the missing
capability; sequential file writes alone are not an atomic transaction. If rollback
cannot restore the prior state, report retained paths for manual recovery and stop.

Persisting the target Requirement and changing its Lane Record from ACTIVE to
COMPLETE is one transaction; failure restores both prior files. An older COMPLETE is
scheduling history and is archived before a new claim. Transition classifies stale
or invalid Lane evidence and a matching COMPLETE without its usable Requirement.

### Solution Plan

A Solution Plan is the Project engineering baseline. It records boundaries,
interfaces, data and migration, quality constraints, risks, verification, and
Feature-scoped compatibility.

Schema compatibility is:

| Created or revised under | Required addition | Earlier Artifact compatibility |
| --- | --- | --- |
| 2.10+ | exactly one `## Implementation Structure` and `## Test Structure` | both may be absent; a revision adds both; a partial pair is invalid |
| 2.11+ | `Artifact Protocol Version = 2.11` and one non-empty `## Solution Summary` in `solution-plan.md` | both may be absent until revision |

`solution-plan-summary.md` is never a Canonical Artifact Path.

Implementation Structure uses:

```markdown
| Component or Role | Source Root | Module or Package Pattern | Responsibility | Allowed Dependencies | Applies To | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
```

Test Structure uses:

```markdown
| Test Level | Test Root | Module or Package Pattern | Production Relationship | Applies To | Evidence |
| --- | --- | --- | --- | --- | --- |
```

Paths and patterns are repository-relative. Solution owns their engineering
decisions; this protocol owns the rendered schema.

A new or normatively revised Solution includes `## Verification Requirements`:

```markdown
| Obligation | Applies To | Required Verification | Passing Criteria | Evidence Required |
| --- | --- | --- | --- | --- |
```

Each non-empty row traces an observable property or risk to active Features,
required checks/test levels or strategies, passing criteria, and the evidence needed.
Name any permitted alternatives and their conditions explicitly; lack of a required
technology is not permission to omit a required outcome. An older Solution may keep
equivalent unambiguous requirements in existing prose until its next revision.
Absent material verification decisions are an ENGINEERING_GAP, not permission for
Implement to invent weaker criteria. This addition does not change the existing
2.11 structure marker or require rewriting historical Solutions.

### Slice Plan

A Slice Plan is an immutable Feature-level ordered decomposition. It stores no
runtime state, cursor, blocker projection, or Review decision. Every Slice that
creates, moves, or materially changes files includes:

```markdown
| Slice ID | Responsibility | Production Path or Pattern | Test Path or Pattern | Governing Decision | Notes |
| --- | --- | --- | --- | --- | --- |
```

Each row resolves to current Implementation and Test Structures. A directory pattern
may leave a filename to repository convention but not a root, module, package,
responsibility, or test topology. A no-file Slice records `NONE` with a reason.

A new or normatively revised Slice Plan includes `## Verification Plan`:

```markdown
| Slice ID | Obligation | Strategies | Rationale | Required Checks | Passing Criteria | Evidence Required |
| --- | --- | --- | --- | --- | --- | --- |
```

Each Slice has at least one non-empty row; obligations resolve to its acceptance
conditions and Solution verification requirements. Strategies use one or more
supported identifiers separated by `; `. Every listed strategy is required unless
the plan explicitly declares a permitted alternative and its selection condition
under Solution authority. Multiple rows/strategies are cumulative, not competing
ways to skip checks. A legacy Slice Plan may retain equivalent explicit information
in prose; without a complete actionable plan it is readable but not usable for
DELIVERY_READY, and Rule 7 returns to Slice for revision. Malformed new content is
invalid; missing upstream engineering decisions route to Solution.

### Verification strategies and evidence

Strategies are execution/evidence patterns inside Implement, not Workflows, Artifact
types, independent Attempts, or Review decisions. The supported identifiers are:

| Strategy | Required execution pattern and evidence |
| --- | --- |
| TDD | Run a relevant test first and capture RED caused by the intended missing/incorrect behavior; implement minimum behavior for GREEN; refactor as needed and rerun relevant verification. A broken environment is not RED evidence. |
| BEHAVIORAL_TEST | Execute tests against approved observable behavior during or after implementation; record expected and actual results, relevant acceptance/regression coverage, target/environment, and execution evidence. Historical RED is not required and must not be claimed. This strategy cannot replace mandatory TDD or required human acceptance. |
| CHARACTERIZATION_TEST | Capture relevant existing behavior before modification, establish repeatable tests, then compare after changes; preserved behavior is not automatically desired behavior beyond the approved scope. |
| MIGRATION_REHEARSAL | Rehearse against the declared representative environment/data; check resulting schema/data integrity and the required failure/recovery paths. |
| STATIC_VALIDATION | Execute applicable parsing, typing, linting, build or static checks; record their limits and retain any required behavioral verification. |
| CONFIGURATION_VALIDATION | Validate configuration and required build/startup/effective-setting behavior in the declared environment; syntactic validity alone does not prove runtime effect. |
| SECURITY_SCAN | Execute the declared scan with applicable scope/rules and inspect findings against required criteria; scan success alone does not prove general security. |
| BENCHMARK | Record comparable baseline and changed results, workload/environment, and required thresholds; retain correctness/regression checks. |
| DOCUMENTATION_VALIDATION | Verify the changed links, examples, commands, structure, or rendering as required; record exactly what was checked and by which evidence source. |
| MANUAL_ACCEPTANCE | Execute declared steps against the identified version/environment and record actual observations and the required acceptor's result; never infer a person's approval. |

TDD is the default candidate for behavioral code changes with executable acceptance
criteria, not a universal requirement. Slice may choose other justified strategies
within Solution requirements. Implement can choose explicitly permitted alternatives,
refine routine cases/commands, and add supplementary verification. It cannot drop a
mandatory check, narrow its coverage, lower a threshold, replace required human
acceptance, or switch strategy because a check failed or its environment is absent.
Changed engineering requirements return to Solution; an inadequate Slice mapping
returns to Slice. Multiple strategy runs remain in the same frozen Attempt.

Implement's selection procedure and candidate guidance live in its Workflow, not
in upstream readiness rules. Existing Slice strategy commitments remain mandatory
unless their approved alternative conditions apply; adding a supported identifier
does not rewrite those commitments. Regression is a verification purpose; unit,
integration, contract, and end-to-end are test levels, not additional strategies.
Record applicable levels and regression checks under the governing obligations.

An implementation method describes how Implement organizes authorized changes,
not what behavior, architecture, Slice boundary, or passing criteria to choose.
Methods are optional free-form prose in Implementation Summary, with a brief reason
when used; they are not Verification Strategies and require no metadata field,
separate table, Artifact, Status, Attempt, or approval gate. A method supplies no
verification evidence by itself. Existing records without method prose remain valid.

Each Implement Record contains `## Verification Selection` with:

```markdown
| Strategy | Rationale | Governing Obligation |
| --- | --- | --- |
```

Metadata `Verification Strategies` is the ordered unique union of selected strategies,
separated by `; `, matching this table exactly. Selection records every mandatory
strategy or explicitly authorized alternative and any supplementary strategies.
Every rationale is non-empty and maps to a Slice/Solution obligation. One valid
strategy plus rationale does not by itself make the record READY_FOR_REVIEW.
Only a BLOCKED record unable to resolve strategy selection may use `NONE`, with an
empty selection table and the concrete upstream blocker; NONE is forbidden for
IN_PROGRESS and READY_FOR_REVIEW.

Each record also contains `## Verification Evidence` with:

```markdown
| Strategy | Obligation or Check | Source | Command or Procedure | Target and Environment | Result | Evidence Reference |
| --- | --- | --- | --- | --- | --- | --- |
```

Strategies resolve to the selection table. Source is TOOL_EXECUTION,
HUMAN_ACCEPTANCE, or MODEL_ASSESSMENT. Result is SUCCEEDED, FAILED, NOT_RUN,
INCONCLUSIVE, or NOT_APPLICABLE; these are check results, never Review Decisions or
another overall Status. Record not-yet-run selected checks as NOT_RUN, never success.
For an unresolved-selection BLOCKED record the evidence table may be empty, while
Blocker Evidence records the gap.

TOOL_EXECUTION preserves the actual command, target/version or file state, relevant
environment/configuration, exit status, and available output or a retrievable
reference. HUMAN_ACCEPTANCE records who accepted, the actual steps/observations,
target, and result when human acceptance is required. MODEL_ASSESSMENT records its
inspected sources and reasoning separately; it cannot manufacture tool output,
historical RED, benchmark measurements, or a person's approval. If a required
source/result is unavailable, report NOT_RUN or INCONCLUSIVE and do not pass the gate.
Evidence references must resolve to available records; an unexecuted command listed
as a plan is not execution evidence. Tool success still requires relevant coverage
and sufficient results for the obligation. Findings about missing/unreliable
required evidence follow the shared review gate.

READY_FOR_REVIEW requires evidence for every required check meeting its passing
criteria under the current upstream versions and Attempt. NOT_APPLICABLE needs an
explicit applicability condition and supporting evidence; it cannot waive a required
obligation. An optional failed check is still evaluated for blocking impact. Pending
work stays IN_PROGRESS while progress remains possible, or BLOCKED with the correct
owner when it cannot proceed. Neither a strategy rationale nor residual-risk prose
can defer a mandatory check to Review.

### Implement Record

An Implement Record contains `## Implementation Summary`, `## Verification Selection`,
`## Verification Evidence`, `## Open Issues`, and `## Self-check`, plus changed files
and File Placement Conformance where applicable. Open Issues records actual issues
or explicit NONE. The summary identifies authorized changes and deviations; Self-check
applies the shared review gate. Strategy-specific evidence follows the section above;
RED/GREEN/refactor is required for TDD only. Handoff is rendered in the response under
the Handoff Protocol, not persisted as a second routing authority in this record.
There is no overall Review Decision or separate Result state in an Implement Record.
Attempt is monotonic for one Feature/Slice across Solution and Slice Plan versions.
The Canonical Artifact Path
contains the latest authorized attempt; Review never edits it.

Before implementation, collect UsedAttempts from only this Feature/Slice's canonical
Implement, standard Implement history, immutable canonical Review Reports, matching
invalid Review history pairs, and the
bounded legacy counter evidence defined below. PASS and FAIL both permanently
occupy their Attempt. An Implement Record and its matching Review, or an identical
required archival copy, refer to one used counter value; conflicting duplicates,
filename/metadata mismatches, or unreadable relevant records block allocation.
Rotated roots, other projects, and supplemental reports do not participate.

`NewAttempt = max(UsedAttempts, default=0) + 1`.

| Existing evidence | Authorized behavior |
| --- | --- |
| No used Attempt | Allocate 1 at authorized Implement entry |
| IN_PROGRESS; unchanged version chain; no Review; same authorized execution | Continue the frozen Attempt |
| IN_PROGRESS with changed upstream versions | At a fresh authorized Implement entry, archive and allocate NewAttempt |
| BLOCKED with valid Recovery | Archive and allocate NewAttempt |
| Current Attempt occupied by a valid invalid-Review history pair | At a fresh authorized Implement entry, archive and allocate NewAttempt |
| Current READY_FOR_REVIEW without Review | Await Review; no reimplementation |
| Stale READY_FOR_REVIEW, or PASS/FAIL requiring authorized reimplementation | Archive and allocate NewAttempt; retain every Review |

An IN_PROGRESS record alone never authorizes a different invocation to resume work;
it must validate an Entry. A newly authorized execution that cannot satisfy the
same-execution continuation row archives the prior record and allocates NewAttempt.
At entry, freeze the counter and exact upstream versions and persist IN_PROGRESS
before code changes; if verification selection is unresolved, persist BLOCKED
instead and resolve its upstream owner without starting implementation. Archive the
prior Implement Record and install the new record as one protected replacement,
rechecking that the prior record and counter evidence have
not changed. History conflict or replacement failure restores the prior record and
authorizes no implementation; never overwrite conflicting history. Subsequent
IN_PROGRESS, BLOCKED, or READY_FOR_REVIEW writes belong to that frozen Attempt and
must verify it and the upstream chain again. An invocation never advances twice.

A file-changing record includes:

```markdown
| Actual Path | Kind | Responsibility | Planned Path or Pattern | Governing Decision | Conformance |
| --- | --- | --- | --- | --- | --- |
```

Kind is `PRODUCTION`, `TEST`, `CONFIGURATION`, `MIGRATION`, or `DOCUMENTATION`;
Conformance is `CONFORMS` or `DEVIATES`. Every created, moved, deleted, or materially
modified path appears, including configuration, migration, and documentation only
when authorized by Solution/Slice placement. Existing paths do not grant new scope.
A deviation records its owner and resolution; passing tests do not make it conforming.

### Legacy implementation evidence

Only Implement Record at `implement-feature-<FeatureNumber>-slice-<SliceNumber>.md`
is a canonical active implementation artifact. New writes cannot create TDD Record
or use `tdd-feature-<FeatureNumber>-slice-<SliceNumber>.md`. Legacy naming is not an
alias that activates another Workflow. Never run an old TDD launcher or normalize
an old Handoff's Next Workflow silently.

Preserve old TDD history and historical documentation exactly. An old active TDD
record or active routing field naming TDD requires explicit evidence migration;
Rule 2 halts rather than ignoring it or allowing two implementation records. This
framework migration alone does not authorize rewriting generated artifacts.

For a separately authorized migration of an affected Slice, archive the exact old
active TDD and its old Review reports, preserving filenames, under
`history/legacy-tdd/`. Existing TDD history stays at its original standard history
paths. Move affected old supplemental reports under Reports History using existing
archival rules. Archive rather than rewrite any other affected active artifact whose
routing names TDD; identify all affected owners/scopes before mutation. Perform the
authorized moves transactionally, reject conflicting destinations, and restore on
failure. Do not fabricate a new Implement Record or Review PASS during migration.
Unresolved legacy blockers must be handled explicitly before archival; migration
cannot erase an unresolved blocking obligation to make the graph progress.

For the exact current Feature/Slice, UsedAttempts additionally reads matching old
`history/tdd-feature-<FeatureNumber>-slice-<SliceNumber>-attempt-<AttemptNumber>.md`
and matching TDD/Review files in `history/legacy-tdd/`. These preserve the maximum
used counter but never establish current readiness, a routing owner, or PASS.
Unrelated histories and rotated projects remain excluded; ambiguous or conflicting
counter evidence stops allocation. After explicit migration, fresh resolution uses
current Solution/Slice verification requirements and allocates above all used
Attempts when Implement is authorized. Even an old PASS is not automatically proof
of a newly applicable verification contract.

### Review Report

A Review Report is immutable evidence for one Slice attempt; PASS and FAIL both
permanently occupy that Attempt. Only Implement allocates a later Attempt under the
Implement Record rules, including after upstream invalidation; Review never allocates one.
Transition determines current progression. A lower FAIL remains
historical control evidence while its upstream versions remain current but cannot
prove completion.

Every report contains exactly one `## Findings` section:

```markdown
## Findings

| # | Severity | Owner Workflow | Affected Scope | Finding | Evidence | Violated Contract |
| --- | --- | --- | --- | --- | --- | --- |
```

Rows are sequential from 1. Severity is `BLOCKING` or `NON_BLOCKING`; Owner is
Plan, Grill, Solution, Slice, or Implement. Finding, Evidence, and Violated Contract are
non-empty. Scope is Project for Plan/Solution, Feature for Grill/Slice, and Slice for
Implement, with every identifier resolvable in the active graph. A no-finding report keeps
the header and separator without data rows. Additional detail may follow but creates
no finding and changes no count.

Metadata counts equal table rows. PASS requires zero blocking rows and no return
metadata. FAIL requires at least one blocking row and exactly one Return Workflow and
Scope selected by the Framework owner precedence; its Scope equals one blocking
finding for that owner. Invalid counts, decision, findings, or disposition make the
report unusable.

## Mutation and retirement

Only an owner creates or replaces its canonical current Artifact; normative changes
advance Version, and downstream Workflows request RETURN instead of editing upstream.

Explicit user authorization is required to retire a Feature. Before writing Planning,
move all its canonical Lane, Requirement, Slice Plan, Implement, and Review evidence
unchanged to `.forgeflow/artifacts/history/retired-feature-<FeatureNumber>/`, and its
supplemental reports—preserving plugin paths and filenames—to
`.forgeflow/reports/history/retired-feature-<FeatureNumber>/`. Existing targets block
without overwrite or merge. For partial retirement, leave the prior Solution at its
canonical path as valid-but-stale under Solution baseline validity and currentness;
the next Solution removes retired Features from all maps. When retiring every
Feature, require Empty Feature Approval and also move the exact prior Solution, if
present, to `history/solution-plan-v<Version>.md` before installing NONE Planning.
An identical existing history copy satisfies archival; conflicting content blocks
the transaction. Plan has this narrow archival permission but cannot edit Solution
content. All evidence moves, prior Planning archival, and the new Planning write
form one transaction; failure restores all prior evidence. Archival transfers no
ownership. A completed empty-project transaction leaves Planning as the sole active
Artifact; any remaining downstream Artifact is still contradictory.
