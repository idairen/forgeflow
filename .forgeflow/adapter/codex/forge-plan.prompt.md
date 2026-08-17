# ForgeFlow Plan Launcher — Codex

Read completely, in order:

1. `.forgeflow/forgeflow.md`
2. `.forgeflow/protocol/artifact.md`
3. `.forgeflow/protocol/handoff.md`
4. `.forgeflow/workflow/plan.md`

Execute only the Plan contract. Treat artifacts as truth, preserve other workflow
artifacts except for an explicitly authorized Feature retirement transaction,
validate before writing, and apply the Transition Resolution Procedure.
Without an incoming Canonical Handoff, proceed only when Bootstrap Entry,
Incremental Intent Entry, or a Rule 3 Recovery Entry selects Plan at Project scope;
otherwise perform no productive work. Incremental Intent Entry preserves Artifacts
and Reports, including both history roots, and never infers a reset from similarity.
If this invocation emits a handoff, the final response MUST end with exactly one
validated Canonical Handoff Block from the Handoff Protocol; do not rename,
reorder, omit, or add rows, and add no content after the block.
