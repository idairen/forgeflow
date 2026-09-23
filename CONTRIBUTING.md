# Contributing To ForgeFlow

Thank you for contributing to ForgeFlow. Contributions may improve the protocol,
Workflows, Adapters, Python CLI, npx installer, Review plugins, tests, examples, or
public documentation.

ForgeFlow is a Technical Preview. Keep changes focused, preserve current behavior
unless the proposal intentionally changes the contract, and distinguish automated
protocol validation from real Agent-host acceptance.

## Development Setup

Requirements:

- Python 3.10 or newer;
- Node.js 18 or newer for installer changes;
- Git;
- Codex or GitHub Copilot CLI only when testing real Runner execution.

```bash
git clone https://github.com/idairen/forgeflow.git
cd forgeflow

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .

forge --help
npm test
```

Do not run `forge init` in the ForgeFlow source checkout as an installation smoke
test. Use a temporary project or the acceptance helpers under
`tests/acceptance/ide/`.

## Repository Areas

| Path | Responsibility |
|------|----------------|
| `.forgeflow/forgeflow.md` | Normative framework entry and precedence |
| `.forgeflow/protocol/` | Artifact, Transition, Handoff and optional invalid-Review recovery contracts |
| `.forgeflow/workflow/` | Workflow ownership and execution contracts |
| `.forgeflow/adapter/` | Thin host-specific launchers |
| `.forgeflow/rules/reviews/` | Review plugin registry and rules |
| `src/forgeflow/` | Optional Python CLI and deterministic state handling |
| `npm/` | Installer-only Node.js package |
| `tests/` | Unit, integration, contract, and real-host acceptance assets |
| `docs/` | User guides, CLI/config reference, migration, testing and release guidance |

The files under `.forgeflow/` are the canonical installed framework source. Avoid
duplicating normative rules in Adapters, README examples, or CLI code.

## Branch And Pull Request Workflow

The repository uses `main` as its default integration branch.

1. Fork the repository and create a focused branch from current `main`.
2. Make the smallest coherent change that resolves the issue.
3. Add or update tests for deterministic behavior.
4. Record user-visible changes under `Unreleased` in `CHANGELOG.md`.
5. Update affected documentation and examples.
6. Push the branch and open a pull request against `main`.

Suggested branch names include `feature/<topic>`, `fix/<issue>`, and `docs/<topic>`.
Conventional Commit-style subjects are preferred but not required.

## Quality Gates

Run these checks from an editable development environment:

```bash
python -m compileall -q src/forgeflow
python -m unittest discover -s tests -p 'test_*.py'
python tests/acceptance/ide/manage.py verify
npm test
node --test .forgeflow/tests/*.test.cjs
npm pack --dry-run --json
python scripts/check_docs.py
```

These commands validate repository behavior and test assets. They do not prove model
quality or IDE compatibility. A claim about Codex or Copilot host behavior requires
a real invocation and evidence recorded through `tests/acceptance/ide/`.

## Change-Specific Expectations

### Protocol Or Workflow Changes

- identify the affected ownership, scope, Artifact, and Handoff invariants;
- update the authoritative framework file rather than only an Adapter launcher;
- add contract or resolver coverage for deterministic behavior;
- consider Forward, Return, Recovery, incremental, stale-evidence, and terminal paths;
- update both architecture languages when the public architecture changes.

### Python CLI Changes

- construct external commands without shell interpolation;
- keep file operations inside the intended project roots;
- preserve exit-code and runtime-evidence behavior;
- cover parsing, state resolution, interruption, timeout, and failure paths as relevant.

### npx Installer Changes

- keep the npm package installer-only;
- do not reimplement Python `plan`, `run`, `status`, `reset`, or `handoff` commands;
- preserve project-owned Artifacts, Reports, runtime evidence, supported config, and
  custom Review plugins during forced refresh;
- reject symbolic-link paths that could escape the project.

### Review Plugin Changes

Create `.forgeflow/rules/reviews/<plugin>/rules.md` and register the plugin in
`.forgeflow/rules/reviews/_index.md`. Rules must be scoped, testable, ordered, and
compatible with Review's canonical PASS/FAIL ownership. See `PLUGINS.md`.

### Documentation Changes

- use relative links for repository files;
- keep capability claims limited to implemented and verified behavior;
- label future direction explicitly;
- keep English and Chinese counterparts aligned when both exist;
- update `CHANGELOG.md` for user-visible changes.

## Pull Request Checklist

- [ ] The PR explains the problem, approach, and affected contract.
- [ ] The change is scoped and contains no unrelated cleanup.
- [ ] Deterministic tests pass and new behavior has coverage.
- [ ] Real-host claims include host, version, model, mode, and captured evidence.
- [ ] Documentation and examples match current behavior.
- [ ] `CHANGELOG.md` records user-visible changes.
- [ ] No secrets, generated runtime evidence, temporary profiles, or local paths are
      committed.
- [ ] Breaking changes and migration steps are explicit.

## Security Reports

Do not open a public issue for a suspected vulnerability. Follow `SECURITY.md`.

## Contribution License

By submitting a contribution, you agree that it may be distributed under the
repository's MIT License and that you have the right to submit it.

## Support and project decisions

Use the GitHub bug form for reproducible defects and the feature/protocol forms
for proposals. For usage questions, use the [usage question form](https://github.com/idairen/forgeflow/issues/new?template=question.yml) after checking [troubleshooting](docs/troubleshooting.md). Include the commit/version, OS, Python/Node versions, adapter/host
versions, model, reproduction steps and redacted evidence. Distinguish actual host
execution from automated fixtures. Account and host-provider issues belong to the
respective provider. Support is best-effort; production suitability is not promised.

The repository owner, `@idairen`, maintains releases, security response and merge
decisions. Contributors propose changes through pull requests. Changes to ownership,
entry, versions, Handoffs or package identity need a recorded design rationale;
record decisions in issues, pull requests or the Changelog. Follow the
[code of conduct](CODE_OF_CONDUCT.md).

Current priorities are real-host acceptance, contract regression coverage and a
reproducible end-to-end example. These are maintenance goals, not delivered
capabilities or promised dates. Releases follow the
[release process](docs/maintainers/releasing.md); current acceptance results must
support every compatibility claim.
