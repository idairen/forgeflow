# Compatibility and evidence

Dedicated adapter files indicate an integration path, not a promise that every
host/model/version combination behaves identically. Match claims to a specific
framework revision and retrievable run evidence.

## Real IDE execution

The maintainer supplied a real offline task-manager workspace. Its artifacts now
support recorded Plan/Grill/Solution/Slice/Implement/Review activity, a concrete
FAIL → rework → PASS chain and an invalid-Review disposition with a verified receipt
digest. See the [sanitized case and manifest](evidence/task-manager/README.md).

This is an inspected **Framework 3.7 / Artifact 2.18 / Implement 2.12** working-tree
baseline, not blanket certification of the current 3.8 / 2.19 / 2.13 release.
F-01 has matching recorded PASS pairs; the project snapshot does not establish
whole-project current completion. A current-CLI compatibility probe reports HALTED;
the case records the exact differences rather than suppressing them.

| Path | Available implementation | Evidence status |
| --- | --- | --- |
| IntelliJ IDEA 2026.2.1 | Codex adapter; model `gpt-6-astra` | Host, adapter and model confirmed by the maintainer; project execution records inspected on the historical baseline |
| Codex extension / CLI | Exact version not supplied | Do not infer a specific extension or CLI build from the adapter name |
| Copilot IDE | Six dedicated Markdown launchers | No supplied run establishes Copilot parity |
| Generic Markdown hosts | Core contracts may be loaded directly | No additional dedicated integration or tested host is claimed |

The host attribution above comes from the maintainer’s explicit confirmation, not
from the project directory name. The evidence source is the supplied project’s
`.forgeflow/artifacts/`; selected excerpts and content hashes are archived in the
linked case. Host OS version and extension/CLI version remain unspecified.

For each real run, record: date, Git commit, Framework version, OS, IDE/extension
versions, adapter, model/mode, exercised scenarios, outcome and sanitized evidence
links. Map only scenarios actually observed to the
[current plan](ide-test-plan.zh-CN.md). One successful happy path cannot stand in
for concurrent claims, upstream rework or recovery failures.

Place reviewed case records under `tests/acceptance/ide/results/current/`, using the
[acceptance instructions](../../tests/acceptance/ide/README.md). The release gate
checks those records; absent records mean the gate cannot establish coverage, not
that it has independently disproved a maintainer's reported success.

## Reported invocation forms

On 2026-09-22 the maintainer additionally confirmed `/forge-plan` in an IntelliJ
Copilot conversation and `forge-plan` inside a Codex CLI conversation. See the
[entry walkthrough](../quickstart.md#ide-entry-and-verification). Extension/CLI
versions and prompt discovery settings for these entry forms were not supplied.
This establishes reported invocation forms, not Copilot parity, current-suite PASS,
or a new host attribution for each artifact in the historical case above.

## Tooling matrix

| Component | Declared target | Evidence boundary |
| --- | --- | --- |
| Python package/CLI | Python 3.10+ | CI configured for Ubuntu with Python 3.10 and 3.13; verify results on the candidate commit |
| npm installer | Node 18+ | CI configured for Ubuntu with Node 18 and 22; verify results on the candidate commit |
| Local automated validation | macOS 26.6.2 arm64, Python 3.14.6, Node 22.23.1 | Local checks; not a Windows/Linux or real-agent certification |
| CLI agent backends | `codex exec` and `gh copilot` | Require independently installed/authenticated compatible executables; mocked runner tests do not validate provider CLIs |
| Windows | No current host evidence recorded here | Do not infer compatibility from pure Python/JavaScript source alone |

Package initialization, graph parsing, agent execution and IDE prompt discovery are
separate checks. Core-required atomic claims and protected multi-file publication
also depend on host capabilities; ForgeFlow does not supply a universal transaction
service. Preserve these limits when announcing a release.

## npm registry installation

The [2026-09-23 registry installation report](evidence/npm-install-2026-09-23.md)
records anonymous cold-cache installation for both adapters and archive integrity.
This validates installer availability, not IDE or agent behavior.

## Reproduce local checks

The [2026-09-23 local installation report](evidence/local-install-2026-09-23.md)
records the maintainer's successful wheel/npm installation walkthrough, its
associated checkout baseline, observed environment and missing raw-run evidence.
This is separate from real-host acceptance and remote CI.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
node --test .forgeflow/tests/*.test.cjs
npm test
python3 examples/complete-delivery/check.py
```

For package comparison and isolated installation, follow the
[release checks](../maintainers/releasing.md#reproducible-local-package-checks).
These commands were exercised during local preparation on 2026-09-22. The public
repository starts from a source snapshot with separate Git history. Check CI and
repository protection settings for its exact candidate commit; earlier private
repository checks do not establish the public repository settings.
