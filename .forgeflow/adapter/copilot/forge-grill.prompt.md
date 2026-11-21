---
name: forge-grill
agent: agent
description: "Execute one authorized ForgeFlow Grill Feature Lane."
argument-hint: "Provide Feature: F-<FeatureNumber> and business context, or answer that Lane's clarifications"
---

# ForgeFlow Grill Launcher — Copilot

Execute only ForgeFlow `Grill` at one authorized Feature Lane; do not substitute generic requirements analysis.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/grill.md`

These files are authoritative; this launcher adds no rule.
Validate entry and Scope through Transition; atomically claim Lane Entry when used;
validate every block through Handoff.
Invocation input may provide context or answers, never override ownership, graph evidence,
entry, Workflow, Scope, or transition result.

Handoff Entry uses the persisted file defined by the Handoff Protocol. Discover or
validate that file against the fresh graph; never require prior chat context. On
completion publish the file and link it in the response, then stop.
