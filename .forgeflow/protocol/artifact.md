# Artifact Protocol

Version: 2.4

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

## Project Evidence Rotation Procedure

This procedure archives the prior active artifact graph and its supplemental Review
plugin reports before a new Plan run. It is a platform-independent Markdown
procedure performed by the active participant; it requires no platform-specific
script or executable framework component.

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
| Planning | Feature IDs in declared order; Empty Feature Approval only for `NONE` |
| Requirement | Feature ID; Planning Version |
| Solution Plan | Based On Requirements: every `F-XX = version` |
| Slice Plan | Feature ID; Based On Solution; Slice IDs in declared order |
| TDD Record | Feature ID; Slice ID; Attempt; Solution Version; Slice Plan Version |
| Review Report | Feature ID; Slice ID; Attempt; Decision; Solution Version; Slice Plan Version; Blocking Findings; Non-blocking Findings; Return Workflow and Return Scope when Decision is FAIL |

Multiple values MUST use semicolon-separated canonical entries in the table, for
example `F-01 = 1.0; F-02 = 1.0`. Their declared order is significant where stated.
Planning `Feature IDs` is the sole Feature order, and each Slice Plan's `Slice IDs`
is the sole Slice order within that Feature. Identifier numbers and filenames do not
override these positions. The same Slice ID may appear under different Features, so
a Slice position is always resolved together with its Feature context.

Planning represents an explicitly approved empty Feature list with the exact value
`NONE`; a blank metadata value is never an empty list. When `Feature IDs` is `NONE`,
Planning MUST include `Empty Feature Approval` rendered as
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
| Requirement | READY Planning containing its Feature; matching Planning Version |
| Solution Plan | READY Planning and every planned READY Requirement; exact Based On Requirements map |
| Slice Plan | Current Planning and Requirements; READY current Solution Plan; declared Feature; matching Based On Solution |
| TDD Record | Current Planning, Requirements, and Solution Plan; READY current Slice Plan containing its Slice; matching Solution and Slice Plan versions |

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
the complete ordered Feature list. READY means the list covers approved scope.

### Requirement

A Requirement is Feature-level. It contains business behavior, rules, acceptance
criteria, edge cases, dependencies, and exclusions. READY means no unresolved
business decision can change observable behavior.

### Solution Plan

A Solution Plan is Project-level. It analyzes all current READY Requirements and
defines boundaries, interfaces, data and migration decisions, quality constraints,
risks, and verification strategy.

### Slice Plan

A Slice Plan is Feature-level and immutable for its version. It contains an ordered
list of independently implementable and reviewable Slices. Slice Plans MUST NOT
store dynamic execution state, cursors, or Review decisions.

### TDD Record

A TDD Record is Slice-level. It records red/green/refactor evidence, commands,
results, changed files, deviations, and the Review attempt being prepared. Attempt
starts at 1 and increments after each FAIL. Its Canonical Artifact Path contains
the latest authorized TDD attempt; the owning TDD workflow replaces that current
record when preparing a higher attempt. Review never edits this artifact.

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
