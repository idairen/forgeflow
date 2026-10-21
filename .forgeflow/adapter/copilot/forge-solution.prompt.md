---
name: forge-solution
agent: agent
description: "Execute the ForgeFlow Solution workflow at the authorized Project scope."
argument-hint: "Provide engineering constraints or answer Solution clarifications"
---

# ForgeFlow Solution Launcher — Copilot

Execute only ForgeFlow `Solution` at the authorized Project; do not substitute generic engineering design.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/solution.md`

These files are authoritative; this launcher adds no rule.
Validate entry and Scope through Transition and every block through Handoff.
Invocation input may provide context or answers, never override ownership, graph evidence,
entry, Workflow, Scope, or transition result.

If Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
