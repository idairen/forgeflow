import tempfile
import unittest
from pathlib import Path

from forgeflow.engine.artifact_parser import ArtifactParser


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
            "| 2 | BLOCKING | TDD | Slice: F-01/S-01 | Test failure | tests/test_api.py | TDD contract |\n"
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


if __name__ == "__main__":
    unittest.main()
