# Artifact Protocol

Version: 2.10

## Purpose

Artifacts and their version references form ForgeFlow's sole persistent source of
truth. Every artifact is a Markdown file and uses Markdown tables for metadata.
No executable parser, external schema, YAML front matter, or platform service is
required.

## Artifact Root

The canonical Artifact Root is `.forgeflow/artifacts/`, relative to the repository
root. All active ForgeFlow artifacts MUST be created, read, and updated directly
under the Artifact Root.

Every canonical filename defined by this protocol is relative to the Artifact
Root. A Canonical Artifact Path is the Artifact Root joined with one canonical
filename from the ownership table below. Files outside the Artifact Root MUST NOT
participate in the active artifact graph.

If the Artifact Root does not exist, the workflow creating the first artifact MUST
create it before writing that artifact.

### History Root

The canonical History Root is `.forgeflow/artifacts/history/`. It is physically
inside the Artifact Root so Project Evidence Rotation preserves project history, but
it is outside the active artifact graph. Transition resolution MUST ignore every
file below the History Root.

Before replacing a canonical current contract artifact with a higher version, its
owner MUST copy the exact prior file into the History Root using one of these names:

| Artifact Type | Historical filename |
| --- | --- |
| Planning | `planning-v<Version>.md` |
| Requirement | `requirement-feature-XX-v<Version>.md` |
| Solution Plan | `solution-plan-v<Version>.md` |
| Slice Plan | `slice-plan-feature-XX-v<Version>.md` |
| TDD Record | `tdd-feature-XX-slice-XX-attempt-NN.md` |

Review Reports are already immutable attempt files and remain directly under the
Artifact Root; they are not copied into History Root. An IN_PROGRESS TDD Record may
be updated within its current attempt. Before TDD advances Attempt or replaces a
READY_FOR_REVIEW or BLOCKED record, it MUST archive the prior exact file.

Historical files are immutable. If the required historical path already exists with
different content, the owner stops with a persisted blocker and MUST NOT replace the
canonical current artifact. If identical content already exists, archival is
already satisfied.

### Reports History Root

The canonical Reports History Root is `.forgeflow/reports/history/`. Supplemental
plugin reports outside this directory are the current report outputs for their
Feature, Slice, attempt, plugin, and format. The Reports History Root is immutable
history and MUST NOT be treated as current Review evidence.

Before Review replaces an existing supplemental report at the same canonical report
path, it MUST move the exact prior file under
`.forgeflow/reports/history/<plugin-name>/` and append the first unused
`-revision-RR` suffix before the format extension, starting at `01`. For example,
replacing `report-feature-01-slice-02-attempt-03.html` archives the prior file as
`report-feature-01-slice-02-attempt-03-revision-01.html`. An existing history path
with different content is a blocker; Review MUST NOT overwrite or merge it.

Project Evidence Rotation moves the complete Reports Root, including its History
Root. A subsequent Plan change never rotates either root; it archives only the
specific artifact or supplemental report that is actually replaced.

## Project Evidence Rotation Procedure

This explicit maintenance procedure archives the prior active artifact graph and
its supplemental Review plugin reports. It runs only when the user explicitly
requests reset or archive maintenance; Plan MUST NOT select it from semantic
similarity or dissimilarity between User Intents. It is a platform-independent
Markdown procedure performed by the active participant; it requires no
platform-specific script or executable framework component.

When invoked, the participant MUST apply these steps in order:

1. Resolve the Artifact Root and the supplemental Reports Root at
   `.forgeflow/reports/` without reading or changing their contents. Neither root
   may be a symbolic link or a non-directory path.
2. Treat each absent root as empty. If both roots are absent or empty, create any
   absent root, leave each empty root in place, and finish without creating a backup.
3. If either root is non-empty, capture the current UTC time once and format it as
   `yyyyMMddHHmmss`. Non-empty means that a directory contains any entry, including
   a hidden file or nested directory.
4. For each non-empty root, form its sibling backup path with that same timestamp:
   `artifacts.yyyyMMddHHmmss` for the Artifact Root and
   `reports.yyyyMMddHHmmss` for the Reports Root.
