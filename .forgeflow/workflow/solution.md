# Solution Workflow

Version: 2.4

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Solution Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | READY Planning; current READY Requirement for every Feature |

Solution creates one coherent engineering baseline after analyzing all business
contracts together. It is the owner of engineering decisions shared across
Features.

## Entry barrier

On Handoff Entry, Solution MUST first execute the Unified Entry Validation Procedure
defined in the Handoff Protocol. Without an incoming handoff, Solution may proceed
only through Recovery Entry when a fresh Rule 3 result selects Solution at Project
scope from a current ENGINEERING_GAP. It then rejects entry unless `BUSINESS_READY`
is derived — meaning all Requirements are current and READY. Partial Requirement
sets cannot authorize a Solution Plan.

## Engineering question ownership

Solution owns engineering questions intentionally left undecided by Requirements.
These include engineering implementation strategy, architecture and component
boundaries, API and interface design, data and migration design, security
mechanisms, technical error handling, operational constraints, and verification
strategy. Detailed code execution inside an approved Slice remains TDD-owned.

Requirements define business success and failure semantics. Solution defines their
technical representation and mechanism, including endpoints, protocols, methods,
request and response schemas, DTOs, serialization, HTTP status codes, technical
error codes and payloads, exception mapping, transactions, retries, timeouts, and
logging. The absence of those engineering decisions from a Requirement is not
missing business policy and MUST NOT cause a RETURN to Grill.

## Engineering clarification

Before producing the Solution Plan, Solution MUST enumerate all engineering
decisions it can infer from Requirements and existing system evidence.

For each decision that:
- cannot be inferred (no existing codebase to inspect), or
- requires a material trade-off (performance vs cost, framework choice, etc.), or
- depends on an external constraint the user must specify (deployment target,
  runtime version, third-party dependency, data migration scope),

Solution MUST ask the user during this invocation and wait for a response.
It emits no handoff while answers are pending and does not proceed until
all clarifications are resolved or explicitly deferred by the user.

If all engineering decisions can be inferred from the approved Requirements
and existing system evidence, Solution proceeds directly to producing the
Solution Plan without asking additional questions.

### Clarification presentation

When presenting clarifications to the user, Solution MUST follow these rules:

- Propose concrete options derived from existing code patterns in the project,
  similar Features already implemented, or well-known industry practices for this
  domain. Each option must have a clear rationale tied to what the artifacts reveal —
  no fabricated suggestions.
- Present at most three to five options per question. Fewer is better when the
  decision space is narrow; do not pad with filler choices.
- The last option MUST always be "Other" followed by a blank field where the user
  may describe an entirely different approach or state their own reasoning.

This is not a multiple-choice exercise. Options are informed suggestions, not a
prepackaged menu. Solution MUST NOT steer the user toward any particular choice.
If a proposed option conflicts with observable evidence in existing code or the
Planning Artifact, omit that option rather than presenting it. A leading question
that assumes an answer violates the engineering question boundary.

## READY quality gate

Before marking the Solution Plan READY, Solution MUST trace every current
Requirement behavior, acceptance criterion, dependency, and business constraint
to actionable engineering decisions and verification. The trace MUST cover all
applicable boundaries, interfaces, data and migration behavior, security, technical
error handling, operations, risks, and cross-Feature interactions.

An unresolved Solution-owned engineering decision blocks READY. An unresolved
Requirement-owned business outcome returns to Grill for the affected Feature.
Neither may be deferred implicitly to Slice, TDD, or Review.

## Required process

1. Validate every Requirement version against Planning.
2. Inspect the existing codebase, interfaces, data model, tests, and conventions.
3. Classify unresolved questions as Requirement-owned business policy or
   Solution-owned engineering decisions using the ownership rules above.
4. Enumerate all Solution-owned engineering decisions that cannot be inferred
   from Requirements or existing system evidence, and ask the user during this
   invocation using the presentation rules above only when external constraints
   or material trade-offs are involved.
5. Reconcile cross-Feature interactions and non-functional constraints.
6. Define boundaries, interfaces, data and migration strategy, security and error
   handling, operational constraints, risks, and verification strategy.
7. Record a Based On Requirements version mapping for every planned Feature.
8. Perform the READY quality gate and record Requirement-to-engineering and
   verification traceability in the Solution Plan.
9. Persist the Solution Plan at its Canonical Artifact Path and mark it READY only
   when all required engineering decisions are actionable and no business choice
   has been invented.
10. Apply the Transition Resolution Procedure after the entry validation already
    required by the Entry barrier.
    If it requires a handoff, validate and render exactly one Canonical Handoff Block
    from the Handoff Protocol as the final content of the response.

Solution MUST NOT decompose Features into Slices, write implementation, or alter
Requirements. Missing business policy produces a RETURN to Grill at the affected
Feature scope.

## Emit conditions after Solution completes

After producing a current Solution Plan:

- **FORWARD to Slice**: When Rule 7 matches, forward to Slice for the first Feature in Planning order lacking a usable current Slice Plan.
- **RETURN**: When Rule 3 selects a persisted blocker, return to its resolved owner and scope.

## Change impact

Any normative Solution Plan change creates a new version. All Slice Plans, TDD
Records, and Review Reports referencing the prior version become stale for
authorization and completion. History is preserved.
