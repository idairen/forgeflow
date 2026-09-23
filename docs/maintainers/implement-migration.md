# Implement migration and release notes

This change targets the current `.forgeflow` contracts. Distribution version numbers
remain unchanged until a maintainer selects and tags the release; changes are Unreleased.

## Breaking behavior

- The workflow/owner is Implement, not TDD. `forge implement` and `forge-implement`
  replace the retired launcher. TDD remains a verification strategy only.
- Implementation filenames and knowledge JSON keys use `implement`. External
  consumers of the old `tdd` key must update; there is no silent compatibility alias.
- Sequence numbers permit 100 and above and reject alternate padding and zero.
- Only Grill uses parallel Feature Lanes. Every Feature needs a current usable
  Slice Plan before Implement; delivery follows declared Feature/Slice order.
- The Handoff input list must equal the resolver's full ordered projection; a
  valid subset, reordered list or unrelated extra file is rejected.
- Implement records require strategy selection, rationale and source-specific
  evidence. Strategy/method guidance does not waive mandatory upstream checks.

## Refresh versus evidence migration

Back up and review your project before choosing `forge init --force`. Both installers
refresh managed framework files and remove `workflow/tdd.md` and the two retired
`forge-tdd.prompt.md` launchers. They leave artifacts, reports and history unchanged.

Active `tdd-feature-…` records and routing fields naming TDD cause HALTED. Follow the
Artifact Protocol's separately authorized, evidence-preserving legacy migration;
archive affected evidence to its defined destinations, preserve consumed Attempts,
and resolve the new graph. Initialization is not evidence migration permission.
Do not fabricate Implement records, carry forward old PASS, or delete blockers.

Invalid Review recovery is likewise explicit maintenance. The optional core procedure
preserves original bytes plus a SHA256 receipt and permanently occupies the Attempt.
CLI routing checks the receipt and selects a new Implement attempt when applicable;
it never archives a Review merely because `forge review` was invoked.

## Validation limits

The CLI is an automation of structural graph rules, not a replacement for semantic
contract evaluation. Independent Review evaluates actual output, coverage, conditional
alternatives, applicability and correctness. Legacy prose-only Slice verification
plans are conservatively routed for structured revision rather than guessed.

The participant must provide the protected mutation/exclusion required by Lane,
Implement and recovery transactions. The runner does not implement a portable
multi-file transaction service. If execution exposes a contract conflict, preserve the evidence and report it;
migration guidance does not authorize weakening the higher-precedence contract.

Historical IDE results are not current conformance evidence. Current
acceptance uses `tests/acceptance/ide/results/current/`; release-gate stays blocked
until real current-version P0 evidence exists. No registry upload, Git tag or GitHub
release is part of local preparation.
