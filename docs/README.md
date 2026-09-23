# ForgeFlow documentation

The normative source is [`.forgeflow/forgeflow.md`](../.forgeflow/forgeflow.md).
These guides explain it and never override it. Start with the
[project overview](../README.md#when-to-use-forgeflow).

## Start here

- [Quickstart and host entry](quickstart.md): installation, conversation versus
  terminal commands, clarification and the first Handoff.
- [Runnable delivery tutorial](../examples/complete-delivery/README.md): an inventory
  defect/repair exercise and the six workflow steps.
- [Existing projects](existing-projects.md): adopting the framework, incremental
  work and sharing project evidence through a team's Git process.

## Daily use and reference

- [CLI and configuration](reference/cli.md): commands, options, config, logs and exit codes.
- [Troubleshooting](troubleshooting.md): symptoms, diagnostics and authorized next actions.
- [Architecture and glossary](../ARCHITECTURE.md) / [中文架构与术语](../ARCHITECTURE.zh-CN.md).
- [Compatibility and evidence](testing/compatibility.md): host claims and their limits.
- [Implement migration](maintainers/implement-migration.md): framework refresh and legacy evidence.
- [Review plugins](../PLUGINS.md): registry, applicability, thresholds and reports.

## Contribute and release

- [Contributing and support](../CONTRIBUTING.md).
- [Security policy](../SECURITY.md).
- [Release process](maintainers/releasing.md).

Run `python3 scripts/check_docs.py` from the source checkout before submitting
public documentation changes. CI checks local link targets, Markdown heading
anchors, and presence of Python command/option/config names in the reference.
The checker supports repository inline and explicit reference links; it is not a
full Markdown renderer. It does not request external URLs or establish that prose,
examples or host claims are semantically correct; those require review.

## Tests and execution evidence

- [Local Python/npm installation report](testing/evidence/local-install-2026-09-23.md):
  maintainer-reported package installation checks and their associated baseline.
- [Real task-manager case](testing/evidence/task-manager/README.md): historical
  FAIL/rework/PASS and recovery evidence with provenance and baseline limits.
- [Current IDE plan](testing/ide-test-plan.zh-CN.md) and
  [execution instructions](../tests/acceptance/ide/README.md).
- [Knowledge-view test plan](testing/cli-knowledge-test-plan.md).
- [Sample Plan/Grill checkpoint](../examples/sample-project/README.md).

Historical IDE plans and results are retained for traceability, not current
conformance evidence. Teaching fixtures are not real-host acceptance. Retired presentations, artwork and
private development history are excluded from this public source snapshot. Historical
commit IDs retained in evidence identify earlier source baselines; those commits
are not part of this repository history.
