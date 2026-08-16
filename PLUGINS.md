# ForgeFlow Plugin System

**Add custom review plugins in pure Markdown -- no Python code required.**

This guide explains how the plugin registry works, how to write rules, and how to manage your review plugins. Read this before contributing or extending ForgeFlow.

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Plugin Registry (_index.md)](#2-plugin-registry-_indexmd)
- [3. Writing Rules](#3-writing-rules)
- [4. Report Generation](#4-report-generation)
- [5. Adding A Custom Plugin (Step-by-Step)](#5-adding-a-custom-plugin-stepbystep)
- [6. Managing Plugins](#6-managing-plugins)
- [7. Best Practices](#7-best-practices)
- [8. Example: Adding a Security Plugin](#8-example-adding-a-security-plugin)
- [9. Roadmap](#9-roadmap)

---

## 1. Overview

ForgeFlow's review engine is driven by **Markdown rule files** stored in `.forgeflow/rules/reviews/<plugin-name>/rules.md`. Each plugin defines a checklist of rules that the LLM executes against project artifacts.

### How It Works

```
Review workflow starts
      |
      v
Reads _index.md (registry)
      |
      v
Sorts enabled plugins by Priority
      |
      v
For each plugin:
  - Reads rules.md
  - LLM executes each rule against codebase/artifacts
  - Records verdict: [x] PASS / [!] FAIL / [~] WARN/N/A
      |
      v
Aggregates all results -> decides PASS or FAIL
      |
      v
Saves report to .forgeflow/reports/<plugin-name>/report.md
```

### Why Markdown?

| Reason | Detail |
|--------|--------|
| **Zero Python dependency** | Rules are plain `.md` files; any text editor works |
| **Version controllable** | Git-tracked, diff-able, merge-friendly |
| **LLM-native format** | The same LLM that executes the rules can also read/interpret them |
| **Easy to maintain** | Add/remove/edit rules without recompiling or redeploying |

---

## 2. Plugin Registry (_index.md)

The plugin registry is a single Markdown table at `.forgeflow/rules/reviews/_index.md`. Each row defines one plugin with 10 fields:

### The 10 Fields Explained

| Field | Example | Meaning |
|-------|---------|---------|
| **Name** | `security` | Human-readable identifier; lowercase with hyphens |
| **Directory** | `security/` | Subdirectory under `.forgeflow/rules/reviews/` |
| **Rules File** | `rules/security/rules.md` | Path to the rule checklist file |
| **Enabled?** | `true` / `false` | If false, the plugin is skipped entirely |
| **Priority** | `1` | Execution order (lower = earlier). 1 = first. |
| **Depends On** | `--` or `security` | Other plugins whose results should be scanned first |
| **Scope** | `code, docs` | Where to apply checks: `code` only, `docs` only, or both |
| **Report Format** | `md` / `csv` / `html` | Output format(s) for the generated report |
| **Blocking Threshold** | `P0-P1` | Which severity levels trigger a pipeline block |
| **Description** | `Security vulnerability...` | One-line summary shown in registry table |

### Pre-Bundled Plugins

| Plugin | Priority | Scope | Enabled? | Description |
|--------|----------|-------|----------|-------------|
| `security` | 1 | code, docs | true | Vulnerability detection, compliance audit |
| `coding-standard` | 2 | code | true | PEP8, naming conventions, style enforcement |
| `architecture` | 3 | code, docs | true | Design patterns, coupling, modularity |
| `performance` | 4 | code | true | Anti-patterns, N+1 queries, cache misses |

---

## 3. Writing Rules

### Rule Checklist Table Format

Each plugin's `rules.md` MUST start with a checklist table:

```markdown
# Plugin Name

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| SEC-001 | No hardcoded passwords | Scan all .py files for literal string assignments to password variables | All credentials sourced from environment variables or vault |
| SEC-002 | SQL Injection Prevention | Check that all database queries use parameterized statements | No raw string formatting in SQL queries |
```

### Rule Checklist Schema

| Column | Required | Description |
|--------|----------|-------------|
| **Rule ID** | Yes | Unique identifier; convention: `<PLUGIN_PREFIX>-NNN` (e.g., `SEC-001`, `PERF-005`) |
| **Description** | Yes | Short label for the rule |
| **Check Criteria** | Yes | What the LLM should check (code pattern, doc requirement, etc.) |
| **Expected Result** | Yes | What a passing result looks like |

### Optional: Supplementary Notes

After the checklist table, you may add free-form Markdown notes:

```markdown
## Notes

- This plugin applies only to Python source code.
- For TypeScript projects, see `rules-ts.md` (optional).

## Examples

### Passing Example

A query using parameterized statements:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Failing Example

Hardcoded credentials detected:
```python
db_password = "admin123"  # Should use os.environ.get('DB_PASSWORD')
```
```

---

## 4. Report Generation

### Report Structure

Each plugin generates a standalone report saved to `.forgeflow/reports/<plugin-name>/report.md`:

```markdown
# Security Review Report

**Rules Version:** 1.0
**Review Date:** 2026-08-15
**Status:** FAIL (with warnings)

## Summary Table

| # | Rule ID | Description | Severity | Status | Finding |
|---|---------|-------------|----------|--------|---------|
| 1 | SEC-001 | No hardcoded passwords | P0 | [!] FAIL | Password found in config.py:15 |
| 2 | SEC-002 | SQL Injection Prevention | P0 | [x] PASS | All queries parameterized |

## Detailed Findings (FAIL/WARN items only)

### SEC-001 -- No hardcoded passwords [P0] [!]

**Location:** `config.py`, line 15
```python
db_password = "admin123"    # Should use env var or Vault
```

**Expected:** Credentials from environment variables or secrets manager.
**Fix:** Replace with `os.environ.get('DB_PASSWORD')` or vault reference.
```

### Report Output Formats

| Format | Location | Use Case |
|--------|----------|----------|
| `md` (default) | `.forgeflow/reports/<name>/report.md` | Git-tracked, auditable |
| `csv` | `.forgeflow/reports/<name>/report.csv` | CI/CD dashboards, data filtering |
| `html` | `.forgeflow/reports/<name>/report.html` | Dashboard / Wiki display |

For now, only **Markdown (md)** is available. CSV and HTML exports can be added later.

---

## 5. Adding A Custom Plugin (Step-by-Step)

### Step 1: Create the Plugin Directory

```bash
mkdir -p .forgeflow/rules/reviews/my-plugin/
touch .forgeflow/rules/reviews/my-plugin/rules.md
```

### Step 2: Write Your Rules

Open `.forgeflow/rules/reviews/my-plugin/rules.md` and write checklist rules:

```markdown
# My Plugin Rules

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| MY-001 | No hardcoded passwords | Scan all .py files for "password =" | All credentials from env vars |
| MY-002 | API key validation | Check config files for API keys | Keys use placeholder values |
```

### Step 3: Register The Plugin

Open `.forgeflow/rules/reviews/_index.md` and add a new row to the registry table:

```markdown
| my-plugin | `my-plugin/` | `rules/my-plugin/rules.md` | true | 5 | -- | code | md | P0-P1 | My plugin description |
```

**Fields explained for your new plugin:**
- **Name**: `my-plugin` (lowercase, hyphens)
- **Directory**: `my-plugin/`
- **Rules File**: `rules/my-plugin/rules.md`
- **Enabled?**: `true`
- **Priority**: `5` (next available number)
- **Depends On**: `--` (independent; or list dependencies)
- **Scope**: `code` (or `docs`, or `code, docs`)
- **Report Format**: `md` (minimum requirement)
- **Blocking Threshold**: `P0-P1` (Critical + High block pipeline)
- **Description**: Brief one-liner

### Step 4: Test It

```bash
forge run --reset    # Fresh run loads all enabled plugins
```

The Review workflow will automatically scan your new plugin's rules.md file.

---

## 6. Managing Plugins

### Enable / Disable A Plugin

Edit `_index.md`:

```markdown
| coding-standard | `coding-standard/` | ... | false | 2 | -- | code | md | P0-P1 | ... |
```

Set **Enabled?** to `false`. The plugin is skipped entirely on next execution.

### Remove A Plugin

1. Delete its directory:
   ```bash
   rm -rf .forgeflow/rules/reviews/my-plugin/
   ```
2. Remove its row from `_index.md`

### Add Dependencies Between Plugins

To make `architecture` depend on `security`:

```markdown
| architecture | `architecture/` | ... | true | 3 | security | code, docs | md | P0-P1 | ... |
```

The engine will scan `security` first and pass its results as context to `architecture`.

### Change Execution Priority

Reorder the **Priority** column in `_index.md`. The engine sorts enabled plugins by Priority ascending:

| Before (Order) | After Reordering |
|-----------------|-------------------|
| security = 1 | security = 1 |
| coding-standard = 2 | architecture = 2 |
| architecture = 3 | coding-standard = 3 |
| performance = 4 | performance = 4 |

Now `architecture` runs before `coding-standard`.

---

## 7. Best Practices

### Rule Writing Guidelines

| Guideline | Why | Example |
|-----------|-----|---------|
| **One rule per check** | Easier to trace failures | Separate "no hardcoded password" from "use env vars" |
| **Use consistent severity naming** | `P0`, `P1`, `P2`, `P3` | P0 = Critical, P1 = High, P2 = Medium, P3 = Info |
| **Be specific in Check Criteria** | LLM can verify objectively | "Scan for string literal assigned to password variable" not "Check security" |
| **Include expected results** | Clear pass/fail signal | "All credentials from os.environ.get()" |

### Plugin Structure Guidelines

| Guideline | Recommendation |
|-----------|----------------|
| Max rules per plugin | 20-50 (group complex ones into sub-plugins) |
| Rules file size | Keep under 1000 lines; split if larger |
| Plugin naming | Lowercase with hyphens: `my-custom-review` |
| Dependency depth | Avoid circular dependencies; max depth = 3 |

### Report Writing Guidelines

When writing detailed findings in the report:

- Include **exact file path and line number** where possible
- Show **code snippet** (max 10 lines) with context
- Provide **Expected behavior** description
- Suggest **Fix action** (what to change)

---

## 8. Example: Adding A Security Plugin

Let's walk through creating a complete security plugin from scratch.

### Step 1: Create the directory

```bash
mkdir -p .forgeflow/rules/reviews/security-audit/
touch .forgeflow/rules/reviews/security-audit/rules.md
```

### Step 2: Write the rules

```markdown
# Security Audit Plugin Rules

## Overview

This plugin checks for common security vulnerabilities in Python and configuration files.

| Rule ID | Description | Check Criteria | Expected Result |
|---------|-------------|----------------|-----------------|
| SEC-AUD-001 | No hardcoded passwords | Scan all .py, .env, .yaml files for literal password strings | All credentials from env vars or vault |
| SEC-AUD-002 | API key not in codebase | Check all .py files for api_key assignment patterns | Keys use placeholders or env vars |
| SEC-AUD-003 | No eval() calls | Scan for eval() function usage | All dynamic execution uses ast.literal_eval() |
| SEC-AUD-004 | SQL parameterized queries | Check database query patterns | No f-string or % formatting in SQL |
```

### Step 3: Register the plugin

Edit `_index.md`:

```markdown
| security-audit | `security-audit/` | `rules/security-audit/rules.md` | true | 5 | -- | code, docs | md, csv | P0-P1 | Security vulnerability detection and compliance audit |
```

### Step 4: Test

```bash
forge run --reset
```

You should see the Review workflow execute your new security rules.

---

## 9. Roadmap

Future plugin features (non-blocking, to be added iteratively):

| Feature | Status | Description |
|---------|--------|-------------|
| `html` report export | Planned | Generated reports as styled HTML for dashboards |
| `csv` report export | Planned | Structured CSV for CI/CD pipelines and filtering |
| Plugin linter | Proposed | Validate rules.md schema at plugin registration time |
| Rule template system | Proposed | Pre-built rule templates for common review types |
| Cross-plugin aggregation | Proposed | Combine findings across multiple plugins into unified report |

---

## Quick Reference

### Directory Structure

```
.forgeflow/rules/reviews/
├── _index.md                    # Plugin registry
├── security/
│    └── rules.md                 # Security plugin rules
├── coding-standard/
│    └── rules.md                 # Coding standard rules
├── architecture/
│    └── rules.md                 # Architecture review rules
├── performance/
│    └── rules.md                 # Performance review rules
└── <your-plugin>/
     └── rules.md                  # Your plugin's rules
```

### Adding A Plugin -- 3 Commands

```bash
# 1. Create directory and rules file
mkdir -p .forgeflow/rules/reviews/my-plugin/ && touch .forgeflow/rules/reviews/my-plugin/rules.md

# 2. Edit rules.md (open in your editor)

# 3. Add row to _index.md (or edit manually)
```

### Registry Table Columns (For Reference)

```markdown
| Name | Directory | Rules File | Enabled? | Priority | Depends On | Scope | Report Format | Blocking Threshold | Description |
```

That's it. You're ready to extend ForgeFlow with custom review rules!
