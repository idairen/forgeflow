# Changelog

All notable changes to ForgeFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `Incremental Intent Entry` for IDE Plan invocations. An explicit
  same-project addition or change can now authorize Plan without an incoming
  Handoff, Bootstrap state, or persisted blocker.
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
- This change documents and implements the IDE Markdown framework behavior only.
  Python CLI parsing and state resolution are not included in this incremental-model
  change.
