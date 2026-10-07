# CLI artifact compatibility

The Markdown protocol remains authoritative. The CLI validates recorded structure;
independent Review evaluates the truth of execution evidence, applicability of
alternatives and substantive coverage. These optional mapping tables are projections
of existing approved obligations, not new approval gates or permission to weaken
Solution/Slice policy. Their absence does not authorize heuristic matching.

## Ordered identifiers and verification-only attempts

`Feature IDs in order` and `Slice IDs in order` are the protocol field names. The
CLI retains the original metadata and projects `Feature IDs` and `Slice IDs` for
existing consumers. Legacy keys are accepted; conflicting values are rejected.
Order is preserved.

An Implement placement section can explicitly state `No product path is added,
moved or modified.`, `No application source, test or configuration change.`, or
`No application files changed.`. Any listed Changed Files must be framework or
evidence bookkeeping under `.forgeflow/` or `docs/`. A malformed table, traversal
path or contradictory product change is rejected. This validates the declaration;
Review must compare it with the actual changed files and approved placement.

## TDD result semantics

In Verification Evidence, Result describes the check execution: a genuine RED test
is `FAILED`, followed by successful GREEN evidence. Capturing RED correctly does
not make the test itself successful. Retain command, pre-change state, actual
failure and output. Environment errors do not establish genuine RED.

Existing records that mark RED as `SUCCEEDED` while recording `exit 1` receive a
specific conflict diagnostic. The CLI never edits them or converts results based
on prose. Preserve historical records; corrections or revalidation follow the
authorized artifact lifecycle and receive independent Review.

## Explicit conditional alternatives

A Slice Plan may project an already approved conditional alternative:

```markdown
## Verification Alternatives

| Slice ID | Obligation | Strategies | Condition |
| --- | --- | --- | --- |
| S-01 | VR-02 | TDD; CHARACTERIZATION_TEST | ED-10: unchanged predecessor; all approved eligibility conditions hold |
```

Obligation must exactly match one Verification Plan row for that Slice. Each group
has at least two declared strategies, belongs to that row and cannot overlap
another group. All strategies outside the group remain mandatory. Exactly one
group member is selected.

Implement records the same group and condition plus its actual evidence:

```markdown
## Verification Alternative Evidence

| Obligation | Strategies | Condition | Evidence Reference |
| --- | --- | --- | --- |
| VR-02 | TDD; CHARACTERIZATION_TEST | ED-10: unchanged predecessor; all approved eligibility conditions hold | docs/revalidation.md: lineage, source hashes and before/after execution output |
```

Condition and strategy text must match the approved mapping. A word such as
`alternative` in rationale is insufficient. A table is a recorded claim; Review
must inspect the referenced provenance and determine whether the condition holds.
No historical PASS automatically satisfies current checks.

## Check-to-evidence mapping

When Implement names its executed checks differently, record the relationship:

```markdown
## Verification Coverage

| Required Check | Evidence Check |
| --- | --- |
| Validate archive rollback and reload | Archive abort integration test |
| Validate archive rollback and reload | Browser reload journey |
```

Required Check exactly matches one current Slice Verification Plan check, split
on `; `. Evidence Check exactly matches an Implement Verification Evidence label.
Every mapped label must exist and its latest result must succeed, or carry an
approved explicit applicability condition for NOT_APPLICABLE. Its strategy must
belong to the obligation. Multiple rows can map a grouped obligation to several
executions; every mapped execution is checked. Extra undeclared checks and dangling
references are rejected. Without a mapping, the existing exact-label path remains.

The CLI does not infer coverage from shared words or a PASS Review. Independent
Review must establish that the mapped executions actually cover each required
property. Missing mappings remain blocked with a specific diagnostic.

## Private real-project regression

Run from this source checkout with the editable environment active:

```bash
PYTHONPATH=src FORGEFLOW_REGRESSION_PROJECT=/absolute/path/to/project \
  python -B -m unittest tests.integration.test_cli_artifact_compatibility -v
```

The opt-in case targets the maintainer's completed two-Feature task-manager snapshot.
It reads the original project, compares source/artifact hashes before and after, and
expects three RED-result conflicts plus three unmapped conditional alternatives.
It never executes the application, updates original records or claims COMPLETE.
Default CI skips this private-project case and runs the portable positive/negative
fixtures. No private project files or absolute paths are bundled into the tests.
