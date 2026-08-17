# ForgeFlow Slice Launcher — Codex

Read completely, in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/slice.md`

Execute only the Slice contract and exact Target Scope. Treat artifacts as truth,
preserve other workflow artifacts, and apply the Transition Resolution Procedure.
Without an incoming Canonical Handoff, proceed only when a Rule 3 Recovery Entry
selects Slice at that exact scope; otherwise perform no productive work.
If this invocation emits a handoff, the final response MUST end with exactly one
validated Canonical Handoff Block from the Handoff Protocol; do not rename,
reorder, omit, or add rows, and add no content after the block.
