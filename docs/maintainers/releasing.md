# ForgeFlow Release Process

This checklist separates repository readiness, package verification, real-host
acceptance, and publication. A prepared test case is not a passed acceptance test.

## 1. Define The Release

- choose the Semantic Version and intended stability level;
- confirm `pyproject.toml` and `package.json` use the same version;
- move completed entries from `Unreleased` into a dated release section;
- document breaking protocol or package changes and migration steps;
- confirm the ForgeFlow name and distribution identifiers remain acceptable for use.

## 2. Verify Repository State

```bash
git status --short
python -m compileall -q src/forgeflow
python -m unittest discover -s tests -p 'test_*.py'
python tests/acceptance/ide/manage.py verify
npm test
```

The working tree must contain no generated runtime evidence, local paths, secrets,
temporary browser profiles, or unreviewed binary output.

## 3. Verify Installable Artifacts

Build and install the Python wheel in a clean environment. Pack the npm tarball,
install it into a temporary project, and execute its `forgeflow init` binary. Inspect
both package manifests before publication.

The npm artifact must remain installer-only. The Python artifact must contain the
current canonical `.forgeflow/` template and provide the `forge` command.

## 4. Record Real-Host Acceptance

Use `tests/acceptance/ide/` to capture critical Codex and Copilot evidence. At
minimum, cover:

- launcher discovery and native-plan isolation;
- single and multiple Feature progression;
- single and multiple Slice progression;
- Return to the correct decision owner;
- Recovery from stale or contradictory evidence;
- same-project incremental Plan behavior;
- Plugin-Based Review PASS and FAIL behavior;
- terminal Project completion.

Record host, version, Adapter, model, mode, input, response, file changes, Handoff,
and final status. Do not convert `NOT RUN` to `PASS` without a real invocation.

```bash
python tests/acceptance/ide/manage.py summary
python tests/acceptance/ide/manage.py release-gate
```

The release-gate command must pass before an IDE core release is approved. It does
not execute an IDE or replace maintainer review of the captured evidence.

## 5. Prepare GitHub

- require the Quality workflow on the default branch;
- disable force pushes and branch deletion for the protected default branch;
- enable Private Vulnerability Reporting;
- verify Issues, templates, CODEOWNERS, license, topics, description, and social card;
- review open P0 defects and security reports;
- decide whether Discussions are useful for the current maintainer capacity.

These repository settings are configured on GitHub and cannot be proven by local
files alone.

## 6. Publish

1. Merge the release preparation with all required checks passing.
2. Create an annotated `vX.Y.Z` tag from the reviewed commit.
3. Create a GitHub Release from the matching Changelog section.
4. Publish the scoped npm package only after registry ownership, 2FA or trusted
   publishing, provenance, and package contents are verified.
5. Publish a Python distribution only after its final public name and ownership are
   intentionally approved; source installation remains the documented fallback.
6. Re-run public installation commands from a clean temporary directory.

Do not describe a package as publicly available until the registry lookup and clean
installation succeed.

## 7. Post-Release

- verify GitHub and registry metadata, checksums, links, and installation commands;
- open a new `Unreleased` section if needed;
- monitor issues and security reports;
- record any known limitations without overstating compatibility.
