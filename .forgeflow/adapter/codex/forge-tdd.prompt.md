# ForgeFlow TDD Launcher — Codex

Read completely, in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/tdd.md`

On Handoff Entry, validate the incoming handoff with the Transition Resolution
Procedure. Then execute only the TDD contract and exact Slice Target Scope, and
preserve every upstream artifact.
Without an incoming Canonical Handoff, proceed only when a Rule 3 Recovery Entry
selects TDD at that exact Slice scope; otherwise perform no productive work.
If this invocation emits a handoff, the final response MUST end with exactly one
validated Canonical Handoff Block from the Handoff Protocol; do not rename,
reorder, omit, or add rows, and add no content after the block.
