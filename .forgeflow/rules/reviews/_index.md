# Review Plugin Index (Registry)

This file serves as the plugin registry for the ForgeFlow review engine.
Each enabled plugin lives in its own subdirectory under `.forgeflow/rules/reviews/<name>/`.

## Plugin Table

| Name | Directory | Rules File | Enabled? | Priority | Depends On | Scope | Report Format | Blocking Threshold | Description |
|------|-----------|-----------|----------|----------|------------|-------|---------------|-------------------|-------------|
| security | `security/` | `rules/security/rules.md` | true | 1 | — | code, docs | md, csv | P0–P1 | Security vulnerability detection and compliance |
| coding-standard | `coding-standard/` | `rules/coding-standard/rules.md` | true | 2 | security | code | md, csv | P0–P1 | Coding style, naming conventions, PEP8 compliance |
| architecture | `architecture/` | `rules/architecture/rules.md` | true | 3 | — | code, docs | md, html, csv | P0–P1 | Design patterns, coupling, modularity assessment |
| performance | `performance/` | `rules/performance/rules.md` | true | 4 | architecture | code | md, csv | P0–P2 | Performance anti-patterns and efficiency analysis |

## Field Definitions

### Name
Human-readable plugin identifier. Must be lowercase with hyphens (no spaces or underscores).

### Directory
Subdirectory under `.forgeflow/rules/reviews/` that contains `rules.md`.

### Rules File
Path to the rule definition file relative to `.forgeflow/rules/reviews/`.

### Enabled?
- `true` — this plugin is active and its rules will be scanned
- `false` — this plugin is inactive; it is skipped during review execution

Set to `false` to temporarily disable a plugin without deleting its rules.

### Priority
Execution order number (lower value = earlier in the scan sequence).
Use sequential integers starting from 1. Plugins with the same priority are scanned in alphabetical order by name.

**Guidance:**
- Set `Priority=1` for foundational checks (e.g., security) that other plugins may depend on
- Each plugin should have a unique priority to ensure deterministic execution order
- Default priorities: security=1, coding-standard=2, architecture=3, performance=4

### Depends On
Comma-separated list of other plugin names this plugin depends on. The engine will scan the listed plugins first and pass their results as context for dependent plugins.

**Examples:**
| Value | Meaning |
|-------|---------|
| — | No dependencies (scans independently) |
| `security` | Depends on security report context |
| `security, architecture` | Depends on both security and architecture results |

Rules are scanned in the order specified here. If a dependency is disabled (`Enabled? = false`), the dependent plugin is also skipped unless overridden by `Force Run = true`.

### Scope
Where this plugin applies its checks:
- `code` — source code files only (`.py`, `.js`, `.ts`, etc.)
- `docs` — design docs, plans, architecture decision records
- `code, docs` — both source and documentation artifacts

### Report Format
Preferred output formats for the generated report. Multiple formats are separated by commas:
- `md` — Markdown (default, always available)
- `csv` — CSV for CI/CD dashboards and data filtering
- `html` — Styled HTML for dashboards or Wiki pages

If multiple formats are listed, all are generated simultaneously. The first format in the list is used as the primary output.

### Blocking Threshold
Defines which severity levels trigger a BLOCK (prevents the pipeline from proceeding). Format: `Pn–Pm`.

| Threshold | Meaning |
|-----------|---------|
| `P0` | Only Critical blocks the pipeline |
| `P0–P1` | Critical and High block the pipeline |
| `P0–P2` | Critical, High, Medium all block (strict mode) |
| `P0–P3` | Anything non-passing is a blocker (most strict) |

**Default recommendation:** `P0–P1` for production-safe projects, `P0–P2` for internal tools.

### Description
Short one-line summary of what the plugin does. Shown in Plugin Registry table and used by users adding new plugins.

## How Plugins Work

Each plugin is defined by a `rules.md` file containing:
1. A checklist table with rule IDs, descriptions, severity levels, check criteria, and expected results
2. Any supplementary notes or context
3. Optional examples for complex rules (positive/negative)

The review engine:
1. Reads this index to determine which plugins are enabled
2. Sorts enabled plugins by `Priority` ascending
3. Resolves `Depends On` relationships — scans dependencies first
4. For each plugin in order: loads `rules.md`, applies rules against artifacts, records verdicts
5. Generates a structured report for each plugin at `.forgeflow/reports/<name>/report.<format>`
6. Aggregates all results and applies `Blocking Threshold` to decide PASS/FAIL

## Adding a New Plugin

To add a new review plugin:
1. Create `.forgeflow/rules/reviews/<new-plugin>/rules.md` with a checklist table
2. Add an entry to the Plugin Table above with `Enabled? = true` and appropriate field values
3. Run `forge-run review` — the engine loads it automatically

### Field Value Tips for New Plugins

- **Priority:** Use next available number (e.g., if max priority is 4, use 5)
- **Depends On:** List plugins whose findings should be visible when scanning this plugin's rules
- **Scope:** `code` alone is safe for most; add `docs` if you need to check design docs
- **Report Format:** At minimum include `md`; add `csv` or `html` as needed
- **Blocking Threshold:** Start with `P0–P1` — adjust stricter only after validation

## Report Output Structure

Each plugin generates a report containing:
- **Header**: Plugin name, rules version, review date
- **Summary Table**: All rules with status (PASS/FAIL/WARN) and severity breakdown
- **Detailed Findings**: For every FAIL and WARN entry
- **Recommendations**: Actionable suggestions organized by severity level

Reports are saved to `.forgeflow/reports/<name>/report.<ext>` for each configured format.

## Backward Compatibility

Existing plugins (security, coding-standard, architecture, performance) are pre-populated with default values for all new fields. Their behavior is unchanged unless you manually modify these fields.
