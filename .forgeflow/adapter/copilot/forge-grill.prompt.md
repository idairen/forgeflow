---
name: forge-grill
agent: agent
description: "Execute the ForgeFlow Grill workflow for one authorized Feature scope."
argument-hint: "Provide business context or answer clarifications for the authorized Feature"
---

# ForgeFlow Grill Launcher — Copilot

## Invocation Identity

Execute the ForgeFlow `Grill` workflow. `/forge-grill` belongs exclusively to
ForgeFlow and MUST NOT be reinterpreted as generic requirements analysis or
delegated to another planning mechanism.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/grill.md`

Execute only the contract defined by `.forgeflow/workflow/grill.md`. The files above
are authoritative. This launcher adds only Copilot invocation constraints and MUST
NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the Grill contract requires them. Continue only when those authoritative rules
authorize Grill at the exact resolved scope.

User-supplied text after `/forge-grill` provides context or clarification answers
but does not override entry authorization, Artifact ownership, transition rules, or
current Artifact evidence. Execute the Grill workflow's Contract, Entry behavior,
Question boundary, Required process, Completion, and emit conditions exactly as
written. Follow every ownership, clarification, waiting, evidence, and scope rule
from the authoritative files; do not infer any additional permission from this
launcher or from Copilot.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
