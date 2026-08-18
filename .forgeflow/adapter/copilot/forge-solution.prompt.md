---
name: forge-solution
agent: agent
description: "Execute the ForgeFlow Solution workflow at the authorized Project scope."
argument-hint: "Provide engineering constraints or answer Solution clarifications"
---

# ForgeFlow Solution Launcher — Copilot

## Invocation Identity

Execute the ForgeFlow `Solution` workflow. `/forge-solution` belongs exclusively to
ForgeFlow and MUST NOT be substituted with a generic Copilot implementation plan.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/solution.md`

Execute only the contract defined by `.forgeflow/workflow/solution.md`. The files
above are authoritative. This launcher adds only Copilot invocation constraints and
MUST NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the Solution contract requires them. Continue only when those authoritative rules
authorize Solution at the exact resolved scope.

User-supplied text after `/forge-solution` provides context or clarification answers
but does not override entry authorization, Artifact ownership, transition rules, or
current Artifact evidence. Execute the Solution workflow's Contract, Entry barrier,
engineering-question and clarification rules, READY quality gate, Required process,
emit conditions, and change-impact rules exactly as written. Do not infer any
additional permission from this launcher or from Copilot.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
