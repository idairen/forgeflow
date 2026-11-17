# Invalid Implement format recovery

Version: 1.0

## Scope and authorization

Load this optional procedure only for an explicit request to repair the format of
one canonical Implement Record, after Framework, Artifact, Transition and Handoff.
It is maintenance, not Implement Entry, a seventh Workflow, or permission to change
code, tests, upstream contracts, Review Reports, or substantive verification policy.
Framework development authorization does not authorize repairing project Artifacts.

Prepare the concrete repair before requesting approval: source path and digest,
observed format errors, exact original-preservation path, proposed changes and
expected routing. Reuse explicit user authorization covering those operations.
Without it, report the diagnosis and proposed repair without changing Artifacts.

## Eligibility and candidate

1. Read the complete canonical file and reproduce a structural error against the
   current Artifact schema. A valid record with a failed or unexecuted check is not
   eligible merely because progress is blocked.
2. Recover one unambiguous Feature, Slice, Attempt, Artifact Version and upstream
   version chain from the source and direct Artifacts. All occurrences must agree
   and the path must match. Do not guess missing identity or versions. An affected
   execution must have stopped, confirmed by the user or observable host evidence;
   timeout is insufficient.
3. Freeze the source bytes, direct upstream inputs and any Review for this Attempt.
   A matching PASS is not eligible: changing its reviewed input requires a separate
   evidence-preserving disposition. With a matching FAIL, preserve that report and
   its disposition; formatting repair never resolves its findings. An invalid or
   mismatched Review requires separate diagnosis, not silent deletion.
4. Build a complete corrected candidate without touching the canonical path. Allowed
   changes are title/section placement, unambiguous labels, splitting combined
   Strategy/Source rows, and recording actual changed paths and their conformance.
   A mistaken Result label can be corrected only from retrievable actual execution
   evidence; `PASS` is not proof of SUCCEEDED. Preserve commands, outputs, known
   failures, missing coverage, deviations and human-acceptance limits.
5. Preserve Feature/Slice, Attempt, Artifact Version and upstream references. Never
   upgrade Status. With a current FAIL, preserve Status as well so its existing
   route remains effective. With no Review, an unsupported READY_FOR_REVIEW may be
   lowered to IN_PROGRESS or BLOCKED, with actual pending evidence or the required
   blocker fields. Do not invent a blocker merely to obtain an Entry.
6. Apply Implement candidate validation using the loaded Artifact schema, including
   complete required-check coverage for READY_FOR_REVIEW. If a valid candidate
   cannot be established within this scope, explain the remaining defect and stop
   without changing the original. Missing execution evidence cannot be fabricated.

## Preserve and replace

Use Artifact Protocol's `history/invalid-implement/<SHA256>/<canonical-implement-filename>`
destination. Keep the original byte-for-byte; record its path/digest, authorization
and corrections under the candidate's Open Issues. Do not occupy the standard
Attempt archive with this malformed snapshot. A conflicting standard archive is
outside this repair's authority and must be reconciled separately before proceeding.

Protect source, destination and frozen inputs against competing writes using the
host's exclusion and conditional mutation. Require regular non-symlink paths and
parents; recheck source digest and frozen inputs before replacement. Verify the
preserved original before atomically installing the validated candidate. If the
host cannot protect this boundary, report the limitation without changing canonical
evidence. On failure keep or restore the exact source; preserve any verified original.
If restoration fails, report retained paths and HALT rather than claim completion.

An interrupted operation with the same source and verified original may resume
under the same authorization. If the canonical file already equals the approved
candidate and its original matches the digest, the repair is an idempotent no-op.
A changed canonical file is re-diagnosed; never overwrite newer execution evidence.

## Exit

Rebuild the graph and resolve ordinary Transition rules. Other invalid Artifacts
still cause HALTED. Emit any canonical routing result with Source Scope Project
as maintenance with no emitting Workflow, then stop without consuming it.
This procedure grants no PASS or completion and allocates no Attempt.

A remaining current FAIL still returns to its recorded owner through Rule 8.
Only a fresh authorized Implement execution can allocate the next Attempt. It
archives the corrected canonical record at the standard Attempt history path,
preserves all Review reports, and performs required verification. Diagnostic
originals never replace the current record or contribute extra consumed Attempts.
