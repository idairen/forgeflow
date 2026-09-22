# First run from a source checkout

This path uses local source, so it does not depend on a published package or registry
ownership. Shell examples below use macOS/Linux. Windows host behavior is not claimed
without corresponding evidence; see [compatibility](testing/compatibility.md).

## 1. Install the Python CLI

From the cloned ForgeFlow repository, with Python 3.10+ available:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
forge --help
```

Keep the environment active. This installs `forge`, not the external Codex or
Copilot executable and not IDE extensions. For installation errors, retain the
command and error text; do not run the workflow until `forge --help` succeeds.

## 2. Initialize a separate project

```bash
project_root="$(mktemp -d)/forgeflow-first-run"
mkdir -p "$project_root"
cd "$project_root"
forge init --adapter codex
forge status
```

Choose `--adapter copilot` instead when testing that host. The expected empty-project
status is `current_workflow: plan`, `target_scope: Project`, with the bootstrap
rule. No Planning or application code should exist yet. Run `forge init` without
`--force` for a new project; forced refresh is an upgrade operation.

## 3. Choose the execution interface

**IDE:** open the initialized project, enable/discover its six launcher files using
the host's supported configuration, and invoke the Plan launcher. The dedicated
files are under `.forgeflow/adapter/codex/` or `.forgeflow/adapter/copilot/`.
Installation alone does not register every host's command menu. Generic Markdown
participants read the framework, Artifact, Transition, Handoff and exactly one
authorized Workflow in order.

**Python orchestrator:** separately install and authenticate the selected external
agent executable. The current backends invoke `codex exec` or `gh copilot`; confirm
that the installed version supports the command shown by this checkout's backend.
Then start with an explicit project intent:

```bash
forge plan --intent "Describe the project outcome and confirmed scope here"
```

Use the [inventory tutorial](../examples/complete-delivery/README.md) for a concrete
intent and six-workflow walkthrough. During clarification, supply the answer in the
same authorized host conversation; do not invent a continuation token or start an
unrelated workflow. A CLI process does not preserve an IDE conversation session.

## 4. Follow the handoff

Save the full workflow response, including its final canonical Handoff, to a file
outside the active Artifact Root. In a new invocation use the selected workflow:

```bash
forge grill --handoff /absolute/path/to/plan-response.md
```

The filename above is a placeholder for actual captured output, not a generated
sample to copy. Let current resolution determine subsequent commands. A correction
response or exit code 2 is a stop/wait, not permission to continue inside that call.
Use `forge status` to inspect the graph; use `forge handoff` only as a historical
runtime view and revalidate it before reuse. The external `forge run --auto`
orchestrator may execute distinct authorized steps, but waits still require action.

## First-time user check

Ask a person unfamiliar with the repository to follow the instructions above and
record the following in an issue or PR, redacting credentials:

| Check | Evidence to capture |
| --- | --- |
| Install and `forge --help` | OS, Python version, command and outcome |
| Initialize a fresh project | Adapter, created paths and any unexpected overwrite |
| Inspect bootstrap status | Full status output; no invented project artifacts |
| Discover the intended IDE launcher | IDE/extension version and how it was discovered |
| Complete the inventory workflow | Actual questions, responses, Handoffs, test output and final graph |
| Explain the next action | Whether the user understood a wait, correction, RETURN or completion |

Record elapsed time and confusing steps as observations, not performance claims.
Do not mark this usability exercise passed merely because installation smoke tests
pass. The local automated checks cover packaging and commands, not a new user's
understanding or host behavior.

Common checks: if `forge` is missing, activate the installation environment; if a
launcher is absent, verify host discovery; if the graph is HALTED, preserve the
reported evidence and diagnose it instead of deleting artifacts; if required
verification is unavailable, keep it pending or blocked rather than claiming PASS.
