# ForgeFlow Release Process

This checklist separates repository readiness, package verification, real-host
acceptance, and publication. A prepared test case is not a passed acceptance test.

Current migration notes: [Implement migration](implement-migration.md). Current IDE
evidence is isolated under `tests/acceptance/ide/results/current/`; old results do
not satisfy this release gate.

## Source publication and validated releases

Publishing source under the repository's MIT License does not itself establish
host compatibility or production readiness. Keep the Technical Preview label and
state unverified capabilities explicitly. Community documents support maintenance;
their existence is not an acceptance test.

For a validated IDE core release, follow all gates below. Query current results
with `manage.py summary` and `manage.py release-gate`; do not reuse a dated local
readiness report as approval. Review CI for the exact candidate commit, scan the
intended Git history and package contents for sensitive material, and check rights
and attribution for contributed or third-party content. Local files cannot prove
remote repository protections, registry ownership or public installability.

## 1. Define The Release

- choose the Semantic Version and intended stability level;
- confirm `pyproject.toml`, `package.json` and `src/forgeflow/__init__.py` use the same version;
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
node --test .forgeflow/tests/*.test.cjs
python scripts/check_docs.py
```

The working tree must contain no generated runtime evidence, local paths, secrets,
temporary browser profiles, or unreviewed binary output.

## 3. Verify Installable Artifacts

Build and install the Python wheel in a clean environment. Pack the npm tarball,
install it into a temporary project, and execute its `forgeflow init` binary. Inspect
both package manifests before publication.

The npm artifact must remain installer-only. The Python artifact must contain the
current canonical `.forgeflow/` template and provide the `forge` command.

### Reproducible local package checks

Install `build` in the active development environment. From the repository root:

```bash
python -m build --sdist --wheel
npm pack --pack-destination dist
python scripts/verify_packages.py \
  --wheel dist/forgeflow-0.1.0-py3-none-any.whl \
  --sdist dist/forgeflow-0.1.0.tar.gz \
  --npm dist/idairen-forgeflow-0.1.0.tgz
python examples/complete-delivery/check.py
```

Use the actual filenames for the chosen release version; do not mix older artifacts
from the output directory. The archive checker compares bundled contracts and
Python sources byte-for-byte with the checkout, verifies the license and installer
entrypoint, rejects project evidence/unsafe paths, and emits SHA256 digests. It is
not a complete malware, secret or legal-provenance scanner.

For a clean local install, create a fresh virtual environment and install the wheel
with `python -m pip install --no-index /absolute/path/to/the.whl`. Follow the
[quickstart](../quickstart.md) in a new project. Separately run the npm tarball with
`npm exec --yes --package /absolute/path/to/the.tgz -- forgeflow init --adapter copilot`.
Neither operation publishes a package or runs an Agent.

## 4. Record Real-Host Acceptance

Use the [current plan](../testing/ide-test-plan.zh-CN.md) and
[acceptance instructions](../../tests/acceptance/ide/README.md) to capture evidence
for every required adapter. At minimum, cover:

- launcher discovery and native-plan isolation;
- single and multiple Feature progression;
- single and multiple Slice progression;
- Return to the correct decision owner;
- Recovery from stale or contradictory evidence;
- default Subsequent Plan behavior;
- structured Solution dependency and shared-component impact behavior;
- source/test placement contracts and blocking layout conformance;
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

### Read-only remote verification

Run these with a working GitHub login; a failed request is unverified, not PASS:

```bash
gh repo view idairen/forgeflow --json nameWithOwner,isPrivate,defaultBranchRef,url
gh run list --repo idairen/forgeflow --commit "$(git rev-parse HEAD)"
gh api repos/idairen/forgeflow/rulesets
gh api repos/idairen/forgeflow/branches/main/protection
gh api repos/idairen/forgeflow/private-vulnerability-reporting
npm whoami
npm owner ls @idairen/forgeflow
```

Use the actual default branch if it differs from `main`. A 404 for one protection
endpoint may mean missing access or a different protection mechanism; review both
rulesets and classic protection, including bypasses and required check names.
Registry package lookup alone does not prove publishing rights. Confirm Python
project ownership using the intended maintainer account before uploading; do not
assume the generic `forgeflow` name is available. No name or version is changed
automatically by these checks.

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

After explicit release authorization, use the reviewed distributions, not a rebuild
with different contents. For example, `npm publish dist/<reviewed-package>.tgz`
and `python -m twine upload dist/<reviewed-wheel>.whl dist/<reviewed-sdist>.tar.gz`
are publishing actions, not preflight checks. Select authentication/provenance
settings for the intended registry account before running them. Never paste tokens
into an issue, command example, Artifact or captured acceptance result.

## 7. Post-Release

- verify GitHub and registry metadata, checksums, links, and installation commands;
- open a new `Unreleased` section if needed;
- monitor issues and security reports;
- record any known limitations without overstating compatibility.

## Source and attribution review

The repository uses MIT and declares no Python or npm runtime dependencies. Build,
test and host tools retain their own licensing and must be reviewed if redistributed.
Git authorship alone does not prove that every contributed file has redistribution
rights. Review imported/generated assets and third-party snippets at the release
commit and retain any required notices.

The maintainer identified the retired roadshow artwork and presentation PDFs as
self-created/generated content and chose not to publish them. This public repository
starts from a source snapshot that excludes those files and the earlier private
Git history. Keep private history and retired assets out of future imports; a
normal file deletion does not remove material already committed to public history.
