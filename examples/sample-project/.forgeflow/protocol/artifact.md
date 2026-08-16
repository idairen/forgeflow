# Artifact Protocol (Sample)

This file shows the structure. The real version lives in `FORGEFLOW_ROOT/.forgeflow/protocol/artifact.md`.

## Purpose

Artifacts are Markdown files under `.forgeflow/artifacts/` that form the sole persistent source of truth.

## Metadata Table Required

Every artifact MUST begin with:
```markdown
# ArtifactTitle

Metadata
---
| Field | Value |
| --- | --- |
| Artifact Type | Planning/Requirement/SolutionPlan/etc |
| Version | 1.0 |
| Status | READY |
| Owner Workflow | Plan/Grill/Solution/etc |
```

## Canonical Filenames

| Artifact Type | Filename Pattern | Example |
|---------------|------------------|---------|
| Planning | `planning.md` | `planning.md` |
| Requirement | `requirement-feature-XX.md` | `requirement-feature-01.md` |
| SolutionPlan | `solution-plan.md` | `solution-plan.md` |
| SlicePlan | `slice-plan-feature-XX.md` | `slice-plan-feature-01.md` |
| TDDRecord | `tdd-feature-XX-slice-XX.md` | `tdd-feature-01-slice-01.md` |
| ReviewReport | `review-feature-XX-slice-XX-attempt-NN.md` | `review-feature-01-slice-01-attempt-01.md` |

## Artifact Root

The canonical artifact root is `.forgeflow/artifacts/`. All active artifacts MUST be stored directly under this directory.
