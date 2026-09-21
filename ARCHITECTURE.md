# ForgeFlow Architecture

Technical Preview aligned to Framework 3.8 / Artifact 2.19 / Transition 1.8.

## Authority and components

The normative order is [Framework](./.forgeflow/forgeflow.md) →
[Artifact](./.forgeflow/protocol/artifact.md) →
[Transition](./.forgeflow/protocol/transition.md) →
[Handoff](./.forgeflow/protocol/handoff.md) → one Workflow → Adapter.
The core is agent-agnostic by design. Dedicated launchers exist for Codex and Copilot;
other participants use the generic Markdown contracts. Integration claims require
real IDE acceptance. A Handoff does not make an Artifact true.

`ArtifactParser` loads canonical paths, metadata, verification tables and bounded
history evidence. `StateResolver` derives barriers, Grill eligibility, blockers,
Rule 1–11 and exact ordered Handoff projections. `HandoffParser` renders/parses the
four canonical message variants. `ForgeRunner` validates each invocation, launches
one agent process, checks its result against fresh graph evidence, and records
non-authoritative diagnostics. `ProjectKnowledgeBuilder` and `ProjectImpactAnalyzer`
render disposable views. Neither a view nor runtime history authorizes progression.

## Flow and concurrency

Plan → dependency-ready Grill Lanes → all Requirements READY → Solution → every
Feature's Slice Plan READY → declared-order Implement/Review → Project Complete.
The barriers are BUSINESS_READY, ENGINEERING_READY, DELIVERY_READY and PROJECT_COMPLETE.
Only Grill uses parallel Lanes. A Lane Record is coordination evidence with ACTIVE
or COMPLETE status, an Attempt, version references and Claim Evidence. Planning
business dependencies determine eligibility. Shared engineering components remain
Solution decisions; the former delivery-lane READ/WRITE scheduler is retired.

Active claims fence Plan mutations. Interrupted execution is not reclaimed on a
timeout. Explicit inactivity confirmation and protected conditional transactions
are required by the core. The Python runner observes and routes claims; participants
remain responsible for the core's atomic publication/recovery requirements. It does
not provide an OS-independent multi-file transaction engine or launch parallel
agent processes. Single-workflow commands and the auto orchestrator stop at waits.

## Implement and evidence

Implement owns one Slice and freezes one Attempt/version chain before code edits.
Solution owns obligations and criteria; Slice maps them; Implement chooses only
approved alternatives or supplementary checks. Ten strategy identifiers are shared
with the Markdown contract. Method prose is optional and grants no authority.
TOOL_EXECUTION, HUMAN_ACCEPTANCE and MODEL_ASSESSMENT are distinct evidence sources.
Required checks with missing/pending evidence cannot authorize Review. The CLI checks
recorded fields and obligation mappings; it cannot establish whether execution
claims are truthful or whether coverage is semantically sufficient. Review remains
independent and owns immutable PASS/FAIL.

Counter reads are bounded to the current Feature/Slice, including legacy TDD history
and invalid-Review receipt pairs. SHA256/identity validation prevents disposed
attempts from becoming reviewable again. Explicit recovery is maintenance, not a
seventh Workflow. The CLI diagnoses and routes; it does not automatically dispose
project evidence.

## Compatibility and boundaries

Feature contract and engineering versions preserve compatible downstream evidence.
A historical Solution baseline is accepted as stale only with supporting Planning
and referenced Requirement history. It cannot establish engineering readiness.
The CLI conservatively routes legacy prose-only verification plans to Slice for a
structured revision; it does not claim general natural-language theorem proving.

`forge init --force` refreshes packaged contracts and removes known retired TDD
launchers while retaining artifacts/reports/history. There is currently no separate
`update` command. Active TDD evidence requires explicit migration, never aliasing.

Runtime state under `.forgeflow/runtime/` is not part of the active Artifact Graph.
History and supplemental reports cannot establish completion. Current-version IDE
acceptance is stored separately from historical evidence. Python/npm packages ship
the same canonical framework, and npm remains installer-only.

See [release process](docs/maintainers/releasing.md) and
[migration notes](docs/maintainers/implement-migration.md). Historical comparisons
and slide decks remain context, not current behavior specifications.