5. Before moving anything, validate every required backup path. If any path already
   exists or is a symbolic link, stop with a blocker. The participant MUST NOT
   overwrite, merge with, or delete any current or backup directory.
6. Move each non-empty root in full to its backup path without selectively copying,
   changing, or deleting its contents. An empty root does not need a backup.
7. Create a new empty Artifact Root and Reports Root before Plan reads or creates
   project evidence.
8. Treat all moves and directory creation as one transaction. If any operation
   fails, restore every successfully moved root and stop Plan. If rollback also
   fails, report every retained current and backup path for manual recovery.

Artifact and Reports Backup Paths are outside the active artifact graph and MUST NOT
participate in transition resolution. Supplemental reports remain non-authoritative
evidence even when their backup suffix associates them with one archived graph.

## Project Knowledge View

The Project Knowledge View is a read-only projection over the canonical current
Artifacts and preserved history. It is not an Artifact Type, has no owner Workflow,
has no Canonical Artifact Path, and MUST NOT participate in transition resolution.
Deleting or regenerating the view cannot change project state.

The active portion MUST be derived exclusively from validated canonical Artifacts
and preserve Planning Feature order and Slice Plan Slice order. For every active
Feature it exposes, when present:

1. the Feature Contract Version from Planning;
2. the current Requirement version and its Planning Version;
3. the Feature Engineering Version and Requirement version used by Solution;
4. the current Slice Plan version and Based On Solution reference;
5. each declared Slice's current TDD attempt and upstream versions; and
6. immutable Review attempts and their decisions.

The historical portion MAY index filenames from Artifact History, Reports History,
current supplemental Reports, and rotated evidence roots. Historical entries remain
non-authoritative and MUST NOT be interpreted as current contracts merely because
they appear in the view. A projection over an invalid Artifact Graph MUST report
that current knowledge is unavailable rather than combining partial valid files
into an apparent baseline.

The canonical traceability chain is:

```text
Planning Change Set
  -> Feature Contract Version
  -> Requirement / Planning Version
  -> Solution / Based On Requirements / Feature Engineering Version
  -> Slice Plan / Based On Solution
  -> TDD Record / Solution Version / Slice Plan Version / Attempt
  -> Review Report / matching versions / Attempt / Decision
```

Human-readable summaries, CLI output, dashboards, and generated indexes MAY render
this view, but they MUST link back to canonical filenames and versions and MUST NOT
invent missing relationships.

### Knowledge queries and timeline

A knowledge query MAY select one active Feature or one declared Slice. Feature
filters use `F-XX`; Slice filters use `F-XX/S-XX` and imply their Feature. A query
MUST reject malformed or inactive identifiers, preserve Planning and Slice Plan
order, and return only the requested subtree without changing the underlying view.

The default query exposes current knowledge only. An explicit history option MAY
also expose immutable history indexes and a contract timeline assembled from
current Planning and Solution plus valid archived `planning-v<Version>.md` and
`solution-plan-v<Version>.md` files. Invalid or unreadable historical metadata is a
non-authoritative query warning; it MUST NOT invalidate an otherwise valid current
Artifact Graph or be silently interpreted as a contract.

JSON and Markdown are permitted rendering formats. Implementations SHOULD write
them to standard output by default rather than persist another potentially stale
knowledge file. Any persisted cache remains disposable and non-authoritative.

## Required metadata block

Every artifact MUST begin with its title followed immediately by a `Metadata`
section containing a two-column Markdown table:

| Field | Value |
| --- | --- |
| Artifact Type | Planning |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Plan |

Field labels are case-sensitive. A participant MUST reject a file whose required
metadata is missing, duplicated, or contradictory.

## Ownership and filenames

| Artifact Type | Owner Workflow | Scope | Canonical filename |
| --- | --- | --- | --- |
| Planning | Plan | Project | `planning.md` |
| Requirement | Grill | Feature | `requirement-feature-XX.md` |
| Solution Plan | Solution | Project | `solution-plan.md` |
| Slice Plan | Slice | Feature | `slice-plan-feature-XX.md` |
| TDD Record | TDD | Slice | `tdd-feature-XX-slice-XX.md` |
| Review Report | Review | Slice attempt | `review-feature-XX-slice-XX-attempt-NN.md` |

