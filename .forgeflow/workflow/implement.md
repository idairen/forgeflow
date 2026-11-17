# Implement Workflow

Version: 2.16

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owns | Implement Record; one Slice's authorized changes, verification execution, and evidence |
| Inputs | valid Handoff or Recovery; current Requirement, Solution, and Slice Plan |

Accept a valid Handoff selected by fresh Transition for this exact Slice:
Rule 10 FORWARD, Rule 3 RETURN for `IMPLEMENTATION_GAP`, or Rule 8 RETURN for
`REVIEW_BLOCKER` whose matching current FAIL names Implement and this Slice as
Return Workflow/Scope. Alternatively, accept no-Handoff Recovery only when Rule 3
selects this Slice's current `IMPLEMENTATION_GAP`.

A Rule 8 Handoff authorizes a new Implement execution directly; do not wait for
Rule 10, re-emit the same RETURN, or relabel the FAIL as `IMPLEMENTATION_GAP`.
Fresh resolution must still select the incoming Workflow/Scope and exact inputs.
Before changing implementation files:

1. validate Transition/Handoff and freeze one
   `Slice: F-<FeatureNumber>/S-<SliceNumber>`;
2. require `DELIVERY_READY` and the complete current version chain;
3. resolve the Slice in its current Slice Plan and reject stale or wider work;
4. inspect applicable implementation and repository instructions;
5. map every changed source, test, configuration, migration, or documentation path
   to authorized Slice placement and applicable Solution structures;
6. apply Strategy selection below to the Slice Verification Plan and Solution
   verification requirements, recording strategies, rationales, and obligations.
   Missing engineering policy returns ENGINEERING_GAP; missing or inadequate Slice
   mapping returns SLICE_VIOLATION. If selection cannot be resolved, prepare that
   blocker and proceed only to the record allocation/persistence step; and
7. apply the Artifact Protocol Implement continuation/allocation table, using bounded
   current and historical counter evidence for this Feature/Slice. Freeze the
   Attempt and exact upstream versions, and persist IN_PROGRESS before code changes.
   For an unresolved selection, persist BLOCKED instead (with Verification Strategies
   NONE when necessary), resolve the upstream RETURN, and stop without implementation.
   Archive and replace prior evidence in one protected transaction when allocating;
   conflict or failure authorizes no implementation. Current READY_FOR_REVIEW
   without Review awaits Review. A matching current FAIL returned by Rule 8 to
   this Implement/Slice permits a new Attempt; archive the prior Implement and
   retain the immutable FAIL. A valid invalid-Review history pair likewise permits
   a new Attempt when fresh Transition selects Implement. Neither case reuses the
   occupied Attempt, edits its Review, or grants another Slice's authority.

Implement may choose filenames within approved patterns/conventions, never new
modules, layers, responsibilities, or test topology.
Within approved constraints, it may refine test cases, commands, and parameters,
add supplementary verification, or select explicitly permitted alternatives;
it cannot waive mandatory checks, lower thresholds, or justify weaker strategies.
TDD is the required default for behavioral changes, with applicability and exceptions
governed upstream; Slice completion authorizes
neither Review nor another Slice in this execution.

## Strategy selection

A strategy defines execution/evidence; a method organizes authorized edits;
neither changes upstream ownership or authorizes Review PASS/FAIL.
Make routine choices from approved contracts and repository evidence without asking
users to select strategies or approve methods; required human acceptance remains a
separate evidence obligation.
Return missing business decisions to Grill (Plan for project scope), engineering
policy to Solution, and Slice mapping to Slice.

Before the entry allocation/persistence step:

1. Collect this Slice's acceptance conditions, Solution verification obligations,
   Slice Verification Plan, mandatory strategies/checks, passing criteria, required
   evidence sources, and permitted alternatives. Do not invent missing obligations.
   Apply Artifact Protocol TDD applicability and exceptions, including for older
   plans. For each new or changed behavior require TDD or a recorded, applicable,
   explicitly user-approved Solution exception. Non-behavioral work needs a concrete
   non-applicability rationale. Missing policy returns ENGINEERING_GAP; inadequate
   mapping returns SLICE_VIOLATION before implementation, using entry persistence.
2. Inspect relevant existing behavior, tests, authorized paths, and available environment;
   identify change types and evidence required before edits.
   Repository facts guide execution, not new requirements.
3. Retain every mandatory strategy and check. Select an explicitly permitted
   alternative only when its stated condition holds, recording the condition and
   supporting evidence in the rationale. Candidate guidance below supports that
   choice or supplementary verification; it never grants an alternative absent from the approved plan.
   Legacy or incomplete plans gain no waiver.
4. Check coverage obligation by obligation: each required property has concrete
   checks, unchanged passing criteria, and the required evidence source.
   Combine strategies as needed; no successful strategy or method discharges another
   obligation, and additional strategies do not justify irrelevant checks.
