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
├── .forgeflow/                     # The ForgeFlow runtime root
│    ├── config.json                 # Single source of truth for CLI settings
│    ├── artifact.md                 # Artifact Protocol spec (read-only)
│    ├── handoff.md                  # Handoff & Transition Protocol spec (read-only)
│    ├── forgeflow.md                # Framework overview / normative rules
│    │
│    ├── adapter/                    # LLM adapters per host
│    │    ├── copilot/                # GitHub Copilot Chat prompts
│    │    └── codex/                  # Codex CLI prompts
│    │        └── <workflow>.prompt.md
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
│    ├── artifacts/                  # Generated workflow outputs (runtime)
│    │    ├── planning.md
│    │    ├── requirement-feature-01.md
│    │    ├── solution-plan.md
│    │    ├── slice-plan-feature-01.md
│    │    ├── tdd-feature-01-slice-01.md
│    │    └── review-feature-01-slice-01-attempt-01.md
│    └── logs/                       # Engine log files (optional)
│        └── forgeflow.log
```

### Key Directories Explained

| Directory | Purpose | Who Writes? | Git-Tracked? |
|-----------|---------|-------------|--------------|
| `artifacts/` | Generated workflow outputs | LLM via runner.py | Yes (tracked), but `.gitignore` excludes runtime `.md` files -- use `--reset` to rotate |
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

### Root Rotation Procedure (Artifact Reset)

When `forge run --reset` is invoked, the Artifact Root undergoes rotation:

1. If `.forgeflow/artifacts/` exists and is non-empty -> rename to `artifacts.YYYYMMDDHHMMSS`
2. Create a fresh empty `.forgeflow/artifacts/` directory
3. All previous artifacts are archived; new run starts clean

This ensures **zero state drift** between project versions.

---

## 5. Handoff & Transition Protocol

### What Is A Handoff?

A **handoff** is a structured Markdown block that records the result of a workflow execution. It declares:
- The transition type (FORWARD / RETURN / TERMINAL)
- The next or returning workflow
- The blocker category (if applicable)
- Evidence-based reason for the decision

### Handoff Block Format

Every handoff MUST use exactly one of these three canonical templates:

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

#### TERMINAL (Pipeline Complete)

```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Source Scope | {{scope}} |
| Completed Scope | {{scope}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{evidence_based_reason}} |
```

### Handoff Emission Rule

**Every workflow that reaches a handoff-producing end MUST:**
1. Validate and render exactly one `### Handoff` block
2. Use the selected variant's exact heading, fields, row order
3. Make it the **final content** of the response (no trailing prose)

The receiving workflow MUST reject a malformed handoff rather than infer or normalize it.

### Transition Resolution Procedure

Before emitting any handoff, the active workflow evaluates these rules in order and stops at the first match:

| Rule | Condition | Action |
|------|-----------|--------|
| **Rule 1** -- No Planning Yet | No Planning exists OR Plan is not READY | FORWARD to Plan (Project scope) |
| **Rule 2** -- Blocker Exists | Upstream workflow identified a blocker | RETURN per Blocker Category routing table |
| **Rule 3** -- Missing/Stale Requirement | First Feature lacks current READY Requirement | FORWARD to Grill (Feature scope) |
| **Rule 4** -- Missing/Stale Solution Plan | SolutionPlan absent, incomplete, or stale | FORWARD to Solution (Project scope) |
| **Rule 5** -- Missing/Stale Slice Plan | First Slice lacks current READY SlicePlan | FORWARD to Slice (Feature scope) |
| **Rule 6** -- Review Failure with Blocker | FAIL ReviewReport exists for active attempt | RETURN per Review Report Findings Table |

### Blocker Routing Rules

When a blocker needs routing, the following table determines ownership:

| Blocker Category | Owner Workflow | Return Scope | Meaning |
|------------------|---------------|--------------|---------|
| `PLAN_GAP` | Plan | Project | Planning missing features, overlapping scope, or incompatible versions |
| `BUSINESS_GAP` | Grill | Feature ID (F-XX) | Requirement missing, outdated, or internally contradictory |
| `ENGINEERING_GAP` | Solution | Project | SolutionPlan missing, outdated, incomplete, or conflicting |
| `SLICE_VIOLATION` | Slice | Feature ID (F-XX) | SlicePlan boundary wrong, dependency invalid, content missing |
| `REVIEW_BLOCKER` | Determined by Review Report Findings Table | Per finding | A review finding triggers routing -- read the findings table to determine owner and scope |

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
     |       +- Reads rules/<plugin-name>/rules.md
     |       +- Executes each rule against artifacts/codebase
     |       +- Records verdict: [x] PASS / [!] FAIL / [~] WARN/N/A
     |
     +-- Compiles results into structured report
     |       +- Saves to .forgeflow/reports/<plugin-name>/report.md
     |
     +- Aggregates verdicts -> decides PASS/FAIL for Review
