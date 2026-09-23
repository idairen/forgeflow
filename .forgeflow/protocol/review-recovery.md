# Invalid Review recovery

Version: 1.0

## Scope and entry

This optional maintenance procedure is loaded only for an explicit request to
recover an invalid Review, after Framework, Artifact, Transition and Handoff.
It is not a Review Entry, a seventh Workflow, or permission to modify implementation.
Ordinary forge-review/forge-implement calls only diagnose and route under Transition.
Framework maintenance authorization does not authorize disposition of project Artifacts.

Diagnose one exact canonical Review path and prepare the concrete disposition before
requesting authorization: source, digest, original/receipt destinations, identity,
occupied Attempt, observed defect and expected version/counter consequences. Reuse
explicit authorization already covering those exact operations; do not ask again.
Without such authorization, report the plan and stop without changing Artifacts.

## Eligibility

For a repeated request, first check the completed-pair or interrupted-transaction
conditions below; source absence alone cannot authorize a new disposition.

1. The source is a regular non-symlink file at a canonical Review path, with a
   reproducible local format defect under the Artifact Protocol (Metadata or Findings
   shape, labels or missing required fields). Merely stale evidence is not eligible.
2. Its filename uniquely identifies an active Feature/Slice and the Attempt of a
   structurally valid canonical Implement. The Implement's version chain may be
   stale; recovery does not make it current. Any readable identity/Attempt fields
   in the source must agree; ambiguous or contradictory identity is not repaired.
3. There is no declared FAIL, positive Blocking Findings count, BLOCKING finding,
   or other known unresolved blocking disposition in that report. Such cases need
   a separate evidence-preserving repair plan; this procedure cannot erase blockers.
   A conforming PASS or FAIL is never eligible, even if the user wants to rerun it.
4. Read the whole source; do not infer missing verification or convert its claimed
   PASS into valid evidence. Other invalid Artifact types and broken references are
   outside this procedure. Existing unrelated graph contradictions may remain;
   removing this one defect does not authorize skipping them.
5. Confirm the affected execution has stopped using explicit user confirmation or
   observable host execution evidence. Silence or timeout is insufficient. Protect
   the source, canonical Implement, and both destination paths against competing
   mutation during disposition; an ACTIVE affected execution is not eligible.

## Protected disposition

Use the original and receipt paths/schema in Artifact Protocol Invalid Review history.
Freeze exact source bytes/digest, canonical Implement bytes, identity and authorization.
Validate the receipt candidate before any active-path change. Both destinations and
their parents must be safe regular paths, not symlinks. Never overwrite a conflicting
file or reuse an occupied name for different evidence.

Under host-provided exclusion and conditional mutation, recheck the frozen source
and Implement, preserve the original bytes at the history path, persist the receipt,
and remove the canonical source as one protected transaction. Verify the original
digest and receipt and source absence before reporting success. No intermediate
state may authorize a Workflow. If the host cannot protect this boundary, stop
with the concrete capability limitation; sequential unprotected writes are insufficient.

On failure restore the original canonical file unchanged and remove only files
created by this transaction, without overwriting another execution's changes. If
rollback is impossible, report retained paths and HALT. An interrupted transaction
may resume only with the same explicit disposition authorization, frozen digest,
and Implement identity, after checking all remaining files under the same protection.
Identical retained bytes may be reused; conflicts or missing trustworthy transaction
evidence require HALT. Never reconstruct a missing original from a prose summary.

An already completed exact original/receipt pair with no canonical source is an
idempotent no-op after validation; do not generate another receipt or change counters.
Validate against the matching archived Implement if that Attempt has since advanced,
using only that exact standard history path. Never revert the newer Implement.

## Exit and subsequent execution

The original and receipt remain immutable. They occupy the old Attempt, provide no
PASS/FAIL or completion evidence, and must not be restored as a new canonical Review
at that Attempt. Do not edit Implement, upstream plans, source, tests or plugin reports.

Rebuild the current graph and use the ordinary Rule precedence and projection.
For a Handoff-producing result emit the canonical block with Source Scope Project
and stop, using the same no-executing-Workflow semantics as read-only routing
correction. A remaining contradiction emits HALTED; report existing no-Handoff
wait/entry conditions without inventing a block. Do not start the selected Workflow.

Only a later valid Implement Entry allocates above all used Attempts, archives the
prior Implement, and performs current required verification. Review subsequently
evaluates that new Attempt independently. Neither this procedure nor an old claimed
PASS authorizes skipping verification or retaining its decision.
