# CLI and configuration reference

The optional Python `forge` CLI executes the installed Markdown contracts. The npm
`forgeflow` executable only installs them. For a first run, use the
[quickstart](../quickstart.md); for failures, use [troubleshooting](../troubleshooting.md).
Run project commands from the directory containing `forgeflow.json`; the Python
CLI does not search parent directories or provide a `--config` option.

## Python commands

`forge --help` (or `-h`) lists commands; `forge COMMAND --help` lists its options.
Running `forge` without a command displays help. The tables below describe the
Python interface; options are not automatically shared between commands.

| Command | Options | Behavior |
| --- | --- | --- |
| `forge init` | `--adapter` / `-a` (`copilot` or `codex`, default `copilot`); `--force` | Install framework and config in the current directory. Existing installation paths require an explicit forced refresh. |
| `forge plan` | `--intent` / `-i`; `--handoff`; `--incremental` | Execute authorized Plan. Non-empty intent with existing Planning requests Subsequent Plan. `--incremental` is a deprecated compatibility flag and requires intent; it is unnecessary for normal subsequent changes. |
| `forge grill` | `--handoff`; `--feature`; `--confirm-inactive` | Execute the resolved Grill scope, or request a specific eligible Lane/Recovery entry with `--feature F-01`. `--feature` cannot be combined with `--handoff`. |
| `forge solution` | `--handoff`; `--confirm-inactive` | Execute the authorized Solution scope. |
| `forge slice` | `--handoff`; `--confirm-inactive` | Execute the authorized Slice scope. |
| `forge implement` | `--handoff`; `--confirm-inactive` | Execute the authorized Implement scope. |
| `forge review` | `--handoff`; `--confirm-inactive` | Execute independent Review through Handoff Entry. |
| `forge run` | `--auto` / `--auto-mode`; `--manual` / `--no-auto`; `--intent` / `-i`; `--reset` | Auto mode invokes separate authorized steps until completion or a stop condition. Manual mode invokes only Plan. The two mode options are mutually exclusive. |
| `forge status` | No command-specific options | Print JSON containing current graph status, resolution and derived knowledge. Successful inspection does not mean the project is COMPLETE. |
| `forge knowledge` | `--feature`; `--slice`; `--history`; `--impact`; `--component`; `--format` | Query derived knowledge; see examples below. |
| `forge handoff` | No command-specific options | Print the last runtime Handoff as JSON. It is historical context and must be revalidated; this JSON is not a substitute for the canonical response supplied to `--handoff`. |
| `forge reset` | `--force` | Without the flag, print guidance without rotating anything. With it, rotate active artifacts and reports into timestamped sibling directories and create empty evidence roots. |

The shared workflow parser exposes `--confirm-inactive` on Grill through Review.
Its meaning is narrow: explicitly confirm that the exact prior Grill claim execution
has stopped. It is not a general approval, a way to override a blocker, or a substitute
for a required Handoff. The graph and core recovery procedure still determine entry.
For an interrupted Lane, identify it with `forge grill --feature F-01 --confirm-inactive`.

`--handoff FILE` reads a UTF-8 file containing the complete prior response with its
final canonical block. Missing, invalid or stale input may produce read-only routing
correction and stop. Save that response and use a fresh invocation; do not consume a
workflow's own Handoff inside the same call.

**Evidence rotation:** `forge run --reset` rotates evidence before executing, without
an additional `--force` flag or interactive confirmation. Use it only for an explicit
archive/reset decision. Neither reset form is a routine repair for HALTED, BLOCKED,
missing verification, or a failed Review. Refresh and evidence migration are separate;
see [migration](../maintainers/implement-migration.md).

## Knowledge queries

```bash
forge knowledge --feature F-01 --format markdown
forge knowledge --slice F-01/S-01 --history
forge knowledge --impact F-01
forge knowledge --component SC-01
```

`--format` accepts `json` (default) or `markdown`. `--history` includes historical
indexes; it does not make historical evidence current. Filters must name active,
canonical identifiers and compatible scopes. An unavailable impact view does not
authorize inferred dependencies. Query results never authorize workflow progression.

## Project configuration

The root `forgeflow.json` is strict JSON. Unknown fields are rejected. The installed
template is:

```json
{
  "mode": "auto",
  "adapter": "copilot",
  "model": null,
  "execution_timeout_seconds": 900,
  "root_artifact_dir": ".forgeflow/artifacts"
}
```

| Field | Required / default | Meaning |
| --- | --- | --- |
| `mode` | Required; template uses `auto` | `auto` or `manual`. Used by `forge run` unless its mode flag overrides it. Single-workflow commands do not use this to chain workflows. |
| `adapter` | Required; template uses `copilot` | `codex` or `copilot`; selects launcher and external CLI backend. `forge init --adapter codex` writes that selection. |
| `model` | Optional; `null` | Non-empty string passed as `--model` to the agent, or `null` to leave model selection to the host. ForgeFlow does not validate provider model availability. |
| `execution_timeout_seconds` | Optional; `900` | Positive number limiting one external agent process. A timeout terminates the process; it is not inactivity confirmation or evidence rollback. |
| `root_artifact_dir` | Required | Must be exactly `.forgeflow/artifacts`. Custom or absolute artifact roots are rejected. |

Config is loaded from the current project root. A run-mode flag overrides `mode`
for that invocation. There are no Python execution flags for model or timeout;
edit their config fields instead. Forced initialization preserves supported existing
config values, then sets `adapter` to the initializer's selected adapter. Always
specify the intended adapter during refresh; omitting it selects `copilot`.

## Agent processes and logs

Codex uses `codex exec --ephemeral` with a workspace-write sandbox. Copilot uses
`gh copilot` with non-interactive tool permissions. Install and authenticate the
selected executable separately. See [security boundaries](../../SECURITY.md#python-cli-runner)
and [clarification handling](../quickstart.md#3-choose-the-execution-interface).

Workflow execution stores disposable diagnostics in `.forgeflow/runtime/`, including
`steps/`, `runs/`, `last-handoff.json` and `last-run.json`. These are not active
Artifacts. Console diagnostics go to stderr; command output goes to stdout.

Optional `FORGEFLOW_LOG_DIR` enables a `forgeflow.log` file in that directory.
This is a logging environment variable, not a config override mechanism. File
logging can create files even during query commands when explicitly enabled.
Logs and captured responses can contain project context; redact before sharing.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Command completed successfully; for queries, this describes the query, not project readiness. |
| `1` | Caught execution/configuration/validation error, or no valid runtime Handoff for `forge handoff`. |
| `2` | Incomplete workflow/pipeline execution, waiting, routing correction, or an argument parsing error such as an unknown subcommand. Inspect stdout and stderr. |
| `130` | User interruption. |

## npm installer

Use `npx --yes @dairen/forgeflow@0.1.0 init --adapter codex` for a pinned preview,
or replace `@0.1.0` with `@next` to follow the moving preview tag. Local-tarball
installation remains available in the [README](../../README.md#install-the-npm-technical-preview).
The executable supports `init` with
`--adapter` / `-a` and `--force`, plus `--help` / `-h` and `--version` / `-v`.
Its default adapter is `copilot`. Successful invocation returns `0`; rejected
arguments or installation failures return `1`. It does not implement the Python
workflow, query or reset commands, or install external agent executables.