```

### Plugin Registry (_index.md)

The registry is a single Markdown table under `.forgeflow/rules/reviews/_index.md`. Each row defines one plugin with 10 fields:

| Field | Example | Description |
|-------|---------|-------------|
| Name | `security` | Human-readable identifier |
| Directory | `security/` | Subdirectory under reviews/ |
| Rules File | `rules/security/rules.md` | Path to rule checklist |
| Enabled? | `true` / `false` | Activates or skips this plugin |
| Priority | `1` | Execution order (lower = earlier) |
| Depends On | `--` or `security, architecture` | Other plugins scanned first |
| Scope | `code, docs` | Where to apply checks |
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

### How Auto-Mode Works

```python
for step in range(MAX_STEPS=50):
    current_workflow = detect_current_workflow()
    artifact_state = HandoffParser.detect_artifact_state(artifacts_dir)
    
     # Execute LLM workflow with retries
    llm_output = try_execute_llm(current_workflow, max_retries=3)
    
     # Parse handoff from response
    handoff = HandoffParser.parse(llm_output)
    
    if handoff is not None:
         # Valid handoff found -- apply transition
        transition = apply_transition(handoff)
        
        if transition == "FORWARD":
            current_workflow = next_workflow
        elif transition == "RETURN":
            current_workflow = return_to_workflow
            log_blocker()
        elif transition == "TERMINAL":
            break   # Pipeline complete!
    else:
         # No valid handoff -- fallback to config rules
        fallback = apply_fallback_transitions(current_workflow)
        if fallback is None:
            break   # Stuck -- no rule matched
        current_workflow = fallback.next_workflow
        
print_summary()   # Persist step history
```

### Key Mechanisms

| Mechanism | Default Value | Purpose |
|-----------|---------------|---------|
| `MAX_STEPS` | 50 total iterations | Prevents infinite loops |
| `MAX_FAILURES_PER_WF` | 3 consecutive failures per workflow | Triggers fallback on repeated LLM failure |
| `RETRY_BACKOFF` | 0.5s -> 1s -> 2s (exponential) | Gentle retry for transient LLM errors |
| `artifacts_dir` | `.forgeflow/artifacts/` | Where all artifacts are persisted |

### Fallback Transition Engine

When handoff parsing fails or the LLM returns an invalid response, the engine falls back to rules defined in `config.json`:

```json
{
   "transitions": [
     {
       "rule_id": "plan_done_to_grill",
       "condition": "Plan DONE, first Feature missing Requirement",
       "forward": "grill",
       "return_to": null
     },
     ...
   ]
}
```

Fallback priority:
1. `auto_next` from workflow config (forward)
2. `on_blocker_return` mapping (conditional forward/return)
3. Global `transitions` rules list

### LLM Execution Hook

When the engine calls `_execute_llm(name)`:

1. Reads prompt from `.forgeflow/adapter/<adapter>/<name>.prompt.md`
2. Passes it as system instruction to the LLM
3. Returns raw text output
4. HandoffParser attempts to parse `### Handoff` block

You can hook into this flow by modifying `runner.py` or providing custom adapters.

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
config.json has "adapter": "copilot"
     |
     +- User runs: forge init --adapter codex
     |       +- Writes {"adapter": "codex"} to config.json
     |
     +- Engine starts: runner.py reads config.json
     |    +- If adapter is set -> use that
     |    +- Otherwise -> detect host from environment variables
     |
     +- PromptResolver resolves:
             .forgeflow/adapter/<selected>/<workflow>.prompt.md
```

### Environment Auto-Detection Fallback

If no adapter is set in `config.json`, the engine auto-detects:

| Host | Detection Keys |
|------|---------------|
| copilot | `GITHUB_TOKEN` or `VS_CODE_EXTENSION` env vars |
| codex | `CODEX_CLI` or `CODEX_HOME` env vars |
| gemini | `GOOGLE_API_KEY` or `GEMINI_CLI` env vars |
| claude | `ANTHROPIC_API_KEY` or `CLAUDE_CLI` env vars |

### Adapter Differences

The copilot and codex adapters differ only in their **prompt templates** -- not in core logic. Each workflow has a separate `.prompt.md` file per adapter:

```
adapter/
    copilot/
     |-- plan.prompt.md       # Copilot-specific system prompt for Plan
     +-- ...
    codex/
     |-- plan.prompt.md       # Codex-specific system prompt for Plan
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
| `forge run [--auto] [--no-auto] [--reset]` | Start pipeline | See below |
| `forge status` | Show current state, artifacts, handoff data | None |
| `forge reset [--force]` | Clean up artifacts/ (dry-run by default) | `--force` to actually delete |
| `forge init [-a copilot\|codex]` | Initialize project | `--adapter`, `--force` |
| `forge handoff` | Debug latest handoff from artifacts/ | None |

### Run Command Modes

| Flag | Behavior | Use Case |
|------|----------|---------|
| Default (no flags) | Auto-mode: loop until TERMINAL or blocked | Fully automated pipeline |
| `--auto` | Explicit auto-mode | Same as default |
| `--no-auto` | Manual mode: one step at a time, you drive transitions | Debugging, review-driven development |
| `--reset` | Clean artifacts/ before running | Start fresh with zero state drift |
| `--force` | Combined with reset: actually delete artifacts | Hard reset |

### Example CLI Session

```bash
# 1. Initialize project for GitHub Copilot Chat
forge init --adapter copilot

# 2. Run auto-mode pipeline (will loop until complete or blocked)
forge run

# 3. Or run in manual mode to inspect each step
forge run --no-auto

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
3. **Deterministic transition engine** (rules defined in config.json, evaluated at runtime)
4. **Plugin-based review system** (pure Markdown rules loaded from `_index.md`)
5. **Adapter pattern** (supports copilot & codex hosts via separate prompt files)

Everything is designed to work with any LLM that supports Markdown I/O -- no external services, databases, or heavy runtimes required.
