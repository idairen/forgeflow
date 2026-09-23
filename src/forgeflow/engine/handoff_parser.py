"""ForgeFlow Handoff parser."""
import re

from .artifact_parser import ArtifactParser
from ..logging_config import get_logger

logger = get_logger()


class HandoffParser:
    """Parse the four canonical Handoff variants; never normalize old TDD entry."""

    _HANDOFF_MARKER = re.compile(r"(?m)^### Handoff[ \t]*$")
    _HANDOFF_ATTEMPT = re.compile(
        r"(?mi)^#{1,6}[ \t]+Handoff(?:[ \t].*)?$"
    )

    _WORKFLOW_SCOPES = {
        "Plan": "Project",
        "Grill": "Feature",
        "Solution": "Project",
        "Slice": "Feature",
        "Implement": "Slice",
        "Review": "Slice",
    }
    _RETURN_CATEGORIES = {
        "PLAN_GAP",
        "BUSINESS_GAP",
        "ENGINEERING_GAP",
        "SLICE_VIOLATION",
        "IMPLEMENTATION_GAP",
        "REVIEW_BLOCKER",
    }
    _CANONICAL_ARTIFACT = re.compile(
        r"(?:planning\.md"
        r"|requirement-feature-(?:0[1-9]|[1-9][0-9]+)\.md"
        r"|solution-plan\.md"
        r"|lane-feature-(?:0[1-9]|[1-9][0-9]+)\.md"
        r"|slice-plan-feature-(?:0[1-9]|[1-9][0-9]+)\.md"
        r"|implement-feature-(?:0[1-9]|[1-9][0-9]+)-slice-(?:0[1-9]|[1-9][0-9]+)\.md"
        r"|review-feature-(?:0[1-9]|[1-9][0-9]+)-slice-(?:0[1-9]|[1-9][0-9]+)-attempt-(?:0[1-9]|[1-9][0-9]+)\.md)"
    )
    _VERSION = re.compile(r"\d+\.\d+")
    _SCOPE = re.compile(r"(?:Project|Feature: F-(?:0[1-9]|[1-9][0-9]+)|Slice: F-(?:0[1-9]|[1-9][0-9]+)/S-(?:0[1-9]|[1-9][0-9]+))")
    _HALTED_REASON = re.compile(r"([a-z][a-z0-9_]*): \S.*")
    _VARIANT_FIELDS = {
        ("FORWARD", None): (
            "Transition",
            "Next Workflow",
            "Source Scope",
            "Target Scope",
            "Input Artifacts",
            "Reason",
        ),
        ("RETURN", None): (
            "Transition",
            "Next Workflow",
            "Source Scope",
            "Target Scope",
            "Blocker Category",
            "Input Artifacts",
            "Reason",
        ),
        ("TERMINAL", "COMPLETE"): (
            "Transition",
            "Terminal Status",
            "Source Scope",
            "Completed Scope",
            "Input Artifacts",
            "Reason",
        ),
        ("TERMINAL", "HALTED"): (
            "Transition",
            "Terminal Status",
            "Source Scope",
            "Affected Scope",
            "Blocker Category",
            "Input Artifacts",
            "Reason",
        ),
    }

    @classmethod
    def render_resolution(cls, resolution, source_scope="Project"):
        """Render read-only routing output; this does not authorize its emitter."""
        if resolution.get("resolution_rule") in {"rule_1_bootstrap", "rule_5_join_pending"}:
            return ""
        status = resolution["pipeline_status"]
        if status == "WAITING":
            return ""
        terminal = status in {"HALTED", "COMPLETE"}
        transition = "TERMINAL" if terminal else (
            "RETURN" if resolution.get("blocker_category") else "FORWARD")
        values = {"Transition": transition, "Source Scope": source_scope}
        if terminal:
            values["Terminal Status"] = status
            values["Completed Scope" if status == "COMPLETE" else "Affected Scope"] = "Project"
        else:
            values["Next Workflow"] = resolution["current_workflow"].capitalize()
            values["Target Scope"] = resolution["target_scope"]
        if transition == "RETURN" or status == "HALTED":
            values["Blocker Category"] = resolution.get("blocker_category", "GRAPH_CONTRADICTION")
        values["Input Artifacts"] = "; ".join(f"{a['filename']} = {a['version']}" for a in resolution.get("input_artifacts", [])) or "NONE"
        values["Reason"] = resolution.get("resolution_rule", "Fresh graph resolution")
        if status == "HALTED":
            values["Reason"] = f"{resolution['reason_code']}: {resolution.get('reason', values['Reason'])}"
        fields = cls._VARIANT_FIELDS[(transition, status if terminal else None)]
        return "### Handoff\n\n| Field | Value |\n| --- | --- |\n" + "\n".join(f"| {f} | {values[f]} |" for f in fields)

    @classmethod
    def parse(
        cls,
        text,
        expected_source_workflow=None,
        expected_source_scope=None,
    ):
        """Return a normalized handoff dict, or ``None`` when invalid."""
        if not isinstance(text, str):
            return None

        markers = list(cls._HANDOFF_MARKER.finditer(text))
        if len(markers) != 1:
            logger.debug("Expected exactly one ### Handoff marker")
            return None

        prefix = text[:markers[0].start()]
        if sum(1 for line in prefix.splitlines() if re.match(r"^\s*(```|~~~)", line)) % 2:
            return None

        block = text[markers[0].end():].strip()
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != "| Field | Value |" or lines[1] != "| --- | --- |":
            logger.debug("Invalid canonical Handoff table header")
            return None

        fields = []
        values = {}
        for line in lines[2:]:
            match = re.fullmatch(r"\| ([^|]+) \| ([^|]+) \|", line)
            if not match:
                logger.debug("Invalid Handoff table row: %s", line)
                return None
            field, value = match.groups()
            if field in values or not value.strip() or "{{" in value or "}}" in value:
                logger.debug("Invalid Handoff field/value: %s", field)
                return None
            fields.append(field)
            values[field] = value.strip()

        transition = values.get("Transition", "")
        terminal_status = values.get("Terminal Status")
        expected_fields = cls._VARIANT_FIELDS.get((transition, terminal_status))
        if expected_fields is None or tuple(fields) != expected_fields:
            logger.debug("Handoff fields do not match a canonical variant")
            return None

        if not cls._validate_scopes(
            values,
            expected_source_workflow,
            expected_source_scope,
        ):
            return None
        if not cls._validate_artifacts(values["Input Artifacts"], terminal_status):
            return None
        if not cls._validate_variant_values(values, transition, terminal_status):
            return None

        normalized = {
            field.lower().replace(" ", "_"): value
            for field, value in values.items()
        }
        if "next_workflow" in normalized:
            normalized["next_workflow"] = normalized["next_workflow"].lower()
        normalized["input_artifacts"] = cls._parse_artifacts(values["Input Artifacts"])
        if terminal_status == "HALTED":
            normalized["reason_code"] = values["Reason"].split(": ", 1)[0]
        normalized["transition_type"] = transition
        logger.debug("Parsed canonical handoff: transition=%s", transition)
        return normalized

    @classmethod
    def has_handoff_attempt(cls, text):
        """Return whether output attempts to emit a Handoff heading."""
        return isinstance(text, str) and cls._HANDOFF_ATTEMPT.search(text) is not None

    @classmethod
    def _validate_scopes(
        cls,
        values,
        expected_source_workflow,
        expected_source_scope,
    ):
        scope_fields = ("Source Scope", "Target Scope", "Completed Scope", "Affected Scope")
        for field in scope_fields:
            value = values.get(field)
            if value is not None and cls._SCOPE.fullmatch(value) is None:
                logger.debug("Invalid %s: %s", field, value)
                return False

        next_workflow = values.get("Next Workflow")
        if next_workflow:
            expected_scope = cls._WORKFLOW_SCOPES.get(next_workflow)
            if expected_scope is None or cls._scope_kind(values["Target Scope"]) != expected_scope:
                logger.debug("Target Scope does not match Next Workflow")
                return False

        if expected_source_workflow:
            canonical = expected_source_workflow.capitalize()
            expected_scope = cls._WORKFLOW_SCOPES.get(canonical)
            if expected_scope is None or cls._scope_kind(values["Source Scope"]) != expected_scope:
                logger.debug("Source Scope does not match emitting workflow")
                return False
        if (
            expected_source_scope is not None
            and values["Source Scope"] != expected_source_scope
        ):
            logger.debug("Source Scope does not match authorized scope")
            return False
        return True

    @classmethod
    def _validate_artifacts(cls, value, terminal_status):
        if value == "NONE":
            return terminal_status == "HALTED"
        entries = value.split("; ")
        if not entries or any(not entry for entry in entries):
            return False
        filenames = set()
        for entry in entries:
            parts = entry.split(" = ")
            if len(parts) != 2:
                logger.debug("Invalid Input Artifacts entry: %s", entry)
                return False
            filename, version = parts
            legacy_terminal = terminal_status == "HALTED" and re.fullmatch(r"tdd-feature-(0[1-9]|[1-9][0-9]+)-slice-(0[1-9]|[1-9][0-9]+)\.md", filename)
            if cls._CANONICAL_ARTIFACT.fullmatch(filename) is None and not legacy_terminal:
                logger.debug("Invalid canonical artifact filename: %s", filename)
                return False
            if filename in filenames:
                logger.debug("Duplicate Input Artifacts filename: %s", filename)
                return False
            filenames.add(filename)
            valid_version = cls._VERSION.fullmatch(version) is not None
            if not valid_version and not (terminal_status == "HALTED" and version == "INVALID_VERSION"):
                logger.debug("Invalid artifact version: %s", version)
                return False
        return True

    @classmethod
    def _validate_variant_values(cls, values, transition, terminal_status):
        if not values["Reason"].strip():
            return False
        if transition == "RETURN":
            return values["Blocker Category"] in cls._RETURN_CATEGORIES
        if terminal_status == "COMPLETE":
            return values["Completed Scope"] == "Project"
        if terminal_status == "HALTED":
            return (
                values["Affected Scope"] == "Project"
                and values["Blocker Category"] == "GRAPH_CONTRADICTION"
                and cls._HALTED_REASON.fullmatch(values["Reason"]) is not None
            )
        return True

    @classmethod
    def _parse_artifacts(cls, value):
        if value == "NONE":
            return []
        return [
            {"filename": filename, "version": version}
            for filename, version in (entry.split(" = ") for entry in value.split("; "))
        ]

    @staticmethod
    def _scope_kind(scope):
        return scope.split(":", 1)[0]

    @staticmethod
    def detect_artifact_state(root_dir):
        """Compatibility wrapper for canonical artifact discovery."""
        return ArtifactParser.detect_artifact_state(root_dir)

    @staticmethod
    def check_artifact_exists(artifacts_dir, artifact_name):
        return ArtifactParser.check_artifact_exists(artifacts_dir, artifact_name)
