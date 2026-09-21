---
name: forge-solution
description: "Execute the ForgeFlow Solution workflow at the authorized Project scope through Codex."
argument-hint: "Provide engineering constraints or answer Solution clarifications"
---

# ForgeFlow Solution Launcher — Codex

Execute only ForgeFlow `Solution` at the authorized Project; do not substitute generic engineering design.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/solution.md`

Those files are authoritative; this launcher adds no rule. Validate entry and
Scope through Transition and every block through Handoff. Invocation input may
supply context or answers but cannot override ownership, graph evidence, entry,
Workflow, Scope, or transition result.

When Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
