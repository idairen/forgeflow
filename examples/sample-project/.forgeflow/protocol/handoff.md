# Handoff Protocol (Sample)

This file shows the structure. The real version lives in `FORGEFLOW_ROOT/.forgeflow/protocol/handoff.md`.

## Purpose

A handoff records the result of a workflow execution — the decision, artifacts produced, and what happens next.

## Canonical Templates

### FORWARD (Progress to Next Workflow)
```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | FORWARD |
| Next Workflow | {{workflow_name}} |
| Source Scope | {{scope}} |
| Target Scope | {{scope}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{reason}} |
```

### RETURN (Blocker — Return to Upstream Owner)
```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | RETURN |
| Next Workflow | {{workflow_name}} |
| Blocker Category | {{category}} |
| Source Scope | {{scope}} |
| Target Scope | {{scope}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{reason}} |
```

### TERMINAL (Pipeline Complete)
```markdown
### Handoff

| Field | Value |
| --- | --- |
| Transition | TERMINAL |
| Source Scope | {{scope}} |
| Completed Scope | {{completed_scope}} |
| Input Artifacts | {{artifact_list}} |
| Reason | {{reason}} |
```

## Blocker Routing Rules

| Blocker Category | Owner Workflow | Meaning |
|------------------|---------------|---------|
| `PLAN_GAP` | Plan | Missing features, overlapping scope |
| `BUSINESS_GAP` | Grill | Requirement missing or contradictory |
| `ENGINEERING_GAP` | Solution | SolutionPlan missing or outdated |
| `SLICE_VIOLATION` | Slice | SlicePlan boundary wrong or dependency invalid |

## Validation Checklist

Before accepting a handoff:
1. Exactly one typed variant (FORWARD/RETURN/TERMINAL) applies
2. Every required field is present and every forbidden field is absent
3. Workflow names are canonical (match known list)
4. Input Artifacts entries use only valid filenames
5. The block is the final content of the response (no trailing prose)
