---
name: forge-review
agent: agent
description: "Execute the ForgeFlow Review workflow for one authorized Slice attempt."
argument-hint: "Provide review context for the authorized Slice attempt"
---

# ForgeFlow Review Launcher — Copilot

Execute only ForgeFlow `Review` at one authorized Slice attempt; do not substitute generic review.

Read completely and in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/transition.md`
4. `.forgeflow/protocol/handoff.md`
5. `.forgeflow/workflow/review.md`

These files are authoritative; this launcher adds no rule.
Validate entry and Scope through Transition and every block through Handoff.
Invocation input may provide context or answers, never override ownership, graph evidence,
entry, Workflow, Scope, or transition result.

If Handoff is required, render exactly one canonical block as final content
and stop without consuming its target.
