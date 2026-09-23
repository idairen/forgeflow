import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forgeflow.engine.project_knowledge import ProjectKnowledgeBuilder


def knowledge_view():
    return {
        "schema_version": 1,
        "authority": "derived_non_authoritative",
        "status": "available",
        "planning": {
            "filename": "planning.md",
            "version": "2.0",
            "status": "READY",
        },
        "solution": None,
        "impact": {
            "schema_version": 1,
            "authority": "derived_non_authoritative",
            "status": "available",
            "feature_order": ["F-02", "F-01"],
            "dependencies": {"F-02": ["F-01"], "F-01": []},
            "reverse_dependencies": {"F-02": [], "F-01": ["F-02"]},
            "feature_components": {"F-02": ["SC-01"], "F-01": ["SC-01"]},
            "component_features": {"SC-01": ["F-02", "F-01"]},
            "feature_decisions": {"F-02": ["ED-01"], "F-01": []},
            "current_change_impact": {
                "F-02": "DIRECT",
                "F-01": "INDIRECT",
            },
        },
        "features": [
            {
                "feature_id": "F-02",
                "contract_version": "2.0",
                "requirement": None,
                "solution_requirement_version": None,
                "engineering_version": None,
                "slice_plan": None,
                "slices": [
                    {"slice_id": "S-02", "implement": None, "reviews": []},
                    {"slice_id": "S-01", "implement": None, "reviews": []},
                ],
            },
            {
                "feature_id": "F-01",
                "contract_version": "1.0",
                "requirement": None,
                "solution_requirement_version": None,
                "engineering_version": None,
                "slice_plan": None,
                "slices": [],
            },
        ],
        "timeline": {
            "planning": [
                {
                    "version": "1.0",
                    "source": "history",
                    "path": "history/planning-v1.0.md",
                },
                {"version": "2.0", "source": "current", "path": "planning.md"},
            ],
            "solution": [],
        },
        "history": {
            "artifact_history": ["planning-v1.0.md"],
            "supplemental_reports": [],
            "report_history": [],
            "rotated_evidence_roots": [],
        },
        "warnings": [],
    }


class ProjectKnowledgeTests(unittest.TestCase):
    def test_default_view_does_not_scan_history(self):
        state = {"status": "empty", "root": "/not-a-project", "artifacts": {}}
        with patch.object(ProjectKnowledgeBuilder, "_knowledge_history", side_effect=AssertionError("history scanned")):
            view = ProjectKnowledgeBuilder.build(state)
        self.assertEqual(view["history"]["artifact_history"], [])

    def test_selects_feature_and_slice_without_reordering(self):
        selected = ProjectKnowledgeBuilder.select(
            knowledge_view(),
            slice_scope="F-02/S-01",
        )

        self.assertEqual(
            [feature["feature_id"] for feature in selected["features"]],
            ["F-02"],
        )
        self.assertEqual(selected["features"][0]["slices"][0]["slice_id"], "S-01")
        self.assertNotIn("history", selected)
        self.assertEqual(
            selected["timeline"]["planning"],
            [{"version": "2.0", "source": "current", "path": "planning.md"}],
        )

    def test_rejects_invalid_or_inactive_filters(self):
        with self.assertRaisesRegex(ValueError, "F-XX/S-XX"):
            ProjectKnowledgeBuilder.select(knowledge_view(), slice_scope="S-01")
        with self.assertRaisesRegex(ValueError, "does not match"):
            ProjectKnowledgeBuilder.select(
                knowledge_view(),
                feature_id="F-01",
                slice_scope="F-02/S-01",
            )
        with self.assertRaisesRegex(ValueError, "Feature is not active"):
            ProjectKnowledgeBuilder.select(knowledge_view(), feature_id="F-99")

    def test_markdown_is_readable_and_keeps_history_when_selected(self):
        selected = ProjectKnowledgeBuilder.select(
            knowledge_view(),
            feature_id="F-02",
            include_history=True,
        )

        rendered = ProjectKnowledgeBuilder.render_markdown(selected)

        self.assertIn("# ForgeFlow Project Knowledge", rendered)
        self.assertIn("## F-02", rendered)
        self.assertIn("### F-02/S-02", rendered)
        self.assertIn("## Contract Timeline", rendered)
        self.assertIn("## History Index", rendered)
        self.assertIn("`planning-v1.0.md`", rendered)

    def test_selects_and_renders_feature_impact(self):
        selected = ProjectKnowledgeBuilder.select(
            knowledge_view(),
            impact_feature="F-01",
        )

        self.assertEqual(
            selected["impact"]["query"]["direct_dependents"],
            ["F-02"],
        )
        rendered = ProjectKnowledgeBuilder.render_markdown(selected)
        self.assertIn("## Project Impact View", rendered)
        self.assertIn("- Feature: `F-01`", rendered)
        self.assertIn("- Direct Dependents: `F-02`", rendered)

    def test_historical_contract_timeline_reads_change_sets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "artifacts"
            history = root / "history"
            history.mkdir(parents=True)
            (history / "planning-v1.0.md").write_text(
                "# Planning\n\n## Metadata\n\n"
                "| Field | Value |\n| --- | --- |\n"
                "| Artifact Type | Planning |\n"
                "| Version | 1.0 |\n"
                "| Status | READY |\n"
                "| Owner Workflow | Plan |\n"
                "| Feature IDs | F-01 |\n"
                "| Feature Contract Versions | F-01 = 1.0 |\n"
                "| Change Set | BASELINE |\n",
                encoding="utf-8",
            )
            state = {
                "status": "empty",
                "root": str(root),
                "artifacts": {},
                "errors": [],
            }

            view = ProjectKnowledgeBuilder.build(state, include_history=True)

        self.assertEqual(
            view["timeline"]["planning"][0]["summary"],
            "BASELINE",
        )
        self.assertEqual(view["warnings"], [])

    def test_invalid_history_warns_without_invalidating_current_view(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "artifacts"
            history = root / "history"
            history.mkdir(parents=True)
            (history / "planning-v1.0.md").write_text(
                "not an artifact",
                encoding="utf-8",
            )
            state = {
                "status": "empty",
                "root": str(root),
                "artifacts": {},
                "errors": [],
            }

            view = ProjectKnowledgeBuilder.build(state, include_history=True)

        self.assertEqual(view["status"], "empty")
        self.assertEqual(
            view["warnings"],
            ["invalid history metadata: planning-v1.0.md"],
        )


if __name__ == "__main__":
    unittest.main()
