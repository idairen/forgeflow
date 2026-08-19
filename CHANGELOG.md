# Changelog

All notable changes to ForgeFlow are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added an open-source community baseline with a Code of Conduct, maintainer-led
  governance, support boundaries, public roadmap, CODEOWNERS, structured bug,
  feature, and protocol-change issue forms, a pull-request template, and monthly
  Dependabot checks for GitHub Actions, Python, and npm metadata.
- Added a maintainer release checklist covering synchronized versions, clean-tree
  verification, installable Python and npm artifacts, critical real-host acceptance,
  GitHub repository controls, publication prerequisites, and post-release checks.
- Added a packaged-artifact CI job that builds Python source and wheel distributions,
  installs the wheel into a clean environment, verifies the embedded framework, and
  installs the npx command from its packed tarball into a temporary project.
- Added repository contract coverage for public governance files and synchronized
  versions across `pyproject.toml`, `package.json`, and the Python module.
- Added IDE acceptance `summary` and `release-gate` commands. They parse centralized
  real-host result records, reject incomplete or duplicate evidence, report outcomes
  by priority and Adapter, require all 199 P0 cases to pass, and block releases for
  recorded P1 failures or blockers. Added focused unit coverage for the gate.
- Added bilingual Markdown presentation guides under `docs/presentations/` that
  position ForgeFlow as an Agent-Agnostic Engineering Protocol for leadership
  audiences. The guides focus on strategic motivation, governing principles,
  organizational value, a simplified leadership architecture, differentiation,
  adoption guidance, and a sourced comparison with GitHub Spec Kit, OpenSpec,
  BMAD Method, and SpecDD. They also present Plugin-Based Review as a governed
  quality extension that preserves Review's canonical PASS/FAIL ownership while
  keeping current capability boundaries explicit.
- Added 13-page English and Chinese executive architecture briefs under
  `docs/presentations/`, positioning ForgeFlow as an AI engineering protocol above
  SDLC methods. The light executive layout covers protocol architecture, Workflow
  execution, Feature/Slice loops, Ownership, Handoff/Return, engineering state,
  governance, Agent independence, and clearly labeled future direction. Added a
  dependency-free Chrome-based generator for reproducible builds.
- Added `ARCHITECTURE.zh-CN.md` as the complete Chinese counterpart of the public
  architecture document, preserving the same implemented architecture, comparison
  scope, open-source advantages, limitations, and normative-source boundaries.
- Added 43 dependency-free Python tests covering strict configuration, canonical
  Artifact and Handoff parsing, every forward graph stage, terminal and recovery
  resolution, stale evidence, incremental authorization, Runner Handoff validation,
  paired Artifact/Report rotation, and repository integration contracts.
- Added GitHub Actions quality gates across Python 3.10/3.13 and Node.js 18/22,
  including Python compilation, core protocol tests, npm installer tests, and npm
  package-content verification.
- Added the dependency-free `@idairen/forgeflow` npm package and its installer-only
  `npx @idairen/forgeflow init` command. It installs or refreshes the current
  Markdown framework and `forgeflow.json` for Copilot or Codex projects, preserves
  project-owned evidence and supported configuration during `--force`, and rejects
  symbolic-link targets.
- Added Node installer tests for initial installation, adapter selection, conflict
  handling, forced refresh, evidence and custom-plugin preservation, config
  validation, symbolic-link rejection, packaged help/version output, and continued
  availability of the Python CLI.
- Added executable IDE acceptance-test assets under `tests/acceptance/ide/`: a case manager
  that reads all 220 scenarios from the canonical test plan, creates clean Copilot
  or Codex workspaces, captures real IDE-generated snapshots, prepares isolated case
  copies and result records, plus a dependency-free Python fixture and reusable
  intent inputs. The tooling prepares evidence but never simulates an IDE workflow.
- Added a UTF-8 CSV catalog for all 220 IDE acceptance cases, including priority,
  adapter coverage, recommended baseline, actions, expected results, and editable
  execution-result fields. The IDE case manager can reproduce the catalog through
  its `export` command.
- Added a 12-page Chinese enterprise roadshow deck for CTOs and engineering
  leaders at `docs/presentations/forgeflow-enterprise-roadshow.pdf`, together with its
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

- Rewrote the security policy around the implemented Markdown, IDE-host, external
  Agent CLI, installer, and local-evidence trust boundaries. It now documents that
  CLI execution can grant project writes and shell tools, identifies relevant
  vulnerability classes, and removes inaccurate no-code-execution, offline-model,
  config-name, reset-deletion, and branch-support claims.
- Replaced the stale contribution workflow with the current `main`-based process,
  repository layout, quality commands, protocol and package contribution rules,
  real-host evidence requirements, and MIT contribution terms.
- Tightened README claims by describing ForgeFlow as a gated lifecycle with Return
  and Recovery, limiting deterministic claims to validated authorization, and making
  npm registry availability conditional on a corresponding public release.
- Ignored local `tmp/` document-generation scratch data without deleting existing
  macOS or browser-generated files.
- Centralized newly prepared IDE result records under the ignored
  `tests/acceptance/ide/results/` root and documented evidence-completion and
  machine-checkable release-gate usage without changing any case to PASS.
- Resynchronized the generated IDE acceptance CSV with the authoritative test plan
  for the two invocation-scope cases whose scenario punctuation had drifted.
- Enforced invocation-scoped execution across the Core, Handoff Protocol, and
  scoped Workflow contracts. Grill and Slice now process exactly one
  Feature per execution; TDD and Review process exactly one Slice or Slice attempt.
  Resolving a different Workflow or Target Scope only permits emitting a Canonical
  Handoff and stopping, never consuming that future scope in the same execution.
  Added five P0 IDE acceptance cases for multi-Feature and multi-Slice isolation.
- Clarified in both architecture documents that ForgeFlow's normative Core is
  agent-agnostic by design, while dedicated Adapters and real-host acceptance
  evidence remain explicitly host-specific and currently limited to Codex and
  GitHub Copilot.
- Reorganized the repository without changing `.forgeflow/`: public documents now
  use purpose-specific `docs/` sections, Python sources use the standard
  `src/forgeflow/` layout, tests are separated into unit, integration, contract,
  and IDE acceptance suites, and all build, CI, command, and documentation paths
  follow the new structure.
- Rebuilt `ARCHITECTURE.md` around the current protocol and implementation, covering
  the four core primitives, typed scopes, versioned Artifact Graph, ordered state
  resolution, Return and Recovery, incremental evidence preservation, execution and
  package boundaries, verification architecture, and current limitations. Added a
  dated comparison with Spec Kit, OpenSpec, BMAD Method, SpecDD, and SpecD using
  their official public documentation, plus an explicit account of ForgeFlow's
  open-source advantages and tradeoffs.
- Rebuilt `examples/sample-project` as an installation-driven walkthrough instead
  of a stale second copy of the ForgeFlow framework. The example now contains a
  reusable intent and protocol-valid comparison Artifacts, while a repository
  contract test parses the checkpoint and verifies its next authorized workflow.
- Repositioned the public documentation around ForgeFlow's implemented role as a
  repository-native control protocol and marked the project as a Technical Preview.
  Dedicated integration claims are now limited to Codex and GitHub Copilot, while
  automated protocol verification is explicitly separated from real IDE acceptance
  and model-output correctness.
- Kept workflow execution exclusively in the Python `forge` CLI. The npm package
  explicitly rejects `plan`, `run`, `status`, `reset`, and `handoff` instead of
  introducing a second Node.js orchestration implementation.
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

- Added a Chinese IDE acceptance test plan with 220 uniquely identified scenarios
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
