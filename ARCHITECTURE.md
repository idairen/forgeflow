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

## Terms used in the workflow

| Term | Meaning |
| --- | --- |
| Feature | A declared business outcome with a stable identity in Planning. |
| Slice | A delivery unit within a Feature, defined by its Slice Plan. |
| Artifact | A canonical persisted record whose validity, versions and currentness are checked against the graph. |
| Handoff | The final routing message for a new invocation; it is not proof that its referenced evidence is valid. |
| Lane | A claimed Grill execution scope for one eligible Feature, not an Implement delivery lane. |
| Attempt | An execution identity used with version references to distinguish current work from retries and history. |
| Barrier | A readiness condition over the relevant complete set, such as all Requirements READY before Solution. |
| Strategy / method | A verification approach with evidence obligations / optional guidance for organizing authorized implementation. |

These are introductory summaries. Exact definitions and validity rules remain in
the normative contracts; this glossary introduces no new state or field.

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

## Strategy and method selection

The [Implement workflow](.forgeflow/workflow/implement.md) owns the selection
procedure. Solution defines obligations, passing criteria and evidence sources;
Slice maps them to each delivery unit. Implement inspects local behavior, tests,
authorized paths and environment, retains mandatory checks, and selects an
alternative only when an approved condition is met. It records the obligation
mapping before implementation. Missing engineering policy returns to Solution;
missing Slice mapping returns to Slice. Routine execution choices do not require
users to choose strategy names.

Strategies can be combined; passing one check never discharges another required
obligation. TDD requires genuine pre-change behavioral RED. BEHAVIORAL_TEST does
not claim historical RED. Characterization and benchmarks retain required baselines;
manual acceptance requires the actual acceptor's result. The full supported list
and evidence schema live in the [Artifact Protocol](.forgeflow/protocol/artifact.md).

Methods such as direct implementation, reproduce-then-repair, behavior-preserving
refactoring, small changes with frequent verification, minimal-diff repair and
mechanical transformation organize authorized changes. They are optional summary
prose, may be combined, and create no new Artifact, Attempt or approval gate.
They cannot change business policy, engineering contracts or Slice boundaries.

## Entry and recovery

Transition defines five entries: Bootstrap, Subsequent Plan, Handoff, Lane and
Recovery. Review accepts only Handoff. Missing/invalid Handoff permits read-only
routing correction when no valid alternative entry applies; it authorizes no
implementation or artifact repair. A receiver validates the complete fresh graph
and exact ordered input projection. Emitting a Handoff ends the invocation.

Invalid-Review recovery is separately authorized maintenance. Only an eligible
format defect may be disposed of through protected preservation of original bytes
and a SHA256 receipt. Known blocking dispositions and valid PASS/FAIL reports are
not eligible. The old Attempt remains occupied; later Implement and Review require
fresh entry and evidence. See the optional
[recovery procedure](.forgeflow/protocol/review-recovery.md), loaded only on request.

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
[migration notes](docs/maintainers/implement-migration.md). The Markdown contracts
define behavior; this explanation does not create additional authority.
