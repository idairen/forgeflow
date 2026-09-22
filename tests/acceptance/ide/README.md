# ForgeFlow IDE acceptance

The [current plan](../../../docs/testing/ide-test-plan.zh-CN.md) defines the cases.
`manage.py` prepares workspaces and checks recorded evidence; it never executes an
IDE, calls an Agent, or turns prepared fixtures into PASS results.

Current results belong in `results/current/`. Older files directly under `results/`
and the [legacy plan](../../../docs/testing/ide-test-plan.legacy.zh-CN.md) remain
historical evidence and do not satisfy the current gate. `inputs.md` is a historical
input library: adapt inputs to the current case and record the exact input used.

## Inspect the current suite

```bash
python3 tests/acceptance/ide/manage.py verify
python3 tests/acceptance/ide/manage.py list --priority P0
python3 tests/acceptance/ide/manage.py show IDE-PLAN-101
```

The current plan contains 25 cases (24 P0, 1 P1) and covers 12 adapter launchers.
Use `verify` and `list` for the current counts, not historical reports. The CSV is
an exported view; regenerate it with `manage.py export` after changing the plan.
Identifiers containing `TDD` are retained case IDs, not a TDD Workflow declaration.

## Create isolated host workspaces

```bash
python3 tests/acceptance/ide/manage.py init \
  --adapter copilot \
  --output tests/acceptance/ide/workspaces/copilot-happy
python3 tests/acceptance/ide/manage.py init \
  --adapter codex \
  --output tests/acceptance/ide/workspaces/codex-happy
```

The helper copies the minimal Python fixture, installs the current framework and
creates empty artifact/report roots. It configures Copilot prompt discovery in
VS Code. Codex discovery depends on the actual host; the helper does not invent
registration files. Open each workspace in its intended host, invoke the actual
launcher and capture the host, version, model, mode, input and full response.

Run the current plan's entry and normal-delivery cases first, then isolated failure,
recovery, version and parity cases. Each invocation remains inside its authorized
Workflow and Scope; a test plan does not override the core's entry requirements.

## Capture and reuse real checkpoints

After a real execution reaches the intended checkpoint and all related processes
have stopped:

```bash
python3 tests/acceptance/ide/manage.py snapshot \
  --source tests/acceptance/ide/workspaces/copilot-happy \
  --output tests/acceptance/ide/snapshots/S1-PLANNED-copilot
python3 tests/acceptance/ide/manage.py prepare IDE-GRAPH-101 \
  --adapter copilot \
  --source tests/acceptance/ide/snapshots/S1-PLANNED-copilot \
  --output tests/acceptance/ide/workspaces/IDE-GRAPH-101-copilot
```

Choose a checkpoint appropriate to each case; some require later Implement/Review
state. The helper rejects existing destinations and symbolic links, copies the
workspace and creates a result template. It does not inject contradictions or run
workflows. Any deliberate malformed fixture must be isolated, identified as test
input and never represented as real successful workflow output.

## Record actual outcomes

Default templates are written outside the tested workspace under:

```text
tests/acceptance/ide/results/current/IDE-GRAPH-101.copilot.result.md
```

Record Framework Version, adapter, host/model versions, exact inputs and outputs,
file changes, Artifact/Report/Handoff evidence, status and any defect. Before PASS,
replace every TODO, use the current Framework Version and set Defect ID to NONE.
The records must refer to retrievable real evidence. Check for secrets before
sharing; only intentionally reviewed evidence should be committed.

```bash
python3 tests/acceptance/ide/manage.py summary
python3 tests/acceptance/ide/manage.py release-gate
```

All P0 cases need valid PASS evidence from every adapter prescribed for that case.
Recorded P1 FAIL/BLOCKED outcomes also block release. NOT RUN stays NOT RUN until
actually executed. The gate validates records, not the truth of their claims;
maintainers must review the evidence. Historical PASS cannot be reused as current
host conformance.
