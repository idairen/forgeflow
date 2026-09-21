# Solution Workflow

Version: 2.13

## Contract

| Field | Value |
| --- | --- |
| Scope | Project |
| Owns | Solution Plan; project engineering baseline |
| Inputs | READY Planning and every current READY Requirement |

Accept only a valid Handoff or Recovery selected from current `ENGINEERING_GAP`.
Validate Transition and Handoff and require `BUSINESS_READY`; a partial Requirement
set never authorizes Solution. Historical and retired Requirements are not active.

## Ownership and clarification

Solution owns architecture, components, implementation strategy, APIs/interfaces,
data/migration, security mechanisms, technical error handling, operations, and
verification. Requirements own business success/failure; Implement owns code inside an
approved Slice. Solution therefore defines endpoints, protocols, methods, schemas,
DTOs, serialization, status/error payloads, exception mapping, transactions, retries,
timeouts, and logging without treating their absence from Requirement as a business
gap.

Solution also owns the properties verification must establish, required checks and
test levels, passing criteria, evidence sources, and any permitted alternative
strategies. Slice maps these decisions to its delivery units. Implement chooses and
refines execution details within those constraints; it cannot replace them by a
rationale. Routine test cases or commands do not require a new engineering decision.

Enumerate decisions supported by Requirements, prior Solution, and system evidence.
Under the Framework clarification policy, ask and wait when an owned decision lacks
usable evidence, has a material trade-off, or depends on user-supplied external
constraints such as runtime, deployment, dependency, or migration scope. Proceed
without unnecessary questions when evidence determines the answer. Pending answers
remain at Project and emit no Handoff; continue only when resolved or explicitly
deferred by the user.

## Ready gate

Every current Requirement behavior, acceptance criterion, dependency, and constraint
must trace to actionable engineering decisions and verification across applicable
boundaries, interfaces, data/migration, security, errors, operations, risks, and
cross-Feature effects. An unresolved engineering decision blocks READY; an unresolved
business outcome returns to Grill. Neither is deferred implicitly downstream.

## Process

1. Validate every current Requirement against Planning and read the complete prior
   Solution. A valid-but-stale Solution may be used for comparison and update only
   after Artifact Protocol baseline validation; it never substitutes for current
   Requirements or satisfies an engineering/delivery barrier. Limit lineage reads
   to the Planning changes and referenced Requirement versions involved.
2. Inspect relevant code, interfaces, data, tests, and conventions; classify questions
   by Framework ownership and resolve required engineering clarification.
3. Reconcile cross-Feature and non-functional constraints. Identify shared components
   and whether each Feature reuses, extends, or introduces them.
4. In canonical `solution-plan.md`, write `Artifact Protocol Version = 2.11` and
   one Solution Summary covering baseline, material cross-Feature effects, and
   verification; never create a separate summary.
5. Define boundaries, interfaces, data/migration, security, technical errors,
   operations, risks, and verification.
   Record the Artifact Protocol Verification Requirements table. Trace applicable
   obligations to Features, required checks/strategies, passing criteria, and
   evidence. Allow alternatives only with explicit conditions and equivalent
   required coverage. TDD may be the default candidate for behavioral changes;
   it is not required for every Slice. Keep correctness/regression requirements
   even when a benchmark, scan, or static check is also required.
6. Define the Artifact Protocol Implementation and Test Structures using
   repository-relative paths and coherent observable conventions. Choose
   package-by-Feature, package-by-layer, or a justified hybrid from evidence.
7. Separate responsibilities and allowed dependencies. Avoid both unrelated
   co-location/catch-all utilities and artificial one-class packages. Shared placement
   requires cohesion and a recorded reason. Define corresponding unit, component,
   integration, contract, and end-to-end test placement.
8. Record Based On Requirements for exactly every current Feature. Remove retired
   Features from all Solution maps; include added Features and use current Planning
   order. Before READY, revalidate all references, map completeness, and impact
   classifications against the current baseline.
9. Compare every Feature with prior Solution: retain compatible Feature Engineering
   Versions and advance every added or materially affected Feature. Resolve
   uncertainty rather than assume compatibility.
10. Record Shared Components and Utilities, Cross-Feature Impact, and all structured
    Artifact Protocol mappings in Planning order; reject cycles and unresolved
    component/decision references.
11. Maintain the Engineering Decision Register with affected Features, Requirement
    or code evidence, and retain/replace/supersede status.
12. Pass the Ready gate and persist canonical READY Solution. Resolve Transition
    from the saved Feature Engineering Versions under its upstream-persistence
    rule; old downstream evidence establishes completion only when its applicable
    version chain is current. Do not retain the pre-revision execution target.
    Emit any exact Handoff as final content, and stop.

Solution never changes Requirements, decomposes Slices, writes code, or leaves
multi-role source/test placement unspecified.

## Change impact

Normative change creates a new Solution version. Only Features whose Engineering
Version advances lose current Slice/Implement/Review evidence; retaining a version requires
current Requirement, repository, and cross-Feature impact evidence.
