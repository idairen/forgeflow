# Complete delivery tutorial: inventory transfer

This runnable teaching example covers a small application and the full ForgeFlow
Plan → Grill → Solution → Slice → Implement → Review path. It includes an intentional
failure and a corrected reference implementation. **The checked-in files are authored
teaching material, not a transcript of an independent IDE delivery or a Review PASS.**
Real host records belong in the acceptance suite; do not manufacture them from this
example. A separate [real task-manager case](../../docs/testing/evidence/task-manager/README.md)
preserves an actual recorded FAIL/rework/PASS chain. Its older baseline and confirmed
IntelliJ IDEA / Codex / gpt-6-astra environment are tracked in the [compatibility table](../../docs/testing/compatibility.md).

## Run without an Agent

From the ForgeFlow source checkout (Python 3.10+; no extra dependencies):

```bash
python3 examples/complete-delivery/check.py
```

The script uses a temporary directory and actually executes the same eight checks
against each implementation. The starter must fail exactly two checks: a rejected
transfer changes a balance, and a missing source creates a negative balance. The
reference must pass all eight. A broken import or environment does not count as the
expected failure. The script does not edit the repository or emit canonical Artifacts.

| File | Purpose |
| --- | --- |
| `intent.md` | Explicit teaching requirements and exclusions |
| `starter/inventory.py` | Intentionally incorrect behavior to reproduce |
| `reference/inventory.py` | Corrected implementation for comparison |
| `tests/test_inventory.py` | Acceptance, rejection, conservation and isolation checks |
| `check.py` | Reproduce the defect and verify the reference in isolation |

## Deliver the change in a real host

First install ForgeFlow using the [quickstart](../../docs/quickstart.md). From this
repository, prepare a separate project; keep the reference implementation outside
it so the exercise does not begin with the answer:

```bash
example_root="$PWD/examples/complete-delivery"
project_root="$(mktemp -d)/inventory-transfer"
mkdir -p "$project_root"
cp "$example_root/intent.md" "$project_root/intent.md"
cp "$example_root/starter/inventory.py" "$project_root/inventory.py"
cp -R "$example_root/tests" "$project_root/tests"
cd "$project_root"
forge init --adapter codex
# Or initialize with --adapter copilot before beginning the run.
```

Open this project in the selected IDE. Launcher discovery follows the host's setup;
installed files do not guarantee automatic slash-command registration. Execute one
authorized workflow at a time. Preserve the full response/Handoff outside the active
Artifact Root and pass it to the next independent invocation. If a material question
arises, answer it at its owner; the table below is a guide, not a pre-approved graph.

| Step | Action and expected checkpoint |
| --- | --- |
| Plan | Submit `intent.md`. Resolve project-level questions and record the approved Feature topology. One inventory-transfer Feature is the illustrative decomposition. |
| Grill | Clarify observable rules, including unchanged state on rejection. Claim the Feature atomically and complete its Requirement/Lane transaction. All Requirements must be READY before Solution. |
| Solution | Inspect the existing code and tests. Approve interfaces, in-memory structure, placement and verification obligations. For this exercise, propose the existing Python implementation and executable tests; engineering decisions belong here. |
| Slice | Map the obligations and paths to a reviewable repair unit. If approved, require TDD with all eight acceptance/regression checks. Every Feature needs a usable Slice Plan before implementation. |
| Implement | Freeze authorized Slice, upstream versions and Attempt. Persist IN_PROGRESS before edits. Run the checks and preserve genuine behavioral RED; repair the ordering of validation and mutation; rerun every required check. Record method, selection, evidence, placement and self-check. |
| Review | In a separate invocation, independently check the current code, contracts and evidence; run applicable plugins and record Findings. Only genuine zero-blocker evaluation yields an immutable PASS. |
| Complete | Fresh Transition must confirm a matching current PASS for every declared Slice. Inspect `forge status`; a test command succeeding alone does not complete the project. |

The conceptual repair is to validate before changing either balance. Within this
single-threaded exercise it prevents observable partial mutation on rejection; it
does not implement concurrent or persistent transactional guarantees.

## Observe a real FAIL and rework when one occurs

The starter's failing tests are **test failures**, not an independent Review FAIL.
Implement must repair known local blockers before READY_FOR_REVIEW. Do not knowingly
submit the defective starter just to obtain a FAIL or weaken the verification plan.

If independent Review discovers a genuine missed obligation:

1. Preserve its immutable FAIL, Findings, violated contract and current Attempt.
2. Follow the exact RETURN to the finding's owner. For an implementation defect,
   a new authorized Implement invocation archives the prior record and allocates
   `max(UsedAttempts) + 1`; it does not edit the old Review.
3. Reproduce the newly identified behavior, repair within the approved scope and
   rerun every required check. Required new policy returns upstream first.
4. A separate Review evaluates the new Attempt. Keep both reports; only the matching
   current PASS can establish completion.

Record an actual FAIL/rework demonstration only when it really happened. For
repeatable structural routing tests independent of a model, run:

```bash
# From the ForgeFlow source checkout:
PYTHONPATH=src python3 -m unittest tests.integration.test_current_framework
```

Those tests use synthetic graphs and prove deterministic checks, not real Review
judgment. A successful run of this tutorial does not establish all recovery or
parallel-Lane scenarios.

## Share a real run

Capture commit/framework versions, IDE and extension, adapter, model/mode, OS,
responses/Handoffs, source changes, test output, final graph and any FAIL/rework.
Redact secrets before sharing. Map only observed scenarios to the
[acceptance plan](../../docs/testing/ide-test-plan.zh-CN.md), using the
[result instructions](../../tests/acceptance/ide/README.md).
