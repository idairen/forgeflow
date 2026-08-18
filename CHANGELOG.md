# Changelog

All notable changes to ForgeFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added executable IDE acceptance-test assets under `tests/ide/`: a case manager
  that reads all 215 scenarios from the canonical test plan, creates clean Copilot
  or Codex workspaces, captures real IDE-generated snapshots, prepares isolated case
  copies and result records, plus a dependency-free Python fixture and reusable
  intent inputs. The tooling prepares evidence but never simulates an IDE workflow.
- Added a 12-page Chinese enterprise roadshow deck for CTOs and engineering
  leaders at `output/pdf/forgeflow-enterprise-roadshow.pdf`, together with its
  purpose-built visual asset at `docs/assets/forgeflow-roadshow-hero.png`.
- Added `Incremental Intent Entry` for IDE and CLI Plan invocations. An explicit
  same-project addition or change can now authorize Plan without an incoming
  Handoff, Bootstrap state, or persisted blocker.
- Added `forge plan --incremental --intent "..."` as the CLI entry for explicit
  same-project additions and changes. The command preserves active project evidence
  and lets a later `forge run` resume from the earliest affected scope.
- Added `Feature Contract Versions` to Planning. Each active Feature carries its own
  business-contract version so a later Planning artifact does not automatically
  invalidate Requirements for unchanged Features.
- Added Planning `Change Set` evidence for added, modified, removed, reordered, and
  project-constraint changes. Stable Feature IDs are preserved and retired IDs
  cannot be reused.
- Added `Feature Engineering Versions` to Solution Plan. Solution records the
  engineering compatibility boundary for every active Feature after analyzing
  cross-Feature impact.
- Added the immutable Reports History Root at `.forgeflow/reports/history/`.
  Replacing a supplemental report for the same plugin, Feature, Slice, attempt, and
  format now archives the exact prior report with the next `-revision-RR` suffix.
- Added an explicit Feature retirement transaction. Removing a Feature archives its
  canonical Artifacts and supplemental Reports under their respective history roots
  before the new Planning version becomes active.

### Changed

- Standardized all Codex and Copilot workflow launchers with explicit metadata,
  invocation identity, authoritative read order, graph-derived authorization, and
  canonical Handoff output sections. Copilot launchers now force `agent: agent`,
  and `forge-plan` explicitly prohibits substitution or delegation to Copilot's
  native planning mode.
- Kept adapter launchers thin by directing every workflow to its authoritative
  Framework, Protocol, and Workflow contracts instead of copying or redefining
  their normative procedures.
- Planning readiness now represents all currently approved project scope rather
  than asserting that every future module must be known during the initial Plan.
- Same-project incremental planning preserves the active Artifact Root, Reports
  Root, Artifact History, and Reports History. Project Evidence Rotation remains
  reserved for an explicitly authorized new project or reset.
- Requirement `Planning Version` now identifies the applicable Feature Contract
  Version instead of requiring equality with the enclosing Planning artifact
  version.
- Slice Plan `Based On Solution`, TDD `Solution Version`, and Review Report
  `Solution Version` now identify the applicable Feature Engineering Version.
- Solution changes invalidate Slice, TDD, and Review evidence only for Features whose
  Feature Engineering Version advances. Compatible completed Features retain their
  existing delivery and Review evidence.
- Plan preserves existing Feature identifiers during additions, modifications, and
  reordering. New Features receive previously unused identifiers.
- The Codex and Copilot Plan launchers now recognize Incremental Intent Entry and
  explicitly preserve project evidence during same-project increments.
- Review plugin execution now archives an existing same-path supplemental report
  before writing its replacement.
- The CLI artifact parser now validates Planning Feature Contract Versions and
  Solution Feature Engineering Versions. The state resolver uses those scoped
  versions when deciding whether Requirement, Slice, TDD, Review, and blocker
  evidence remains current.
- Incremental CLI execution treats an unchanged Artifact Graph as a valid waiting
  response, while rejecting partial graph changes that omit a valid Handoff or
  remain after an execution error.

### Safety

- Incremental Intent Entry is limited to Plan at Project scope and requires explicit
  user confirmation that the intent belongs to the same project.
- Ambiguous project continuity must be presented to the user before any Artifact or
  Report is changed.
- Incremental planning cannot bypass an invalid Artifact Graph, actionable persisted
  blocker, or current FAIL Review.
- Explicit new-project and reset requests continue to rotate Artifacts and Reports
  together with the same UTC suffix.
- Feature retirement is transactional: partial archival must be rolled back, and
  existing retirement targets cannot be overwritten or merged.

### Documentation

- Added a Chinese IDE acceptance test plan with 215 uniquely identified scenarios
  covering prompt discovery and host isolation, all six workflows, entry and
  Handoff variants, blockers and recovery, incremental evolution, evidence history,
  Review plugins, invalid graphs, session restart, and Codex/Copilot parity.
- Added comprehensive public-facing English and Chinese Concept & Architecture
  Guides under `docs/`. The guides explain ForgeFlow's mental model, six-workflow
  lifecycle, Artifact Graph, deterministic transitions, Review architecture,
  incremental development, IDE and CLI execution paths, and current capability
  boundaries without requiring prior knowledge of the normative specifications.
- Updated the Framework, Artifact Protocol, Handoff Protocol, all six workflow
  specifications, Codex and Copilot Plan launchers, Review plugin registry,
  architecture guide, and plugin guide for the incremental model.
- Updated framework versions to `2.5`, Artifact Protocol to `2.5`, Handoff Protocol
  to `2.7`, and workflow specifications to `2.5`.

### Migration Notes

- Existing IDE projects must refresh their installed `.forgeflow` framework files
  before using Incremental Intent Entry.
- A new or migrated non-empty Planning artifact must provide `Feature Contract
  Versions` for every active Feature and a `Change Set`. Use `BASELINE` for the first
  Planning version governed by this protocol.
- A new or migrated Solution Plan must provide `Feature Engineering Versions` for
  every active Feature.
- Existing Requirement, Slice Plan, TDD, and Review version fields retain their
  names, but their matching semantics are now Feature-scoped as described above.
- Existing CLI projects must refresh their installed `.forgeflow` files and migrate
  active Planning and Solution metadata before using `forge plan --incremental`.
