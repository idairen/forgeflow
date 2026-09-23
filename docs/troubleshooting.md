# Troubleshooting

Start with the exact command, stdout, stderr and exit code. For an initialized
project, run `forge status` from the directory containing `forgeflow.json` and retain
its diagnostics. Keep original evidence until the cause is understood. These are
operating instructions; the [core](../.forgeflow/forgeflow.md) owns entry and recovery.

| Symptom | Check | Next action |
| --- | --- | --- |
| `forge` is not found | Was the Python environment activated? Does its `bin/forge --help` work? | Activate the installation environment or use the absolute executable path. The npm installer does not install `forge`. |
| Configuration not found | Current directory and presence of `forgeflow.json` | Change to the initialized project root. Initialize only if this project has no installation; the CLI does not search parent directories. |
| Unsupported field or invalid config value | Compare JSON to the [config reference](reference/cli.md#project-configuration) | Correct the specific field. Keep the canonical artifact path; do not add undocumented model/API-key fields. |
| Initialization says files already exist | Inspect `.forgeflow/` and `forgeflow.json` | If this is an upgrade, inspect the [migration guide](maintainers/implement-migration.md), preserve evidence, then explicitly refresh with the intended adapter. |
| Refresh rejects a symbolic link | The named path and its destination | Investigate the layout and use a normal project-owned installation path. Do not remove evidence or weaken the installer check to force the refresh. |
| Launcher does not appear in the IDE | Selected host, prompt discovery configuration, and adapter file presence | Follow the [host entry instructions](quickstart.md#ide-entry-and-verification). File installation alone does not register a command menu. |
| Agent executable missing or authentication fails | Selected adapter and whether its executable is installed/authenticated in this environment | Resolve installation or account access using the host's instructions. ForgeFlow does not manage provider credentials. |
| Agent rejects a flag or model | Exact external executable version, error, and configured model | Compare with the [backend boundary](reference/cli.md#agent-processes-and-logs). Record the incompatibility; mocked runner tests do not prove host compatibility. |
| Execution times out or is interrupted | Agent output, changed files, current graph and any ACTIVE claim | Preserve partial work. Confirm the previous execution stopped before any eligible claim recovery. Raising the timeout does not release a claim or undo writes. |
| Plan asks a question and exits | Is it an IDE conversation or a single CLI invocation? | Use the [clarification instructions](quickstart.md#3-choose-the-execution-interface). Do not fabricate a continuation token or Handoff. |
| Missing/invalid/stale Handoff or routing correction | Complete response, final canonical block, current graph and requested workflow | Save the correction and make a fresh authorized invocation. `forge handoff` JSON is a historical view, not the canonical response file. |
| `BLOCKED` or a wait | Recorded blocker owner/scope, missing decision/evidence, and claim state | Supply the missing decision or evidence through the owner workflow's valid entry. Use claim-specific recovery only when its prerequisites hold. |
| `HALTED` / contradictory graph | Exact parser/resolver diagnostics and referenced files/versions | Preserve evidence and diagnose the contradiction. Any repair or migration needs its own authorization; ordinary workflow commands cannot silently repair it. |
| Active legacy TDD files | Whether they are active evidence or explicitly historical material | Follow [Implement migration](maintainers/implement-migration.md). Do not simply rename them, delete history or inherit an old PASS. |
| Required verification unavailable | Approved obligations, environment and evidence source | Keep checks pending or record the appropriate blocker. Convenience does not authorize weakening mandatory checks. |
| Exit code `2` | stderr for usage errors; stdout for workflow outcome | Correct invalid arguments or handle the actual wait/correction. The code alone cannot distinguish them. |

`forge reset --force` and `forge run --reset` rotate project evidence. They are not
general troubleshooting commands. Likewise, `init --force` refreshes managed files;
it does not migrate active artifacts or make incompatible evidence valid.

## Asking for help

Use the [usage question form](https://github.com/idairen/forgeflow/issues/new?template=question.yml)
for help and the bug form for reproducible defects. Include:

- package/commit and framework version, OS, Python/Node versions;
- IDE/extension or external CLI version, adapter and model;
- exact command or host input, observed result and expected result;
- redacted stdout/stderr, graph diagnostics and relevant artifact versions;
- whether an agent process or Lane is still active and what has already been tried.

Do not publish credentials, private source or unreviewed full transcripts. Report
suspected vulnerabilities through the [security policy](../SECURITY.md).
