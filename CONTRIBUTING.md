# Contributing to ForgeFlow

Thank you for your interest in contributing! This document explains how to contribute code, documentation, plugins, and workflows. Read it before submitting a PR.

---

## Table of Contents

- [1. Getting Started](#1-getting-started)
- [2. Development Workflow](#2-development-workflow)
- [3. Code Style Guidelines](#3-code-style-guidelines)
- [4. Documentation Guidelines](#4-documentation-guidelines)
- [5. Plugin Contribution](#5-plugin-contribution)
- [6. Pull Request Process](#6-pull-request-process)
- [7. Code Review Checklist](#7-code-review-checklist)
- [8. Release Checklist](#8-release-checklist)

---

## 1. Getting Started

### Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|-----------------|-------|
| Python | >= 3.10 | Core runtime for CLI engine |
| pip | Latest | For dependency management |
| git | Latest | For version control |

### Setup Instructions

```bash
# 1. Fork and clone the repository
git clone https://github.com/<your-username>/forgeflow.git
cd forgeflow

# 2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install in editable mode
pip install -e .

# 4. Verify the installation
forge --help
forge init --adapter copilot
```

### Project Structure

```
project-root/
├── forgeflow/                      # Python package source code
│     ├── cli/
│     │     └── main.py             # CLI entry point (all subcommands)
│     └── engine/
│         ├── runner.py             # Auto-mode pipeline engine
│         ├── config.py             # Config loader & adapter resolver
│         ├── handoff_parser.py     # Handoff block parser
│         └── yaml_parser.py        # forgeflow.json schema parser
│
├── .forgeflow/                     # Runtime root (per-project)
│     ├── workflow/                 # Workflow specs (*.md)
│     ├── protocol/                 # Artifact & handoff protocol specs
│     ├── adapter/                  # LLM adapter prompt files
│     ├── rules/                    # Plugin registry + rules
│     └── artifacts/                # Generated artifacts (runtime)
│
├── forgeflow.json                  # Project config (single data source)
├── ARCHITECTURE.md                 # Full system architecture doc
├── PLUGINS.md                      # Plugin system guide
└── README.md                       # Quick start & overview
```

---

## 2. Development Workflow

### Branch Strategy

| Branch | Purpose | Who Can Push? |
|--------|---------|---------------|
| `main` | Production-ready code | Maintainers only |
| `dev` | Integration branch for PRs | All contributors |
| `feature/<name>` | Feature development branches | Feature authors |
| `fix/<issue-number>` | Bug fix branches | Bug reporters |
| `docs/<name>` | Documentation updates | Documentation team |

### Development Steps

```bash
# 1. Create a feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/my-plugin

# 2. Make your changes...

# 3. Test your changes
forge --help                          # Verify CLI works
python -c "from forgeflow.engine.runner import ForgeRunner; print('OK')"   # Engine imports

# 4. Commit with descriptive message
git add .
git commit -m "feat: add my-plugin review rules"

# 5. Push and open PR to dev branch
git push origin feature/my-plugin
```

### Testing Checklist Before PR Submission

| Check | Command/Action | Expected Result |
|-------|----------------|-----------------|
| CLI works | `forge --help` | Shows all subcommands |
| Config loads | `forge init --adapter copilot` | Writes config.json |
| Plan prompt | `python -c "from forgeflow.engine.runner import ForgeRunner; r = ForgeRunner(); print(r.adapter_name)"` | Outputs adapter name |
| No import errors | `python -c "import forgeflow.cli.main"` | No exceptions |
| Handoff parser | Verify empty dir returns "empty" status | Bug fix verified |

---

## 3. Code Style Guidelines

### Python Code

| Rule | Detail | Example |
|------|--------|---------|
| **File encoding** | UTF-8 only | Always include `# -*- coding: utf-8 -*-` if non-ASCII characters present |
| **Indentation** | 4 spaces (no tabs) | Standard Python style |
| **Line length** | Max 120 characters | Use parentheses for long lines |
| **Docstrings** | Every public function/class must have a docstring | Google-style or NumPy-style preferred |
| **Logging** | Use `get_logger()` from `forgeflow.logging_config` | Never use `print()` for production logging |
| **Error handling** | Catch specific exceptions, log warnings | Never swallow errors silently |

### Logging Examples

```python
# GOOD
from forgeflow.logging_config import get_logger
logger = get_logger()
logger.info("Starting plan workflow")
logger.debug("Loaded %d characters from %s", len(content), path)
logger.warning("Fallback transition failed: %s", error_message)

# BAD
print("Something happened")  # Never use print for logging
raise Exception(error)      # Always log first, then raise
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Class names | PascalCase | `ForgeRunner`, `HandoffParser` |
| Function names | snake_case | `_execute_llm()`, `detect_artifact_state()` |
| Constant names | UPPER_SNAKE_CASE | `MAX_STEPS`, `DEFAULT_ADAPTER` |
| Variable names | snake_case | `current_workflow`, `handoff_block` |
| Private methods | Leading underscore | `_apply_fallback_transitions()` |

### Code Organization

- Each Python file should be focused on a single responsibility
- Import order: stdlib → third-party (if any) → local package
- No circular imports allowed
- New files must include a module-level docstring

---

## 4. Documentation Guidelines

### Markdown Style

| Rule | Detail | Example |
|------|--------|---------|
| **Heading hierarchy** | Start with `#`, no skipping levels | `# H1` → `## H2` → `### H3` |
| **Tables** | Always include header row and separator | Use standard CommonMark table syntax |
| **Links** | Relative paths only for internal links | `[ARCHITECTURE.md](./ARCHITECTURE.md)` |
| **Code blocks** | Specify language for syntax highlighting | ```python, ```bash, ```json |
| **Emphasis** | Bold for key terms, italic for notes | Use sparingly; avoid ALL CAPS |

### Documentation Checklist Before PR Submission

| Check | Detail |
|-------|--------|
| All new sections have a table of contents entry | Links point to the right sections |
| All external links are valid | No broken references in README, ARCHITECTURE.md, or PLUGINS.md |
| Code examples work as written | Copy-paste test passes |
| Plugin registry table updated | Any plugin change updates `_index.md` accordingly |
| CLI commands match actual behavior | `forge plan`, `forge run --auto`, etc. |

---

## 5. Plugin Contribution

### When To Contribute A Plugin

You should contribute a new plugin when:
- The plugin serves **more than one project** (general-purpose)
- It addresses a **common concern** (security, performance, code quality)
- It has a **well-defined rule checklist** that can be validated by LLMs

### How To Contribute A Plugin

```bash
# 1. Create the plugin directory
mkdir -p .forgeflow/rules/reviews/my-plugin/
touch .forgeflow/rules/reviews/my-plugin/rules.md

# 2. Write your rules (see PLUGINS.md for format)

# 3. Register in _index.md
# Add a row with: Name, Directory, Rules File, Enabled?, Priority, 
# Depends On, Scope, Report Format, Blocking Threshold, Description

# 4. Test
forge run --reset

# 5. Submit PR
git add .forgeflow/rules/reviews/
git commit -m "feat: add my-plugin for general-purpose review"
```

### Plugin Review Criteria

| Criterion | Weight | Detail |
|-----------|--------|--------|
| **Generality** | High | Would others find this useful? |
| **Rule quality** | High | Are rules specific, testable, and well-scoped? |
| **Documentation** | Medium | Is `rules.md` well-commented with examples? |
| **Integration** | Medium | Does it fit into the existing pipeline flow? |
| **Conflict** | Low | Does it duplicate an existing plugin's purpose? |

### Recommended Plugin Topics (Priority Order)

1. **Dependency security** -- Vulnerability scanning of pip/npm dependencies
2. **Code coverage validation** -- Ensures test coverage meets thresholds
3. **Documentation review** -- Checks docs completeness and accuracy
4. **I18n compliance** -- Validates localization readiness
5. **Accessibility audit** -- Checks for accessibility best practices

---

## 6. Pull Request Process

### PR Template

When creating a PR, use this template:

```markdown
## What does this PR do?
<!-- Brief description of what changed and why -->

## How to test?
<!-- Steps to reproduce the behavior -->
1. Run `forge plan --intent "..."`
2. Check that artifact is generated correctly
3. Verify handoff block parses correctly
4. For same-project additions, run `forge plan --incremental --intent "..."`
   and verify unaffected Feature evidence remains current

## Checklist
- [ ] Code follows style guidelines
- [ ] All documentation updated (README, ARCHITECTURE.md, PLUGINS.md)
- [ ] Plugin registry (_index.md) updated if applicable
- [ ] No breaking changes to existing functionality
- [ ] Test plan included above

## Related Issues
<!-- Link to relevant issues: #123 -->
```

### PR Review Process

| Step | Who | Action |
|------|-----|--------|
| 1 | Author | Submit PR with template filled out |
| 2 | Maintainer | Assign at least one reviewer |
| 3 | Reviewer | Check code quality, docs, plugin rules |
| 4 | Reviewer | Request changes or approve |
| 5 | Author | Address feedback |
| 6 | Maintainer | Merge to `dev` after approval |

### Acceptance Criteria For Merging

- [ ] All checks pass (imports work, CLI responds)
- [ ] Documentation is up-to-date
- [ ] No breaking changes to existing functionality
- [ ] Plugin rules are specific and testable
- [ ] Code has sufficient logging (no `print()` statements)

---

## 7. Code Review Checklist

### Python Code

| Check | Detail |
|-------|--------|
| Module docstring present? | Every `.py` file must have a top-level description |
| Logging used correctly? | Use `get_logger()`, not `print()` |
| Error handling adequate? | Exceptions caught with specific types, logged with warnings |
| No hardcoded values? | Config-driven where possible |
| Import order correct? | stdlib → local package (no third-party yet) |

### Documentation

| Check | Detail |
|-------|--------|
| All links valid? | Internal and external links checked |
| Tables properly formatted? | Header row + separator present |
| Consistent terminology? | Use "artifact", "workflow", "handoff" correctly |
| Updated for changes? | No stale documentation after code modifications |

### Plugins

| Check | Detail |
|-------|--------|
| Rules.md follows checklist format? | Has table with Rule ID, Description, Criteria, Expected |
| _index.md updated? | New row added with all 10 fields |
| Plugin name is unique? | No conflicts with existing plugins |
| Scope appropriate? | `code`, `docs`, or `code, docs` correctly assigned |

---

## 8. Release Checklist

Before publishing a new version:

- [ ] Update `pyproject.toml` version number
- [ ] Update all workflow versions (Plan v2.3, Handoff v2.4, etc.)
- [ ] Update `_index.md` for any plugin changes
- [ ] Test `forge init`, `forge plan`, `forge run --reset` end-to-end
- [ ] Verify README links all point to existing files
- [ ] Run through ARCHITECTURE.md examples
- [ ] Check that .gitignore covers all new file types
- [ ] Update changelog (if applicable)

---

## Quick Reference

### Directory Structure Reminder

```
.project-root/
├── forgeflow/                      # Python source
│     ├── cli/main.py               # CLI entry point
│     └── engine/                   # Engine components
│         ├── runner.py             # Auto-mode loop
│         ├── config.py             # Config loader
│         ├── handoff_parser.py     # Handoff parser
│         └── yaml_parser.py        # JSON schema parser
├── .forgeflow/                     # Runtime root
│     ├── workflow/                 # Workflow specs
│     ├── protocol/                 # Protocol specs
│     ├── adapter/                  # LLM adapters
│     ├── rules/                    # Plugin registry + rules
│     └── artifacts/                # Generated artifacts
├── forgeflow.json                  # Project config
├── ARCHITECTURE.md                 # Architecture doc
├── PLUGINS.md                      # Plugin guide
└── README.md                       # Overview & quick start
```

### Useful Commands

| Command | Purpose |
|---------|---------|
| `forge --help` | Show all subcommands |
| `forge init --adapter copilot` | Initialize project |
| `forge run` | Start auto-mode pipeline |
| `forge status` | Show current state |
| `forge reset --force` | Clean artifacts/ |
| `forge handoff` | Debug latest handoff |

### Communication Channels

For questions or discussions:
- Open an issue with the "question" label
- Tag a maintainer in comments for urgent issues

---

Thank you for contributing to ForgeFlow! Your efforts make this framework more robust and useful for everyone.
