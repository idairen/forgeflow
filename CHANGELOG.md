# Changelog

Changes below describe the current unreleased implementation. Package versions remain
0.1.0; this file does not assert registry publication or real-host acceptance.
Earlier development notes remain available in Git history.

## [Unreleased]

### TDD required by default for behavioral changes

- Require TDD for new or changed executable behavior, including bug fixes and the
  behavioral portion of mixed Slices. Non-behavioral work records non-applicability.
- Require explicitly user-approved, scoped Solution exceptions with equivalent
  coverage before replacing TDD with BEHAVIORAL_TEST. Slice maps the decision;
  Implement checks it before changes and Review independently verifies it.
- Retain risk-specific supplementary strategies, with an explanation of the
  additional evidence they supply. Preserve old evidence without inventing RED;
  older plans missing policy return to their owner before new behavioral work.
- Framework 3.11, Artifact 2.22, Solution/Implement 2.16, Slice 2.15, Review 2.14.
  Existing schemas and strategy identifiers are unchanged; semantic applicability
  is a participant obligation, not an automatic CLI code classifier.

### Review rework and Implement format recovery

- Accept fresh FORWARD and REVIEW_BLOCKER RETURN Handoffs explicitly in Implement,
  Solution and Slice, separately from no-Handoff gap Recovery. Rule 8 authorizes
  its receiving execution directly; Implement archives the failed Attempt and
  allocates a new one without changing the immutable Review.
- Require candidate validation before Implement publication, including entry writes,
  single-valued evidence cells, title/Metadata placement, file conformance and
  check-specific coverage. Clarify that the Planning/Solution structure marker
  stays 2.11 independently of the protocol document version.
- Add an explicitly authorized Implement format-repair procedure. Preserve invalid
  originals outside standard Attempt archives; retain identity and evidence, and
  keep conflicting archives and Review decisions protected.
- Add runner-entry, malformed-record and repair-to-rework regressions. Tests use
  synthetic artifacts and mocked Agent writes; they do not establish live IDE
  compliance or repair any existing project's evidence.
- Framework 3.10, Artifact 2.21, Transition 1.9, Implement/Solution 2.15 and Slice
  2.14; no new Workflow, Entry mode, status enum or package release.

### Planning language and verification deferral

- Persist the initial Plan language in Project Intent and inherit it across all
  Workflow questions and Artifact prose, preserving canonical protocol syntax.
- Ask users whether to repair/retry, temporarily defer specific failed/unavailable
  checks, or pause. Record explicit decisions, risks, and retry checkpoints without
  relabeling evidence or repeating an unchanged approval request.
- Allow independent current-Slice work after deferral; route changes to mandatory
  verification scheduling through versioned Solution/Slice revisions with concrete
  successor checks before completion. Existing readiness and PASS gates remain.
- Update Framework to 3.9, Artifact Protocol to 2.20, Plan/Slice/Review to 2.13,
  and Solution/Implement to 2.14. No Artifact status or result enum changes.

### CLI artifact compatibility

- Parse the protocol's ordered Feature/Slice metadata keys while retaining legacy
  CLI aliases; reject conflicting aliases and avoid dependent missing-key errors.
- Accept explicit verification-only placement declarations when the Changed Files
  list contains only framework/evidence bookkeeping; malformed tables and
  contradictory implementation changes remain errors.
- Diagnose a RED row marked successful despite a recorded failing test exit.
  Original execution evidence is never rewritten or automatically reinterpreted.
- Support explicit conditional-strategy and check-to-evidence mappings. Remove
  English-keyword-based strategy waivers and keep unmapped obligations blocked.
- Add an opt-in read-only regression against the maintainer's completed project.
  These checks validate recorded structure, not a fresh IDE or application run.

### Framework and execution alignment

- Align public documentation and the optional CLI with Framework 3.8, Artifact 2.19,
  Transition 1.8, Handoff 2.15 and Implement 2.13.
- Use exactly six Workflows: Plan, Grill, Solution, Slice, Implement and Review.
  TDD is a verification strategy within Implement, not a separate Workflow.
- Limit parallel Feature Lanes to Grill. Join every current Requirement before
  Solution and require every Feature's current Slice Plan before Implement.
  Deliver in declared Feature/Slice order.
- Validate canonical identifiers, current version chains, persisted blockers,
  ordered Handoff projections and bounded historical Attempt evidence.
- Validate Implement strategy selection and recorded verification evidence,
  including BEHAVIORAL_TEST. Keep methods optional within the authorized Slice.
- Route missing/invalid Handoffs through read-only correction. Require explicit
  claim-specific recovery; ordinary commands never dispose of invalid Reviews.
- Preserve valid-but-stale Solution baselines only with supporting lineage;
  stale evidence cannot satisfy delivery or completion gates.

### Release preparation

- Record the maintainer-reported local Python/npm installation checks, with
  checkout attribution and explicit limits on raw evidence and host coverage.
- Add CLI/configuration reference, troubleshooting and existing-project adoption
  guidance, introductory terms, and maintainer-confirmed host invocation forms.
- Add a usage-question issue form and Python package project links.
- Check public documentation links/anchors and CLI/config name coverage in CI;
  this does not validate external URLs or real-host behavior.

- Archive sanitized real-project evidence for FAIL/rework/PASS and invalid-Review
  recovery, with original hashes and explicit historical/current-version limits.
  Preserve current-CLI compatibility diagnostics without changing source artifacts.


- Add an executable inventory-transfer teaching example, with actual failure and
  repair checks, and a full six-workflow walkthrough. Teaching results do not
  constitute independent Review or IDE acceptance.
- Add a first-run guide and compatibility/evidence matrix, distinguishing reported
  successful IDE execution from public case records awaiting archival.
- Remove the unused historical roadshow image from the current source tree.
- Verify wheel, sdist and npm archive contents against the checkout in CI; run the
  executable example in the Python matrix.

### Installation and maintenance

- Package the current framework in Python and npm distributions. The npm package
  remains installer-only; Python provides the optional `forge` orchestrator.
- Forced initialization removes retired managed TDD launchers while preserving
  project artifacts, reports and history. Active legacy evidence requires a
  separately authorized migration; old PASS evidence is not silently inherited.
- Keep knowledge and impact views derived and non-authoritative. Enumerate history
  only when requested for the knowledge view.
- Add package smoke checks and current Markdown regressions to CI. Separate current
  IDE acceptance from historical results; unexecuted tests remain NOT RUN.
- Consolidate support/governance guidance, remove obsolete presentation assets and
  duplicate guides, and update acceptance instructions to the current case set.

### Compatibility and validation limits

The `implement` workflow, filenames and knowledge keys replace `tdd`. Read the
[migration guide](docs/maintainers/implement-migration.md) before upgrading.
The CLI checks structure and recorded results; independent Review evaluates their
truthfulness, coverage and correctness. Host-provided exclusion and protected
transactions remain necessary. Automated checks do not prove real IDE compliance.

Follow the [release process](docs/maintainers/releasing.md) before tagging or
publishing. No current real-host PASS or registry availability is implied here.
