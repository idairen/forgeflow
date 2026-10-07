# CLI artifact compatibility repair — 2026-10-07

Public baseline: `bc57f670e985c7725a13d20e6bbf2b3e57c68d22`. Branch: `fix/cli-artifact-compatibility`.

Scope: synchronize the CLI repair, portable tests and documentation onto the public
source lineage. Public package identities, repository links, release assets and
framework contracts remain unchanged. This record was generated before the local
commit; no registry publication is part of this change.

## Behavior

- Parse ordered metadata and reject conflicting aliases without cascading errors.
- Accept explicit verification-only placement declarations; reject contradictory changes.
- Diagnose RED result conflicts while preserving original records.
- Require explicit conditional strategy and check-to-evidence mappings, with cumulative checks retained.
- Treat mapping/evidence truth as an independent Review obligation.

## Validation

117 Python tests passed locally, including the opt-in original-project regression.
35 Markdown contract tests and 10 npm tests passed. Documentation and IDE inventory
checks passed. The opt-in project remained byte-identical and HALTED with three
RED-result conflicts and three missing conditional mappings. No application or
live host/model execution is claimed. CI skips the unavailable private sample.

## File inventory

- `CHANGELOG.md`
- `docs/reference/cli.md`
- `src/forgeflow/engine/artifact_parser.py`
- `src/forgeflow/engine/verification.py`
- `docs/maintainers/cli-artifact-compatibility.md`
- `tests/integration/test_cli_artifact_compatibility.py`
- `docs/maintainers/2026-10-07-cli-artifact-compatibility-repair.md`

## Exact unified diffs

Zero-context diffs preserve exact changed lines; the public baseline supplies surrounding context. The record itself is listed but its diff is omitted to avoid recursion.

```diff
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -10,0 +11,15 @@
+
+### CLI artifact compatibility
+
+- Parse the protocol's ordered Feature/Slice metadata keys while retaining legacy
+  CLI aliases; reject conflicting aliases and avoid dependent missing-key errors.
+- Accept explicit verification-only placement declarations when the Changed Files
+  list contains only framework/evidence bookkeeping; malformed tables and
+  contradictory implementation changes remain errors.
+- Diagnose a RED row marked successful despite a recorded failing test exit.
+  Original execution evidence is never rewritten or automatically reinterpreted.
+- Support explicit conditional-strategy and check-to-evidence mappings. Remove
+  English-keyword-based strategy waivers and keep unmapped obligations blocked.
+- Add an opt-in read-only regression against the maintainer's completed project.
+  These checks validate recorded structure, not a fresh IDE or application run.
+
```

```diff
--- a/docs/reference/cli.md
+++ b/docs/reference/cli.md
@@ -107,0 +108,4 @@
+For ordered metadata, verification-only attempts, RED result semantics and explicit
+verification mappings, see [artifact compatibility](../maintainers/cli-artifact-compatibility.md).
+Structural validation does not establish the truth or coverage of execution claims.
+
```

