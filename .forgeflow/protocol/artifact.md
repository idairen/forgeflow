# Artifact Protocol

Version: 2.2

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

## Artifact Root Rotation Procedure

This procedure archives the prior active artifact graph before a new Plan run. It
is a platform-independent Markdown procedure performed by the active participant;
it requires no platform-specific script or executable framework component.

When invoked, the participant MUST apply these steps in order:

1. Resolve the Artifact Root without reading or changing artifact contents.
2. If the Artifact Root does not exist, create it as an empty directory and finish
   the procedure without creating a backup.
3. If the Artifact Root is empty, leave it in place and finish the procedure
   without creating a backup.
4. If the Artifact Root is non-empty, capture the current UTC time once and format
   it as `yyyyMMddHHmmss`. Non-empty means that the directory contains any entry,
   including a hidden file or nested directory.
5. Form an Artifact Backup Path as a sibling of the Artifact Root whose directory
   name is `artifacts.yyyyMMddHHmmss`, replacing the timestamp portion with the
   captured value.
6. If that Artifact Backup Path already exists, stop with a blocker. The participant
   MUST NOT overwrite, merge with, or delete either directory.
7. Move the entire Artifact Root to the Artifact Backup Path without selectively
   copying, changing, or deleting its contents.
8. Create a new empty Artifact Root before Plan reads or creates any project
   artifact.

An Artifact Backup Path is outside the active artifact graph and MUST NOT
participate in transition resolution. If any move or directory creation fails, the
participant MUST stop Plan, preserve all successfully retained data, report the
exact failing step and paths, and MUST NOT write a new active artifact.

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

## Type-specific metadata

| Artifact Type | Additional required fields |
| --- | --- |
| Planning | Feature IDs in declared order |
| Requirement | Feature ID; Planning Version |
| Solution Plan | Based On Requirements: every `F-XX = version` |
| Slice Plan | Feature ID; Based On Solution; Slice IDs in declared order |
| TDD Record | Feature ID; Slice ID; Attempt; Solution Version; Slice Plan Version |
| Review Report | Feature ID; Slice ID; Attempt; Decision; Solution Version; Slice Plan Version; Blocking Findings; Non-blocking Findings; Return Workflow and Return Scope when Decision is FAIL |

Multiple values MUST use semicolon-separated canonical entries in the table, for
example `F-01 = 1.0; F-02 = 1.0`. Their declared order is significant where stated.

## Status values

| Artifact Type | Allowed Status |
| --- | --- |
| Planning, Requirement, Solution Plan, Slice Plan | DRAFT, BLOCKED, READY |
| TDD Record | IN_PROGRESS, BLOCKED, READY_FOR_REVIEW |
| Review Report | READY |

Review Report Decision is exactly PASS or FAIL. Attempt is a positive integer.
`Blocking Findings` and `Non-blocking Findings` are non-negative integers. Version
uses `major.minor` decimal notation such as `1.0`.

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

Every finding in the report body MUST identify its Severity as `BLOCKING` or
`NON_BLOCKING`, Owner Workflow, Affected Scope, observable Evidence, and Violated
Contract. The metadata counts MUST equal the findings in the body.

- PASS requires `Blocking Findings` to be 0. `Return Workflow` and `Return Scope`
  MUST be absent. PASS MAY contain non-blocking findings.
- FAIL requires `Blocking Findings` to be greater than 0 and requires exactly one
  `Return Workflow` and `Return Scope`.
- The return destination is selected from all blocking findings using the owner
  precedence in the Framework. Its scope MUST be the affected Feature for Grill,
  Project for Solution, the affected Feature for Slice, or the affected Slice for
  TDD.

A Review Report that violates these decision, count, finding, or return rules is
invalid and cannot authorize a transition or prove completion.

## Versions and mutation

Only the owning workflow may create or replace its canonical current artifact.
Normative content changes require a new version. Canonical Artifact Paths hold the
current contract; source control or a separate archive may preserve replaced
versions. Archived files are outside the active artifact graph.

Downstream workflows MUST request a RETURN when an upstream contract change is
needed. No workflow may change another workflow's artifact or status.
