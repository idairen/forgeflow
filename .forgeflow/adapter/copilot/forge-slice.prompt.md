---
name: forge-slice
agent: agent
description: "Execute the ForgeFlow Slice workflow for one authorized Feature scope."
argument-hint: "Provide decomposition context for the authorized Feature"
---

# ForgeFlow Slice Launcher — Copilot

## Invocation Identity

Execute the ForgeFlow `Slice` workflow. `/forge-slice` belongs exclusively to
ForgeFlow and MUST NOT be substituted with a generic Copilot task or implementation
plan.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/slice.md`

Execute only the contract defined by `.forgeflow/workflow/slice.md`. The files above
are authoritative. This launcher adds only Copilot invocation constraints and MUST
NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the Slice contract requires them. Continue only when those authoritative rules
authorize Slice at the exact resolved scope.

User-supplied text after `/forge-slice` provides context but does not override entry
authorization, Artifact ownership, transition rules, or current Artifact evidence.
Execute the Slice workflow's Contract, READY quality gate, Required process, emit
conditions, and change-impact rules exactly as written. Follow every ownership,
scope, decomposition, traceability, and evidence rule from the authoritative files;
do not infer any additional permission from this launcher or from Copilot.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