Identifiers use `F-XX` and `S-XX`. The numeric portions in filenames, metadata,
Planning, and Slice Plans MUST match.

Every narrow routing scope is a graph reference, not a declaration. `Feature: F-XX`
in BLOCKED Affected Scope or FAIL Review Return Scope MUST resolve to an ID declared
by active Planning. `Slice: F-XX/S-XX` MUST also resolve to an ID declared by the
Canonical Slice Plan for that Feature. Only Planning declares Features, and only a
Slice Plan declares Slices. Artifact text, blocker metadata, Review findings, and
conversation context cannot create identifiers. An unresolved routing scope is a
graph contradiction rather than an actionable or stale route.

## Type-specific metadata

| Artifact Type | Additional required fields |
| --- | --- |
| Planning | Feature IDs in declared order; Feature Contract Versions for every Feature; Change Set; Empty Feature Approval only for `NONE` |
| Requirement | Feature ID; Planning Version |
| Solution Plan | Based On Requirements and Feature Engineering Versions: every `F-XX = version`; structured impact metadata defined below for Solutions created under this protocol version |
| Slice Plan | Feature ID; Based On Solution; Slice IDs in declared order |
| TDD Record | Feature ID; Slice ID; Attempt; Solution Version; Slice Plan Version |
| Review Report | Feature ID; Slice ID; Attempt; Decision; Solution Version; Slice Plan Version; Blocking Findings; Non-blocking Findings; Return Workflow and Return Scope when Decision is FAIL |

Multiple values MUST use semicolon-separated canonical entries in the table, for
example `F-01 = 1.0; F-02 = 1.0`. Their declared order is significant where stated.
Planning `Feature IDs` is the sole Feature order, and each Slice Plan's `Slice IDs`
is the sole Slice order within that Feature. Identifier numbers and filenames do not
override these positions. The same Slice ID may appear under different Features, so
a Slice position is always resolved together with its Feature context.

Planning `Feature Contract Versions` MUST contain exactly one entry for every active
Feature ID. A new Feature uses the Planning artifact's current Version. An unchanged
Feature retains its prior contract version across later Planning versions. A Feature
whose intent, boundary, dependency, exclusion, success condition, or applicable
project constraint changes advances its contract version to the new Planning
Version. Requirement `Planning Version` refers to this Feature-scoped contract
version, not necessarily the current Planning artifact's own Version.

Planning `Change Set` is `BASELINE` for the first Planning version. A later version
records every added, modified, removed, or reordered Feature and whether project
constraints changed. Stable Feature IDs MUST be preserved and retired identifiers
MUST NOT be reused. A project-constraint change MUST advance every affected Feature
Contract Version; it does not invalidate an unaffected Feature merely because the
Planning artifact version changed.

Solution Plan `Feature Engineering Versions` MUST contain exactly one entry for
every active Feature ID. A new or engineering-affected Feature uses the current
Solution Plan Version. An unaffected Feature retains its prior engineering version.
`Based On Solution` and `Solution Version` fields in Feature- and Slice-scoped
artifacts refer to the applicable Feature Engineering Version, not necessarily the
current Solution Plan artifact's own Version.

### Structured Solution impact metadata

A Solution Plan created or normatively revised under Artifact Protocol 2.9 MUST
include all of the following metadata fields. A pre-2.9 Solution that omits the
entire set remains readable during migration; the derived Project Impact View is
then `unavailable`. A partial set is invalid.

| Field | Canonical value |
| --- | --- |
| Shared Component IDs | `NONE` or ordered unique `SC-XX` identifiers separated by `; ` |
| Feature Dependencies | one ordered entry per active Feature: `F-XX = NONE` or `F-XX = F-YY, F-ZZ` |
| Feature Shared Components | one ordered entry per active Feature: `F-XX = NONE` or `F-XX = SC-YY, SC-ZZ` |
| Feature Decision References | one ordered entry per active Feature: `F-XX = NONE` or `F-XX = ED-YY, ED-ZZ` |
| Cross-Feature Impact | one ordered entry per active Feature: `F-XX = DIRECT`, `INDIRECT`, or `UNAFFECTED` |