5. Record strategies, rationale and governing obligations in Verification Selection;
   list concrete checks in Verification Evidence as NOT_RUN until executed. Use the
   existing tables, not a new decision Artifact. Unresolved selection follows the
   existing BLOCKED allocation and RETURN rules without code changes.

Apply all relevant candidate rows under step 3, not one row for the whole Slice:

| Change or obligation | Candidate strategies and selection evidence |
| --- | --- |
| New or changed executable behavior | TDD is required by default: establish meaningful behavioral RED before edits, then GREEN and refactor/regression evidence. BEHAVIORAL_TEST replaces it only for the exact scope/condition of an explicitly user-approved Solution exception; preserve required coverage and evidence. |
| Existing behavior without reliable coverage | CHARACTERIZATION_TEST captures the baseline before modification; preservation/regression checks verify unchanged behavior. Any new or changed behavior still requires TDD or an approved exception. Existing behavior alone is not an acceptance policy. |
| Data/schema migration | MIGRATION_REHEARSAL against the declared data/environment, plus required behavior, integrity and recovery checks. Do not design migration policy here. |
| Configuration, build or startup settings | CONFIGURATION_VALIDATION for parsing and effective behavior; STATIC_VALIDATION supplements it where applicable. Syntax alone cannot establish runtime effect. |
| Performance changes | BENCHMARK with the required comparable baseline, workload and thresholds, while retaining correctness/regression verification. |
| Security-related changes | SECURITY_SCAN where applicable to the obligation, plus required behavioral checks such as access control. A clean scan does not prove those behaviors. |
| Documentation or examples | DOCUMENTATION_VALIDATION; execute examples when required and compare them with the approved contract and actual implementation. |
| Required human acceptance | MANUAL_ACCEPTANCE with the actual designated acceptor's observations/result; never replace it with model assessment. |
| Applicable typing, linting, parsing or build checks | STATIC_VALIDATION alongside any required behavioral evidence. |

Mandatory TDD remains mandatory even when another candidate is more convenient.
A failed check, unavailable environment, or missed pre-change baseline is not
permission to switch to a weaker strategy or manufacture evidence. Correct a local
problem or apply the Verification failure choice below before persisting its
blocker; changes to requirements return to their owner.

## Verification failure choice

When a required check fails, cannot execute, or remains inconclusive after a
bounded routine correction, MUST present the user with a choice in Planning's
communication language. Do not retry indefinitely or silently stop at BLOCKED.
Expected TDD RED followed by normal implementation is not a failure requiring this
choice. Report the exact checks, results, cause, affected obligations, known risk,
and which work can proceed independently. Offer:

1. Repair the problem or provide the missing environment, then retry.
2. Temporarily defer the named checks and continue the permitted work, with an
   explicit retry trigger/checkpoint and the required upstream revision if needed.
3. Pause and retain the blocker.

Allow another user-proposed resolution under the Framework clarification policy.
Wait for an explicit answer before deferring checks; independent already-authorized
work may continue. While waiting, emit no Handoff and grant no future Scope.
An existing recorded answer covering the same checks, versions, and continuation
scope is sufficient; do not ask again merely because a new session starts.

On deferral, persist the Artifact Protocol verification-deferral details in Open
Issues and preserve the actual Verification Evidence results. Continue independent
work in the current Slice as IN_PROGRESS. When an unchanged required gate prevents
further progress, use the recorded decision to request the concrete upstream
revision via BLOCKED/RETURN. Explain that entering later Slices requires that
revision and fresh routing. Never reinterpret user approval as passing evidence,
edit another owner's plans, or claim that a known correctness defect is resolved.
If retry is chosen, execute it and record the actual outcome; if pause is chosen,
persist the appropriate blocker. Revisit an expired deferral at its recorded trigger.

## Implementation methods

After code inspection, Implement may choose or combine methods within the current Slice;
these examples are optional and non-exhaustive:

| Method | When it fits and its boundary |
| --- | --- |
| Direct implementation | A clear, bounded change within approved structures and responsibilities. |
| Reproduce then repair | A reproducible deviation from an existing contract; reproduce, locate the cause, repair, and verify regressions without redefining expected behavior. |
| Behavior-preserving refactoring | Internal restructuring authorized by this Slice; preserve required behavior and approved module responsibilities/dependencies. |
| Small changes with frequent verification | Changes benefit from short feedback cycles; these are execution steps, not new Slices or additional delivery authority. |
| Minimal-diff repair | A localized issue can be fixed within a narrow change; small size never excuses an unresolved blocking issue. |
| Mechanical transformation | Repeated edits follow an explicit rule within authorized paths; inspect and verify transformed output, including generated changes. |

Record any chosen method and reason briefly in Implementation Summary.
Methods may change within the frozen Attempt when inspection reveals better steps;
update material changes in that prose, preserving selected verification obligations
and pre-change evidence. A method change creates no new Attempt or approval gate.
Changes to business behavior, architecture/interfaces/data policy, delivery boundaries,
or passing criteria outside the approved contracts require RETURN to their owner.

