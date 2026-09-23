import contextlib
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from forgeflow.cli.main import cmd_knowledge, main_cli


class CliKnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.view = {
            "schema_version": 1,
            "authority": "derived_non_authoritative",
            "status": "available",
            "planning": None,
            "solution": None,
            "features": [],
            "impact": {
                "schema_version": 1,
                "authority": "derived_non_authoritative",
                "status": "unavailable",
                "reason": "no_current_solution",
            },
            "timeline": {"planning": [], "solution": []},
            "history": {
                "artifact_history": [],
                "supplemental_reports": [],
                "report_history": [],
                "rotated_evidence_roots": [],
            },
            "warnings": [],
        }

    def test_json_output_hides_history_by_default(self):
        runner = MagicMock()
        runner.get_state.return_value = {"project_knowledge": self.view}
        args = SimpleNamespace(
            feature=None,
            slice_scope=None,
            history=False,
            format="json",
            impact=None,
            component=None,
        )

        with patch("forgeflow.cli.main._make_runner", return_value=runner), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            result = cmd_knowledge(args)

        self.assertEqual(result, 0)
        parsed = json.loads(output.getvalue())
        self.assertNotIn("history", parsed)

    def test_markdown_output_and_cli_registration(self):
        runner = MagicMock()
        runner.get_state.return_value = {"project_knowledge": self.view}
        args = SimpleNamespace(
            feature=None,
            slice_scope=None,
            history=True,
            format="markdown",
            impact=None,
            component=None,
        )
        with patch("forgeflow.cli.main._make_runner", return_value=runner), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            result = cmd_knowledge(args)

        self.assertEqual(result, 0)
        self.assertIn("# ForgeFlow Project Knowledge", output.getvalue())

        with contextlib.redirect_stdout(io.StringIO()) as help_output:
            with self.assertRaisesRegex(SystemExit, "0"):
                main_cli(["knowledge", "--help"])
        self.assertIn("--feature", help_output.getvalue())
        self.assertIn("--slice", help_output.getvalue())
        self.assertIn("--impact", help_output.getvalue())
        self.assertIn("--component", help_output.getvalue())

    def test_json_output_selects_feature_impact(self):
        runner = MagicMock()
        runner.get_state.return_value = {"project_knowledge": self.view}
        self.view["impact"] = {
            "schema_version": 1,
            "authority": "derived_non_authoritative",
            "status": "available",
            "feature_order": ["F-01", "F-02"],
            "dependencies": {"F-01": [], "F-02": ["F-01"]},
            "reverse_dependencies": {"F-01": ["F-02"], "F-02": []},
            "feature_components": {"F-01": ["SC-01"], "F-02": ["SC-01"]},
            "component_features": {"SC-01": ["F-01", "F-02"]},
            "feature_decisions": {"F-01": ["ED-01"], "F-02": []},
            "current_change_impact": {"F-01": "DIRECT", "F-02": "INDIRECT"},
        }
        args = SimpleNamespace(
            feature=None,
            slice_scope=None,
            history=False,
            impact="F-01",
            component=None,
            format="json",
        )

        with patch("forgeflow.cli.main._make_runner", return_value=runner), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            result = cmd_knowledge(args)

        self.assertEqual(result, 0)
        parsed = json.loads(output.getvalue())
        self.assertEqual(
            parsed["impact"]["query"]["direct_dependents"],
            ["F-02"],
        )


if __name__ == "__main__":
    unittest.main()
