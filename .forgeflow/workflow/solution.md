# Solution Workflow

Version: 2.9

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Solution Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | READY Planning; current READY Requirement for every Feature |

Solution creates one coherent engineering baseline after analyzing every current
active business contract together with the prior engineering baseline. Historical
or retired Requirements remain history but are not active constraints. Solution is
the owner of engineering decisions shared across Features.

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

1. Validate every active Requirement version against Planning and read the complete
   prior Solution Plan when present. Do not design from only the latest changed
   Requirement.
2. Inspect the existing codebase, interfaces, data model, tests, and conventions.
3. Classify unresolved questions as Requirement-owned business policy or
   Solution-owned engineering decisions using the ownership rules above.
4. Enumerate all Solution-owned engineering decisions that cannot be inferred
   from Requirements or existing system evidence, and ask the user during this
   invocation using the presentation rules above only when external constraints
   or material trade-offs are involved.
5. Reconcile cross-Feature interactions and non-functional constraints. Identify
   existing or extractable shared components and utilities, and define whether each
   affected Feature reuses, extends, or introduces them.
6. Define boundaries, interfaces, data and migration strategy, security and error
   handling, operational constraints, risks, and verification strategy. Define the
   Implementation Structure and Test Structure required by the Artifact Protocol.
   Choose package-by-Feature, package-by-layer, or a justified hybrid from existing
   repository evidence and the approved architecture; do not assume a language or
   framework. For multiple roles such as controllers/adapters, services/use cases,
   repositories/data access, domain types, and support components, state their
   package or module boundaries and allowed dependency direction. Define the
   corresponding unit and integration test placement.
7. Record a Based On Requirements version mapping for every planned Feature.
8. Compare every active Feature with the prior Solution Plan when present. Record a Feature
   Engineering Versions map for every active Feature: retain the prior value when
   the Feature's engineering contract is compatible, and use the new Solution Plan
   Version for each added or materially affected Feature. Cross-cutting changes MUST
   name and advance every affected Feature; uncertainty is an engineering decision
   that must be resolved rather than treated as compatibility. A shared-component
   change advances every Feature whose engineering contract is affected, while
   unaffected Features retain their prior engineering versions.
9. Record `Shared Components and Utilities` and `Cross-Feature Impact` sections in
   the Solution Plan. The impact analysis MUST cover every active Feature and state
   its direct, indirect, or unaffected classification, supporting reason, and
   Feature Engineering Version action. Use `NONE` when no shared component applies.
   Also write the complete structured impact metadata defined by the Artifact
   Protocol: Shared Component IDs, Feature Dependencies, Feature Shared Components,
   Feature Decision References, and Cross-Feature Impact. Preserve Planning order,
   reject dependency cycles, and resolve every component and decision reference.
10. Maintain an `Engineering Decision Register` in the Solution Plan. Every current
   decision records its affected Features, supporting Requirement or codebase
   evidence, and whether it retains, replaces, or supersedes a prior decision.
   Superseded decisions remain in history and MUST NOT be presented as current.
11. Perform the READY quality gate and record Requirement-to-engineering and
   verification traceability in the Solution Plan.
12. Persist the Solution Plan at its Canonical Artifact Path and mark it READY only
   when all required engineering decisions are actionable and no business choice
   has been invented.
13. Apply the Transition Resolution Procedure after the entry validation already
    required by the Entry barrier.
    If it requires a handoff, validate and render exactly one Canonical Handoff Block
    from the Handoff Protocol as the final content of the response.

Solution MUST NOT decompose Features into Slices, write implementation, or alter
Requirements. Missing business policy produces a RETURN to Grill at the affected
Feature scope.

Solution MUST NOT leave a new multi-role implementation in an unspecified source
or test package. It also MUST NOT require artificial one-class packages when the
repository convention and cohesion evidence support a broader module. The decision
is responsibility- and evidence-based rather than a fixed naming recipe.

## Emit conditions after Solution completes

After producing a current Solution Plan:

- **FORWARD to Slice**: When Rule 7 matches, forward to Slice for the first Feature in Planning order lacking a usable current Slice Plan.
- **RETURN**: When Rule 3 selects a persisted blocker, return to its resolved owner and scope.

## Change impact

Any normative Solution Plan change creates a new artifact version. Only Features
whose Feature Engineering Version advances have stale Slice Plans, TDD Records, and
Review Reports. Evidence for a Feature whose engineering version is retained remains
usable. History is preserved, and compatibility MUST be supported by the current
Requirements, codebase evidence, and explicit cross-Feature impact analysis.