## Review-ready gate

Apply the Framework review gate before READY_FOR_REVIEW. Trace every Requirement and
Slice condition through Solution to implementation, tests, and evidence; inspect
scope, regressions, security, maintainability risk, placement, and required checks.
Correct local blockers; return business, engineering, or decomposition gaps to their owners.
Every required strategy/check needs adequate current evidence meeting its passing criteria.
Record coverage, commands/procedures, results, and residual non-blocking risk.
Distinguish tool execution, human acceptance, and model assessment under Artifact
Protocol; never invent executed checks or approval.
Required NOT_RUN or INCONCLUSIVE results prevent READY_FOR_REVIEW. This self-check
is not a Review decision, and a successful irrelevant command cannot satisfy it.

## Process

All commands follow the Framework command lifecycle.
Before every canonical write, including entry allocation, apply the candidate
validation below. A malformed candidate is corrected before publication, not handed
to the next Workflow for repair.

1. Confirm path/obligation mappings and persist the selected strategies and their
   rationales in the single Implement Record for the frozen Attempt.
2. Execute any required pre-change evidence steps. For TDD, run a relevant test and
   capture genuine behavior-related RED; for CHARACTERIZATION_TEST capture existing
   behavior; for BENCHMARK capture a comparable baseline. Other strategies follow
   their own declared pattern and never manufacture a RED phase.
3. Implement only the authorized changes. With TDD, implement minimum behavior for
   GREEN, refactor as needed, and rerun relevant verification. For other strategies,
   follow their declared implementation/verification sequence.
4. Execute every required check across all selected strategies, including behavioral
   regression, migration, build/startup, or human acceptance requirements when
   applicable. Preserve actual outputs/observations, environment, target, and results.
   Follow the Strategy selection restrictions on switching; correct local failures,
   otherwise apply Verification failure choice and record the user's decision
   before continuing permitted work or persisting the appropriate blocker.
5. Record Implementation Summary, Verification Selection, Verification Evidence,
   changed files, File Placement Conformance, Open Issues, shared components,
   implemented decisions, and deviations with owner/resolution. Multiple strategies
   or rerunning checks do not create another Attempt or another Artifact.
6. Perform and record the Review-ready self-check and validate the complete candidate.
7. Recheck the canonical record against the Attempt and upstream versions frozen at
   entry. Never allocate another Attempt at this step. If the record was replaced
   or the version chain changed, stop without overwriting evidence; any further
   implementation requires a fresh authorized entry.
8. Persist canonical READY_FOR_REVIEW Implement Record only after the full gate
   passes. While required work remains, retain IN_PROGRESS or persist BLOCKED with
   its owner/Scope; do not defer mandatory verification to Review.
9. Resolve Transition. READY_FOR_REVIEW normally forwards to Review; upstream RETURN,
   blocker waiting, and graph HALTED follow the same protocols. Emit any required
   exact Handoff as final response content and stop; do not store a parallel Handoff
   inside the Implement Record.

Implement never invents policy, redesigns contracts, changes Slice boundaries, implements
future work, issues Review PASS/FAIL, creates Review Reports, or declares completion.
TERMINAL / COMPLETE requires a matching PASS and therefore is never emitted by Implement.

Absent/ambiguous required engineering structure is `ENGINEERING_GAP`; absent,
overlapping, or inconsistent Planned File Placement is `SLICE_VIOLATION`; local
path, implementation, test, or evidence failure is corrected before READY or
persisted as `IMPLEMENTATION_GAP` when blocked across invocations.

## Candidate validation

Validate the complete candidate Implement Record against the loaded Artifact schema
and frozen direct inputs before publication:

- The first line is its level-one title, followed by exactly one Metadata section
  and its table. No prose or Changed Files/placement tables precede the title.
- Identity, Status, Attempt, upstream versions and required sections match the
  canonical path and frozen entry. Metadata strategy lists match Selection; each
  Selection/Evidence row has exactly one Strategy, and each Evidence row exactly
  one Source and Result. `PASS`/`FAIL` are Review decisions, never execution results.
- Changed Files and File Placement Conformance describe actual changes, including
  build outputs when changed. An unplanned path is a deviation, never automatically
  CONFORMS because it already exists or tests pass.
- Trace each required check to concrete evidence and its passing criteria. A total
  test count, successful suite, or generic coverage claim cannot establish an
  untested scenario. Missing required evidence remains NOT_RUN/INCONCLUSIVE and
  prevents READY_FOR_REVIEW; apply Verification failure choice when appropriate.

This is local candidate validation, not another full-graph scan or test rerun.
Correct formatting without changing observed outcomes, inventing coverage, or
allocating another Attempt. If a previously published record is already malformed,
ordinary execution follows Rule 2; the separately authorized Implement format
recovery procedure is described in `protocol/implement-recovery.md`.
