# Concept and architecture guide

The current workflow chain is Plan → Grill → Solution → Slice → Implement → Review.
See the maintained [architecture](../../ARCHITECTURE.md), [CLI quickstart](../../README.md),
and [normative framework](../../.forgeflow/forgeflow.md).

Grill Lanes may run for independent dependency-ready Features. All Requirements join
before Solution and all Slice Plans join before Implement. Implementation/review is
ordered by declared Feature and Slice positions. A Workflow invocation never consumes
its own Handoff. The external auto runner can start a new, freshly validated invocation.

Solution defines verification obligations; Slice maps them to delivery units;
Implement executes approved strategies and records evidence; Review independently
judges the result. TDD is one strategy, not a separate workflow. Methods are optional
local execution choices and do not change scope, ownership or passing criteria.

Artifacts are persistent authority. Lane records coordinate claims; runtime logs,
knowledge views, supplemental reports and historical PASS records cannot establish
current completion. [Migration notes](../maintainers/implement-migration.md) describe
breaking changes from the former TDD and parallel delivery-lane model.
