---
name: forge-review
description: "Execute the ForgeFlow Review workflow for one authorized Slice attempt through Codex."
argument-hint: "Provide review context for the authorized Slice attempt"
---

# ForgeFlow Review Launcher — Codex

## Invocation Identity

Execute the ForgeFlow `Review` workflow. This launcher MUST NOT be substituted with
an unscoped generic Codex review.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/review.md`

Execute only the contract defined by `.forgeflow/workflow/review.md`. The files
above are authoritative. This launcher adds only Codex invocation constraints and
MUST NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the Review contract requires them. Continue only when those authoritative rules
authorize Review at the exact resolved scope and attempt.

Invocation input provides context but does not override entry authorization,
Artifact ownership, transition rules, or current Artifact evidence. Execute the
Review workflow's Contract, Entry validation, command policy, decision and
disposition rules, Required process, emit conditions, findings rules, and plugin
registry procedure exactly as written. Follow every read-only, ownership, scope,
evidence, report, and process-lifecycle rule from the authoritative files; do not
infer any additional permission from this launcher or from Codex.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