Every map MUST contain exactly the active Feature IDs in Planning order. A Feature
dependency target MUST be another active Feature and MUST NOT be the source Feature.
Dependencies MUST be acyclic. Component references MUST resolve through `Shared
Component IDs`. Decision references MUST resolve to current entries in the
Solution Plan's `Engineering Decision Register`. `NONE` cannot be combined with an
identifier in the same value.

`Feature Dependencies` means that the Feature on the left consumes an engineering
contract owned or exposed by the Features on the right. Therefore a change to a
dependency can directly or transitively affect its dependents. Shared-component
membership means co-usage, not dependency direction. `Cross-Feature Impact`
classifies the current Solution revision rather than predicting every possible
future change.

The derived Project Impact View may calculate reverse and transitive relationships
from these fields. Such calculations are non-authoritative and MUST NOT replace the
Solution-owned impact decision or alter transition resolution.

Planning represents an explicitly approved empty Feature list with the exact value
`NONE`; a blank metadata value is never an empty list. When `Feature IDs` is `NONE`,
`Feature Contract Versions` MUST also be `NONE`, and Planning MUST include
`Empty Feature Approval` rendered as
`APPROVED: <non-empty user approval evidence>`. That field is forbidden when any
Feature is declared. `NONE` cannot be combined with Feature identifiers. A READY
empty Planning is valid only when it is the sole active artifact; any Requirement,
Solution Plan, Slice Plan, TDD Record, or Review Report in that graph is a
contradiction rather than evidence for an empty project.

## Status values

| Artifact Type | Allowed Status |
| --- | --- |
| Planning, Requirement, Solution Plan, Slice Plan | DRAFT, BLOCKED, READY |
| TDD Record | IN_PROGRESS, BLOCKED, READY_FOR_REVIEW |
| Review Report | READY |

Review Report Decision is exactly PASS or FAIL. Attempt is a positive integer.
`Blocking Findings` and `Non-blocking Findings` are non-negative integers. Version
uses `major.minor` decimal notation such as `1.0`.

## Persisted blocker metadata

Every Planning, Requirement, Solution Plan, Slice Plan, or TDD Record whose Status
is `BLOCKED` MUST include all of these additional metadata fields:

| Field | Requirement |
| --- | --- |
| Blocker Category | One non-terminal owner category defined by the Handoff Protocol |
| Blocker Owner | One canonical workflow name |
| Affected Scope | Canonical Project, declared Feature, or declared Slice scope required by the category route |
| Blocker Reason | Non-empty description of the unresolved condition |
| Blocker Evidence | Observable artifact, code, command, or user-decision evidence |

Persisted BLOCKED artifacts may use `PLAN_GAP`, `BUSINESS_GAP`, `ENGINEERING_GAP`,
`SLICE_VIOLATION`, or `IMPLEMENTATION_GAP`. `REVIEW_BLOCKER` belongs only to FAIL
Review Reports, and `GRAPH_CONTRADICTION` belongs only to terminal halt handoffs.
The Blocker Owner and Affected Scope MUST match the category routing table. A
BLOCKED artifact with missing or contradictory blocker metadata is invalid graph
evidence. A structurally valid BLOCKED artifact whose upstream chain became stale is
preserved but non-actionable. A valid current BLOCKED artifact remains the persistent
blocker record until its owner replaces that canonical artifact with a higher valid
version or attempt whose Status is no longer `BLOCKED`. Handoff text and conversation
context do not replace this persisted evidence.

Blocker currentness depends on the complete upstream barrier chain:

| BLOCKED Artifact Type | Required usable current upstream chain |
| --- | --- |
| Planning | None |
| Requirement | READY Planning containing its Feature; Planning Version matching that Feature's current Feature Contract Version |
| Solution Plan | READY Planning and every planned READY Requirement; exact Based On Requirements map |
| Slice Plan | Current Planning and Requirements; READY current Solution Plan; declared Feature; Based On Solution matching that Feature's current Feature Engineering Version |
| TDD Record | Current Planning, Requirements, and Solution Plan; READY current Slice Plan containing its Slice; Solution Version matching that Feature's current Feature Engineering Version and matching Slice Plan Version |