```diff
--- a/src/forgeflow/engine/artifact_parser.py
+++ b/src/forgeflow/engine/artifact_parser.py
@@ -237 +237 @@
-        if root_entries and "planning.md" not in artifacts:
+        if root_entries and not (root / "planning.md").exists():
@@ -268 +268 @@
-                diagnostics.append({"code": "artifact_invalid", "artifacts": [cls._artifact_evidence(root / artifact['filename'])]})
+                diagnostics.append({"code": cls._diagnostic_code(str(error)), "artifacts": [cls._artifact_evidence(root / artifact['filename'])]})
@@ -294,0 +295,12 @@
+        coverage = record.get("verification_coverage", [])
+        current_checks = {check for row in plan.get("verification_plan", [])
+                          if row["Slice ID"] == meta["Slice ID"]
+                          for check in row["Required Checks"].split("; ")}
+        if any(mapping["Required Check"] not in current_checks for mapping in coverage):
+            raise ValueError("Verification Coverage references undeclared required check")
+        applicable_alternatives = [row for row in plan.get("verification_alternatives", [])
+                                   if row["Slice ID"] == meta["Slice ID"]]
+        for row in record.get("verification_alternative_evidence", []):
+            if not any(all(row[k] == approved[k] for k in ("Obligation", "Strategies", "Condition"))
+                       for approved in applicable_alternatives):
+                raise ValueError("conditional strategy alternative lacks matching condition evidence")
@@ -298,0 +311,11 @@
+            for alternative in applicable_alternatives:
+                if alternative["Obligation"] != obligation["Obligation"]:
+                    continue
+                choices = set(alternative["Strategies"].split("; "))
+                if len(choices & selected) != 1:
+                    raise ValueError("conditional strategy alternative requires exactly one selected strategy")
+                matching = [row for row in record.get("verification_alternative_evidence", [])
+                            if all(row[k] == alternative[k] for k in ("Obligation", "Strategies", "Condition"))]
+                if len(matching) != 1:
+                    raise ValueError("conditional strategy alternative lacks matching condition evidence")
+                required -= choices
@@ -300,7 +323,4 @@
-                # Conditions remain normative prose evaluated by the participant;
-                # the CLI never infers an unstated alternative from convenience.
-                if "alternative" not in obligation["Rationale"].lower():
-                    raise ValueError("READY_FOR_REVIEW omits mandatory Slice strategy")
-                choices = [s for s in record.get("verification_selection", []) if s["Governing Obligation"] == obligation["Obligation"]]
-                if not choices:
-                    raise ValueError("missing permitted alternative rationale")
+                # Prose is not a machine-readable permission to omit a strategy.
+                # In particular, one English keyword cannot authorize a waiver.
+                raise ValueError("READY_FOR_REVIEW omits mandatory Slice strategy; "
+                                 "conditional alternatives require explicit verification mapping")
@@ -308,5 +328,13 @@
-                rows = [e for e in evidence if e["Obligation or Check"] == check]
-                if not rows or rows[-1]["Result"] not in {"SUCCEEDED", "NOT_APPLICABLE"}:
-                    raise ValueError(f"READY_FOR_REVIEW missing or pending required check: {check}")
-                if rows[-1]["Result"] == "NOT_APPLICABLE" and "applicab" not in obligation["Rationale"].lower():
-                    raise ValueError("NOT_APPLICABLE lacks an explicit plan condition")
+                labels = [mapping["Evidence Check"] for mapping in coverage if mapping["Required Check"] == check]
+                labels = labels or [check]
+                rows = [e for e in evidence if e["Obligation or Check"] in labels]
+                if not rows:
+                    raise ValueError(f"required check has no explicit evidence mapping: {check}")
+                for label in labels:
+                    results = [e for e in rows if e["Obligation or Check"] == label]
+                    if not results or results[-1]["Result"] not in {"SUCCEEDED", "NOT_APPLICABLE"}:
+                        raise ValueError(f"READY_FOR_REVIEW missing or pending required check: {check}")
+                    if results[-1]["Strategy"] not in required | selected.intersection(set(obligation["Strategies"].split("; "))):
+                        raise ValueError("required check evidence uses unrelated strategy")
+                    if results[-1]["Result"] == "NOT_APPLICABLE" and "applicab" not in obligation["Rationale"].lower():
+                        raise ValueError("NOT_APPLICABLE lacks an explicit plan condition")
@@ -374,0 +403 @@
+            return None, errors
@@ -476,0 +506,9 @@
+        # The Markdown contracts name these ordered lists explicitly. Retain
+        # their source keys, and project aliases for existing graph consumers.
+        for canonical, internal in (("Feature IDs in order", "Feature IDs"),
+                                    ("Slice IDs in order", "Slice IDs")):
+            if canonical in metadata:
+                if internal in metadata and metadata[internal] != metadata[canonical]:
+                    errors.append(f"conflicting metadata aliases: {canonical} / {internal}")
+                else:
+                    metadata[internal] = metadata[canonical]
@@ -590,0 +629,9 @@
+            if name == "File Placement Conformance":
+                end = next((i for i in range(index, len(lines))
+                            if lines[i].startswith("## ")), len(lines))
+                body = "\n".join(lines[index:end]).strip()
+                # The contract requires the table for implementation file
+                # changes, not for a verification-only Attempt. A malformed
+                # table or a contradictory Changed Files list still fails.
+                if cls._no_implementation_changes(text, body):
+                    continue
@@ -596,0 +644,21 @@
+
+    @staticmethod
+    def _no_implementation_changes(text, placement):
+        declarations = (
+            "No product path is added, moved or modified.",
+            "No application source, test or configuration change.",
+            "No application files changed.",
+        )
+        if not placement.startswith(declarations) or "|" in placement:
+            return False
+        changed = re.search(r"(?ms)^## Changed Files\s*\n(.*?)(?=^## |\Z)", text)
+        if changed:
+            for line in changed.group(1).splitlines():
+                if not line.startswith("- "):
+                    continue
+                path = line[2:].split(":", 1)[0].strip().strip("`")
+                if not path.startswith((".forgeflow/", "docs/")):
+                    return False
+                if ".." in path.split("/"):
+                    return False
+        return True
```

```diff
--- a/src/forgeflow/engine/verification.py
+++ b/src/forgeflow/engine/verification.py
@@ -13,0 +14,3 @@
+    "Verification Alternatives": ("Slice ID", "Obligation", "Strategies", "Condition"),
+    "Verification Alternative Evidence": ("Obligation", "Strategies", "Condition", "Evidence Reference"),
+    "Verification Coverage": ("Required Check", "Evidence Check"),
@@ -69,0 +73,2 @@
+        if "Slice IDs" not in metadata:
+            raise ValueError("missing metadata: Slice IDs in order")
@@ -77 +82,15 @@
-        return {"verification_plan": rows, "verification_actionable": True}
+        alternatives = table(text, "Verification Alternatives") if "## Verification Alternatives" in text else []
+        groups = set()
+        for alternative in alternatives:
+            key = (alternative["Slice ID"], alternative["Obligation"])
+            governing = [r for r in rows if (r["Slice ID"], r["Obligation"]) == key]
+            choices = strategy_list(alternative["Strategies"])
+            if len(governing) != 1 or len(choices) < 2 or not set(choices) <= set(strategy_list(governing[0]["Strategies"])):
+                raise ValueError("Verification Alternatives must reference one declared obligation and its strategies")
+            for choice in choices:
+                identity = (*key, choice)
+                if identity in groups:
+                    raise ValueError("overlapping Verification Alternatives")
+                groups.add(identity)
+        return {"verification_plan": rows, "verification_actionable": True,
+                "verification_alternatives": alternatives}
@@ -118,0 +138,6 @@
+                if any(e["Strategy"] == "TDD" and e["Result"] == "SUCCEEDED"
+                       and re.search(r"\bRED\b", e["Obligation or Check"])
+                       and re.search(r"\bexit(?:\s+status)?\s*[=:]?\s*1\b", e["Evidence Reference"])
+                       for e in evidence):
+                    raise ValueError("TDD RED result conflicts with recorded exit status; "
+                                     "expected failing test must be recorded as FAILED")
@@ -122 +147,11 @@
-    return {"verification_selection": selection, "verification_evidence": evidence}
+    coverage = table(text, "Verification Coverage") if "## Verification Coverage" in text else []
+    for mapping in coverage:
+        if mapping["Evidence Check"] not in {e["Obligation or Check"] for e in evidence}:
+            raise ValueError("Verification Coverage references missing evidence")
+    if len({tuple(row.values()) for row in coverage}) != len(coverage):
+        raise ValueError("duplicate Verification Coverage mapping")
+    alternatives = table(text, "Verification Alternative Evidence") if "## Verification Alternative Evidence" in text else []
+    for alternative in alternatives:
+        strategy_list(alternative["Strategies"])
+    return {"verification_selection": selection, "verification_evidence": evidence,
+            "verification_coverage": coverage, "verification_alternative_evidence": alternatives}
```

```diff
--- /dev/null
+++ b/docs/maintainers/cli-artifact-compatibility.md
@@ -0,0 +1,106 @@
+# CLI artifact compatibility
+
+The Markdown protocol remains authoritative. The CLI validates recorded structure;
+independent Review evaluates the truth of execution evidence, applicability of
+alternatives and substantive coverage. These optional mapping tables are projections
+of existing approved obligations, not new approval gates or permission to weaken
+Solution/Slice policy. Their absence does not authorize heuristic matching.
+
+## Ordered identifiers and verification-only attempts
+
+`Feature IDs in order` and `Slice IDs in order` are the protocol field names. The
+CLI retains the original metadata and projects `Feature IDs` and `Slice IDs` for
+existing consumers. Legacy keys are accepted; conflicting values are rejected.
+Order is preserved.
+
+An Implement placement section can explicitly state `No product path is added,
+moved or modified.`, `No application source, test or configuration change.`, or
+`No application files changed.`. Any listed Changed Files must be framework or
+evidence bookkeeping under `.forgeflow/` or `docs/`. A malformed table, traversal
+path or contradictory product change is rejected. This validates the declaration;
+Review must compare it with the actual changed files and approved placement.
+
+## TDD result semantics
+
+In Verification Evidence, Result describes the check execution: a genuine RED test
+is `FAILED`, followed by successful GREEN evidence. Capturing RED correctly does
+not make the test itself successful. Retain command, pre-change state, actual
+failure and output. Environment errors do not establish genuine RED.
+
+Existing records that mark RED as `SUCCEEDED` while recording `exit 1` receive a
+specific conflict diagnostic. The CLI never edits them or converts results based
+on prose. Preserve historical records; corrections or revalidation follow the
+authorized artifact lifecycle and receive independent Review.
+
+## Explicit conditional alternatives
+
+A Slice Plan may project an already approved conditional alternative:
+
+```markdown
+## Verification Alternatives
+
+| Slice ID | Obligation | Strategies | Condition |
+| --- | --- | --- | --- |
+| S-01 | VR-02 | TDD; CHARACTERIZATION_TEST | ED-10: unchanged predecessor; all approved eligibility conditions hold |
+```
+
+Obligation must exactly match one Verification Plan row for that Slice. Each group
+has at least two declared strategies, belongs to that row and cannot overlap
+another group. All strategies outside the group remain mandatory. Exactly one
+group member is selected.
+
+Implement records the same group and condition plus its actual evidence:
+
+```markdown
+## Verification Alternative Evidence
+
+| Obligation | Strategies | Condition | Evidence Reference |
+| --- | --- | --- | --- |
+| VR-02 | TDD; CHARACTERIZATION_TEST | ED-10: unchanged predecessor; all approved eligibility conditions hold | docs/revalidation.md: lineage, source hashes and before/after execution output |
+```
+
+Condition and strategy text must match the approved mapping. A word such as
+`alternative` in rationale is insufficient. A table is a recorded claim; Review
+must inspect the referenced provenance and determine whether the condition holds.
+No historical PASS automatically satisfies current checks.
+
+## Check-to-evidence mapping
+
+When Implement names its executed checks differently, record the relationship:
+
+```markdown
+## Verification Coverage
+
+| Required Check | Evidence Check |
+| --- | --- |
+| Validate archive rollback and reload | Archive abort integration test |
+| Validate archive rollback and reload | Browser reload journey |
+```
+
+Required Check exactly matches one current Slice Verification Plan check, split
+on `; `. Evidence Check exactly matches an Implement Verification Evidence label.
+Every mapped label must exist and its latest result must succeed, or carry an
+approved explicit applicability condition for NOT_APPLICABLE. Its strategy must
+belong to the obligation. Multiple rows can map a grouped obligation to several
+executions; every mapped execution is checked. Extra undeclared checks and dangling
+references are rejected. Without a mapping, the existing exact-label path remains.
+
+The CLI does not infer coverage from shared words or a PASS Review. Independent
+Review must establish that the mapped executions actually cover each required
+property. Missing mappings remain blocked with a specific diagnostic.
+
+## Private real-project regression
+
+Run from this source checkout with the editable environment active:
+
+```bash
+PYTHONPATH=src FORGEFLOW_REGRESSION_PROJECT=/absolute/path/to/project \
+  python -B -m unittest tests.integration.test_cli_artifact_compatibility -v
+```
+
+The opt-in case targets the maintainer's completed two-Feature task-manager snapshot.
+It reads the original project, compares source/artifact hashes before and after, and
+expects three RED-result conflicts plus three unmapped conditional alternatives.
+It never executes the application, updates original records or claims COMPLETE.
+Default CI skips this private-project case and runs the portable positive/negative
+fixtures. No private project files or absolute paths are bundled into the tests.
```

```diff
--- /dev/null
+++ b/tests/integration/test_cli_artifact_compatibility.py
@@ -0,0 +1,160 @@
+"""Protocol compatibility and fail-closed verification mapping regressions."""
+import hashlib
+import os
+import unittest
+from pathlib import Path
+
+from forgeflow.engine.artifact_parser import ArtifactParser
+from forgeflow.engine.verification import parse_verification
+from tests.integration import test_current_framework as fixtures
+
+markdown_table = fixtures.markdown_table
+
+
+class CompatibilityTests(unittest.TestCase):
+    setUp = fixtures.CurrentFrameworkTests.setUp
+    write = fixtures.CurrentFrameworkTests.write
+    graph = fixtures.CurrentFrameworkTests.graph
+    plan = fixtures.CurrentFrameworkTests.plan
+    req = fixtures.CurrentFrameworkTests.req
+    delivery = fixtures.CurrentFrameworkTests.delivery
+    implement = fixtures.CurrentFrameworkTests.implement
+    def test_ordered_protocol_keys_preserve_order_and_reject_conflicts(self):
+        self.delivery(("S-02", "S-01"))
+        for filename, old, new in (("planning.md", "Feature IDs", "Feature IDs in order"),
+                                  ("slice-plan-feature-01.md", "Slice IDs", "Slice IDs in order")):
+            path = self.root / filename
+            path.write_text(path.read_text().replace(f"| {old} |", f"| {new} |"))
+        state, resolution = self.graph()
+        self.assertEqual(state["errors"], [])
+        self.assertEqual(resolution["target_scope"], "Slice: F-01/S-02")
+        path = self.root / "planning.md"
+        path.write_text(path.read_text().replace("| Feature IDs in order | F-01 |",
+                                                "| Feature IDs in order | F-01 |\n| Feature IDs | F-02 |"))
+        state, resolution = self.graph()
+        self.assertEqual(len(state["errors"]), 1)
+        self.assertIn("conflicting metadata aliases", state["errors"][0])
+        self.assertEqual(resolution["pipeline_status"], "HALTED")
+
+    def test_missing_ordered_key_has_no_keyerror_or_cascade(self):
+        self.delivery()
+        path = self.root / "slice-plan-feature-01.md"
+        path.write_text(path.read_text().replace("| Slice IDs | S-01 |\n", ""))
+        self.assertEqual(self.graph()[0]["errors"],
+                         ["slice-plan-feature-01.md: missing metadata: Slice IDs"])
+
+    def test_verification_only_placement_and_contradictory_changes(self):
+        self.delivery()
+        self.implement()
+        path = self.root / "implement-feature-01-slice-01.md"
+        path.write_text(path.read_text() + "\n## Changed Files\n\n- .forgeflow/docs/check.md: evidence\n"
+                        "\n## File Placement Conformance\n\nNo application files changed.\n")
+        self.assertEqual(self.graph()[0]["errors"], [])
+        path.write_text(path.read_text().replace(".forgeflow/docs/check.md", "src/app.ts"))
+        self.assertIn("invalid File Placement Conformance table header", self.graph()[0]["errors"][0])
+
+    def test_red_result_conflict_is_not_accepted_as_execution_evidence(self):
+        self.delivery(strategy="TDD")
+        self.implement(strategy="TDD")
+        path = self.root / "implement-feature-01-slice-01.md"
+        text = path.read_text().replace("| acceptance |", "| Genuine RED |")
+        text = text.replace("embedded output: exit=0; 1 test passed", "red.log: exit 1; missing approved behavior")
+        path.write_text(text)
+        self.assertIn("TDD RED result conflicts", self.graph()[0]["errors"][0])
+        # A real FAILED RED followed by GREEN is structurally valid; arbitrary
+        # nonzero exits are not silently converted or historical files rewritten.
+        text = text.replace("| SUCCEEDED | red.log", "| FAILED | red.log")
+        green = "| TDD | acceptance | TOOL_EXECUTION | python -m unittest | current | SUCCEEDED | green.log: exit 0 |\n"
+        text = text.replace("\n\n## Open Issues", "\n" + green + "\n## Open Issues")
+        self.assertEqual(parse_verification(text, {"Status": "READY_FOR_REVIEW", "Verification Strategies": "TDD"},
+                                            "Implement Record")["verification_evidence"][0]["Result"], "FAILED")
+
+    def test_prose_keyword_cannot_waive_mandatory_strategy(self):
+        self.delivery(strategy="TDD")
+        path = self.root / "slice-plan-feature-01.md"
+        path.write_text(path.read_text().replace("Required by approved scope", "Convenient alternative"))
+        self.implement()
+        self.assertIn("omits mandatory Slice strategy", " ".join(self.graph()[0]["errors"]))
+
+    def test_explicit_conditional_alternative_requires_matching_evidence(self):
+        self.delivery(strategy="TDD; CHARACTERIZATION_TEST")
+        plan = self.root / "slice-plan-feature-01.md"
+        plan.write_text(plan.read_text() + markdown_table("Verification Alternatives",
+            ("Slice ID", "Obligation", "Strategies", "Condition"),
+            [("S-01", "approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10: unchanged source")]))
+        self.implement(strategy="CHARACTERIZATION_TEST")
+        self.assertIn("lacks matching condition evidence", " ".join(self.graph()[0]["errors"]))
+        record = self.root / "implement-feature-01-slice-01.md"
+        record.write_text(record.read_text() + markdown_table("Verification Alternative Evidence",
+            ("Obligation", "Strategies", "Condition", "Evidence Reference"),
+            [("approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10: unchanged source", "before/after hashes and logs")]))
+        self.assertEqual(self.graph()[0]["errors"], [])
+        record.write_text(record.read_text().replace("ED-10: unchanged source", "Different condition"))
+        self.assertIn("lacks matching condition evidence", " ".join(self.graph()[0]["errors"]))
+
+    def test_coverage_maps_labels_without_fuzzy_matching_or_waiving_failures(self):
+        self.delivery()
+        self.implement()
+        record = self.root / "implement-feature-01-slice-01.md"
+        text = record.read_text().replace("| acceptance |", "| executed regression |")
+        record.write_text(text)
+        self.assertIn("no explicit evidence mapping", " ".join(self.graph()[0]["errors"]))
+        mapping = markdown_table("Verification Coverage", ("Required Check", "Evidence Check"),
+                                 [("acceptance", "executed regression")])
+        record.write_text(text + mapping)
+        self.assertEqual(self.graph()[0]["errors"], [])
+        record.write_text((text + mapping).replace("| SUCCEEDED |", "| NOT_RUN |"))
+        self.assertIn("missing or pending required check", " ".join(self.graph()[0]["errors"]))
+        record.write_text(text + mapping.replace("| acceptance |", "| undeclared |"))
+        self.assertIn("undeclared required check", " ".join(self.graph()[0]["errors"]))
+        record.write_text(text + mapping.replace("| executed regression |", "| missing output |"))
+        self.assertIn("references missing evidence", " ".join(self.graph()[0]["errors"]))
+
+    def test_invalid_alternative_groups_do_not_authorize_waivers(self):
+        self.delivery(strategy="TDD; CHARACTERIZATION_TEST")
+        plan = self.root / "slice-plan-feature-01.md"
+        base = plan.read_text()
+        headers = ("Slice ID", "Obligation", "Strategies", "Condition")
+        for choices in ("TDD", "TDD; BEHAVIORAL_TEST"):
+            with self.subTest(choices=choices):
+                plan.write_text(base + markdown_table("Verification Alternatives", headers,
+                    [("S-01", "approved behavior", choices, "ED-10")]))
+                self.assertIn("must reference one declared obligation", " ".join(self.graph()[0]["errors"]))
+        row = ("S-01", "approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10")
+        plan.write_text(base + markdown_table("Verification Alternatives", headers, [row, row]))
+        self.assertIn("overlapping Verification Alternatives", " ".join(self.graph()[0]["errors"]))
+
+    def test_all_mapped_executions_must_pass(self):
+        self.delivery()
+        self.implement()
+        path = self.root / "implement-feature-01-slice-01.md"
+        pending = "| BEHAVIORAL_TEST | second execution | TOOL_EXECUTION | pytest | current | NOT_RUN | pending |\n"
+        text = path.read_text().replace("\n\n## Open Issues", "\n" + pending + "\n## Open Issues")
+        text += markdown_table("Verification Coverage", ("Required Check", "Evidence Check"),
+                               [("acceptance", "acceptance"), ("acceptance", "second execution")])
+        path.write_text(text)
+        self.assertIn("missing or pending required check", " ".join(self.graph()[0]["errors"]))
+
+
+class ReadOnlyRealProjectRegression(unittest.TestCase):
+    @unittest.skipUnless(os.environ.get("FORGEFLOW_REGRESSION_PROJECT"), "opt-in private regression project")
+    def test_inspects_original_project_without_rewriting_evidence(self):
+        project = Path(os.environ["FORGEFLOW_REGRESSION_PROJECT"])
+        root = project / ".forgeflow/artifacts"
+        def snapshot():
+            paths = [p for p in (project / ".forgeflow").rglob("*") if ".git" not in p.parts]
+            for folder in ("src", "e2e", "public"):
+                paths += list((project / folder).rglob("*"))
+            paths += [project / filename for filename in ("package.json", "package-lock.json", "angular.json", "playwright.config.ts")]
+            return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
+        before = snapshot()
+        state = ArtifactParser.detect_artifact_state(root)
+        self.assertEqual(before, snapshot())
+        self.assertIn("planning.md", state["artifacts"])
+        self.assertIn("slice-plan-feature-01.md", state["artifacts"])
+        self.assertIn("slice-plan-feature-02.md", state["artifacts"])
+        self.assertEqual(len(state["errors"]), 6)
+        self.assertEqual(sum("TDD RED result conflicts" in e for e in state["errors"]), 3)
+        self.assertEqual(sum("conditional alternatives require explicit verification mapping" in e
+                             for e in state["errors"]), 3)
+        self.assertFalse(any("KeyError" in e or "invalid File Placement" in e for e in state["errors"]))
```
