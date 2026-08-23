# Grill Workflow

Version: 2.9

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owned artifact | Requirement |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | READY Planning; Target Scope naming one planned Feature |

Grill completes the stakeholder-owned business contract for exactly one Feature.
The incoming Target Scope is the complete authorization boundary; other Features
are future execution scopes and MUST NOT be analyzed, questioned, or modified.
Ambiguity must be challenged and resolved with the user, never invented.

## Entry behavior

On Handoff Entry, run the Unified Entry Validation Procedure. Without a handoff,
proceed only through Recovery Entry when fresh Rule 3 selects Grill at the exact
Feature Target Scope from a current `BUSINESS_GAP`. After valid entry, do not emit a
handoff to the same Feature or ask the user to restart it. A different Feature
requires a FORWARD Handoff, termination of this execution, and a new invocation.

## Question boundary

A question is Requirement-owned only when its answer defines stakeholder business
policy or actor-observable behavior for the targeted Feature without choosing an
implementation mechanism.

| Grill MAY ask | Grill MUST defer |
| --- | --- |
| actors, goals, triggers, permissions, business information and rules | architecture, frameworks, components, libraries, storage, transactions, migrations |
| validation constraints, business state transitions, success/failure outcomes | APIs, endpoints, transports, methods, schemas, DTOs, serialization names or types |
| edge cases, acceptance criteria, business dependencies and exclusions | technical errors, status/error codes, payloads, exceptions, retries, timeouts, logging |
| whether an operation is rejected, access denied, or partial business effects forbidden | Slice boundaries, tests, code structure, and implementation execution |

For a mixed question, ask only the business-outcome portion. Defer engineering to
Solution, decomposition to Slice, and implementation to TDD. A deferred downstream
choice neither blocks Requirement readiness nor becomes a Requirement decision.

## Requirement clarification

Before writing, enumerate confirmed and unresolved business decisions from current
Planning, relevant existing behavior, and any prior Requirement. For every ambiguous,
missing, or conflicting Requirement-owned decision, ask the user and wait at the
same Target Scope; continue follow-up clarification there until resolved. If none
exists, proceed without manufacturing a question.

### Clarification presentation

- Offer only concrete options supported by current artifacts, existing behavior, or
  established domain alternatives, with a brief relevant rationale.
- Present at most three to five options, using fewer when sufficient; the final
  option is always `Other` with free-form input.
- Do not pad, fabricate, lead, recommend, or include an option that conflicts with
  observable evidence. Options support a decision; they are not approval evidence.

## Required process

1. Validate and freeze exactly one planned Feature. Record existing canonical
   Requirement paths; only the targeted Feature's path may change.
2. Inspect relevant behavior and dependencies. Analyze goals, actors, triggers,
   permissions, rules, information, validation, states, outcomes, edge cases,
   acceptance criteria, dependencies, and exclusions under the Question boundary.
3. Separate confirmed decisions from unresolved questions and run Requirement
   clarification. Do not write a stakeholder answer that the user did not provide.
4. Complete the business contract and trace its objectives, rules, and acceptance
   evidence to the target Feature and current Planning Change Set context. Retired or
   superseded intent is history, not an active constraint.
5. Persist a new Requirement at its Canonical Artifact Path with the Feature ID and
   that Feature's current Feature Contract Version as `Planning Version`; the
   enclosing Planning artifact may have a later version. Mark READY only when no
   unresolved business decision remains.
6. Compare the Requirement mutation set with the pre-write set. Exactly zero or one
   Requirement may change, and any changed path MUST be the target's canonical path.
   Any other Requirement mutation is non-conforming and forbids READY, FORWARD, or
   work on another Feature.
7. Apply the Transition Resolution Procedure. If it selects a transition, validate
   and render exactly one Canonical Handoff Block as final response content, then
   stop without consuming its Target Scope.

While awaiting an answer, remain at the same Target Scope, emit no Handoff, and do
not re-run transition resolution. A pending answer is not a blocker. If a necessary
business decision cannot be obtained, keep Requirement not ready and report the
blocker. Grill MUST NOT choose architecture, storage, framework components, Slice
boundaries, tests, or implementation.

## Completion

Completion concerns only the targeted Feature. Solution is ineligible until every
planned Requirement is current and READY. An unchanged READY Requirement remains
current across incremental Planning when its Planning Version still equals that
Feature's Feature Contract Version.

Completing the targeted Feature does not continue the Grill loop inside this
execution. A Grill execution that creates or modifies Requirements for more than one Feature is
non-conforming. Even when another Feature is next, emit its FORWARD Handoff and stop;
the user, IDE host, or external CLI Runner must start a separate validated execution.

### Emit conditions after Grill completes a Feature

- **FORWARD to Grill**: Rule 5 selects a different Feature lacking a usable current Requirement.
- **FORWARD to Solution**: Rule 6 selects Solution at Project scope.
- **RETURN**: Rule 3 selects a persisted blocker or Rule 8 selects a current Review failure; return to the resolved owner and scope.

<!-- forgeflow-eof: .forgeflow/workflow/grill.md -->
