# ForgeFlow

ForgeFlow is a repository-native Markdown protocol for AI-assisted software delivery,
with an optional Python CLI and an npm framework installer. **Technical Preview**:
local tests and package checks do not establish real Codex/Copilot acceptance.

The normative source is [`.forgeflow/`](.forgeflow/forgeflow.md): Framework 3.8,
Artifact 2.19, Transition 1.8, Handoff 2.15, and Implement 2.13. The CLI follows
those contracts; it does not supersede them or decide whether a model's evidence is true.

## Delivery model

```text
Plan
  -> dependency-ready Grill Features (isolated, atomically claimed Lanes)
  -> all Requirements READY
  -> Solution
  -> Slice every Feature
  -> Implement -> Review for each Slice in declared order
  -> all current attempts PASS -> Project Complete
```

Only Grill has parallel Feature Lanes. Delivery requires every Feature's current
Slice Plan. Feature/Slice order is declared order, not numeric or filesystem order.
Identifiers use `01` through `09`, then ordinary decimal notation (`10`, `100`).

| Workflow | Owns |
| --- | --- |
| Plan | Approved intent, Feature topology, project constraints |
| Grill | Observable Feature behavior, Requirement, Lane claim |
| Solution | Engineering design, verification obligations and passing criteria |
| Slice | Delivery decomposition, placement and verification mapping |
| Implement | One Slice's changes, verification execution and evidence |
| Review | Independent findings and immutable PASS/FAIL disposition |

TDD is a verification strategy inside Implement. Other supported strategies include
`BEHAVIORAL_TEST`, `CHARACTERIZATION_TEST`, `MIGRATION_REHEARSAL`, `STATIC_VALIDATION`,
`CONFIGURATION_VALIDATION`, `SECURITY_SCAN`, `BENCHMARK`, `DOCUMENTATION_VALIDATION`
and `MANUAL_ACCEPTANCE`. A method such as direct implementation or small-step repair
is optional prose, not a workflow or an approval gate. Mandatory checks cannot be
replaced by a more convenient strategy.

## Install from a checkout

Python 3.10+ is required for `forge`. From this repository:

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/forge --help
```

In a target repository, use the installed command:

```bash
forge init --adapter codex
# Or: forge init --adapter copilot
forge status
forge plan --intent "Describe the approved project objective"
```

The selected agent executable must be installed and authenticated separately.
Initialization installs repository launchers; IDE discovery/registration depends on
the host. Generic Markdown participants can read the core directly.

The npm package is an **installer only**, requiring Node 18+. To test a local
package without depending on registry publication:

```bash
npm pack --pack-destination /tmp
# In a disposable target directory; use the actual tarball emitted above:
npm exec --yes --package /absolute/path/to/idairen-forgeflow-0.1.0.tgz -- forgeflow init --adapter codex
```

This does not install Python or the agent executables. Registry publication is a
separate maintainer action; these instructions do not claim a published release.

## CLI

| Command | Behavior |
| --- | --- |
| `forge init --adapter codex` | Install the bundled framework |
| `forge init --adapter codex --force` | Refresh managed files, remove retired TDD launchers, preserve project evidence |
| `forge plan --intent "…"` | Bootstrap or an authorized subsequent Plan change |
| `forge grill/solution/slice/implement/review --handoff FILE` | Execute exactly one graph-authorized Workflow/Scope |
| `forge run --auto` | External orchestrator: revalidate each graph and Handoff, stop on wait/blocker/halt |
| `forge run --manual` | Execute only Plan |
| `forge status` | Current graph, resolution, ordered input projection and knowledge view |
| `forge knowledge --feature F-01 --format markdown` | Derived, non-authoritative Feature view |
| `forge knowledge --slice F-01/S-01 --history` | Slice view with optional history index |
| `forge handoff` | Last runtime Handoff; always revalidate before reuse |
| `forge reset --force` | Explicitly rotate both artifact and supplemental-report evidence roots |

The slash-separated names in the table are alternatives, not a literal command.
`FILE` contains the complete previous response with its final canonical Handoff.
Missing or invalid Handoff input produces read-only routing correction and stops;
a later invocation consumes the corrected block. Eligible Bootstrap, Subsequent
Plan and blocker Recovery do not need a synthetic incoming Handoff.

Use `forge grill --feature F-02` to request one eligible Lane directly. For an
interrupted claim, specify both `--feature F-02` and `--confirm-inactive`; the core
procedure still owns protected claim replacement.

An active Grill blocker claim needs explicit confirmation that its previous
execution stopped (`forge grill --confirm-inactive`). Timeout is not confirmation.
Interrupted Lane recovery and invalid-Review disposition require the explicit,
claim-specific maintenance procedures in the Markdown core; no ordinary command
silently releases a claim or archives a Review. The host/participant must provide
protected transactions; the CLI does not turn sequential agent file writes into
atomic multi-file updates.

Exit codes: `0` successful step/completion, `1` error or invalid command, `2`
incomplete/waiting/routing correction, `130` interruption. Runtime logs under
`.forgeflow/runtime/` are disposable diagnostics, never workflow authority.

## Upgrading existing projects

Read [migration notes](docs/maintainers/implement-migration.md) before refreshing.
`init --force` preserves artifacts, reports and history. Active `tdd-feature-*.md`
files or TDD routing require a separately authorized evidence migration and HALT
until resolved. They are not renamed automatically. Old PASS evidence does not
prove a new verification obligation.

## Validation and release

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
node --test .forgeflow/tests/*.test.cjs
npm test
python tests/acceptance/ide/manage.py verify
python tests/acceptance/ide/manage.py release-gate
```

The final command intentionally remains blocked until current-version real IDE
results have been captured. Historical results and presentations describe earlier
versions and are not current conformance evidence. CLI validation checks structure,
references, routing and recorded results; independent Review must assess semantic
coverage, actual execution output and business correctness. Legacy prose-only Slice
verification plans require a structured revision for automated CLI routing.

See [architecture](ARCHITECTURE.md), [中文架构](ARCHITECTURE.zh-CN.md),
[release process](docs/maintainers/releasing.md), [contributing](CONTRIBUTING.md),
[security](SECURITY.md), and [license](LICENSE).
