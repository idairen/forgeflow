---
name: forge-slice
description: "Execute the ForgeFlow Slice workflow for one authorized Feature scope through Codex."
argument-hint: "Provide decomposition context for the authorized Feature"
---

# ForgeFlow Slice Launcher — Codex

Execute only ForgeFlow `Slice` at one authorized Feature; do not substitute generic delivery decomposition.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/slice.md`

These files are authoritative; this launcher adds no rule.
Validate entry and Scope through Transition and every block through Handoff.
Invocation input may provide context or answers, never override ownership, graph evidence,
entry, Workflow, Scope, or transition result.

Handoff Entry uses the persisted file defined by the Handoff Protocol. Discover or
validate that file against the fresh graph; never require prior chat context. On
completion publish the file and link it in the response, then stop.
