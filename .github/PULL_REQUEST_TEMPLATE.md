## Summary

Describe the problem and the focused change.

## Contract Impact

Identify affected Workflows, Scopes, Artifacts, Handoffs, Adapters, CLI behavior, or
installer behavior. Write `None` when the change has no contract impact.

## Validation

List exact commands and real-host evidence. Distinguish automated tests from actual
Codex or Copilot execution.

## Checklist

- [ ] The change is focused and contains no unrelated cleanup.
- [ ] Tests cover deterministic behavior changes.
- [ ] Host compatibility claims include captured real-host evidence.
- [ ] Documentation and examples match current behavior.
- [ ] `CHANGELOG.md` records user-visible changes.
- [ ] No secrets, runtime evidence, temporary profiles, or local paths are committed.
- [ ] Breaking changes and migration steps are explicit.
