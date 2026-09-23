# Adopting ForgeFlow in an existing project

ForgeFlow can use existing system context as input to Plan. Existing code proves
what the system currently does; it does not approve new business scope or create
historical Review evidence. The [six workflow owners](../README.md#delivery-model)
still apply. This guide creates no shortcut entry or additional workflow.

## Establish a baseline

1. Use a focused branch or isolated checkout. Inspect uncommitted changes and retain
   the current application test results, including known failures.
2. Check whether `.forgeflow/` or `forgeflow.json` already exists. For an existing
   installation, inspect its evidence and [migration needs](maintainers/implement-migration.md).
   Do not initialize over it or reset merely to obtain an empty graph.
3. For a project without ForgeFlow, follow the [installation guide](quickstart.md),
   then run `forge init --adapter codex` (or `copilot`) in the application root.
   Inspect the resulting diff and `forge status` before starting an agent.
4. Supply an explicit objective and boundaries. Name relevant existing behavior and
   confirmed compatibility constraints. Leave unresolved business decisions open;
   existing libraries and directory layouts do not decide those questions.

For example, an intent might request one approved new inventory capability while
preserving specified existing operations. It need not request a rewrite or invent
Features for every existing module. Plan establishes the approved Feature topology;
Grill resolves behavior; Solution owns engineering decisions; Slice scopes delivery.

Run approved baseline checks before changes and retain their results as baseline
evidence. Passing existing tests does not by itself satisfy a new obligation or
constitute an independent ForgeFlow Review.

## Add work after adoption

Inspect the current graph first. New or changed project scope enters through an
authorized Subsequent Plan intent, such as `forge plan --intent "..."`; ACTIVE
claims, blockers and entry checks still apply. Preserve stable identities and
versioned history. A bug report or small change does not automatically authorize
jumping to Implement. Current Review findings return to the owner and scope
determined by the core, with a new invocation for the target workflow.

## Git and team handoff

Decide the application's evidence-sharing policy explicitly. This source repository's
ignore rules protect framework development from generated test/run output; they
are not a universal ignore policy for downstream application projects.

| Material | Suggested treatment in an application repository |
| --- | --- |
| Installed framework and `forgeflow.json` | Version together so collaborators use a known contract/config baseline; review upgrades separately from application changes where practical. |
| Current artifacts and required immutable history/receipts | Preserve and share the complete evidence needed to resolve the graph. If committed, review for sensitive data. If kept outside Git, provide an access-controlled, retrievable shared record. |
| Review plugin reports | Preserve required attempt-scoped reports and revisions with their referenced evidence; report publication alone is not a canonical PASS. |
| `.forgeflow/runtime/`, optional logs, temporary profiles | Treat as local diagnostics, normally ignored. Capture a redacted subset only when needed for diagnosis. |
| Credentials and private host configuration | Keep outside committed content. Share only the non-secret host setup needed by collaborators. |

An application PR should identify the intended change, affected Feature/Slice,
contract versions, verification and Review evidence. Git merge approval does not
replace ForgeFlow Review, and a ForgeFlow PASS does not merge a PR.

Before switching branches, sharing a checkpoint or recovering a Lane, coordinate
with active writers. Git branches and worktrees are not the core's atomic claim or
protected multi-file publication mechanism. A branch merge can leave contradictory
evidence; revalidate the resulting graph rather than editing status fields to agree.

Only Grill supports parallel Feature Lanes under the current contract. Do not infer
parallel Implement/Review permission from multiple branches or available agents.

For a worked exercise, use the [delivery tutorial](../examples/complete-delivery/README.md).
For observed execution rather than teaching fixtures, see the
[historical task-manager case](testing/evidence/task-manager/README.md).
