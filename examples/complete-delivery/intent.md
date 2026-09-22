# Tutorial intent: safe inventory transfers

Provide one inventory-transfer capability for a local, single-user inventory tool.
Move a positive whole-number quantity between two different stock locations.
A successful transfer preserves the total quantity. A rejected transfer changes
nothing, including the set of locations. A destination may be created on success;
a missing source has zero stock. Reject insufficient stock, identical locations,
zero/negative quantities and non-integer quantities. Booleans are not quantities.
Initial stock must contain non-negative integers. Returned snapshots must not let
callers mutate internal inventory.

This teaching example excludes concurrent users, persistence, networking,
authentication, pricing and deployment. It is a single-process in-memory exercise,
not a claim about database transactions or production inventory systems.

These are explicit tutorial requirements. Do not treat them as inferred policy for
another project. Solution owns technical design and Slice owns decomposition.
