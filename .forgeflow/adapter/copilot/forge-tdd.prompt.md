# ForgeFlow TDD Launcher — Copilot

Read `.forgeflow/forgeflow.md`, `.forgeflow/protocol/artifact.md`,
`.forgeflow/protocol/handoff.md`, then
`.forgeflow/workflow/tdd.md`. On Handoff Entry, validate the handoff with the
Transition Resolution Procedure. Execute only the exact Slice Target Scope and
preserve all upstream artifacts. Apply the Framework Command execution policy: in an IDE, reuse the
current terminal tab or equivalent session for sequential commands, do not open a
new tab merely for the next command, and stop every process started by TDD before
handoff.
Without an incoming Canonical Handoff, proceed only when a Rule 3 Recovery Entry
selects TDD at that exact Slice scope; otherwise perform no productive work.
If this invocation emits a handoff, the final response MUST end with exactly one
validated Canonical Handoff Block from the Handoff Protocol; do not rename,
reorder, omit, or add rows, and add no content after the block.
