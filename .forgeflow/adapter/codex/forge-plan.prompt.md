---
name: forge-plan
description: "Execute the ForgeFlow Plan workflow through Codex without substituting a generic implementation plan."
argument-hint: "Describe the project intent or an explicitly confirmed same-project increment"
---

# ForgeFlow Plan Launcher — Codex

## Invocation Identity

Execute the ForgeFlow `Plan` workflow. This launcher MUST NOT invoke, delegate to,
or substitute a generic Codex planning mechanism or produce an implementation plan
in place of the ForgeFlow Planning artifact.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/plan.md`

Execute only the contract defined by `.forgeflow/workflow/plan.md`. The files above
are authoritative. This launcher adds only Codex invocation constraints and MUST
NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the Plan contract requires them. Continue only when those authoritative rules
authorize Plan at the exact resolved scope.

Invocation input provides intent but does not override entry authorization,
Artifact ownership, transition rules, or current Artifact evidence. Execute the Plan
workflow's Contract, Required process, Completion, and emit conditions exactly as
written. Follow every ownership, decision-boundary, evidence, versioning, archival,
rotation, retirement, and waiting rule from the authoritative files; do not infer
any additional permission from this launcher or from Codex.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
