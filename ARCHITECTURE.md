# ForgeFlow Architecture

**Artifact-driven AI workflow orchestrator for CLI and IDE extensions.**

This document explains how ForgeFlow works at every layer: from the overall architecture down to individual components. Read this before contributing code or creating custom plugins.

---

## Table of Contents

- [1. System Overview](#1-system-overview)
- [2. Directory Structure](#2-directory-structure)
- [3. The Workflow Chain](#3-the-workflow-chain)
- [4. Artifact Protocol](#4-artifact-protocol)
- [5. Handoff & Transition Protocol](#5-handoff--transition-protocol)
- [6. Plugin System](#6-plugin-system)
- [7. Auto-Mode Engine](#7-auto-mode-engine)
- [8. Adapter Pattern](#8-adapter-pattern)
- [9. CLI Reference](#9-cli-reference)

---

## 1. System Overview

ForgeFlow is a **pure-Markdown workflow orchestrator** that coordinates AI-driven development through a strict artifact graph and deterministic handoff protocol. It works with both:

- **CLI mode**: The `forge` Python command-line interface for automation
- **IDE mode**: GitHub Copilot Chat, Codex CLI, or any Markdown-capable LLM

### Core Philosophy

> Artifacts before conversations. Every piece of project state lives in a Markdown file. No database, no external service, no hidden state. The LLM is only a reader/writer of Markdown — never the source of truth.

### Key Principles

| Principle | Meaning |
|-----------|---------|
| **Artifacts are authoritative** | Planning.md, SolutionPlan.md, etc. are the only persistent truth |
| **Handoffs are typed & validated** | Every workflow emits a `### Handoff` block; receivers validate before acting |
| **Plugins are pure Markdown** | Custom review rules live in `.md` files; no Python required |
| **Auto-mode is optional** | You can drive the pipeline step-by-step manually, or let the engine loop automatically |

---

## 2. Directory Structure

```
project-root/
├── forgeflow.json                  # Single source of truth for CLI settings
└── .forgeflow/                     # ForgeFlow framework and runtime root
│    ├── forgeflow.md                # Framework overview / normative rules
│    ├── protocol/                   # Artifact and Handoff protocols
│    │
│    ├── adapter/                    # LLM adapters per host
│    │    ├── copilot/                # GitHub Copilot Chat prompts
│    │    └── codex/                  # Codex CLI prompts
│    │        └── forge-<workflow>.prompt.md
│    │
│    ├── workflow/                   # Workflow specs (per-workflow.md)
│    │    ├── plan.md                # Plan -> Planning artifact
│    │    ├── grill.md               # Grill -> Requirement artifacts
│    │    ├── solution.md            # Solution -> SolutionPlan
│    │    ├── slice.md               # Slice -> SlicePlan
│    │    ├── tdd.md                 # TDD -> TDD Record
│    │    └── review.md              # Review -> Review Report
│    │
│    ├── rules/                      # Plugin registry
│    │    └── reviews/
│    │        ├── _index.md           # Plugin registry (10-field table)
│    │        ├── security/
│    │        │    └── rules.md        # Security review rules
│    │        ├── coding-standard/
│    │        │    └── rules.md        # Coding standard rules
│    │        ├── architecture/
│    │        │    └── rules.md        # Architecture review rules
│    │        └── performance/
│    │            └── rules.md        # Performance review rules
│    │
│    ├── artifacts/                  # Generated workflow outputs (created on demand)
│    │    ├── planning.md
│    │    ├── requirement-feature-01.md
│    │    ├── solution-plan.md
│    │    ├── slice-plan-feature-01.md
│    │    ├── tdd-feature-01-slice-01.md
│    │    └── review-feature-01-slice-01-attempt-01.md
│    ├── reports/                    # Supplemental plugin review evidence
│    └── runtime/                    # Non-authoritative CLI step summaries
│         └── steps/
```

### Key Directories Explained

| Directory | Purpose | Who Writes? | Git-Tracked? |
|-----------|---------|-------------|--------------|
| `artifacts/` | Generated workflow outputs | LLM via runner.py | Yes (tracked), but `.gitignore` excludes runtime `.md` files -- use `--reset` to rotate |
| `reports/` | Supplemental, attempt-scoped plugin reports | Review workflow | No (`.gitignore`) |
| `adapter/` | Host-specific prompt templates | Developer configures | Yes |
| `workflow/` | Workflow spec Markdown | LLM reads, you edit | Yes |
| `rules/reviews/` | Plugin rule definitions | You add | Yes |
| `logs/` | CLI engine debug logs | Runner auto-writes | No (.gitignore) |

---

## 3. The Workflow Chain

ForgeFlow uses a **6-stage linear pipeline** with optional upstream returns:

```text
Plan (Project) -> Grill (Feature) -> Solution (Project) -> Slice (Feature)
        |                                               |
     Grill <- -- LOOP - ---------------------------------|
                                                          |
                                                  Slice (Feature)
                                                          |
                                                      TDD (Slice)
                                                          |
                                                    Review (Slice)
                                                     /     \
                                                PASS      FAIL
                                                   |         |
                                                   v        v
                                         Next Slice   RETURN to
                                           (TDD)       Upstream
```

### Workflow Details

| Stage | Scope | Artifact Produced | Owner | Reads |
|-------|-------|-------------------|-------|-------|
| **Plan** | Project | `Planning.md` | Plan | User intent, existing system context |
| **Grill** | Feature | `Requirement-Feature-XX.md` | Grill | Planning.md |
| **Solution** | Project | `SolutionPlan.md` | Solution | All Requirements (GRILL output) |
| **Slice** | Feature | `SlicePlan-Feature-XX.md` | Slice | SolutionPlan.md, Requirement |
| **TDD** | Slice | `TDDRecord-Feature-XX-Slice-XX.md` | TDD | SlicePlan, Requirement |
| **Review** | Slice | `ReviewReport-Feature-XX-Slice-XX-attempt-NN.md` | Review | TDD Record, implementation, tests |

### Execution Flow (Detailed)

```
1. Plan runs -> produces Planning.md with ordered Feature list [F-01, F-02, ...]
2. Grill runs per Feature -> produces Requirement-{F-XX}.md
3. Solution runs after ALL Requirements are READY -> produces SolutionPlan.md
4. Slice runs per Feature -> produces SlicePlan-{F-XX}.md with ordered Slices [S-01, S-02, ...]
5. For each Slice (in order):
   a. TDD runs -> produces TDDRecord-{Feature}-{Slice}.md
   b. Review runs -> produces ReviewReport
       - PASS: Move to next Slice
       - FAIL: Return to TDD with blocker category & scope
```

### Loop Behavior Per Workflow

| Workflow | Loops? | Meaning |
|----------|--------|---------|
| Plan | No | Single pass -- defines all Features upfront |
| Grill | Yes (per Feature) | Can loop back to Plan if Requirement needs re-planning |
| Solution | No | Single pass after all Requirements are READY |
| Slice | Yes (per Feature) | Can loop back to Solution if SlicePlan violates engineering contract |
| TDD | No | Single pass per Slice -- produces one TDD Record attempt |
| Review | Yes (per Slice) | Can loop back to TDD on FAIL |

---

## 4. Artifact Protocol

### What Is An Artifact?

An artifact is a **Markdown file** stored under `.forgeflow/artifacts/`. It is the sole persistent source of truth for project state.

### Artifact Root

The canonical artifact root is: **`.forgeflow/artifacts/`** (relative to repository root).

All active artifacts MUST be created, read, and updated directly under this root. Files outside this root do NOT participate in the transition graph.

### Canonical Filename Convention

| Artifact Type | Owner Workflow | Scope | Canonical Filename |
|---------------|----------------|-------|-------------------|
| Planning | Plan | Project | `planning.md` |
| Requirement | Grill | Feature | `requirement-feature-XX.md` |
| Solution Plan | Solution | Project | `solution-plan.md` |
| Slice Plan | Slice | Feature | `slice-plan-feature-XX.md` |
| TDD Record | TDD | Slice | `tdd-feature-XX-slice-XX.md` |
| Review Report | Review | Slice attempt | `review-feature-XX-slice-XX-attempt-NN.md` |

### Metadata Table Requirement

Every artifact MUST begin with a metadata table:

```markdown
# Planning

| Field | Value |
| --- | --- |
| Artifact Type | Planning |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Plan |
```

### Status Values Per Artifact Type

| Artifact Type | Allowed Status |
|---------------|----------------|
| Planning, Requirement, SolutionPlan, SlicePlan | `DRAFT`, `BLOCKED`, `READY` |
| TDD Record | `IN_PROGRESS`, `BLOCKED`, `READY_FOR_REVIEW` |
| Review Report | `READY` |

Every BLOCKED non-Review artifact persists Blocker Category, Blocker Owner,
Affected Scope, Blocker Reason, and Blocker Evidence. Review persists blockers in
its immutable FAIL Review Report. Every Review Report contains exactly one
seven-column canonical Findings table. The artifact parser validates its structure,
sequential row numbers, severity, owner/scope shape, rendered content, metadata
counts, PASS/FAIL decision, and FAIL disposition. The state resolver then validates
every finding scope against Planning and the applicable Slice Plan. Invalid Review
evidence halts as a graph contradiction rather than authorizing a transition.

An intentional empty project is not represented by a blank cell. Planning uses
`Feature IDs = NONE` plus `Empty Feature Approval = APPROVED: <evidence>`. The
parser normalizes this to an empty ordered list. After graph contradiction, blocker,
and Planning readiness checks, the resolver derives Rule 11 completion without
requiring Requirement, Solution, Slice, TDD, or Review artifacts. Any such downstream
artifact beside an empty Planning makes the graph contradictory.

Replaced contract versions are archived under `.forgeflow/artifacts/history/` using
versioned filenames. The History Root is preserved by Project Evidence Rotation but is
excluded from the active artifact graph.

### Project Evidence Rotation Procedure

When an explicit new-project or reset operation is authorized, the Artifact Root and
supplemental Reports Root undergo one coordinated rotation:

1. Validate both roots and determine independently whether each is non-empty
2. Capture one UTC timestamp and preflight every required backup before moving either root
3. Rename non-empty roots in full to paired `artifacts.YYYYMMDDHHMMSS` and `reports.YYYYMMDDHHMMSS` paths
4. Create fresh empty `.forgeflow/artifacts/` and `.forgeflow/reports/` directories
5. Restore every moved root if any move or directory creation fails

An empty root does not receive an empty backup. Reports remain supplemental and do
not participate in the active artifact graph. In IDE execution, an explicit
new-project or reset request authorizes rotation; a request that merely appears
unrelated requires user confirmation before either root is changed. A clean
Bootstrap requires both evidence roots to be absent or empty; residual reports also
require explicit reset authorization.

---

## 5. Handoff & Transition Protocol

### What Is A Handoff?

A **handoff** is a structured Markdown block that records the result of a workflow execution. It declares:
- The transition type (FORWARD / RETURN / TERMINAL)
- The next or returning workflow
- The blocker category (if applicable)
- Evidence-based reason for the decision

### Handoff Block Format

Every handoff MUST use exactly one of four canonical templates. Scope values are
exactly `Project`, `Feature: F-XX`, or `Slice: F-XX/S-XX`.

#### FORWARD (Progress to Next Workflow)

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | FORWARD |
| Next Workflow | {{workflow_name}} |
| Source Scope | {{scope}} |
| Target Scope | {{scope}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{evidence_based_reason}} |
```

#### RETURN (Blocker -- Return to Upstream Owner)

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | RETURN |
| Next Workflow | {{workflow_name}} |
| Source Scope | {{scope}} |
| Target Scope | {{scope}} |
| Blocker Category | {{blocker_category}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{evidence_based_reason}} |
```

#### TERMINAL / COMPLETE

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Terminal Status | COMPLETE |
| Source Scope | {{scope}} |
| Completed Scope | Project |
| Input Artifacts | {{artifact_list}} |
| Reason | {{evidence_based_reason}} |
```

#### TERMINAL / HALTED

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Terminal Status | HALTED |
| Source Scope | {{scope}} |
| Affected Scope | Project |
| Blocker Category | GRAPH_CONTRADICTION |
| Input Artifacts | {{artifact_list}} |
| Reason | {{evidence_based_reason}} |
```

### Handoff Emission Rule

**Every workflow that reaches a handoff-producing end MUST:**
1. Validate and render exactly one `### Handoff` block
2. Use the selected variant's exact heading, fields, row order
3. Make it the **final content** of the response (no trailing prose)

The receiving workflow MUST reject a malformed handoff rather than infer or normalize it.

For HALTED, validation is evidence-bearing rather than status-only. ArtifactParser
retains structured diagnostics for invalid canonical files, including a readable
version or `INVALID_VERSION`. StateResolver selects the deterministic primary
contradiction and emits its graph error code plus sorted terminal evidence. The
Handoff parser accepts `NONE` only for HALTED, and Runner requires the Reason code
and Input Artifacts to match the resolver projection exactly. This prevents an agent
from terminating the pipeline with nonexistent, stale, unrelated, or falsely
versioned evidence.

### Transition Resolution Procedure

Before emitting any handoff, the active workflow evaluates these rules in order and stops at the first match:

| Rule | Condition | Action |
|------|-----------|--------|
| **Rule 1** -- Bootstrap | Empty Artifact Root has no Planning | Authorize Plan at `Project` without synthetic handoff |
| **Rule 2** -- Graph contradiction | Active graph is structurally invalid, including unresolved Blocker or FAIL Review routing scopes | TERMINAL / HALTED |
| **Rule 3** -- Persisted blocker | BLOCKED artifact has valid metadata and a complete usable current upstream chain | Select by owner priority, Planning Feature position, then Slice Plan position; RETURN or Recovery Entry |
| **Rule 4** -- Planning not ready | Planning exists but is not usable | FORWARD to Plan at `Project` |
| **Rule 5** -- Missing/stale Requirement | A declared first Feature lacks usable Requirement | FORWARD to Grill at `Feature: F-XX` |
| **Rule 6** -- Missing/stale Solution Plan | At least one Feature exists; Requirements ready; Solution Plan not usable | FORWARD to Solution at `Project` |
| **Rule 7** -- Missing/stale Slice Plan | A declared first Feature lacks usable Slice Plan | FORWARD to Slice at `Feature: F-XX` |
| **Rule 8** -- Current Review failure | Current TDD attempt has matching FAIL | RETURN per Review Report disposition |
| **Rule 9** -- Review required | First incomplete Slice is READY_FOR_REVIEW without matching Review | FORWARD to Review at `Slice: F-XX/S-XX` |
| **Rule 10** -- TDD required | Delivery ready and first incomplete Slice needs implementation | FORWARD to TDD at `Slice: F-XX/S-XX` |
| **Rule 11** -- Project complete | Every Slice has a current matching PASS Review, or READY Planning is validly `NONE` and sole active artifact | TERMINAL / COMPLETE |

### Blocker Routing Rules

When a blocker needs routing, the following table determines ownership:

| Blocker Category | Owner Workflow | Return Scope | Meaning |
|------------------|---------------|--------------|---------|
| `PLAN_GAP` | Plan | `Project` | Planning missing features, overlapping scope, or incompatible versions |
| `BUSINESS_GAP` | Grill | `Feature: F-XX` | Requirement missing, outdated, or internally contradictory |
| `ENGINEERING_GAP` | Solution | `Project` | SolutionPlan missing, outdated, incomplete, or conflicting |
| `SLICE_VIOLATION` | Slice | `Feature: F-XX` | SlicePlan boundary wrong, dependency invalid, content missing |
| `IMPLEMENTATION_GAP` | TDD | `Slice: F-XX/S-XX` | Implementation, test, or local evidence is blocked |
| `REVIEW_BLOCKER` | Determined by Review Report Findings Table | Per finding | A review finding triggers routing -- read the findings table to determine owner and scope |
| `GRAPH_CONTRADICTION` | None; terminal halt | `Project` | Active graph cannot authorize productive work |

---

## 6. Plugin System

ForgeFlow uses a **pure-Markdown plugin registry** for extensible review rules. No Python code is required to add custom reviews.

### How Plugins Work

```text
Review workflow
     |
     +-- Reads _index.md (plugin registry)
     |       +- Lists all enabled plugins + priority order
     |
     +-- For each enabled plugin (sorted by Priority):
     |       +- Resolves the registered Rules File relative to rules/reviews/
     |       +- Executes each rule against artifacts/codebase
     |       +- Records PASS / VIOLATION / UNKNOWN / N/A
     |       +- Maps VIOLATION severity through Blocking Threshold
     |
     +-- Compiles results into structured report
     |       +- Saves attempt-scoped reports under .forgeflow/reports/<plugin-name>/
     |
     +- Aggregates plugin evidence into the core Review Report Findings table
             +- Core rows determine counts, PASS/FAIL, and RETURN disposition
```

Attempt-scoped plugin reports remain supplemental. They never replace the
canonical Review Report or serve as an independent transition authority.

### Plugin Registry (_index.md)

The registry is a single Markdown table under `.forgeflow/rules/reviews/_index.md`. Each row defines one plugin with 11 fields:

| Field | Example | Description |
|-------|---------|-------------|
| Name | `security` | Human-readable identifier |
| Directory | `security/` | Subdirectory under reviews/ |
| Rules File | `security/rules.md` | Path relative to `.forgeflow/rules/reviews/` |
| Enabled? | `true` / `false` | Activates or skips this plugin |
| Priority | `1` | Execution order (lower = earlier) |
| Depends On | `--` or `security, architecture` | Other plugins scanned first |
| Scope | `code, docs` | Where to apply checks |
| Applicability | `Executable service code` | Evidence boundary evaluated before compliance |
| Report Format | `md, csv` | Output format(s) for report |
| Blocking Threshold | `P0-P1` | Severity levels that block pipeline |
| Description | `Security vulnerability detection...` | One-line summary |

### Adding A Custom Plugin

**Step 1:** Create the rules file

```bash
mkdir -p .forgeflow/rules/reviews/my-plugin/
touch .forgeflow/rules/reviews/my-plugin/rules.md
```

**Step 2:** Write checklist rules in `rules.md`

```markdown
# My Plugin Rules

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| MY-001 | No hardcoded passwords | Scan all .py files for "password =" | All credentials from env vars |
```

**Step 3:** Add entry to `_index.md`

```markdown
| my-plugin | `my-plugin/` | `rules/my-plugin/rules.md` | true | 5 | -- | code | md, csv | P0-P1 | My custom plugin description |
```

That's it. The Review workflow will automatically pick it up on next execution.

---

## 7. Auto-Mode Engine

The auto-mode engine is responsible for orchestrating the pipeline loop. It lives in `runner.py`.

CLI artifact discovery validates only canonical files located directly under the
configured Artifact Root. It reads status and version data from each artifact's
leading Metadata table, reports malformed canonical artifacts as an invalid graph,
and excludes `history/`, backup directories, nested files, and non-canonical files
from the active artifact set.

### How Auto-Mode Works

```python
for step in range(MAX_STEPS=50):
    before = detect_artifact_state(artifacts_dir)
    authorization = resolve_pipeline_state(before)
    current_workflow = authorization.current_workflow
    current_scope = authorization.target_scope

    llm_output = try_execute_llm(current_workflow, max_retries=3)
    handoff = parse_handoff(
        llm_output,
        expected_source_workflow=current_workflow,
        expected_source_scope=current_scope,
    )

    after = detect_artifact_state(artifacts_dir)
    resolution = resolve_pipeline_state(after)
    if not handoff_matches_graph(handoff, after, resolution):
        return PIPELINE_BLOCKED

    persist_step_history()
    if resolution.pipeline_status in {"COMPLETE", "HALTED"}:
        break
```

### Key Mechanisms

| Mechanism | Default Value | Purpose |
|-----------|---------------|---------|
| `MAX_STEPS` | 50 total iterations | Prevents infinite loops |
| `MAX_FAILURES_PER_WF` | 3 consecutive failures per workflow | Blocks after repeated execution or Handoff failure |
| `artifacts_dir` | `.forgeflow/artifacts/` | Where all artifacts are persisted |
| `runtime_dir` | `.forgeflow/runtime/` | Non-authoritative CLI step summaries |

### Failure Safety

When agent execution fails, or its response attempts an invalid canonical Handoff
three times, the Runner returns `PIPELINE_BLOCKED`. A response with no Handoff marker
and unchanged Workflow/Scope authorization returns `PIPELINE_WAITING` without a
retry; if authorization changed, the missing Handoff blocks the run. The Runner
never synthesizes a FORWARD, RETURN, or TERMINAL result from configuration. Step
summaries are written under `.forgeflow/runtime/steps/`, outside the authoritative
Artifact Root.

### LLM Execution Hook

When the engine calls `_execute_llm(name)`:

1. Reads prompt from `.forgeflow/adapter/<adapter>/forge-<name>.prompt.md`
2. Appends engine-derived Bootstrap or Recovery Entry context when the current graph authorizes one
3. Appends an optional Plan User Intent as escaped, non-normative JSON invocation data
4. Invokes the matching non-interactive agent CLI from the project root
5. Grants workspace-scoped execution permissions needed by the workflow
6. Returns the agent's final response from standard output
7. HandoffParser attempts to parse the final `### Handoff` block

The `codex` adapter uses `codex exec` with the `workspace-write` sandbox. The
`copilot` adapter uses `gh copilot` with non-interactive `write` and `shell`
permissions while retaining its default project-root path boundary. The optional
`model` and `execution_timeout_seconds` keys in `forgeflow.json` select a model and
bound each invocation. Process failures and malformed handoffs are retried by the
Runner's workflow-level retry loop rather than by nested backend retries.

---

## 8. Adapter Pattern

ForgeFlow supports multiple **host adapters** -- each adapts the core workflows to a specific LLM interface.

### Supported Adapters

| Adapter | Files | When Used |
|---------|-------|-----------|
| `copilot` | `.forgeflow/adapter/copilot/*.prompt.md` | Default; IDE GitHub Copilot Chat |
| `codex` | `.forgeflow/adapter/codex/*.prompt.md` | CLI Codex mode |

### How Adapter Selection Works

```text
forgeflow.json has "adapter": "copilot"
     |
     +- User runs: forge init --adapter codex
     |       +- Refreshes managed framework files and updates forgeflow.json
     |
     +- Engine starts: runner.py reads forgeflow.json
     |    +- Uses the configured adapter, defaulting to copilot
     |
     +- PromptResolver resolves:
             .forgeflow/adapter/<selected>/forge-<workflow>.prompt.md
```

### Adapter Differences

The copilot and codex adapters differ only in their **prompt templates** -- not in core logic. Each workflow has a separate `.prompt.md` file per adapter:

```
adapter/
    copilot/
     |-- forge-plan.prompt.md # Copilot-specific system prompt for Plan
     +-- ...
    codex/
     |-- forge-plan.prompt.md # Codex-specific system prompt for Plan
     +-- ...
```

The `copilot` adapter is the recommended default. Use `codex` when running from CLI with a different LLM backend.

---

## 9. CLI Reference

### Available Subcommands

| Command | Description | Parameters |
|---------|-------------|------------|
| `forge --help` | Show help message | None |
| `forge plan` | Execute Plan workflow (Project scope) | `--intent TEXT` |
| `forge run [--auto\|--manual] [--reset]` | Start pipeline | See below |
| `forge status` | Show current state, artifacts, handoff data | None |
| `forge reset [--force]` | Rotate artifacts and supplemental reports (dry-run by default) | `--force` to archive and rotate |
| `forge init [-a copilot\|codex]` | Install or refresh framework resources | `--adapter`, `--force` |
| `forge handoff` | Debug latest handoff from artifacts/ | None |

Command exit status is deterministic: `0` means success, `1` means an execution or
configuration error, `2` means the pipeline ended without successful completion,
and `130` means the user interrupted execution.

### Run Command Modes

| Flag | Behavior | Use Case |
|------|----------|---------|
| Default (no flags) | Use `forgeflow.json` `mode` | Project-configured behavior |
| `--auto` | Override this invocation to auto mode | Loop until TERMINAL or blocked |
| `--manual` | Override this invocation to manual mode | Execute Plan once; `--no-auto` is an alias |
| `--reset` | Rotate artifacts and reports before running | Start fresh without mixing project evidence |
| `--force` | Authorize `forge reset` rotation or `forge init` refresh | Explicit state-changing action |

### Example CLI Session

```bash
# 1. Initialize project for GitHub Copilot Chat
forge init --adapter copilot

# 2. Run auto-mode pipeline (will loop until complete or blocked)
forge run

# 3. Or run in manual mode to inspect each step
forge run --manual

# 4. Check status at any time
forge status

# 5. Reset and start fresh
forge reset --force
```

---

## Summary

ForgeFlow is a **pure-Markdown artifact-driven workflow** that coordinates AI development through:

1. **6 canonical workflows** (Plan -> Grill -> Solution -> Slice -> TDD -> Review)
2. **Typed handoff protocol** (FORWARD / RETURN / TERMINAL with validation)
3. **Deterministic transition procedure** (ordered Markdown rules evaluated from the active artifact graph)
4. **Plugin-based review system** (pure Markdown rules loaded from `_index.md`)
5. **Adapter pattern** (supports copilot & codex hosts via separate prompt files)

Everything is designed to work with any LLM that supports Markdown I/O -- no external services, databases, or heavy runtimes required.
