# ForgeFlow Compatibility

Version: 2.2

ForgeFlow core is platform-independent and consists entirely of Markdown. It
requires only a participant capable of reading and updating Markdown files in the
order defined by the framework.

## Canonical specifications

| Contract | Version | Path |
| --- | --- | --- |
| Framework | 2.2 | `forgeflow.md` |
| Artifact Protocol | 2.2 | `protocol/artifact.md` |
| Handoff Protocol | 2.2 | `protocol/handoff.md` |
| Transition Protocol | 2.2 | `protocol/transition.md` |
| Conformance Protocol | 2.2 | `protocol/conformance.md` |

## Workflow compatibility

| Workflow | Artifact Type | Scope | Specification |
| --- | --- | --- | --- |
| Plan | Planning | Project | `workflow/plan.md` |
| Grill | Requirement | Feature | `workflow/grill.md` |
| Solution | Solution Plan | Project | `workflow/solution.md` |
| Slice | Slice Plan | Feature | `workflow/slice.md` |
| TDD | TDD Record | Slice | `workflow/tdd.md` |
| Review | Review Report | Slice | `workflow/review.md` |

## Platform adapters

Adapters are optional Markdown launchers. They add no framework rule and cannot
override the core specifications.

| Adapter | Status | Path |
| --- | --- | --- |
| Generic participant | Supported through the core specifications | `forgeflow.md` |
| Codex | Supported | `adapter/codex/` |
| Copilot | Supported | `adapter/copilot/` |
| Claude | No launcher supplied | `adapter/claude/` |
| Gemini | No launcher supplied | `adapter/gemini/` |

A new platform becomes compatible by supplying Markdown launchers that reference
the canonical specifications. No Python package, schema engine, plugin, model API,
or platform-specific state store is part of ForgeFlow core.
