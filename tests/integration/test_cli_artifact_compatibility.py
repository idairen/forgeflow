"""Protocol compatibility and fail-closed verification mapping regressions."""
import hashlib
import os
import unittest
from pathlib import Path

from forgeflow.engine.artifact_parser import ArtifactParser
from forgeflow.engine.verification import parse_verification
from tests.integration import test_current_framework as fixtures

markdown_table = fixtures.markdown_table


class CompatibilityTests(unittest.TestCase):
    setUp = fixtures.CurrentFrameworkTests.setUp
    write = fixtures.CurrentFrameworkTests.write
    graph = fixtures.CurrentFrameworkTests.graph
    plan = fixtures.CurrentFrameworkTests.plan
    req = fixtures.CurrentFrameworkTests.req
    delivery = fixtures.CurrentFrameworkTests.delivery
    implement = fixtures.CurrentFrameworkTests.implement
    def test_ordered_protocol_keys_preserve_order_and_reject_conflicts(self):
        self.delivery(("S-02", "S-01"))
        for filename, old, new in (("planning.md", "Feature IDs", "Feature IDs in order"),
                                  ("slice-plan-feature-01.md", "Slice IDs", "Slice IDs in order")):
            path = self.root / filename
            path.write_text(path.read_text().replace(f"| {old} |", f"| {new} |"))
        state, resolution = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(resolution["target_scope"], "Slice: F-01/S-02")
        path = self.root / "planning.md"
        path.write_text(path.read_text().replace("| Feature IDs in order | F-01 |",
                                                "| Feature IDs in order | F-01 |\n| Feature IDs | F-02 |"))
        state, resolution = self.graph()
        self.assertEqual(len(state["errors"]), 1)
        self.assertIn("conflicting metadata aliases", state["errors"][0])
        self.assertEqual(resolution["pipeline_status"], "HALTED")

    def test_missing_ordered_key_has_no_keyerror_or_cascade(self):
        self.delivery()
        path = self.root / "slice-plan-feature-01.md"
        path.write_text(path.read_text().replace("| Slice IDs | S-01 |\n", ""))
        self.assertEqual(self.graph()[0]["errors"],
                         ["slice-plan-feature-01.md: missing metadata: Slice IDs"])

    def test_verification_only_placement_and_contradictory_changes(self):
        self.delivery()
        self.implement()
        path = self.root / "implement-feature-01-slice-01.md"
        path.write_text(path.read_text() + "\n## Changed Files\n\n- .forgeflow/docs/check.md: evidence\n"
                        "\n## File Placement Conformance\n\nNo application files changed.\n")
        self.assertEqual(self.graph()[0]["errors"], [])
        path.write_text(path.read_text().replace(".forgeflow/docs/check.md", "src/app.ts"))
        self.assertIn("invalid File Placement Conformance table header", self.graph()[0]["errors"][0])

    def test_red_result_conflict_is_not_accepted_as_execution_evidence(self):
        self.delivery(strategy="TDD")
        self.implement(strategy="TDD")
        path = self.root / "implement-feature-01-slice-01.md"
        text = path.read_text().replace("| acceptance |", "| Genuine RED |")
        text = text.replace("embedded output: exit=0; 1 test passed", "red.log: exit 1; missing approved behavior")
        path.write_text(text)
        self.assertIn("TDD RED result conflicts", self.graph()[0]["errors"][0])
        # A real FAILED RED followed by GREEN is structurally valid; arbitrary
        # nonzero exits are not silently converted or historical files rewritten.
        text = text.replace("| SUCCEEDED | red.log", "| FAILED | red.log")
        green = "| TDD | acceptance | TOOL_EXECUTION | python -m unittest | current | SUCCEEDED | green.log: exit 0 |\n"
        text = text.replace("\n\n## Open Issues", "\n" + green + "\n## Open Issues")
        self.assertEqual(parse_verification(text, {"Status": "READY_FOR_REVIEW", "Verification Strategies": "TDD"},
                                            "Implement Record")["verification_evidence"][0]["Result"], "FAILED")

    def test_prose_keyword_cannot_waive_mandatory_strategy(self):
        self.delivery(strategy="TDD")
        path = self.root / "slice-plan-feature-01.md"
        path.write_text(path.read_text().replace("Required by approved scope", "Convenient alternative"))
        self.implement()
        self.assertIn("omits mandatory Slice strategy", " ".join(self.graph()[0]["errors"]))

    def test_explicit_conditional_alternative_requires_matching_evidence(self):
        self.delivery(strategy="TDD; CHARACTERIZATION_TEST")
        plan = self.root / "slice-plan-feature-01.md"
        plan.write_text(plan.read_text() + markdown_table("Verification Alternatives",
            ("Slice ID", "Obligation", "Strategies", "Condition"),
            [("S-01", "approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10: unchanged source")]))
        self.implement(strategy="CHARACTERIZATION_TEST")
        self.assertIn("lacks matching condition evidence", " ".join(self.graph()[0]["errors"]))
        record = self.root / "implement-feature-01-slice-01.md"
        record.write_text(record.read_text() + markdown_table("Verification Alternative Evidence",
            ("Obligation", "Strategies", "Condition", "Evidence Reference"),
            [("approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10: unchanged source", "before/after hashes and logs")]))
        self.assertEqual(self.graph()[0]["errors"], [])
        record.write_text(record.read_text().replace("ED-10: unchanged source", "Different condition"))
        self.assertIn("lacks matching condition evidence", " ".join(self.graph()[0]["errors"]))

    def test_coverage_maps_labels_without_fuzzy_matching_or_waiving_failures(self):
        self.delivery()
        self.implement()
        record = self.root / "implement-feature-01-slice-01.md"
        text = record.read_text().replace("| acceptance |", "| executed regression |")
        record.write_text(text)
        self.assertIn("no explicit evidence mapping", " ".join(self.graph()[0]["errors"]))
        mapping = markdown_table("Verification Coverage", ("Required Check", "Evidence Check"),
                                 [("acceptance", "executed regression")])
        record.write_text(text + mapping)
        self.assertEqual(self.graph()[0]["errors"], [])
        record.write_text((text + mapping).replace("| SUCCEEDED |", "| NOT_RUN |"))
        self.assertIn("missing or pending required check", " ".join(self.graph()[0]["errors"]))
        record.write_text(text + mapping.replace("| acceptance |", "| undeclared |"))
        self.assertIn("undeclared required check", " ".join(self.graph()[0]["errors"]))
        record.write_text(text + mapping.replace("| executed regression |", "| missing output |"))
        self.assertIn("references missing evidence", " ".join(self.graph()[0]["errors"]))

    def test_invalid_alternative_groups_do_not_authorize_waivers(self):
        self.delivery(strategy="TDD; CHARACTERIZATION_TEST")
        plan = self.root / "slice-plan-feature-01.md"
        base = plan.read_text()
        headers = ("Slice ID", "Obligation", "Strategies", "Condition")
        for choices in ("TDD", "TDD; BEHAVIORAL_TEST"):
            with self.subTest(choices=choices):
                plan.write_text(base + markdown_table("Verification Alternatives", headers,
                    [("S-01", "approved behavior", choices, "ED-10")]))
                self.assertIn("must reference one declared obligation", " ".join(self.graph()[0]["errors"]))
        row = ("S-01", "approved behavior", "TDD; CHARACTERIZATION_TEST", "ED-10")
        plan.write_text(base + markdown_table("Verification Alternatives", headers, [row, row]))
        self.assertIn("overlapping Verification Alternatives", " ".join(self.graph()[0]["errors"]))

    def test_all_mapped_executions_must_pass(self):
        self.delivery()
        self.implement()
        path = self.root / "implement-feature-01-slice-01.md"
        pending = "| BEHAVIORAL_TEST | second execution | TOOL_EXECUTION | pytest | current | NOT_RUN | pending |\n"
        text = path.read_text().replace("\n\n## Open Issues", "\n" + pending + "\n## Open Issues")
        text += markdown_table("Verification Coverage", ("Required Check", "Evidence Check"),
                               [("acceptance", "acceptance"), ("acceptance", "second execution")])
        path.write_text(text)
        self.assertIn("missing or pending required check", " ".join(self.graph()[0]["errors"]))


