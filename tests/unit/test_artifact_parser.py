import tempfile
import unittest
from pathlib import Path

from forgeflow.engine.artifact_parser import ArtifactParser
from forgeflow.engine.project_knowledge import ProjectKnowledgeBuilder


def artifact_document(title, rows, body=""):
    metadata = "\n".join(f"| {field} | {value} |" for field, value in rows)
    return (
        f"# {title}\n\n## Metadata\n\n"
        f"| Field | Value |\n| --- | --- |\n{metadata}\n{body}"
    )


class ArtifactParserTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "artifacts"

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, name, content):
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_text(content, encoding="utf-8")

    def test_missing_and_empty_roots_are_empty(self):
        missing = ArtifactParser.detect_artifact_state(self.root)
        self.root.mkdir()
        empty = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(missing["status"], "empty")
        self.assertEqual(empty["status"], "empty")

    def test_parses_valid_planning_metadata(self):
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "Added F-01"),
                ],
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "active")
        self.assertEqual(state["artifacts"]["planning.md"]["version"], "1.0")

    def test_validates_protocol_211_planning_structure(self):
        body = (
            "\n\n## Project Intent\n\nDeliver task management."
            "\n\n## Project Goals\n\n- Manage tasks."
            "\n\n## Success Measures\n\n- Tasks can be managed."
            "\n\n## Project Constraints\n\nNONE — no project constraints supplied."
            "\n\n## Assumptions\n\n- Users are authenticated."
            "\n\n## Exclusions\n\n- Billing."
            "\n\n## Features\n\n"
            "| Feature ID | Title | Outcome | Dependencies |\n"
            "| --- | --- | --- | --- |\n"
            "| F-01 | Tasks | Users manage tasks. | NONE |"
            "\n\n## Change Set\n\n"
            "| Feature ID | Change | Previous Contract Version | "
            "Current Contract Version | Rationale |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| F-01 | BASELINE | NONE | 1.0 | Initial scope. |"
            "\n\n## Intent Evolution\n\nInitial approved scope.\n"
        )
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "BASELINE"),
                    ("Artifact Protocol Version", "2.11"),
                ],
                body,
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "active")

    def test_rejects_incomplete_protocol_211_planning_structure(self):
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "BASELINE"),
                    ("Artifact Protocol Version", "2.11"),
                ],
                "\n\n## Project Intent\n\nOnly one section.\n",
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(
            any(
                "exactly one ## Project Goals" in error
                for error in state["errors"]
            )
        )

    def test_rejects_out_of_order_protocol_211_planning_sections(self):
        sections = list(ArtifactParser._PLANNING_SECTIONS)
        sections[0], sections[1] = sections[1], sections[0]
        body_parts = []
        for section in sections:
            if section == "Features":
                content = (
                    "| Feature ID | Title | Outcome | Dependencies |\n"
                    "| --- | --- | --- | --- |\n"
                    "| F-01 | Tasks | Users manage tasks. | NONE |"
                )
            elif section == "Change Set":
                content = (
                    "| Feature ID | Change | Previous Contract Version | "
                    "Current Contract Version | Rationale |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| F-01 | BASELINE | NONE | 1.0 | Initial scope. |"
                )
            else:
                content = "Content."
            body_parts.append(f"## {section}\n\n{content}")
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "BASELINE"),
                    ("Artifact Protocol Version", "2.11"),
                ],
                "\n\n" + "\n\n".join(body_parts) + "\n",
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(
            any("canonical order" in error for error in state["errors"])
        )

    def test_rejects_nonempty_root_without_valid_planning(self):
        self.write("notes.md", "not canonical")

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertIn("non_empty_artifact_root_without_valid_planning", state["errors"])
        self.assertEqual(state["ignored"], ["notes.md"])

    def test_rejects_filename_metadata_identifier_mismatch(self):
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "Added F-01"),
                ],
            ),
        )
        self.write(
            "requirement-feature-01.md",
            artifact_document(
                "Requirement",
                [
                    ("Artifact Type", "Requirement"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Grill"),
                    ("Feature ID", "F-02"),
                    ("Planning Version", "1.0"),
                ],
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(
            any("Feature ID does not match canonical filename" in error for error in state["errors"])
        )

    def test_validates_review_findings_and_return_precedence(self):
        findings = (
            "\n## Findings\n\n"
            "| # | Severity | Owner Workflow | Affected Scope | Finding | Evidence | Violated Contract |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| 1 | BLOCKING | Solution | Project | Design mismatch | src/api.py | Solution contract |\n"
            "| 2 | BLOCKING | Implement | Slice: F-01/S-01 | Test failure | tests/test_api.py | Implement contract |\n"
        )
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "Added F-01"),
                ],
            ),
        )
        self.write(
            "review-feature-01-slice-01-attempt-01.md",
            artifact_document(
                "Review",
                [
                    ("Artifact Type", "Review Report"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Review"),
                    ("Feature ID", "F-01"),
                    ("Slice ID", "S-01"),
                    ("Attempt", "1"),
                    ("Decision", "FAIL"),
                    ("Solution Version", "1.0"),
                    ("Slice Plan Version", "1.0"),
                    ("Blocking Findings", "2"),
                    ("Non-blocking Findings", "0"),
                    ("Return Workflow", "Solution"),
                    ("Return Scope", "Project"),
                ],
                findings,
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)
        review = state["artifacts"]["review-feature-01-slice-01-attempt-01.md"]

        self.assertEqual(len(review["findings"]), 2)
        self.assertFalse(
            any("Return Workflow does not match" in error for error in state["errors"])
        )

    def test_history_and_noncanonical_files_are_ignored(self):
        self.root.mkdir()
        (self.root / "history").mkdir()
        (self.root / "draft.txt").write_text("draft", encoding="utf-8")

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertEqual(state["ignored"], ["draft.txt", "history/"])

    def test_check_artifact_exists_accepts_only_direct_canonical_files(self):
        self.write("planning.md", "content")
        self.write("notes.md", "content")

        self.assertTrue(ArtifactParser.check_artifact_exists(self.root, "planning.md"))
        self.assertFalse(ArtifactParser.check_artifact_exists(self.root, "notes.md"))
        self.assertFalse(
            ArtifactParser.check_artifact_exists(self.root, "history/planning.md")
        )

    def test_validates_structured_solution_impact_metadata(self):
        self._write_impact_graph(
            "F-01 = F-02; F-02 = NONE",
            "F-01 = SC-01; F-02 = SC-01",
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "active")

    def test_rejects_partial_cyclic_or_unknown_impact_relationships(self):
        self._write_impact_graph(
            "F-01 = F-02; F-02 = F-01",
            "F-01 = SC-99; F-02 = NONE",
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(any("contains a cycle" in error for error in state["errors"]))
        self.assertTrue(
            any("unknown component" in error for error in state["errors"])
        )

    def test_rejects_partial_solution_impact_metadata(self):
        self._write_impact_graph(
            "F-01 = NONE; F-02 = NONE",
            None,
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(
            any("partial Solution impact metadata" in error for error in state["errors"])
        )

    def test_validates_paired_solution_structure_sections(self):
        self._write_single_feature_planning()
        structure = (
            "\n## Implementation Structure\n\n"
            "| Component or Role | Source Root | Module or Package Pattern | Responsibility | Allowed Dependencies | Applies To | Evidence |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| Service | src | inventory.service | use case | domain | F-01 | existing convention |\n"
            "\n## Test Structure\n\n"
            "| Test Level | Test Root | Module or Package Pattern | Production Relationship | Applies To | Evidence |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| Unit | tests | inventory.service | mirrors production | F-01 | existing convention |\n"
        )
        self.write(
            "solution-plan.md",
            artifact_document(
                "Solution",
                [
                    ("Artifact Type", "Solution Plan"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Solution"),
                    ("Based On Requirements", "F-01 = 1.0"),
                    ("Feature Engineering Versions", "F-01 = 1.0"),
                ],
                structure,
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "active")

    def test_rejects_partial_solution_structure_sections(self):
        self._write_single_feature_planning()
        implementation_only = (
            "\n## Implementation Structure\n\n"
            "| Component or Role | Source Root | Module or Package Pattern | Responsibility | Allowed Dependencies | Applies To | Evidence |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
        )
        self.write(
            "solution-plan.md",
            artifact_document(
                "Solution",
                [
                    ("Artifact Type", "Solution Plan"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Solution"),
                    ("Based On Requirements", "F-01 = 1.0"),
                    ("Feature Engineering Versions", "F-01 = 1.0"),
                ],
                implementation_only,
            ),
        )

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertTrue(
            any("must include both" in error for error in state["errors"])
        )

    def test_rejects_malformed_file_placement_table_header(self):
        errors = []

        ArtifactParser._validate_structure_sections(
            "## Planned File Placement\n\n| Wrong | Header |\n| --- | --- |\n",
            "Slice Plan",
            errors,
        )

        self.assertEqual(errors, ["invalid Planned File Placement table header"])

    def test_rejects_empty_solution_summary_when_present(self):
        errors = []

        ArtifactParser._validate_solution_summary(
            "## Solution Summary\n\n## Implementation Structure\n\n"
            "## Test Structure\n",
            {"Artifact Protocol Version": "2.11"},
            "Solution Plan",
            errors,
        )

        self.assertEqual(errors, ["Solution Summary section is empty"])

    def test_forbids_standalone_solution_plan_summary_in_artifact_root(self):
        self._write_single_feature_planning()
        self.write("solution-plan-summary.md", "# Summary\n")

        state = ArtifactParser.detect_artifact_state(self.root)

        self.assertEqual(state["status"], "invalid")
        self.assertIn(
            "forbidden artifact filename: solution-plan-summary.md",
            state["errors"],
        )

    def _write_single_feature_planning(self):
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "1.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01"),
                    ("Feature Contract Versions", "F-01 = 1.0"),
                    ("Change Set", "BASELINE"),
                ],
            ),
        )

    def _write_impact_graph(self, dependencies, component_map):
        self.write(
            "planning.md",
            artifact_document(
                "Planning",
                [
                    ("Artifact Type", "Planning"),
                    ("Version", "2.0"),
                    ("Status", "READY"),
                    ("Owner Workflow", "Plan"),
                    ("Feature IDs", "F-01; F-02"),
                    ("Feature Contract Versions", "F-01 = 1.0; F-02 = 2.0"),
                    ("Change Set", "Added F-02"),
                ],
            ),
        )
        rows = [
            ("Artifact Type", "Solution Plan"),
            ("Version", "2.0"),
            ("Status", "READY"),
            ("Owner Workflow", "Solution"),
            ("Based On Requirements", "F-01 = 1.0; F-02 = 1.0"),
            ("Feature Engineering Versions", "F-01 = 1.0; F-02 = 2.0"),
            ("Shared Component IDs", "SC-01"),
            ("Feature Dependencies", dependencies),
        ]
        if component_map is not None:
            rows.extend(
                [
                    ("Feature Shared Components", component_map),
                    ("Feature Decision References", "F-01 = ED-01; F-02 = ED-01"),
                    ("Cross-Feature Impact", "F-01 = INDIRECT; F-02 = DIRECT"),
                ]
            )
        self.write("solution-plan.md", artifact_document("Solution", rows))

    def test_project_knowledge_view_preserves_declared_order_and_history(self):
        def parsed(filename, artifact_type, version, status, **metadata):
            return {
                "filename": filename,
                "path": str(self.root / filename),
                "artifact_type": artifact_type,
                "owner_workflow": metadata.get("Owner Workflow", "Plan"),
                "version": version,
                "status": status,
                "metadata": metadata,
            }

        artifacts = {
            "planning.md": parsed(
                "planning.md",
                "Planning",
                "2.0",
                "READY",
                **{
                    "Feature IDs": "F-02; F-01",
                    "Feature Contract Versions": "F-02 = 2.0; F-01 = 1.0",
                    "Change Set": "Added F-02",
                },
            ),
            "requirement-feature-02.md": parsed(
                "requirement-feature-02.md",
                "Requirement",
                "1.0",
                "READY",
                **{"Feature ID": "F-02", "Planning Version": "2.0"},
            ),
            "solution-plan.md": parsed(
                "solution-plan.md",
                "Solution Plan",
                "2.0",
                "READY",
                **{
                    "Based On Requirements": "F-02 = 1.0; F-01 = 1.0",
                    "Feature Engineering Versions": "F-02 = 2.0; F-01 = 1.0",
                },
            ),
            "slice-plan-feature-02.md": parsed(
                "slice-plan-feature-02.md",
                "Slice Plan",
                "1.0",
                "READY",
                **{
                    "Feature ID": "F-02",
                    "Based On Solution": "2.0",
                    "Slice IDs": "S-02; S-01",
                },
            ),
            "implement-feature-02-slice-02.md": parsed(
                "implement-feature-02-slice-02.md",
                "Implement Record",
                "1.0",
                "READY_FOR_REVIEW",
                **{
                    "Feature ID": "F-02",
                    "Slice ID": "S-02",
                    "Attempt": "2",
                    "Solution Version": "2.0",
                    "Slice Plan Version": "1.0",
                },
            ),
            "review-feature-02-slice-02-attempt-01.md": parsed(
                "review-feature-02-slice-02-attempt-01.md",
                "Review Report",
                "1.0",
                "READY",
                **{
                    "Feature ID": "F-02",
                    "Slice ID": "S-02",
                    "Attempt": "1",
                    "Decision": "FAIL",
                    "Solution Version": "2.0",
                    "Slice Plan Version": "1.0",
                },
            ),
        }
        state = {
            "status": "active",
            "root": str(self.root),
            "artifacts": artifacts,
            "errors": [],
        }
        artifact_history = self.root / "history"
        artifact_history.mkdir(parents=True)
        (artifact_history / "planning-v1.0.md").write_text(
            "old planning",
            encoding="utf-8",
        )
        reports = self.root.parent / "reports"
        (reports / "security").mkdir(parents=True)
        (reports / "security" / "current.md").write_text("current", encoding="utf-8")
        (reports / "history" / "security").mkdir(parents=True)
        (reports / "history" / "security" / "old.md").write_text(
            "old",
            encoding="utf-8",
        )
        (self.root.parent / "artifacts.20260820010101").mkdir()

        view = ProjectKnowledgeBuilder.build(state, reports, include_history=True)

        self.assertEqual(view["authority"], "derived_non_authoritative")
        self.assertEqual(
            [feature["feature_id"] for feature in view["features"]],
            ["F-02", "F-01"],
        )
        feature = view["features"][0]
        self.assertEqual(feature["engineering_version"], "2.0")
        self.assertEqual(
            [item["slice_id"] for item in feature["slices"]],
            ["S-02", "S-01"],
        )
        self.assertEqual(feature["slices"][0]["implement"]["Attempt"], "2")
        self.assertEqual(
            feature["slices"][0]["reviews"][0]["Decision"],
            "FAIL",
        )
        self.assertEqual(
            view["history"]["artifact_history"],
            ["planning-v1.0.md"],
        )
        self.assertEqual(
            view["history"]["supplemental_reports"],
            ["security/current.md"],
        )
        self.assertEqual(
            view["history"]["report_history"],
            ["security/old.md"],
        )
        self.assertEqual(
            view["history"]["rotated_evidence_roots"],
            ["artifacts.20260820010101"],
        )

    def test_invalid_graph_has_no_active_project_knowledge(self):
        view = ProjectKnowledgeBuilder.build(
            {
                "status": "invalid",
                "root": str(self.root),
                "artifacts": {},
                "errors": ["contradiction"],
            }
        )

        self.assertEqual(view["status"], "unavailable")
        self.assertEqual(view["reason"], "invalid_artifact_graph")
        self.assertNotIn("features", view)


if __name__ == "__main__":
    unittest.main()
