import unittest

from forgeflow.engine.handoff_parser import HandoffParser


def handoff_table(rows):
    body = "\n".join(f"| {field} | {value} |" for field, value in rows)
    return f"Result\n\n### Handoff\n| Field | Value |\n| --- | --- |\n{body}"


class HandoffParserTests(unittest.TestCase):
    def test_parses_canonical_forward_handoff(self):
        parsed = HandoffParser.parse(
            handoff_table(
                [
                    ("Transition", "FORWARD"),
                    ("Next Workflow", "Grill"),
                    ("Source Scope", "Project"),
                    ("Target Scope", "Feature: F-01"),
                    ("Input Artifacts", "planning.md = 1.0"),
                    ("Reason", "Planning is ready"),
                ]
            ),
            expected_source_workflow="plan",
            expected_source_scope="Project",
        )

        self.assertEqual(parsed["transition"], "FORWARD")
        self.assertEqual(parsed["next_workflow"], "grill")
        self.assertEqual(
            parsed["input_artifacts"],
            [{"filename": "planning.md", "version": "1.0"}],
        )

    def test_parses_return_to_prior_owner_and_scope(self):
        parsed = HandoffParser.parse(
            handoff_table(
                [
                    ("Transition", "RETURN"),
                    ("Next Workflow", "Implement"),
                    ("Source Scope", "Slice: F-01/S-01"),
                    ("Target Scope", "Slice: F-01/S-01"),
                    ("Blocker Category", "IMPLEMENTATION_GAP"),
                    (
                        "Input Artifacts",
                        "review-feature-01-slice-01-attempt-01.md = 1.0",
                    ),
                    ("Reason", "Implementation requires correction"),
                ]
            ),
            expected_source_workflow="review",
            expected_source_scope="Slice: F-01/S-01",
        )

        self.assertEqual(parsed["transition"], "RETURN")
        self.assertEqual(parsed["next_workflow"], "implement")
        self.assertEqual(parsed["blocker_category"], "IMPLEMENTATION_GAP")

    def test_parses_terminal_complete_and_halted_variants(self):
        complete = HandoffParser.parse(
            handoff_table(
                [
                    ("Transition", "TERMINAL"),
                    ("Terminal Status", "COMPLETE"),
                    ("Source Scope", "Slice: F-01/S-01"),
                    ("Completed Scope", "Project"),
                    (
                        "Input Artifacts",
                        "review-feature-01-slice-01-attempt-01.md = 1.0",
                    ),
                    ("Reason", "All declared work passed review"),
                ]
            ),
            expected_source_workflow="review",
        )
        halted = HandoffParser.parse(
            handoff_table(
                [
                    ("Transition", "TERMINAL"),
                    ("Terminal Status", "HALTED"),
                    ("Source Scope", "Project"),
                    ("Affected Scope", "Project"),
                    ("Blocker Category", "GRAPH_CONTRADICTION"),
                    ("Input Artifacts", "NONE"),
                    ("Reason", "planning_missing: planning evidence is invalid"),
                ]
            ),
            expected_source_workflow="plan",
        )

        self.assertEqual(complete["terminal_status"], "COMPLETE")
        self.assertEqual(halted["reason_code"], "planning_missing")

    def test_rejects_noncanonical_field_order_and_duplicate_marker(self):
        wrong_order = handoff_table(
            [
                ("Transition", "FORWARD"),
                ("Source Scope", "Project"),
                ("Next Workflow", "Grill"),
                ("Target Scope", "Feature: F-01"),
                ("Input Artifacts", "planning.md = 1.0"),
                ("Reason", "Planning is ready"),
            ]
        )

        self.assertIsNone(HandoffParser.parse(wrong_order))
        self.assertIsNone(
            HandoffParser.parse(wrong_order + "\n\n### Handoff\ninvalid")
        )

    def test_rejects_scope_artifact_and_reason_violations(self):
        bad_scope = handoff_table(
            [
                ("Transition", "FORWARD"),
                ("Next Workflow", "Solution"),
                ("Source Scope", "Project"),
                ("Target Scope", "Feature: F-01"),
                ("Input Artifacts", "planning.md = 1.0"),
                ("Reason", "Continue"),
            ]
        )
        bad_artifact = handoff_table(
            [
                ("Transition", "FORWARD"),
                ("Next Workflow", "Grill"),
                ("Source Scope", "Project"),
                ("Target Scope", "Feature: F-01"),
                ("Input Artifacts", "notes.md = 1.0"),
                ("Reason", "Continue"),
            ]
        )
        bad_halted_reason = handoff_table(
            [
                ("Transition", "TERMINAL"),
                ("Terminal Status", "HALTED"),
                ("Source Scope", "Project"),
                ("Affected Scope", "Project"),
                ("Blocker Category", "GRAPH_CONTRADICTION"),
                ("Input Artifacts", "NONE"),
                ("Reason", "Invalid graph"),
            ]
        )

        self.assertIsNone(HandoffParser.parse(bad_scope))
        self.assertIsNone(HandoffParser.parse(bad_artifact))
        self.assertIsNone(HandoffParser.parse(bad_halted_reason))

    def test_detects_any_handoff_heading_attempt(self):
        self.assertTrue(HandoffParser.has_handoff_attempt("## Handoff draft"))
        self.assertFalse(HandoffParser.has_handoff_attempt("No transition emitted"))


if __name__ == "__main__":
    unittest.main()
