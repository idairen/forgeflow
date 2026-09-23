---
name: forge-plan
description: "Execute the ForgeFlow Plan workflow through Codex without substituting a generic implementation plan."
argument-hint: "Describe the project intent or an explicitly confirmed same-project increment"
---

# ForgeFlow Plan Launcher — Codex

Execute only ForgeFlow `Plan` at Project; do not substitute generic project planning or Codex's native planning mechanism.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/plan.md`

Those files are authoritative; this launcher adds no rule. Validate entry and
Scope through Transition and every block through Handoff. Invocation input may
supply context or answers but cannot override ownership, graph evidence, entry,
Workflow, Scope, or transition result.

When Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
