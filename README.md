# ForgeFlow

ForgeFlow is a repository-native Markdown protocol for AI-assisted software delivery,
with an optional Python CLI and an npm framework installer. **Technical Preview**:
local tests and package checks do not establish host compatibility. See the
[compatibility and evidence table](docs/testing/compatibility.md) for the inspected real-project
case, its version baseline and remaining host metadata.

The normative source is [`.forgeflow/`](.forgeflow/forgeflow.md): Framework 3.8,
Artifact 2.19, Transition 1.8, Handoff 2.15, and Implement 2.13. The CLI follows
those contracts; it does not supersede them or decide whether a model's evidence is true.

## When to use ForgeFlow

Use ForgeFlow when a change needs explicit business decisions, scoped delivery,
traceable verification and independent Review. It can guide a new application or
an approved change to an existing codebase. The six workflow boundaries and retained
evidence add work; consider that cost for one-off edits that need little coordination.
It does not supply a hosted agent, provider account or universal IDE registration.

Start with the [quickstart](docs/quickstart.md), then the
[delivery tutorial](examples/complete-delivery/README.md). For an existing codebase,
use the [adoption guide](docs/existing-projects.md). Keep the
[CLI/config reference](docs/reference/cli.md) and
[troubleshooting guide](docs/troubleshooting.md) nearby.

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
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
forge --help
```

Keep this environment active when changing to a target repository. Alternatively,
use the absolute path to the installed `.venv/bin/forge` command:

```bash
forge init --adapter codex
# Or: forge init --adapter copilot
forge status
forge plan --intent "Describe the approved project objective"
```

The selected agent executable must be installed and authenticated separately.
Initialization installs repository launchers; IDE discovery/registration depends on
the host. Generic Markdown participants can read the core directly.

## Install the npm Technical Preview

The public npm package is [`@dairen/forgeflow`](https://www.npmjs.com/package/@dairen/forgeflow),
an **installer only** requiring Node 18+. In your application directory:

```bash
npx --yes @dairen/forgeflow@0.1.0 init --adapter codex
# Or use the Copilot adapter:
npx --yes @dairen/forgeflow@0.1.0 init --adapter copilot
```

Use `@next` instead of `@0.1.0` to follow the moving preview tag. Both commands
install framework files; neither installs Python, an agent executable or an IDE
extension. Follow the [host entry instructions](docs/quickstart.md#ide-entry-and-verification)
after initialization. The Python CLI is optional for IDE use.

To test a local package from a source checkout:

```bash
npm pack --pack-destination /tmp
# In a disposable target directory; use the actual tarball emitted above:
npm exec --yes --package /absolute/path/to/dairen-forgeflow-0.1.0.tgz -- forgeflow init --adapter codex
```

GitHub Release v0.1.0 retains its original `@idairen/forgeflow` tarball as historical
release content. The npm registry package uses `@dairen/forgeflow` after the scope
correction; these are distinct package identities. PyPI publication is not claimed.

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

Exit codes: `0` successful step/completion, `1` execution or validation error, `2`
incomplete/waiting/routing correction **or command-line argument parsing error**
(such as an unknown subcommand), `130` interruption. Inspect the response and
stderr before treating `2` as a workflow wait. Runtime logs under
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

The final command evaluates the current-version IDE records on disk. Reported
successful runs must be archived and mapped to cases before the gate can confirm
their coverage. Historical IDE results describe earlier versions and are not current conformance
evidence. CLI validation checks structure,
references, routing and recorded results; independent Review must assess semantic
coverage, actual execution output and business correctness. Legacy prose-only Slice
verification plans require a structured revision for automated CLI routing.

See [architecture](ARCHITECTURE.md), [中文架构](ARCHITECTURE.zh-CN.md),
[release process](docs/maintainers/releasing.md), [contributing](CONTRIBUTING.md),
[security](SECURITY.md), and [license](LICENSE).

## Documentation and support

Use the [documentation index](docs/README.md) to find migration and testing guides.
Follow the [first-run guide](docs/quickstart.md) and
[complete delivery tutorial](examples/complete-delivery/README.md) for a runnable
application defect/repair example and all six workflow steps. The earlier
[sample checkpoint](examples/sample-project/README.md) illustrates Plan/Grill only.
Teaching fixtures are not substitutes for independent real-host evidence.
For questions, defect reports and project decisions, see
[contributing and support](CONTRIBUTING.md#support-and-project-decisions).

ForgeFlow is distributed under the [MIT License](LICENSE). Source availability,
package publication and a validated host release are distinct milestones. The
release gate reports the current evidence; no stored test count is a release approval.
