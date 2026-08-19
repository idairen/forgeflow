# ForgeFlow Governance

ForgeFlow currently uses a maintainer-led governance model appropriate for an early
Technical Preview.

## Roles

- **Maintainer:** owns repository administration, releases, security response,
  roadmap decisions, and final merge authority.
- **Contributor:** proposes code, protocol, documentation, tests, plugins, or issue
  analysis through the public contribution process.
- **Reviewer:** provides scoped technical review; review does not imply maintainer
  authority unless explicitly granted.

The current maintainer is the repository owner, `@idairen`.

## Decision Process

Routine fixes and documentation changes may proceed through a normal pull request.
Changes to protocol precedence, Artifact ownership, scope semantics, canonical
Handoffs, compatibility, or package identity require an issue or clearly documented
design rationale before merge.

The maintainer considers correctness, backward compatibility, evidence, maintenance
cost, security, and alignment with ForgeFlow's role as an Agent-agnostic engineering
protocol. Final decisions are recorded in issues, pull requests, releases, or the
Changelog rather than private undocumented agreements.

## Releases

Releases follow Semantic Versioning during the Technical Preview, with the caveat
that minor releases may still contain protocol changes. The release checklist in
`docs/maintainers/releasing.md` defines the required evidence.

## Evolution

Governance may expand to multiple maintainers, documented voting, or working groups
when sustained contributor activity makes that useful. This file records current
governance, not a promise of future roles.
