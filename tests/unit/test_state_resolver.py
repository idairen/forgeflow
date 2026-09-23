import unittest

from forgeflow.engine.state_resolver import StateResolver


def artifact(filename, artifact_type, version, status, **metadata):
    return {
        "filename": filename,
        "path": f"/project/.forgeflow/artifacts/{filename}",
        "artifact_type": artifact_type,
        "owner_workflow": metadata.get("Owner Workflow", "Plan"),
        "version": version,
        "status": status,
        "metadata": metadata,
        "verification_actionable": artifact_type == "Slice Plan",
    }


def planning(status="READY", features="F-01", versions="F-01 = 1.0"):
    return artifact(
        "planning.md",
        "Planning",
        "1.0",
        status,
        **{
            "Feature IDs": features,
            "Feature Contract Versions": versions,
        },
    )


def requirement(status="READY", planning_version="1.0"):
    return artifact(
        "requirement-feature-01.md",
        "Requirement",
        "1.0",
        status,
        **{"Feature ID": "F-01", "Planning Version": planning_version},
    )


def solution(status="READY", requirement_version="1.0"):
    return artifact(
        "solution-plan.md",
        "Solution Plan",
        "1.0",
        status,
        **{
            "Based On Requirements": f"F-01 = {requirement_version}",
            "Feature Engineering Versions": "F-01 = 1.0",
        },
    )


def slice_plan(status="READY", solution_version="1.0", slices="S-01"):
    return artifact(
        "slice-plan-feature-01.md",
        "Slice Plan",
        "1.0",
        status,
        **{
            "Feature ID": "F-01",
            "Based On Solution": solution_version,
            "Slice IDs": slices,
        },
    )


def implement(status="READY_FOR_REVIEW", attempt="1"):
    return artifact(
        "implement-feature-01-slice-01.md",
        "Implement Record",
        "1.0",
        status,
        **{
            "Feature ID": "F-01",
            "Slice ID": "S-01",
            "Attempt": attempt,
            "Solution Version": "1.0",
            "Slice Plan Version": "1.0",
        },
    )


def review(decision="PASS", return_workflow=None, return_scope=None):
    metadata = {
        "Feature ID": "F-01",
        "Slice ID": "S-01",
        "Attempt": "1",
        "Decision": decision,
        "Solution Version": "1.0",
        "Slice Plan Version": "1.0",
    }
    if return_workflow is not None:
        metadata["Return Workflow"] = return_workflow
        metadata["Return Scope"] = return_scope
    result = artifact(
        "review-feature-01-slice-01-attempt-01.md",
        "Review Report",
        "1.0",
        "READY",
        **metadata,
    )
    result["findings"] = []
    return result


def state(*artifacts, status="active"):
    return {
        "status": status,
        "artifacts": {item["filename"]: item for item in artifacts},
        "errors": [],
        "diagnostics": [],
    }


class StateResolverTests(unittest.TestCase):
    def assert_resolution(self, artifact_state, workflow, scope, rule):
        resolution = StateResolver.resolve(artifact_state)
        self.assertEqual(resolution["current_workflow"], workflow)
        self.assertEqual(resolution["target_scope"], scope)
        self.assertEqual(resolution["resolution_rule"], rule)

    def test_resolves_every_forward_stage_from_graph_evidence(self):
        cases = [
            (state(), "plan", "Project", "rule_1_bootstrap"),
            (
                state(planning()),
                "grill",
                "Feature: F-01",
                "rule_5_requirement_required",
            ),
            (
                state(planning(), requirement()),
                "solution",
                "Project",
                "rule_6_solution_required",
            ),
            (
                state(planning(), requirement(), solution()),
                "slice",
                "Feature: F-01",
                "rule_7_slice_plan_required",
            ),
            (
                state(planning(), requirement(), solution(), slice_plan()),
                "implement",
                "Slice: F-01/S-01",
                "rule_10_implement_required",
            ),
            (
                state(planning(), requirement(), solution(), slice_plan(), implement()),
                "review",
                "Slice: F-01/S-01",
                "rule_9_review_required",
            ),
        ]

        for artifact_state, workflow, scope, rule in cases:
            with self.subTest(rule=rule):
                self.assert_resolution(artifact_state, workflow, scope, rule)

    def test_completed_graph_resolves_terminal_complete(self):
        resolution = StateResolver.resolve(
            state(
                planning(),
                requirement(),
                solution(),
                slice_plan(),
                implement(),
                review(),
            )
        )

        self.assertEqual(resolution["pipeline_status"], "COMPLETE")
        self.assertEqual(resolution["resolution_rule"], "rule_11_project_complete")

    def test_explicit_empty_project_resolves_complete(self):
        resolution = StateResolver.resolve(
            state(planning(features="NONE", versions="NONE"))
        )

        self.assertEqual(resolution["pipeline_status"], "COMPLETE")

    def test_failed_review_returns_to_declared_owner_and_scope(self):
        artifact_state = state(
            planning(),
            requirement(),
            solution(),
            slice_plan(),
            implement(),
            review("FAIL", "Implement", "Slice: F-01/S-01"),
        )

        self.assert_resolution(
            artifact_state,
            "implement",
            "Slice: F-01/S-01",
            "rule_8_review_failure",
        )
        self.assertTrue(StateResolver.has_current_failed_review(artifact_state))

    def test_current_persisted_blocker_has_precedence(self):
        blocked = requirement(status="BLOCKED")
        blocked["metadata"].update(
            {
                "Blocker Category": "BUSINESS_GAP",
                "Blocker Owner": "Grill",
                "Affected Scope": "Feature: F-01",
            }
        )

        resolution = StateResolver.resolve(state(planning(), blocked))

        self.assertEqual(resolution["resolution_rule"], "rule_3_persisted_blocker")
        self.assertEqual(resolution["entry_mode"], "recovery")
        self.assertEqual(resolution["blocker_category"], "BUSINESS_GAP")

    def test_stale_requirement_returns_to_grill(self):
        self.assert_resolution(
            state(planning(), requirement(planning_version="0.9")),
            "grill",
            "Feature: F-01",
            "rule_5_requirement_required",
        )

    def test_undeclared_feature_is_a_graph_contradiction(self):
        extra = artifact(
            "requirement-feature-02.md",
            "Requirement",
            "1.0",
            "READY",
            **{"Feature ID": "F-02", "Planning Version": "1.0"},
        )

        resolution = StateResolver.resolve(state(planning(), extra))

        self.assertEqual(resolution["pipeline_status"], "HALTED")
        self.assertEqual(
            resolution["reason"], "artifact_feature_not_declared_in_planning"
        )
        self.assertEqual(resolution["reason_code"], "identifier_reference_invalid")

    def test_invalid_parser_state_halts_with_diagnostic_evidence(self):
        invalid_state = {
            "status": "invalid",
            "artifacts": {},
            "diagnostics": [
                {
                    "code": "invalid_version",
                    "artifacts": [{"filename": "planning.md", "version": "INVALID_VERSION"}],
                }
            ],
        }

        resolution = StateResolver.resolve(invalid_state)

        self.assertEqual(resolution["pipeline_status"], "HALTED")
        self.assertEqual(resolution["reason"], "invalid_version")
        self.assertEqual(len(resolution["terminal_evidence"]), 1)


if __name__ == "__main__":
    unittest.main()
