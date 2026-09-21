# Review plugins

The authoritative registry is [`.forgeflow/rules/reviews/_index.md`](.forgeflow/rules/reviews/_index.md).
Review evaluates enabled plugins within the authorized Slice in dependency/priority
order, applies applicability and registered blocking thresholds, and generates every
configured report format. Implement self-checking does not replace independent Review.

| Plugin | Applicability | Formats | Blocking threshold |
| --- | --- | --- | --- |
| security | Executable code/security configuration; absent surfaces N/A | md, csv | P0–P1 |
| coding-standard | Python source | md, csv | P0–P1 |
| architecture | Implemented architecture | md, html, csv | P0–P1 |
| performance | Implemented runtime/data surfaces | md, csv | P0–P1 |

PASS, VIOLATION, UNKNOWN and N/A are plugin verdicts, not canonical Review decisions.
Only applicable VIOLATION findings cross the registered threshold; UNKNOWN needs
independent blocking evidence to block. Required missing evidence is still evaluated
under the framework gate. The canonical Findings table aggregates Review PASS/FAIL.

Reports live under `.forgeflow/reports/<plugin>/` at the exact attempt-scoped paths
specified by the registry. Replacement requires immutable revision archival. Reports
never join the active Artifact Graph. Do not impose the retired exact CSV/Markdown
serialization template; use the current registry's summary and detail requirements.

To add a plugin, create its rules file and one complete registry row. The core remains
Markdown; no plugin runtime API or platform integration is required or implied.
