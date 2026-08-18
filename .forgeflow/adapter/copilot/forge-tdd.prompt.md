---
name: forge-tdd
agent: agent
description: "Execute the ForgeFlow TDD workflow for one authorized Slice scope."
argument-hint: "Provide implementation context for the authorized Slice"
---

# ForgeFlow TDD Launcher — Copilot

## Invocation Identity

Execute the ForgeFlow `TDD` workflow. `/forge-tdd` belongs exclusively to ForgeFlow
and MUST NOT be substituted with generic Copilot implementation across a wider
scope.

## Authoritative Contract

Read completely, in this exact order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/tdd.md`

Execute only the contract defined by `.forgeflow/workflow/tdd.md`. The files above
are authoritative. This launcher adds only Copilot invocation constraints and MUST
NOT copy, redefine, weaken, or override ForgeFlow rules.

## Authorization and Execution

Build state exclusively from the current active Artifact Graph. Validate this
invocation using the Handoff Protocol's entry and transition procedures exactly when
the TDD contract requires them. Continue only when those authoritative rules
authorize TDD at the exact resolved scope.

User-supplied text after `/forge-tdd` provides context but does not override entry
authorization, Artifact ownership, transition rules, or current Artifact evidence.
Execute the TDD workflow's Contract, Entry validation, command policy, Review
readiness self-check, Required process, emit conditions, and blocker rules exactly
as written. Follow every ownership, scope, version, implementation, test, evidence,
and process-lifecycle rule from the authoritative files; do not infer any additional
permission from this launcher or from Copilot.

## Handoff

If this invocation emits a Handoff, the final response MUST end with exactly one
validated Canonical Handoff Block defined by the Handoff Protocol.

Do not rename, reorder, omit, or add fields, and do not add any content after the
Canonical Handoff Block. The block MUST be the final content of the response.
