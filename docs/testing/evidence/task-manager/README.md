# Real-project case: offline task manager

Inspected 2026-09-22 from the maintainer-provided project. The maintainer reports a
successful real IDE run. This directory preserves sanitized excerpts and a
[content manifest](manifest.json), not synthetic PASS reports or a new execution.
The original workspace was read only; application tests were not rerun there.

## Host confirmed by the maintainer

| Field | Value | Attribution |
| --- | --- | --- |
| IDE / client | IntelliJ IDEA 2026.2.1 | Explicit maintainer confirmation |
| Adapter | Codex | Explicit maintainer confirmation |
| Model | `gpt-6-astra` | Explicit maintainer confirmation |
| Project evidence | `.forgeflow/artifacts/` in the supplied task-manager workspace | Maintainer-provided location; inspected read-only |
| Extension / CLI version | Not supplied | Not inferred from adapter files |
| Host OS version | Not supplied | Browser executable paths do not establish the exact version |

## Baseline and scope

The source framework working tree identifies Framework **3.7**, Artifact **2.18**,
Transition **1.8**, Handoff **2.15**, Implement **2.12**. The release checkout uses
Framework 3.8 / Artifact 2.19 / Implement 2.13. Transition and Handoff bytes match;
the three revised contracts do not. The nested framework Git HEAD is recorded in
the manifest, but its working-tree content hashes are the inspected baseline.
The application root has no Git repository identifying one application commit.

The project has two Features, each with three Slices. Current F-01 records pair
S-01 Attempt 7, S-02 Attempt 5 and S-03 Attempt 6 with PASS under Feature engineering
version 1.3 and Slice Plan 1.6. This supports a recorded Feature delivery chain.
F-02 contains later BLOCKED/stale implementation evidence and Slice Plan revisions;
the inspected snapshot does not demonstrate current whole-project COMPLETE.

## Observed scenarios

| Scenario | Evidence and supported conclusion |
| --- | --- |
| Plan through Review | Planning, two Requirements, Solution, two Slice Plans, Implement and Review records exist; the manifest identifies 33 canonical-path files and their hashes |
| Independent FAIL → rework → PASS | F-01/S-03 Attempt 5 records PERF-001 and returns to Implement; Attempt 6 records removal of the query loop and independent probe results, then PASS |
| Verification execution | Attempt 6 Review records 52 tests, typecheck and query probe executed during Review; it separately states that 12 browser results/build evidence were inspected, not rerun by Review |
| Strategy gap returns upstream | F-02/S-01 Attempt 5 persists BLOCKED / ENGINEERING_GAP with Strategies NONE instead of fabricating RED or waiving mandatory TDD |
| Invalid Review recovery | F-01/S-01 Attempt 4 original/receipt pair exists; SHA256 matches and canonical source is absent. The dated record describes explicit authorization and preservation |
| Current release CLI compatibility | A read-only parse of this older snapshot returns HALTED with 16 diagnostics. These are retained in the manifest, not silently fixed or suppressed |

Read the original-source excerpts:

- [FAIL, F-01/S-03 Attempt 5](review-feature-01-slice-03-attempt-05.excerpt.md)
- [PASS after rework, Attempt 6](review-feature-01-slice-03-attempt-06.excerpt.md)
- [Unresolved strategy selection](implement-feature-02-slice-01.excerpt.md)
- [Explicit invalid-Review disposition](2026-09-13-f01-s01-review-recovery.excerpt.md)

These records document the decisions made in that run; this audit does not
independently re-adjudicate the substantive Review findings. For example, the
recorded plugin violation is historical evidence, not a new rule declaring every
query loop blocking regardless of the Framework gate.

## Compatibility findings and limits

Current CLI diagnostics include Feature/Slice identifier metadata shape, File
Placement Conformance headers and RED/GREEN evidence representation. A historical
RED row recorded as SUCCEEDED is not accepted as FAILED RED by the current parser.
This comparison identifies concrete migration/parser compatibility work; it does
not prove that the original IDE execution did not happen. No project Artifact or
framework contract was changed to make the diagnostic pass.

The recovery record explicitly says rollback/fault injection was not exercised and
advisory locks require cooperating writers. Successful disposition plus a matching
digest does not prove every crash or competing-writer scenario.

The maintainer explicitly identifies IntelliJ IDEA 2026.2.1, the Codex adapter and
`gpt-6-astra` as the environment for this project. This confirmation supplies the
host attribution missing from the retained project files. The exact extension/CLI
build and host OS version remain unspecified. macOS application paths in browser
commands do not establish those versions. Presence of the Copilot adapter does not
show that Copilot executed this case.

Candidate acceptance mappings are IDE-REV-101/102, IDE-TDD-103/104 and IDE-HIS-101,
subject to the exact case assertions, host metadata and baseline review. Do not
mark the entire current suite PASS from this case, assume Copilot parity, infer
concurrent Lane coverage from COMPLETE Lane records, or claim current terminal
completion. Current release-gate records remain separate from this historical case.

## Provenance

Each excerpt lists its original relative path, line range and SHA256. Absolute
local paths are redacted; the manifest separately hashes the resulting excerpt.
Original artifacts remain in the maintainer's project. This publication bundle is
a curated subset, not a byte-for-byte full project archive, test-output archive or
complete host conversation. Additional public evidence should be reviewed for
secrets and linked here before making broader claims.
