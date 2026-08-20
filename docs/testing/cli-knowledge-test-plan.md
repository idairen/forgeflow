# ForgeFlow CLI Knowledge Test Plan

## Scope

This plan verifies the derived Project Knowledge View and `forge knowledge`
command. It does not replace the IDE acceptance baseline and does not treat query
output as transition authority.

## Required cases

| ID | Case | Expected result |
| --- | --- | --- |
| CLI-KNO-001 | Empty Artifact Root | Status is `empty`; no Features are invented. |
| CLI-KNO-002 | Valid multi-Feature graph | Planning Feature order and each Slice Plan order are preserved. |
| CLI-KNO-003 | `--feature F-XX` | Only the active requested Feature subtree is returned. |
| CLI-KNO-004 | `--slice F-XX/S-XX` | Only the active requested Slice is returned under its Feature. |
| CLI-KNO-005 | Malformed or inactive filter | Command fails without changing files. |
| CLI-KNO-006 | Default query | Historical indexes and archived timeline entries are omitted. |
| CLI-KNO-007 | `--history` | Artifact/Report history, rotated roots, and valid archived contract versions are indexed. |
| CLI-KNO-008 | Invalid historical metadata | Current view remains available and includes a warning. |
| CLI-KNO-009 | Invalid active Artifact Graph | Current knowledge is `unavailable`; partial Artifacts are not combined. |
| CLI-KNO-010 | `--format markdown` | Output is readable and links canonical filenames and versions. |
| CLI-KNO-011 | Query execution | No Artifact, Report, Runtime, or source file is created or modified. |
| CLI-KNO-012 | `forge status` compatibility | Full non-authoritative `project_knowledge` remains present. |
| CLI-KNO-013 | Structured multi-Feature Solution | Forward, reverse, and component indexes preserve Planning order. |
| CLI-KNO-014 | `--impact F-XX` | Direct and transitive dependents are returned; component peers remain separate. |
| CLI-KNO-015 | `--component SC-XX` | Only active Features mapped to the component are returned. |
| CLI-KNO-016 | Legacy Solution without impact metadata | Knowledge remains available and impact status is explicitly `unavailable`. |
| CLI-KNO-017 | Partial, cyclic, or unresolved impact metadata | Active graph is invalid; no partial impact result is presented. |

## Automated commands

```bash
PYTHONPATH=src python3 -m unittest \
  tests.unit.test_project_knowledge \
  tests.unit.test_project_impact \
  tests.integration.test_cli_knowledge \
  tests.integration.test_runner_protocol
```

The full repository regression remains mandatory before release.
