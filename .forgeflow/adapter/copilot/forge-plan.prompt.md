---
name: forge-plan
agent: agent
description: "Execute the ForgeFlow Plan workflow. Never use or delegate to Copilot's native planning mode."
argument-hint: "Describe the project intent or an explicitly confirmed same-project increment"
---

# ForgeFlow Plan Launcher — Copilot

Execute only ForgeFlow `Plan` at Project; do not substitute generic project planning or Copilot's native planning mechanism.

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
