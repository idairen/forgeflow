"""Real on-disk graph regressions for the shipped Markdown protocol."""
import asyncio
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from forgeflow.engine.artifact_parser import ArtifactParser
from forgeflow.engine.handoff_parser import HandoffParser
from forgeflow.engine.runner import ForgeRunner
from forgeflow.engine.state_resolver import StateResolver
from forgeflow.scaffold import initialize_project


def document(kind, owner, extra, status="READY", version="1.0", body=""):
    rows = {"Artifact Type": kind, "Version": version, "Status": status,
            "Owner Workflow": owner, **extra}
    return f"# {kind}\n\n## Metadata\n\n| Field | Value |\n| --- | --- |\n" + "\n".join(f"| {k} | {v} |" for k, v in rows.items()) + "\n\n" + body


def markdown_table(name, headers, rows):
    return f"## {name}\n\n| " + " | ".join(headers) + " |\n| " + " | ".join("---" for _ in headers) + " |\n" + "\n".join("| " + " | ".join(row) + " |" for row in rows) + "\n\n"


class CurrentFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.root = self.project / ".forgeflow/artifacts"
        self.root.mkdir(parents=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def graph(self):
        state = ArtifactParser.detect_artifact_state(self.root)
        return state, StateResolver.resolve(state)

    def plan(self, features=("F-01",), dependencies=None, version="1.0", changes=""):
        dependencies = dependencies or {}
        body = markdown_table("Features", ("Feature ID", "Title", "Outcome", "Dependencies"),
                              [(f, "Capability", "Approved behavior", dependencies.get(f, "NONE")) for f in features])
        self.write("planning.md", document("Planning", "Plan", {"Feature IDs": "; ".join(features),
            "Feature Contract Versions": "; ".join(f"{f} = {version}" for f in features), "Change Set": "BASELINE" if version == "1.0" else "MODIFIED"}, version=version, body=body + changes))

    def req(self, feature="F-01", status="READY", **extra):
        self.write(f"requirement-feature-{feature[2:]}.md", document("Requirement", "Grill", {"Feature ID": feature, "Planning Version": "1.0", **extra}, status=status))

    def lane(self, feature="F-01", status="ACTIVE", dependencies="NONE", version="1.0"):
        self.write(f"lane-feature-{feature[2:]}.md", document("Feature Lane Record", "Grill", {
            "Feature ID": feature, "Feature Contract Version": version, "Attempt": "1",
            "Dependency Requirement Versions": dependencies, "Claim Evidence": "Lane entry for " + feature}, status=status))

    def delivery(self, slices=("S-01",), strategy="BEHAVIORAL_TEST", feature="F-01"):
        self.plan((feature,))
        self.req(feature)
        self.write("solution-plan.md", document("Solution Plan", "Solution", {
            "Based On Requirements": feature + " = 1.0", "Feature Engineering Versions": feature + " = 1.0"}))
        rows = [(s, "approved behavior", strategy, "Required by approved scope", "acceptance", "expected behavior", "actual tool execution") for s in slices]
        body = markdown_table("Verification Plan", ("Slice ID", "Obligation", "Strategies", "Rationale", "Required Checks", "Passing Criteria", "Evidence Required"), rows)
        self.write(f"slice-plan-feature-{feature[2:]}.md", document("Slice Plan", "Slice", {
            "Feature ID": feature, "Based On Solution": "1.0", "Slice IDs": "; ".join(slices)}, body=body))

    def implement(self, slice_id="S-01", strategy="BEHAVIORAL_TEST", result="SUCCEEDED", source="TOOL_EXECUTION", status="READY_FOR_REVIEW", attempt=1, feature="F-01"):
        body = "## Implementation Summary\n\nImplement approved behavior.\n\n"
        body += markdown_table("Verification Selection", ("Strategy", "Rationale", "Governing Obligation"), [(strategy, "Approved Slice plan", "approved behavior")])
        body += markdown_table("Verification Evidence", ("Strategy", "Obligation or Check", "Source", "Command or Procedure", "Target and Environment", "Result", "Evidence Reference"), [(strategy, "acceptance", source, "python -m unittest", "current worktree; Python", result, "embedded output: exit=0; 1 test passed")])
        body += "## Open Issues\n\nNONE\n\n## Self-check\n\nChecked scope and required evidence.\n"
        self.write(f"implement-feature-{feature[2:]}-slice-{slice_id[2:]}.md", document("Implement Record", "Implement", {
            "Feature ID": feature, "Slice ID": slice_id, "Attempt": str(attempt), "Solution Version": "1.0", "Slice Plan Version": "1.0", "Verification Strategies": strategy}, status=status, body=body))

    def review(self, slice_id="S-01", decision="PASS", attempt=1, feature="F-01"):
        extra = {"Feature ID": feature, "Slice ID": slice_id, "Attempt": str(attempt), "Solution Version": "1.0", "Slice Plan Version": "1.0", "Decision": decision, "Blocking Findings": "0" if decision == "PASS" else "1", "Non-blocking Findings": "0"}
        rows = []
        if decision == "FAIL":
            extra.update({"Return Workflow": "Implement", "Return Scope": f"Slice: {feature}/{slice_id}"})
            rows = [("1", "BLOCKING", "Implement", f"Slice: {feature}/{slice_id}", "Incorrect result", "Observed failure", "Requirement acceptance")]
        self.write(f"review-feature-{feature[2:]}-slice-{slice_id[2:]}-attempt-{attempt:02d}.md", document("Review Report", "Review", extra, body=markdown_table("Findings", ("#", "Severity", "Owner Workflow", "Affected Scope", "Finding", "Evidence", "Violated Contract"), rows)))

    def test_real_implement_review_complete_with_exact_projection(self):
        self.delivery()
        self.assertEqual(self.graph()[1]["current_workflow"], "implement")
        self.implement()
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(result["current_workflow"], "review")
        self.assertEqual([e["filename"] for e in result["input_artifacts"]], ["planning.md", "requirement-feature-01.md", "solution-plan.md", "slice-plan-feature-01.md", "implement-feature-01-slice-01.md"])
        rendered = HandoffParser.render_resolution(result)
        handoff = HandoffParser.parse(rendered)
        self.assertIsNotNone(handoff)
        self.assertEqual(ForgeRunner._handoff_graph_errors(handoff, state, result, None, "Project"), [])
        handoff["input_artifacts"] = list(reversed(handoff["input_artifacts"]))
        self.assertIn("input_artifact_projection_does_not_match_graph", ForgeRunner._handoff_graph_errors(handoff, state, result, None, "Project"))
        self.review()
        self.assertEqual(self.graph()[1]["pipeline_status"], "COMPLETE")

    def test_canonical_numbers_above_99(self):
        self.delivery(("S-100",), feature="F-100")
        self.implement("S-100", attempt=100, feature="F-100")
        self.review("S-100", attempt=100, feature="F-100")
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(result["pipeline_status"], "COMPLETE")
        self.assertIsNotNone(HandoffParser.parse(HandoffParser.render_resolution(result)))

    def test_fail_rework_pass_preserves_prior_attempt_evidence(self):
        initialize_project(self.project, "codex", force=True)
        self.delivery()
        self.implement(attempt=1)
        self.review(decision="FAIL", attempt=1)
        original_record = (self.root / "implement-feature-01-slice-01.md").read_text()
        original_review = (self.root / "review-feature-01-slice-01-attempt-01.md").read_bytes()
        resolution = self.graph()[1]
        self.assertEqual(resolution["resolution_rule"], "rule_8_review_failure")
        incoming = HandoffParser.render_resolution(resolution, "Slice: F-01/S-01")

        async def rework(name, user_input=None, entry_context=None):
            # Real runner/graph entry, mocked Agent writes; not live IDE acceptance.
            self.assertEqual(name, "implement")
            self.assertEqual(entry_context["entry_mode"], "handoff")
            received = HandoffParser.parse(entry_context["handoff"])
            self.assertEqual(received["transition"], "RETURN")
            self.assertEqual(received["blocker_category"], "REVIEW_BLOCKER")
            self.assertEqual(received["target_scope"], "Slice: F-01/S-01")
            self.write("history/implement-feature-01-slice-01-attempt-01.md", original_record)
            self.implement(attempt=2)
            return HandoffParser.render_resolution(self.graph()[1], "Slice: F-01/S-01")

        runner = ForgeRunner(self.project / "forgeflow.json")
        runner._execute_llm = AsyncMock(side_effect=rework)
        output = asyncio.run(runner.execute_single("implement", handoff_text=incoming))
        self.assertEqual(runner._execute_llm.await_count, 1)
        self.assertEqual(HandoffParser.parse(output)["next_workflow"], "review")
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(result["current_workflow"], "review")
        self.review(attempt=2)
        self.assertEqual(self.graph()[1]["pipeline_status"], "COMPLETE")
        self.assertEqual(
            (self.root / "review-feature-01-slice-01-attempt-01.md").read_bytes(),
            original_review,
        )
        self.assertEqual(
            (self.root / "history/implement-feature-01-slice-01-attempt-01.md").read_text(),
            original_record,
        )

    def test_pending_required_check_cannot_reach_review(self):
        self.delivery()
        self.implement(result="NOT_RUN")
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")
        self.implement(result="NOT_RUN", status="IN_PROGRESS")
        self.assertEqual(self.graph()[1]["current_workflow"], "implement")

    def test_observed_malformed_implement_candidates_are_rejected(self):
        self.delivery()
        self.implement()
        name = "implement-feature-01-slice-01.md"
        original = (self.root / name).read_text()
        cases = [
            ("Stray summary\n\n" + original, "artifact must begin with a level-one title"),
            (original.replace("| SUCCEEDED |", "| PASS |"), "invalid evidence result"),
            (original.replace("| TOOL_EXECUTION |", "| TOOL_EXECUTION; MODEL_ASSESSMENT |"), "invalid evidence source"),
            (original.replace("| BEHAVIORAL_TEST | acceptance |", "| BEHAVIORAL_TEST; STATIC_VALIDATION | acceptance |"), "evidence strategy is not selected"),
        ]
        for content, error in cases:
            with self.subTest(error=error):
                self.write(name, content)
                state, result = self.graph()
                self.assertIn(f"{name}: {error}", state["errors"])
                self.assertEqual(result["pipeline_status"], "HALTED")

    def test_format_repair_original_does_not_conflict_with_later_attempt_archive(self):
        self.delivery()
        self.implement()
        self.review(decision="FAIL")
        failed_review = (self.root / "review-feature-01-slice-01-attempt-01.md").read_bytes()
        name = "implement-feature-01-slice-01.md"
        corrected = (self.root / name).read_text()
        malformed = "Stray summary\n\n" + corrected
        self.write(name, malformed)
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")
        digest = hashlib.sha256(malformed.encode()).hexdigest()
        original_path = f"history/invalid-implement/{digest}/{name}"
        # Simulate an explicitly authorized format-only repair, not a recovery engine.
        self.write(original_path, malformed)
        corrected = corrected.replace("## Open Issues\n\nNONE", "## Open Issues\n\n"
            f"User authorized moving stray prose; original: {original_path}; SHA256 {digest}.")
        self.write(name, corrected)
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(state["artifacts"][name]["next_attempt"], 2)
        self.assertEqual(result["resolution_rule"], "rule_8_review_failure")
        self.write("history/implement-feature-01-slice-01-attempt-01.md", corrected)
        self.implement(attempt=2)
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(state["artifacts"][name]["used_attempts"], [1, 2])
        self.assertEqual(result["current_workflow"], "review")
        self.assertEqual((self.root / original_path).read_bytes(), malformed.encode())
        self.assertEqual((self.root / "review-feature-01-slice-01-attempt-01.md").read_bytes(), failed_review)

    def test_conflicting_standard_attempt_archive_still_blocks(self):
        self.delivery()
        self.implement(status="IN_PROGRESS")
        name = "implement-feature-01-slice-01.md"
        self.write("history/implement-feature-01-slice-01-attempt-01.md", (self.root / name).read_text())
        self.implement()
        state, result = self.graph()
        self.assertTrue(any("conflicting Attempt history" in e for e in state["errors"]))
        self.assertEqual(result["pipeline_status"], "HALTED")

    def test_wrong_scope_review_return_does_not_launch_implement(self):
        initialize_project(self.project, "codex", force=True)
        self.delivery(("S-01", "S-02"))
        self.implement()
        self.review(decision="FAIL")
        incoming = HandoffParser.render_resolution(self.graph()[1]).replace(
            "| Target Scope | Slice: F-01/S-01 |", "| Target Scope | Slice: F-01/S-02 |")
        runner = ForgeRunner(self.project / "forgeflow.json")
        runner._execute_llm = AsyncMock()
        output = asyncio.run(runner.execute_single("implement", handoff_text=incoming))
        runner._execute_llm.assert_not_called()
        self.assertEqual(HandoffParser.parse(output)["target_scope"], "Slice: F-01/S-01")

    def test_method_cannot_replace_strategy_or_human_evidence(self):
        self.delivery(strategy="MANUAL_ACCEPTANCE")
        self.implement(strategy="MANUAL_ACCEPTANCE", source="MODEL_ASSESSMENT")
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")
        self.implement(strategy="Direct implementation")
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")

    def test_mandatory_tdd_cannot_be_replaced_by_behavioral_testing(self):
        self.delivery(strategy="TDD")
        self.implement()
        self.assertIn("omits mandatory Slice strategy", " ".join(self.graph()[0]["errors"]))

    def test_current_fail_precedes_earlier_missing_implementation(self):
        self.delivery(("S-01", "S-02"))
        self.implement("S-02")
        self.review("S-02", "FAIL")
        self.assertEqual(self.graph()[1]["resolution_rule"], "rule_8_review_failure")
        self.assertEqual(self.graph()[1]["target_scope"], "Slice: F-01/S-02")

    def test_legacy_slice_without_actionable_plan_routes_to_slice(self):
        self.delivery()
        path = self.root / "slice-plan-feature-01.md"
        path.write_text(path.read_text().split("## Verification Plan")[0])
        self.assertEqual(self.graph()[1]["current_workflow"], "slice")

    def test_grill_dependency_claim_join_and_completion(self):
        self.plan(("F-02", "F-01"), {"F-02": "F-01"})
        self.assertEqual(self.graph()[1]["target_scope"], "Feature: F-01")
        self.lane()
        self.assertEqual(self.graph()[1]["pipeline_status"], "WAITING")
        self.req()
        self.lane(status="COMPLETE")
        self.assertEqual(self.graph()[1]["target_scope"], "Feature: F-02")
        self.lane("F-02", dependencies="F-01 = 1.0")
        self.assertEqual(self.graph()[1]["pipeline_status"], "WAITING")
        self.req("F-02")
        self.lane("F-02", "COMPLETE", "F-01 = 1.0")
        self.assertEqual(self.graph()[1]["current_workflow"], "solution")

    def test_stale_active_lane_halts_and_subsequent_plan_waits(self):
        self.plan()
        self.lane(version="0.9")
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")
        self.lane()
        state, result = self.graph()
        self.assertEqual(ForgeRunner._subsequent_plan_error(state, result), "subsequent_plan_requires_released_lanes")

    def test_legacy_tdd_is_terminal_diagnostic_not_ignored(self):
        self.plan()
        self.write("tdd-feature-01-slice-01.md", "# Legacy\n\n| Version | 1.0 |\n")
        state, result = self.graph()
        self.assertEqual(result["pipeline_status"], "HALTED")
        self.assertEqual(result["input_artifacts"][0]["filename"], "tdd-feature-01-slice-01.md")
        self.assertIsNotNone(HandoffParser.parse(HandoffParser.render_resolution(result)))

    def test_disposed_review_requires_next_attempt_and_valid_digest(self):
        self.delivery()
        self.implement()
        name = "review-feature-01-slice-01-attempt-01.md"
        original = b"# Invalid review\n"
        self.write("history/invalid-review/" + name, original.decode())
        values = {"Source Filename": name, "SHA256": hashlib.sha256(original).hexdigest(), "Feature ID": "F-01", "Slice ID": "S-01", "Attempt": "1", "Implement Version": "1.0", "Authorization": "User approved exact disposition", "Reason": "Missing metadata"}
        receipt = "# Receipt\n\n| Field | Value |\n| --- | --- |\n" + "\n".join(f"| {k} | {v} |" for k, v in values.items())
        self.write("history/invalid-review/" + name.replace(".md", ".receipt.md"), receipt)
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertEqual(result["current_workflow"], "implement")
        self.assertEqual(state["artifacts"]["implement-feature-01-slice-01.md"]["next_attempt"], 2)
        self.write("history/invalid-review/" + name, "tampered")
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")

    def test_installer_refresh_removes_retired_launchers_preserves_evidence(self):
        initialize_project(self.project, "codex", force=True)
        self.write("tdd-feature-01-slice-01.md", "legacy evidence")
        legacy = self.project / ".forgeflow/workflow/tdd.md"
        legacy.write_text("retired launcher")
        initialize_project(self.project, "codex", force=True)
        self.assertFalse(legacy.exists())
        self.assertTrue((self.project / ".forgeflow/protocol/transition.md").is_file())
        self.assertEqual((self.root / "tdd-feature-01-slice-01.md").read_text(), "legacy evidence")

    def test_missing_handoff_corrects_without_agent_execution(self):
        initialize_project(self.project, "codex", force=True)
        self.delivery()
        runner = ForgeRunner(self.project / "forgeflow.json")
        runner._execute_llm = AsyncMock()
        output = asyncio.run(runner.execute_single("implement"))
        runner._execute_llm.assert_not_called()
        self.assertEqual(HandoffParser.parse(output)["next_workflow"], "implement")

    def test_valid_handoff_executes_exactly_one_agent(self):
        initialize_project(self.project, "codex", force=True)
        self.delivery()
        incoming = HandoffParser.render_resolution(self.graph()[1])
        runner = ForgeRunner(self.project / "forgeflow.json")
        runner._execute_llm = AsyncMock(return_value="Need required environment.")
        asyncio.run(runner.execute_single("implement", handoff_text=incoming))
        self.assertEqual(runner._execute_llm.await_count, 1)
        self.assertEqual(runner.history[-1]["result"], "STEP_WAITING")

    def test_bootstrap_with_reports_does_not_launch_plan(self):
        initialize_project(self.project, "codex", force=True)
        reports = self.project / ".forgeflow/reports"
        reports.mkdir()
        (reports / "residual.md").write_text("existing project evidence")
        runner = ForgeRunner(self.project / "forgeflow.json")
        runner._execute_llm = AsyncMock()
        output = asyncio.run(runner.execute_single("plan", user_input="new intent"))
        runner._execute_llm.assert_not_called()
        self.assertIn("explicit reset", output)
        self.assertFalse((self.root / "planning.md").exists())

    def test_explicit_lane_entry_and_interrupted_recovery(self):
        self.plan(("F-01", "F-02"))
        state, _ = self.graph()
        entry = StateResolver.grill_entry(state, "F-02")
        self.assertEqual(entry["entry_mode"], "lane")
        self.assertEqual(entry["target_scope"], "Feature: F-02")
        self.lane("F-02")
        state, _ = self.graph()
        with self.assertRaisesRegex(ValueError, "inactivity"):
            StateResolver.grill_entry(state, "F-02")
        recovered = StateResolver.grill_entry(state, "F-02", confirm_inactive=True)
        self.assertEqual(recovered["entry_mode"], "recovery")
        self.assertEqual(recovered["confirmed_inactive_claim"]["attempt"], "1")
        self.assertFalse(recovered["release_only"])

    def test_two_blocked_active_lanes_do_not_defer_each_other_forever(self):
        self.plan(("F-01", "F-02"))
        for f in ("F-01", "F-02"):
            self.req(f, "BLOCKED", **{"Blocker Category": "BUSINESS_GAP", "Blocker Owner": "Grill", "Affected Scope": f"Feature: {f}", "Blocker Reason": "Missing business decision", "Blocker Evidence": "Question remains unanswered"})
            self.lane(f)
        state, result = self.graph()
        self.assertEqual(result["resolution_rule"], "rule_3_persisted_blocker")
        self.assertEqual(result["target_scope"], "Feature: F-01")
        recovered = StateResolver.grill_entry(state, "F-02", confirm_inactive=True)
        self.assertEqual(recovered["target_scope"], "Feature: F-02")

    def test_membership_revision_needs_prior_planning_and_requirement_lineage(self):
        self.delivery()
        old = (self.root / "planning.md").read_text()
        self.write("history/planning-v1.0.md", old)
        changes = markdown_table("Change Set", ("Feature ID", "Change", "Previous Contract Version", "Current Contract Version", "Rationale"), [
            ("F-01", "MODIFIED", "1.0", "2.0", "Approved scope update"),
            ("F-02", "ADDED", "NONE", "2.0", "Approved new Feature")])
        self.plan(("F-01", "F-02"), version="2.0", changes=changes)
        state, result = self.graph()
        self.assertEqual(state["errors"], [])
        self.assertTrue(state["artifacts"]["solution-plan.md"]["valid_but_stale"])
        self.assertEqual(result["current_workflow"], "grill")
        (self.root / "history/planning-v1.0.md").unlink()
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")

    def test_metadata_only_implement_is_invalid_not_reviewable(self):
        self.delivery()
        self.implement()
        path = self.root / "implement-feature-01-slice-01.md"
        path.write_text(path.read_text().split("## Implementation Summary")[0])
        self.assertEqual(self.graph()[1]["pipeline_status"], "HALTED")
