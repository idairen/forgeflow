# Grill Workflow

Version: 2.10

## Contract

| Field | Value |
| --- | --- |
| Scope | Feature |
| Owns | Feature Lane Record; Requirement; observable business behavior and acceptance policy |
| Inputs | READY Planning; usable dependency Requirements; one eligible or recovered Feature Target Scope |

Grill obtains stakeholder decisions but never invents them.

## Ownership and entry

Accept only a valid Handoff, Lane Entry, or Recovery selected by the Transition
Protocol. Validate the complete graph, resolve exactly one planned Feature, and
freeze it as the only productive and Requirement-mutation Scope. Handoff and Lane
Entry atomically create its ACTIVE Feature Lane Record before work. Blocker Recovery
and interrupted Lane Recovery follow their distinct Transition conditions and the
Artifact Protocol's archival/replacement transaction. A confirmed inactive claim may
be released without replacement only under the Project-blocker recovery branch;
that branch authorizes no business work. Another Feature always requires
another execution and its own authorization.

Every transitive Planning dependency must have a usable current Requirement at
claim time and before persistence. An ACTIVE claim for the same Feature rejects an
ordinary Entry; only explicit, valid Recovery may replace it. Independent eligible
Features may run in other executions, but their files, clarification, commands, and
evidence are outside this Lane.

A Grill-owned question changes observable Feature behavior without choosing an API,
technology, architecture, or implementation. It includes actors, triggers,
permissions, business information and rules, validation, state transitions, success
and failure, edge cases, acceptance criteria, dependencies, and exclusions.

Grill does not choose implementation strategy, components, storage, transactions,
migrations, tests, Slices, code layout, interfaces, schemas, serialization, technical
status/error codes, exception mapping, retries, timeouts, or logging. It owns whether
a business action is rejected, access denied, or partial effects forbidden; Solution
owns the mechanism. Ask only the business portion of a mixed question.

## Clarification

Enumerate decisions supported by Planning, current Requirement evidence, and
observable behavior. Ask and wait for every missing, ambiguous, or conflicting
business decision under the Framework policy; skip unnecessary questions.
Engineering decisions neither block READY nor become Requirement decisions.

Waiting stays at the same Feature without Handoff and is not itself a blocker. If a
required decision cannot be obtained across invocations, persist
`BUSINESS_GAP` under the Artifact and Transition Protocols while retaining the Lane
claim for explicit Recovery. Independent Lanes remain eligible.

## Process

1. Validate entry, atomically establish and freeze the current Lane Attempt under
   the Artifact Protocol's monotonic counter rule, and record existing canonical
   Requirement and Lane paths. Release-only Recovery instead releases the confirmed
   inactive claim, resolves the Project blocker, and stops without business work.
2. Inspect relevant behavior and dependencies; analyze goals, actors, triggers,
   rules, outcomes, edge cases, acceptance, dependencies, and exclusions.
3. Separate confirmed business decisions, Grill clarifications, and deferred
   engineering questions; resolve the owned decisions without invention.
4. Trace the business contract to the targeted Feature and current Planning Change
   Set; historical intent is not an active constraint.
   At each work checkpoint and before persistence, recheck the frozen claim,
   Planning, dependencies, and Project blockers. A replaced or absent claim stops
   this execution without any canonical write or archival. On a Project blocker,
   release only the still-owned claim and stop business work. For a PLAN_GAP found
   here, atomically persist the BLOCKED Requirement and archive/release the owned
   Lane; on failure restore prior files. Re-resolve the committed graph, emit the
   exact RETURN to Plan, and stop. Never mark this unfinished Lane COMPLETE.
5. Persist a new target Requirement version with Feature ID and its current Feature
   Contract Version as Planning Version; mark READY only when business decisions are
   complete. Requirement persistence and Lane Status COMPLETE form one Artifact
   Protocol transaction.
6. Verify that no other Feature's Requirement changed; otherwise stop without a
   forward Handoff.
7. Resolve Transition. On join-pending, report Lane completion without a Handoff and
   stop. Otherwise emit any exact Handoff as final content and stop.

## Ready

Completion applies only to the target Feature. An unchanged READY Requirement stays
current while its Planning Version matches that Feature's Contract Version. Solution
is eligible only after every planned Requirement is current and READY and no ACTIVE
Lane remains. A COMPLETE Lane Record never authorizes work on another Feature.
