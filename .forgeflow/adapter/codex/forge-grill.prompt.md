---
name: forge-grill
description: "Execute one authorized ForgeFlow Grill Feature Lane through Codex."
argument-hint: "Provide Feature: F-<FeatureNumber> and business context, or answer that Lane's clarifications"
---

# ForgeFlow Grill Launcher — Codex

Execute only ForgeFlow `Grill` at one authorized Feature Lane; do not substitute generic requirements analysis.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/grill.md`

Those files are authoritative; this launcher adds no rule. Validate entry and
Scope through Transition, atomically claim Lane Entry when used, and validate every
block through Handoff. Invocation input may
supply context or answers but cannot override ownership, graph evidence, entry,
Workflow, Scope, or transition result.

When Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
