# Security Policy

ForgeFlow is a repository-native engineering protocol with optional IDE launchers
and a Python orchestrator. This policy describes the implemented trust boundaries,
supported versions, safe-use expectations, and vulnerability-reporting process.

## Reporting A Vulnerability

Do not disclose suspected vulnerabilities in a public issue.

Report them by email to [idairen@qq.com](mailto:idairen@qq.com) with the subject
`ForgeFlow Security Vulnerability Report`. Include:

- the affected version, commit, Adapter, and host;
- reproduction steps or a minimal repository;
- expected and observed behavior;
- the potential impact and affected files or credentials;
- a proposed mitigation, if available.

The maintainer aims to acknowledge reports within 48 hours and provide an initial
assessment within seven days. Resolution and disclosure timing depend on severity
and whether an upstream Agent host or CLI is involved. Reporters receive credit
unless they request anonymity.

GitHub Private Vulnerability Reporting should become the preferred channel after it
is enabled for the public repository. Until then, use the email address above.

## Supported Versions

ForgeFlow is currently a Technical Preview. Only the latest published release and
the current default branch are eligible for security fixes. Pre-release protocol,
Adapter, CLI, and installer behavior may change between minor versions.

| Version | Support |
|---------|---------|
| Latest published release | Security fixes when practicable |
| Default branch | Development fixes; not a stable release |
| Older releases | Upgrade required unless explicitly announced otherwise |

## Trust Boundaries

### Markdown Protocol Core

The normative ForgeFlow core consists of Markdown contracts. The JSON configuration
schema supports optional tooling and does not define or override core authority.
Reading these files does not itself execute code, but Markdown instructions are
consumed by an AI Agent. Treat framework files, project Artifacts, supplemental Reports, source code,
and user input as potentially untrusted prompt input.

Artifact ownership and Handoff validation constrain ForgeFlow state transitions.
They do not sandbox an Agent, prove generated content is safe, or prevent a host from
misinterpreting instructions.

### IDE Hosts

IDE execution inherits the permissions, network access, data-retention policy,
authentication, model behavior, and tool controls of the selected host. ForgeFlow
does not override those controls. Review host settings before exposing proprietary
source code, secrets, customer data, or regulated information.

### Python CLI Runner

The optional `forge` CLI starts an external Agent process in the project root:

- the Codex Adapter uses `codex exec` with a workspace-write sandbox;
- the Copilot Adapter uses `gh copilot` with the project root as its working
  directory and `write` and `shell` tools enabled non-interactively. The working
  directory is not a filesystem sandbox; access restrictions and tool permissions
  are controlled by the host.

Commands are constructed with `asyncio.create_subprocess_exec` rather than shell
interpolation, but the selected Agent may still read project files, modify source
code, invoke tools, execute shell commands, and communicate with external services
according to host permissions. ForgeFlow validates protocol output after execution;
it cannot guarantee that an Agent made no unauthorized change before validation.

### Installer And Local Evidence

The npx installer copies managed framework files into the current project. Forced
refresh rejects symbolic links and preserves project-owned Artifacts, Reports,
runtime evidence, supported configuration, and custom Review plugins.

`forge reset --force` rotates active Artifacts and Reports into timestamped sibling
directories. It does not intentionally delete project source code. Backups are local
files and are not encrypted by ForgeFlow.

## Relevant Vulnerability Classes

Reports are especially useful for:

- command, argument, path, or symlink injection in the CLI or installer;
- reads or writes escaping the selected project root;
- unsafe refresh or rotation that loses or overwrites project-owned evidence;
- malformed Artifact or Handoff input bypassing authorization checks;
- prompt injection that bypasses an implemented ForgeFlow security boundary;
- secrets exposed through logs, runtime evidence, errors, packages, or fixtures;
- supply-chain compromise of published npm or Python artifacts;
- discrepancies that grant broader Agent permissions than documented.

Model hallucinations, insecure generated application code, and host behavior outside
an implemented ForgeFlow boundary are not automatically ForgeFlow vulnerabilities.
They may still justify a safety issue or documentation correction when ForgeFlow
creates a misleading expectation.

## Safe-Use Guidance

1. Run ForgeFlow on an isolated branch, worktree, or disposable copy.
2. Apply the least privileges supported by the selected Agent host.
3. Keep secrets out of prompts, Artifacts, Reports, fixtures, and source files
   exposed to the Agent.
4. Inspect `git diff`, generated evidence, executed commands, and Agent output before
   accepting changes.
5. Require the project's normal code review, tests, security checks, and deployment
   controls; a ForgeFlow Review PASS is not a production approval.
6. Treat third-party Review plugins and modified `.forgeflow/` files as executable
   instructions for trust purposes, even though they are Markdown.
7. Verify package provenance and checksums when installing published releases.
8. Stop execution and preserve evidence if unexpected file access, network activity,
   or tool invocation occurs.

## Maintainer Response Process

For a confirmed vulnerability, the maintainer will:

1. classify the affected trust boundary and versions;
2. reproduce the issue in an isolated environment;
3. develop a minimal fix and regression test when feasible;
4. validate Python and npm package artifacts as applicable;
5. publish a patched release and security advisory;
6. credit the reporter and document mitigations unless disclosure must be delayed.

No response-time guarantee is made for this Technical Preview, but critical reports
involving code execution, credential exposure, project-root escape, or destructive
file operations receive priority.
