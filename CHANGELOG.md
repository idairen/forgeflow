# Changelog

Version 0.1.0 is a Technical Preview distributed through a GitHub pre-release.
Package versions remain 0.1.0. The npm installer is now published as
`@dairen/forgeflow`; PyPI publication and current-version real-host acceptance
are not claimed.
This public repository starts from a source snapshot. Earlier private development
history and retired presentation assets are not included.

## [Unreleased]

- Document npm registry installation using `@dairen/forgeflow@0.1.0` and the
  moving `next` preview tag. Earlier GitHub Release attachments remain unchanged.

- Correct the npm package scope to `@dairen/forgeflow` to match the npm publisher.
  GitHub remains `idairen/forgeflow`. Update installer guidance and tarball names;
  the earlier GitHub v0.1.0 attachments retain their original package identity.

## [0.1.0] - 2026-09-23

Initial public Technical Preview. GitHub release assets provide local installation
packages; npm/PyPI registry installation is not claimed.

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
publishing. npm availability does not establish current real-host PASS or PyPI availability.