class ReadOnlyRealProjectRegression(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("FORGEFLOW_REGRESSION_PROJECT"), "opt-in private regression project")
    def test_inspects_original_project_without_rewriting_evidence(self):
        project = Path(os.environ["FORGEFLOW_REGRESSION_PROJECT"])
        root = project / ".forgeflow/artifacts"
        def snapshot():
            paths = [p for p in (project / ".forgeflow").rglob("*") if ".git" not in p.parts]
            for folder in ("src", "e2e", "public"):
                paths += list((project / folder).rglob("*"))
            paths += [project / filename for filename in ("package.json", "package-lock.json", "angular.json", "playwright.config.ts")]
            return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
        before = snapshot()
        state = ArtifactParser.detect_artifact_state(root)
        self.assertEqual(before, snapshot())
        self.assertIn("planning.md", state["artifacts"])
        self.assertIn("slice-plan-feature-01.md", state["artifacts"])
        self.assertIn("slice-plan-feature-02.md", state["artifacts"])
        self.assertEqual(len(state["errors"]), 6)
        self.assertEqual(sum("TDD RED result conflicts" in e for e in state["errors"]), 3)
        self.assertEqual(sum("conditional alternatives require explicit verification mapping" in e
                             for e in state["errors"]), 3)
        self.assertFalse(any("KeyError" in e or "invalid File Placement" in e for e in state["errors"]))
