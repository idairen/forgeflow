# ForgeFlow Sample Project

This example demonstrates ForgeFlow installation and the first two workflow
artifacts without maintaining a second copy of the framework.

The canonical framework always comes from the repository's root `.forgeflow/`
directory or a published ForgeFlow package. The files under `expected-artifacts/`
are protocol-valid examples for comparison; they are not active project state and
must not be copied over model output.

## Contents

```text
sample-project/
├── README.md
├── intent.md
└── expected-artifacts/
    ├── planning.md
    └── requirement-feature-01.md
```

`intent.md` contains a small project request. The expected artifacts demonstrate a
valid graph after Plan and Grill have completed for the first Feature. At that
point, ForgeFlow resolves Grill for `F-02` as the next authorized workflow.

## Try It From a Source Checkout

Run these commands from the ForgeFlow repository root. The temporary directory
keeps generated framework and runtime files out of the tracked example.

```bash
repository_root="$(pwd)"
sample_root="$(mktemp -d)/forgeflow-sample"
cp -R examples/sample-project "$sample_root"
cd "$sample_root"

node "$repository_root/npm/bin/forgeflow.js" init --adapter copilot
```

To use the Python installer instead, install ForgeFlow from the checkout and run:

```bash
forge init --adapter copilot
```

When the npm package is published, the equivalent public installation command is:

```bash
npx @dairen/forgeflow@next init --adapter copilot
```

Use `--adapter codex` for the Codex launcher set.

## Run the Workflow

In an IDE whose host integration discovers the installed launcher prompts, invoke
ForgeFlow Plan with the contents of `intent.md`. Launcher discovery and command
syntax depend on the host; the prompt files alone do not register slash commands.

With the optional Python CLI and an authenticated external agent CLI:

```bash
forge plan --intent "$(cat intent.md)"
forge run
forge status
```

Generated artifacts belong under `.forgeflow/artifacts/`. Compare their metadata,
filenames, ownership, versions, and dependency references with
`expected-artifacts/`; exact prose may differ because model output is not
deterministic.

## Expected Checkpoint

The included checkpoint contains:

- READY Planning version `1.0` with three ordered Features;
- READY Requirement `F-01` tied to its Feature Contract Version `1.0`;
- no Requirement for `F-02` or `F-03`, and no Solution Plan yet.

The active graph represented by that checkpoint authorizes Grill at `Feature: F-02`
scope. Repository tests parse this directory with the production Artifact Parser
and assert that exact resolution, preventing the example from drifting away from
the current protocol and declared Feature order.

## Important Boundaries

- Do not edit copied Workflow, Protocol, or Adapter files to customize a project;
  use supported Review plugins and project evidence instead.
- Do not treat `expected-artifacts/` as generated evidence for another project.
- Do not interpret protocol-test success as proof of real IDE behavior or model
  correctness.