The BLOCKED artifact itself does not need READY status. Every artifact before it in
the table's dependency chain does. Matching a direct version while an earlier
barrier is unusable does not make the blocker current. A stale downstream blocker
remains preserved evidence but MUST NOT authorize RETURN, Recovery Entry, or work.

When a non-Review workflow discovers a blocker that cannot be resolved within the
current invocation, it MUST persist the blocker in its own owned artifact before it
emits RETURN or stops. It records the upstream owner in `Blocker Owner` and never
edits that owner's artifact. Review persists blockers through its immutable FAIL
Review Report and required return metadata instead of using Status `BLOCKED`.

## Artifact contracts

### Planning

Planning contains project intent, constraints, exclusions, success measures, and
the complete ordered Feature list for the currently approved scope. READY means the
list covers all intent approved so far; it does not assert that the user will never
add another module through a Subsequent Plan Entry.

### Requirement

A Requirement is Feature-level. It contains business behavior, rules, acceptance
criteria, edge cases, dependencies, and exclusions. READY means no unresolved
business decision can change observable behavior.

### Solution Plan

A Solution Plan is Project-level. It analyzes all current READY Requirements and
defines boundaries, interfaces, data and migration decisions, quality constraints,
risks, and verification strategy. Its Feature Engineering Versions map records the
smallest compatibility boundary for downstream reuse. Adding or changing one Feature
does not invalidate another Feature unless Solution records a material cross-Feature
engineering impact by advancing that Feature's engineering version.

A Solution Plan created or normatively revised under Artifact Protocol 2.10 MUST
contain exactly one `## Implementation Structure` section and exactly one
`## Test Structure` section. A pre-2.10 Solution that omits both remains readable
during migration. A revised Solution MUST add both; one without the other is an
incomplete engineering contract.

`Implementation Structure` defines repository-relative source roots, the chosen
organization strategy, responsibility boundaries, module or package patterns,
allowed dependency direction, applicable Features or Shared Components, and the
evidence supporting the choice. It MUST use this table header:

```markdown
| Component or Role | Source Root | Module or Package Pattern | Responsibility | Allowed Dependencies | Applies To | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
```

`Test Structure` defines where unit, component, integration, contract, or end-to-end
tests belong and how they relate to production structure. It MUST use this table
header:

```markdown
| Test Level | Test Root | Module or Package Pattern | Production Relationship | Applies To | Evidence |
| --- | --- | --- | --- | --- | --- |
```

Paths and patterns are repository-relative. Solution MUST prefer observable project
conventions when they are coherent. When introducing multiple architectural roles,
it MUST state whether organization is by Feature, by layer, or a justified hybrid;
it MUST NOT silently place unrelated responsibilities into one package or module.
Likewise, it MUST NOT create a generic catch-all `utility` area when a cohesive
domain, mapping, validation, serialization, infrastructure, or shared-component
responsibility can be named. Shared placement is valid only when the responsibilities
are cohesive and the Solution records the reason.

Tests MUST follow the repository's established convention or an explicit Test
Structure. Unit and component tests SHOULD mirror the production package/module
they exercise when the language and framework support that convention. Integration,
contract, and end-to-end tests MAY use dedicated roots or packages when explicitly
defined. ForgeFlow does not require Java, Spring, or any one test topology.

### Slice Plan

A Slice Plan is Feature-level and immutable for its version. It contains an ordered
list of independently implementable and reviewable Slices. Slice Plans MUST NOT
store dynamic execution state, cursors, or Review decisions.

Every Slice that creates, moves, or materially changes production or test files
MUST include a `Planned File Placement` table with this exact header:

```markdown
| Slice ID | Responsibility | Production Path or Pattern | Test Path or Pattern | Governing Decision | Notes |
| --- | --- | --- | --- | --- | --- |
```

Each row MUST resolve to the current Solution's Implementation Structure and Test
Structure. A directory pattern may leave a filename to repository naming
conventions, but it cannot leave the package, module, source root, test root, or
architectural responsibility undecided. Slices that change no files record `NONE`
with the reason.

### TDD Record

