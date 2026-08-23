# Solution Workflow

Version: 2.13

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owned artifact | Solution Plan |
| Output | Owned artifact at its Canonical Artifact Path defined by the Artifact Protocol |
| Required inputs | READY Planning; current READY Requirement for every Feature |

Solution creates one coherent engineering baseline by analyzing every current
active business contract together with the prior engineering baseline. Historical
or retired Requirements remain history. Solution owns engineering decisions shared
across Features.

## Entry barrier

On Handoff Entry, run the Unified Entry Validation Procedure. Without a handoff,
proceed only through Recovery Entry when fresh Rule 3 selects Solution at Project
scope from a current `ENGINEERING_GAP`. Reject entry unless `BUSINESS_READY` is
derived from current READY Requirements for every Feature; a partial set never
authorizes Solution.

## Engineering question ownership

| Solution owns | Solution does not own |
| --- | --- |
| implementation strategy, architecture, components, APIs and interfaces | stakeholder business success or failure semantics |
| data and migration design, security mechanisms, technical error handling | Feature decomposition into Slices |
| operational constraints, verification strategy, cross-Feature engineering | detailed implementation and test execution |

Solution technically represents approved business outcomes through endpoints,
protocols, methods, schemas, DTOs, serialization, status/error codes and payloads,
exceptions, transactions, retries, timeouts, and logging. Their absence from a
Requirement is not missing business policy and MUST NOT trigger RETURN to Grill.

## Engineering clarification

Before writing, enumerate engineering decisions supported by all Requirements,
existing system evidence, and the prior Solution. Ask the user during this
invocation and wait only when a decision cannot be inferred, has a material
trade-off, or depends on an external constraint. Emit no Handoff while an answer is
pending. Proceed without questions when every decision is supported; an explicit
user deferral must remain visible and cannot silently satisfy READY.

While any answer is pending, Solution remains at Project scope, writes no READY
Solution Plan, emits no Handoff, and does not begin Slice.

### Clarification presentation

- Offer only concrete options supported by current artifacts, existing patterns,
  similar implementations, or established engineering alternatives, with rationale.
- Present at most three to five options, using fewer when sufficient; the final
  option is always `Other` with free-form input.
- Do not pad, fabricate, lead, recommend, or include an option conflicting with
  observable evidence.

## READY quality gate

READY requires every current Requirement behavior, acceptance criterion, dependency,
and business constraint to trace to actionable engineering decisions and
verification. Coverage includes boundaries, interfaces, data/migration behavior,
security, technical errors, operations, risks, and cross-Feature interactions.
An unresolved Solution-owned decision blocks READY; unresolved business policy
returns to Grill at the affected Feature. Neither is implicitly deferred downstream.

## Required process

1. Validate every active Requirement version against Planning and read the complete
   prior Solution Plan. Never design only from the latest changed Requirement.
2. Inspect the codebase, interfaces, data model, tests, and conventions. Classify
   unresolved questions by Requirement or Solution ownership and run Engineering
   clarification for non-inferable decisions, material trade-offs, and external constraints.
3. Reconcile cross-Feature and non-functional constraints. Identify existing or
   extractable shared components and utilities and define whether each Feature
   reuses, extends, or introduces them.
4. Write one concise `## Solution Summary` inside canonical `solution-plan.md`,
   covering the current baseline, material cross-Feature effects, and verification
   approach. Never create `solution-plan-summary.md` or another standalone summary file.
5. Define boundaries, interfaces, data/migration strategy, security, technical
   errors, operations, risks, and verification. Provide the Artifact Protocol's
   Implementation Structure and Test Structure. From repository evidence and the
   approved architecture, choose package-by-Feature, package-by-layer, or a justified
   hybrid without assuming a language/framework. Define responsibility boundaries,
   dependency direction, and production/unit/integration-test placement for
   controllers/adapters, services/use cases, repositories/data access, domain types,
   and support components.
6. Record `Based On Requirements` for every active Feature. Compare each Feature
   with the prior Solution and record `Feature Engineering Versions`: retain a
   compatible prior value; use the new Solution Plan Version for added or materially
   affected Features. Cross-cutting or shared-component changes MUST name and advance
   every affected Feature; unaffected Features retain their versions. Resolve
   compatibility uncertainty as an engineering decision.
7. Record `Shared Components and Utilities` and `Cross-Feature Impact` for every
   active Feature, including direct/indirect/unaffected classification, rationale,
   and version action; use `NONE` when applicable. Populate all structured metadata:
   `Shared Component IDs`, `Feature Dependencies`, `Feature Shared Components`,
   `Feature Shared Component Access`, `Feature Decision References`, and
   `Cross-Feature Impact`. Preserve Planning order and resolve every reference.
   Validate that the union of Planning and Solution dependencies is acyclic. Mark
   each shared-component relationship `READ` or `WRITE`; when either of two Features
   writes the same component, establish an engineering dependency order between
   them. Resolve an unsupported ordering through Engineering clarification rather
   than guessing. Only `READ`/`READ` co-usage is parallel-safe without another edge.
8. Maintain an `Engineering Decision Register`. Each current decision records
   affected Features, Requirement or codebase evidence, and whether it retains,
   replaces, or supersedes a prior decision. Superseded decisions remain history,
   never current.
9. Perform the READY quality gate and record Requirement-to-engineering and
   verification traceability. Persist the Solution Plan at its Canonical Artifact
   Path and mark READY only when all decisions are actionable and no business policy
   was invented.
10. Apply the Transition Resolution Procedure. If it selects a transition, validate
    and render exactly one Canonical Handoff Block as final response content, then stop.

Solution MUST NOT alter Requirements, decompose Slices, or implement code. It MUST
NOT leave multi-role production or test placement unspecified, but also MUST NOT
create artificial one-class packages when repository convention and cohesion support
a broader module. Structure decisions are evidence- and responsibility-based.

## Emit conditions after Solution completes

- **FORWARD to Slice**: Rule 7 selects the default dependency-ready Feature Lane lacking a usable current Slice Plan; other ready lanes may start separately through Feature Lane Entry.
- **RETURN**: Rule 3 selects a persisted blocker; return to its resolved owner and scope.

## Change impact

Every normative change creates a new Solution Plan version. Only Features whose
Feature Engineering Version advances have stale Slice, TDD, and Review evidence;
retained Feature versions keep compatible evidence usable. Preserve history and
support compatibility with current Requirements, codebase evidence, and explicit
cross-Feature impact analysis.

<!-- forgeflow-eof: .forgeflow/workflow/solution.md -->
