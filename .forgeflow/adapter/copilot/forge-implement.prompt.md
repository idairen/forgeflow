---
name: forge-implement
agent: agent
description: "Execute the ForgeFlow Implement workflow for one authorized Slice scope."
argument-hint: "Provide implementation context for the authorized Slice"
---

# ForgeFlow Implement Launcher — Copilot

Execute only ForgeFlow `Implement` at one authorized Slice; do not substitute generic implementation.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/implement.md`

Those files are authoritative; this launcher adds no rule. Validate entry and
Scope through Transition and every block through Handoff. Invocation input may
supply context or answers but cannot override ownership, graph evidence, entry,
Workflow, Scope, or transition result.

When Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