A TDD Record is Slice-level. It records red/green/refactor evidence, commands,
results, changed files, deviations, and the Review attempt being prepared. Attempt
starts at 1 and increments after each FAIL. Its Canonical Artifact Path contains
the latest authorized TDD attempt; the owning TDD workflow replaces that current
record when preparing a higher attempt. Review never edits this artifact.

A TDD Record for a Slice that changes files MUST contain a `File Placement
Conformance` table linking every created or moved production/test path to its Slice
placement row and governing Solution decision. The table uses this exact header:

```markdown
| Actual Path | Kind | Responsibility | Planned Path or Pattern | Governing Decision | Conformance |
| --- | --- | --- | --- | --- | --- |
```

`Kind` is `PRODUCTION` or `TEST`; `Conformance` is `CONFORMS` or `DEVIATES`. Every
`DEVIATES` row records its owner and resolution in the TDD Record deviations
evidence. Merely passing tests does not make an architectural placement deviation
conforming.

### Review Report

A Review Report is immutable evidence for one Slice attempt. A correction creates
attempt `NN + 1`; it never overwrites an earlier report. Only the latest valid
attempt with current upstream versions participates in progression.

A lower FAIL Review Report remains historical control evidence after the current
TDD Record advances to a higher attempt, provided its Solution Plan and Slice Plan
references are still current. It authorizes retry ordering but cannot prove Slice
completion. A PASS proves completion only when it matches the current TDD attempt
and current upstream versions.

Every Review Report MUST contain exactly one `## Findings` section with this exact
table header and column order:

```markdown
## Findings

| # | Severity | Owner Workflow | Affected Scope | Finding | Evidence | Violated Contract |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | BLOCKING | TDD | Slice: F-01/S-01 | Test failure | test_x failed | Requirement AC-3 |
```

Each data row is one finding. Row numbers start at 1 and are sequential; Severity
is exactly `BLOCKING` or `NON_BLOCKING`; Owner Workflow is Plan, Grill, Solution,
Slice, or TDD; and Finding, Evidence, and Violated Contract are non-empty rendered
values without placeholders. Affected Scope MUST match the owner: Project for Plan
and Solution, Feature for Grill and Slice, and Slice for TDD. A report with no
findings retains the header and separator but has no data rows. Additional detailed
evidence MAY follow the table, but it does not create findings or affect counts.

The metadata counts MUST equal the rows of each severity in this canonical table.

- PASS requires `Blocking Findings` to be 0. `Return Workflow` and `Return Scope`
  MUST be absent. PASS MAY contain non-blocking findings.
- FAIL requires `Blocking Findings` to be greater than 0 and requires exactly one
  `Return Workflow` and `Return Scope`.
- The return destination is selected from all blocking findings using the owner
  precedence in the Framework. `Return Workflow` MUST equal that selected owner,
  and `Return Scope` MUST equal the Affected Scope of at least one blocking finding
  owned by it. Every Feature and Slice identifier in every finding and Return Scope
  MUST resolve in active Planning and the applicable Canonical Slice Plan before
  the report is valid.

A Review Report that violates these decision, count, finding, or return rules is
invalid and cannot authorize a transition or prove completion.

## Versions and mutation

Only the owning workflow may create or replace its canonical current artifact.
Normative content changes require a new version. Canonical Artifact Paths hold the
current contract; the required History Root preserves replaced versions. Historical
files and Artifact Backup Paths are outside the active artifact graph.

Downstream workflows MUST request a RETURN when an upstream contract change is
needed. No workflow may change another workflow's artifact or status.

### Feature retirement

Removing a Feature from current Planning requires explicit user authorization.
Before the new Planning version is written, the active participant MUST move every
canonical Requirement, Slice Plan, TDD Record, and Review Report owned by that
Feature, without changing content, below
`.forgeflow/artifacts/history/retired-feature-XX/`. It MUST likewise move every
matching supplemental plugin report below
`.forgeflow/reports/history/retired-feature-XX/`, preserving the plugin directory and
filename. Existing retirement targets are blockers and MUST NOT be overwritten or
merged. Both moves and the new Planning write form one transaction; failure restores
all moved evidence and stops Plan. Retirement is archival coordination, not a
transfer of artifact ownership. The next Solution version removes the retired
Feature from Based On Requirements and Feature Engineering Versions.
