# Local release preparation report

Date: 2026-09-22. Scope: align the external Python CLI, npm installer,
documentation, and acceptance tooling with the existing `.forgeflow` contracts.
The framework itself was not changed. Package versions remain 0.1.0; these changes
are unreleased. No tag, registry upload, or remote release was created.

## Changes

- Implement replaces TDD as a workflow, command, artifact type, and knowledge key.
  TDD remains a supported verification strategy.
- Parsing checks structured verification plans, strategy selection and evidence,
  current Lane metadata, canonical identifiers, and legacy active artifacts.
- Routing applies global readiness barriers, declared delivery order, Grill Lane
  eligibility, ordered Handoff projections, and explicit recovery entry checks.
- Attempt inspection accounts for archived records and invalid-Review recovery
  receipts. Receipt integrity checks do not authorize automatic evidence disposal.
- Default knowledge queries avoid history enumeration. History is explicit.
- Both installers remove retired managed TDD launchers during forced refresh,
  preserve project evidence, and ship the current framework.
- Public documentation describes current behavior and migration limits. Historical
  IDE evidence is separate from the new acceptance suite; CI includes package smoke
  checks and the Markdown regression suite.

See [migration details](implement-migration.md) for breaking changes and limits.

## Local validation

| Check | Result |
|---|---|
| Python unit, integration, and repository contract tests | 100 passed |
| Markdown contract regressions | 35 passed |
| npm installer tests | 10 passed |
| IDE suite structure | 25 cases and 12 workflow prompts verified |
| Python wheel and sdist build | Passed |
| Wheel build from extracted sdist | Passed |
| Isolated wheel installation, initialization, and bootstrap status | Passed |
| Local npm tarball installation and initialization | Passed |
| Packaged Python source and framework template comparison | Matched checkout |
| Whitespace check and unchanged `.forgeflow` diff | Passed |

These are local results. The configured CI Python/Node matrix has not been run in
this session. Mocked runner tests and static Markdown checks do not demonstrate
real agent or IDE compliance, evidence truthfulness, or semantic review quality.

## Release gate

**BLOCKED:** all 24 P0 IDE cases are NOT RUN; the one P1 case is also NOT RUN.
Current-version evidence from the prescribed Codex and Copilot adapters is required.
Historical PASS results are not reused. Run:

```sh
python3 tests/acceptance/ide/manage.py release-gate
```

Protected multi-file mutations remain the executing participant's responsibility;
the CLI does not supply a portable transaction service. Outstanding framework
contract ambiguities still require separate review and any authorized core repair.
This report records local preparation, not approval to publish.
