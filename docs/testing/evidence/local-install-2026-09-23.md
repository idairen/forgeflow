# Local package installation report — 2026-09-23

## Attribution and baseline

The maintainer reported running all commands in the supplied local Python/npm
installation walkthrough successfully: “全部命令执行了一遍，都通过。”
This is a maintainer-reported result, not an independently replayed installation
or a captured terminal transcript. The report was recorded on 2026-09-23.

The checkout HEAD inspected immediately after that report was
`c5edbc8e9f891fd453eef727a6153a4182fdd896` on `change-tdd-to-implement`, with a clean
working tree. The walkthrough targeted package version `0.1.0`. No commit ID or
archive hashes were captured in the maintainer's terminal report, so this HEAD is
the associated checkout baseline, not a verified fingerprint of the tested bytes.

Current machine inspection when recording this report found macOS 26.6.2
(build 25G83), Python 3.14.6, Node.js v22.23.1 and npm 10.9.8. These are the
recorder's observed environment values; the maintainer did not separately capture
the versions used in the earlier terminal execution.

## Reported checks

All rows below have status **PASS — maintainer reported**.

| Check | Executed walkthrough operation |
| --- | --- |
| Python packaging | Create a temporary build virtual environment, install `build`, build wheel and sdist with `python -m build --outdir ...`. |
| npm packaging | Run `npm pack --pack-destination ...` into the same temporary package directory. |
| Archive consistency | Run `scripts/verify_packages.py` with the `0.1.0` wheel, sdist and npm tarball. |
| Isolated wheel install | Create a second virtual environment and install the wheel with `pip install --no-index`. |
| Python entrypoint | Run the newly installed `forge --help`. |
| Python initialization | In a fresh temporary application directory, run `forge init --adapter codex` and `forge status`. |
| npm initialization | In another fresh directory, run `npm exec --yes --package <local-tarball> -- forgeflow init --adapter copilot`. |
| Cross-package inspection | Use the isolated Python `forge status` to read the project initialized by npm. |

The commands built local artifacts and installed those files. They did not publish
packages, require a public GitHub repository, or invoke an agent workflow.
Reproduction instructions are in the
[release guide](../../maintainers/releasing.md#reproducible-local-package-checks).

## Limits and next verification

Raw stdout/stderr, temporary directory paths and generated archive hashes were not
provided for this run. The sdist was built and inspected, but this walkthrough did
not separately install from the sdist. Registry installation, Windows/Linux behavior,
external agent execution and current-version IDE acceptance are outside this report.

Remote CI must be checked for the exact PR head and again for the merge candidate
as appropriate. Do not reuse this report as proof of a later commit's package bytes
or as a PASS result for the current IDE acceptance suite. The
[historical real-project case](task-manager/README.md) remains separate evidence.
