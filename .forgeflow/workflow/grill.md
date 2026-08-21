# Grill Workflow

Version: 2.8

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Requirement |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | READY Planning; Target Scope naming one planned Feature |

Grill resolves the complete business contract for exactly one Feature. It may
challenge ambiguity and obtain stakeholder decisions, but it may not invent them.
The incoming Target Scope is the complete authorization boundary for this
execution. Planning may contain other Features, but they are future execution
scopes and MUST NOT be analyzed, questioned, or written during this execution.

## Entry behavior

On Handoff Entry, Grill MUST first execute the Unified Entry Validation Procedure
defined in the Handoff Protocol. Without an incoming handoff, Grill may proceed only
through Recovery Entry when a fresh Rule 3 result selects Grill at the exact Feature
Target Scope from a current BUSINESS_GAP. Once entry is valid, Grill MUST begin the
Required process and MUST NOT emit a handoff to the same Feature scope or instruct
the user to restart that scope. When the procedure selects another Feature, Grill
emits a FORWARD handoff to Grill at that different Target Scope and stops. The next
Feature requires a new Grill execution that accepts that Canonical Handoff.

## Question boundary

Grill MAY ask only Requirement-owned questions. A question is Requirement-owned
only when its answer expresses stakeholder-owned business policy, changes
actor-observable Feature behavior, and remains meaningful without choosing an API,
technology, architecture, or implementation mechanism.

Requirement-owned topics include actors, goals, triggers, permissions, business
rules, required business information, validation constraints, state transitions,
business success and failure outcomes, edge cases, acceptance criteria,
dependencies, and exclusions.

Grill MUST NOT ask the user to choose:

- implementation strategy, architecture, framework, component, library, storage,
  transaction, migration, test, Slice, or code structure;
- API or interface design, including endpoints, transport or protocol, methods,
  request or response schemas, DTOs, serialization field names, or types;
- technical error handling, including HTTP status codes, technical error codes or
  payloads, exception mapping, retries, timeouts, or logging.

Business failure semantics remain Requirement-owned: Grill may ask whether an
operation must be rejected, access must be denied, or partial business effects are
forbidden. How that outcome is represented or implemented is Solution-owned. If a
candidate question mixes both concerns, Grill MUST ask only the business-outcome
portion. It MUST defer engineering implementation strategy, API or interface
design, and technical error handling to Solution; decomposition to Slice; and
detailed code or test execution to TDD. A deferred downstream decision MUST NOT
block Requirement readiness or be recorded as a Requirement decision.

## Requirement clarification

Before producing the Requirement artifact, Grill MUST present a list of all business
decisions it can infer from the Planning Artifact and any existing Requirement version.
For each decision that remains ambiguous, missing, or conflicting:

- ask the user during this invocation and wait for an answer;
- continue at the same Target Scope after each answer to explore follow-up questions;
- do not invent stakeholder decisions when evidence is insufficient.

If the Planning Artifact contains all necessary business information and no ambiguities
exist, Grill proceeds directly to producing the Requirement without asking additional questions.

### Clarification presentation

When presenting clarifications to the user, Grill MUST follow these rules:

- Propose concrete options derived from existing code patterns in the project,
  similar Feature implementations already present, or well-known industry practices
  for this domain. Each option must have a clear rationale tied to the artifact
  being analyzed — no fabricated suggestions.
- Present at most three to five options per question. Fewer is better when the
  decision space is narrow; do not pad with filler choices.
- The last option MUST always be "Other" followed by a blank field where the user
  may describe an entirely different approach or state their own reasoning.

This is not a multiple-choice exercise. Options are informed suggestions, not a
prepackaged menu. Grill MUST NOT steer the user toward any particular choice.
If a proposed option conflicts with observable evidence in existing code or the
Planning Artifact, omit that option rather than presenting it. A leading question
that assumes an answer violates the Question boundary.

## Required process

1. Validate that Target Scope identifies exactly one Feature in the current
   Planning. Freeze that Feature as the only productive scope for this execution.
   Before writing, record the canonical Requirement paths that already exist; the
   only permitted Requirement mutation is the target Feature's canonical path.
2. Inspect relevant existing behavior and dependencies.
3. Analyze goal, actors, triggers, rules, observable behavior, edge cases,
   acceptance criteria, dependencies, and out-of-scope behavior to identify the
   required business decisions, applying the Question boundary above.
4. Separate confirmed decisions from unresolved questions.
5. Apply Requirement clarification: enumerate all ambiguous, missing, or conflicting
   business decisions and ask the user during this invocation using the presentation
   rules above. Continue at the same Target Scope after each answer to explore
   follow-up questions when needed.
6. Resolve all questions that could change observable business behavior and
   complete the business contract without inventing stakeholder decisions.
7. Record why the current business contract exists by tracing its objectives,
   rules, and acceptance evidence to the targeted Feature boundary and current
   Planning Change Set context. Retired or superseded intent remains history and
   MUST NOT be cited as an active constraint.
8. Persist a new Requirement version at its Canonical Artifact Path with its
   Feature ID and that Feature's current Feature Contract Version rendered as
   Planning Version. The enclosing Planning artifact may have a later version.
9. Mark it READY only when no unresolved business decision remains.
10. Compare the Requirement mutation set with the pre-write set. Confirm that
    exactly zero or one Requirement changed and that any changed path is the target
    Feature's canonical Requirement. Creating, replacing, or editing another
    Feature's Requirement makes the execution non-conforming; it MUST NOT emit a
    FORWARD Handoff or continue to another Feature.
11. Apply the Transition Resolution Procedure. If it requires a handoff, validate
   and render exactly one Canonical Handoff Block from the Handoff Protocol as the
   final content of the response, then stop without consuming its Target Scope.

While waiting for a stakeholder answer, Grill remains active at the same Target
Scope and emits no handoff. A pending answer is not itself a blocker. After entry
validation, Grill MUST NOT reapply the Transition Resolution Procedure to select an
exit until the Requirement is READY or a decision cannot be obtained and a blocker
has been identified.

Grill MUST NOT cross the Question boundary or choose architecture, data storage,
framework components, Slice boundaries, tests, or implementation. If a business
decision cannot be obtained, the Requirement remains not ready and the workflow
reports a blocker.

## Completion

Completion concerns only the targeted Feature. The procedure selects the next
missing Requirement; Solution is not eligible until every planned Requirement is
current and READY. An unchanged READY Requirement remains current across an
incremental Planning version when its Planning Version still matches its Feature
Contract Version.

Completing the targeted Feature does not continue the Grill loop inside this
execution. Even when the next result is Grill at another Feature, this execution
MUST emit that FORWARD Handoff and MUST NOT create the next Requirement. A Grill
execution that creates or modifies Requirements for more than one Feature is
non-conforming.

The user or IDE host must start the next Grill invocation with that Handoff. CLI
auto mode may start a separate validated execution through its external Runner, but
it never expands the current Grill execution's mutation set.

### Emit conditions after Grill completes a Feature

After producing a current Requirement artifact:

- **FORWARD to Grill**: When Rule 5 selects another Feature lacking a usable current Requirement, forward to Grill at that different Feature scope.
- **FORWARD to Solution**: When Rule 6 matches, forward to Solution at Project scope.
- **RETURN**: When Rule 3 selects a persisted blocker or Rule 8 selects a current Review failure, return to the resolved owner and scope.
