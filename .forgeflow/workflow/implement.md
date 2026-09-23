# Implement Workflow

Version: 2.13

## Contract

| Field | Value |
| --- | --- |
| Scope | Slice |
| Owns | Implement Record; one Slice's authorized changes, verification execution, and evidence |
| Inputs | valid Handoff or Recovery; current Requirement, Solution, and Slice Plan |

Accept only a valid Handoff or Recovery selected from current
`IMPLEMENTATION_GAP`. Before changing implementation files:

1. validate Transition/Handoff and freeze one
   `Slice: F-<FeatureNumber>/S-<SliceNumber>`;
2. require `DELIVERY_READY` and the complete current version chain;
3. resolve the Slice in its current Slice Plan and reject stale or wider work;
4. inspect applicable implementation and repository instructions;
5. map every changed source, test, configuration, migration, or documentation path
   to authorized Slice placement and applicable Solution structures;
6. resolve the Slice Verification Plan and Solution verification requirements;
   select strategies only within them and record rationale/obligation mappings.
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
   awaits Review and cannot be restarted as implementation, except when its Attempt
   is occupied by a valid invalid-Review history pair and fresh Transition selects
   Implement under the Artifact Protocol allocation rule.

Implement may choose filenames from approved patterns and conventions, not a new module,
layer, responsibility, or test topology. It may refine test cases, commands, and
parameters and add supplementary verification within approved constraints. It may
select an explicitly permitted alternative, but cannot waive mandatory checks,
lower thresholds, or use a rationale to approve a weaker strategy. TDD is one
strategy, not this Workflow's universal execution order. Completing the Slice
authorizes neither Review nor another Slice in this execution.

## Strategy selection

A strategy determines the execution pattern and evidence; a method organizes the
authorized edits. Neither changes upstream ownership or authorizes Review PASS/FAIL.
Implement makes routine choices from approved contracts and repository evidence,
without asking the user to select strategy names or approve an implementation method.
Missing business decisions return to Grill (or Plan for project scope); missing
engineering policy returns to Solution; missing Slice mapping returns to Slice.
Actual required human acceptance remains a separate evidence obligation.

Before the entry allocation/persistence step:

1. Collect this Slice's acceptance conditions, Solution verification obligations,
   Slice Verification Plan, mandatory strategies/checks, passing criteria, required
   evidence sources, and permitted alternatives. Do not invent missing obligations.
2. Inspect relevant existing behavior, tests, authorized paths, and available
   environment. Identify change types and any pre-change evidence that must be
   captured before edits. Repository facts guide execution, not new requirements.
3. Retain every mandatory strategy and check. Select an explicitly permitted
   alternative only when its stated condition holds, recording the condition and
   supporting evidence in the selection rationale. Candidate guidance below may
   guide that choice or supplementary verification; it never grants an alternative
   absent from the approved plan. A legacy or incomplete plan gains no waiver.
4. Check coverage obligation by obligation: each required property has concrete
   checks, unchanged passing criteria, and the required evidence source. Combine
   strategies where needed; neither one successful strategy nor a method discharges
   another obligation. Do not add irrelevant checks just to use more strategies.
5. Record strategies, rationale and governing obligations in Verification Selection;
   list concrete checks in Verification Evidence as NOT_RUN until executed. Use the
   existing tables, not a new decision Artifact. Unresolved selection follows the
   existing BLOCKED allocation and RETURN rules without code changes.

The following are candidates only, subject to step 3. Apply all relevant rows rather
than selecting one row for the whole Slice:

| Change or obligation | Candidate strategies and selection evidence |
| --- | --- |
| New or changed executable behavior | TDD when a meaningful behavior-related failing test can be established before edits with a practical feedback cycle. BEHAVIORAL_TEST when permitted and tests are built during/after implementation; record why and preserve the same required behavioral coverage. |
| Existing behavior without reliable coverage | CHARACTERIZATION_TEST captures the relevant baseline before modification; TDD or BEHAVIORAL_TEST verifies approved changed behavior. Existing behavior alone is not an acceptance policy. |
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
problem or persist its blocker; changes to requirements return to their owner.

## Implementation methods

After inspecting the code, Implement may choose or combine the following methods
within the current Slice. These are guidance, not a required enumeration:

| Method | When it fits and its boundary |
| --- | --- |
| Direct implementation | A clear, bounded change within approved structures and responsibilities. |
| Reproduce then repair | A reproducible deviation from an existing contract; reproduce, locate the cause, repair, and verify regressions without redefining expected behavior. |
| Behavior-preserving refactoring | Internal restructuring authorized by this Slice; preserve required behavior and approved module responsibilities/dependencies. |
| Small changes with frequent verification | Changes benefit from short feedback cycles; these are execution steps, not new Slices or additional delivery authority. |
| Minimal-diff repair | A localized issue can be fixed within a narrow change; small size never excuses an unresolved blocking issue. |
| Mechanical transformation | Repeated edits follow an explicit rule within authorized paths; inspect and verify transformed output, including generated changes. |

If used, record the method and reason briefly in Implementation Summary. Methods may
change within the frozen Attempt as inspection reveals better local execution steps;
update that prose when material, while preserving selected verification obligations
and pre-change evidence. A method change creates no new Attempt or approval gate.
Changes to business behavior, architecture/interfaces/data policy, delivery boundaries,
or passing criteria outside the approved contracts require RETURN to their owner.

## Review-ready gate

Apply the Framework review gate before READY_FOR_REVIEW. Trace every Requirement and
Slice condition through Solution to implementation, tests, and evidence; inspect
scope, regressions, security, maintainability risk, placement, and required checks.
Correct local blockers and return business, engineering, or decomposition gaps to
their owners. Every required strategy/check must have adequate current evidence
meeting its passing criteria. Record coverage, commands/procedures, results, and
residual non-blocking risk. Distinguish tool execution, human acceptance, and model
assessment under the Artifact Protocol; never invent executed checks or approval.
Required NOT_RUN or INCONCLUSIVE results prevent READY_FOR_REVIEW. This self-check
is not a Review decision, and a successful irrelevant command cannot satisfy it.

## Process

All commands follow the Framework command lifecycle.

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
   A failed check or missing environment is not permission to switch to a weaker
   strategy. Correct local failures; otherwise persist the appropriate blocker.
5. Record Implementation Summary, Verification Selection, Verification Evidence,
   changed files, File Placement Conformance, Open Issues, shared components,
   implemented decisions, and deviations with owner/resolution. Multiple strategies
   or rerunning checks do not create another Attempt or another Artifact.
6. Perform and record the Review-ready self-check.
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
