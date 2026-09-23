# First run

For IDE-only use, install the npm preview in your application directory with
`npx --yes @dairen/forgeflow@0.1.0 init --adapter codex` (or `copilot`), then follow
[host entry and verification](#ide-entry-and-verification). Python is not needed
for this installer path; `forge status` requires the separate Python CLI.

The steps below install the optional Python CLI from source. Shell examples use macOS/Linux. Windows host behavior is not claimed
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

**IDE or agent conversation:** open the initialized project in the selected host
and use the [entry instructions below](#ide-entry-and-verification). The dedicated
launcher files are under `.forgeflow/adapter/codex/` or
`.forgeflow/adapter/copilot/`. Installation alone does not register every host's
command menu. Generic Markdown participants read the framework, Artifact,
Transition, Handoff and exactly one authorized Workflow in order.

**Python orchestrator:** separately install and authenticate the selected external
agent executable. The current backends invoke `codex exec` or `gh copilot`; confirm
that the installed version supports the command shown by this checkout's backend.
Then start with an explicit project intent:

```bash
forge plan --intent "Describe the project outcome and confirmed scope here"
```

Use the [inventory tutorial](../examples/complete-delivery/README.md) for a concrete
intent and six-workflow walkthrough.

In an IDE, answer clarification questions in the same authorized host conversation.
The Python CLI instead launches a single agent process per invocation: it does not
provide an interactive clarification loop or a command to resume that conversation.
Codex runs with `--ephemeral`; Copilot runs with `--no-ask-user`.

If a CLI Plan call asks for clarification, retain its questions and inspect
`forge status`. If the project is still at Bootstrap with no Planning artifact and
an empty Reports Root, make a new `forge plan --intent "..."` call containing the
complete original intent and your explicit answers. This is a fresh invocation,
not a resumed conversation. For clarification in a later workflow, use the IDE
host with the captured context and the current workflow's required entry or
recovery authorization. Do not reset evidence, invent a continuation token, or
advance to the next workflow merely to bypass a question.

## 4. Follow the handoff

Save the full workflow response, including its final canonical Handoff, to a file
outside the active Artifact Root. In a new invocation use the selected workflow:

```bash
forge grill --handoff /absolute/path/to/plan-response.md
```

The filename above is a placeholder for actual captured output, not a generated
sample to copy. Let current resolution determine subsequent commands. A correction
response ends the invocation. Exit code `2` can mean incomplete execution, waiting,
routing correction, or a command-line argument error; inspect the response and
stderr to distinguish them. It never authorizes automatic progression.
Use `forge status` to inspect the graph; use `forge handoff` only as a historical
runtime view and revalidate it before reuse. The external `forge run --auto`
orchestrator may execute distinct authorized steps, but waits still require action.

## IDE entry and verification

The maintainer confirmed these invocation forms on 2026-09-22. They are reported
working entry points, not a claim that every host version discovers the files
without configuration. The exact discovery settings and extension/CLI versions
for these two invocation forms have not been supplied.

| Interface | Where to type | Plan invocation |
| --- | --- | --- |
| IntelliJ IDEA + Copilot | Copilot conversation in the project | `/forge-plan` |
| Codex CLI | Inside the Codex conversation opened for the project | `forge-plan` |
| Optional Python orchestrator | Terminal in the initialized project root | `forge plan --intent "..."` |

For either conversation interface:

1. Initialize with the matching adapter: `forge init --adapter copilot` for
   IntelliJ + Copilot, or `forge init --adapter codex` for Codex.
2. Open the initialized application root in the host. Confirm that
   `.forgeflow/adapter/<adapter>/forge-plan.prompt.md` exists and is accessible.
3. Enter the reported invocation in that host's conversation and supply your
   explicit project intent. `forge-plan` inside Codex is not a standalone shell
   executable installed by the Python or npm package.
4. Inspect the response and changes. The launcher requires the Framework,
   Artifact, Transition, Handoff and Plan contracts, in order. Plan may ask
   questions and wait; it must not switch to a generic native planning mode or
   begin implementing application code.
5. When Plan legitimately finishes, retain its canonical Handoff. Start the next
   authorized workflow in a new invocation with that complete context. Its target
   comes from current resolution, not from this tutorial's assumed sequence.

If the host cannot find the launcher, first check the selected adapter and project
root, then its prompt discovery settings. Do not infer registration from the
presence of a Markdown file. The acceptance helper configures VS Code Copilot
prompt locations, but that is not an IntelliJ configuration recipe. Capture the
actual host settings when documenting a new working installation.

This invocation confirmation is separate from the
[historical task-manager artifact case](testing/evidence/task-manager/README.md).
It does not independently identify which host produced each archived artifact or
establish current-version acceptance. See the [compatibility matrix](testing/compatibility.md).

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
