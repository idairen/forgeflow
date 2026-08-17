"""Deterministic runtime projection from the active Artifact Graph."""
import re


class StateResolver:
    """Apply the ordered Handoff Protocol transition rules."""

    _OWNER_ORDER = ("Plan", "Grill", "Solution", "Slice", "TDD")
    _FEATURE = re.compile(r"F-\d{2}")
    _SLICE = re.compile(r"S-\d{2}")
    _FEATURE_SCOPE = re.compile(r"Feature: (F-\d{2})")
    _SLICE_SCOPE = re.compile(r"Slice: (F-\d{2})/(S-\d{2})")
    _VERSION_ENTRY = re.compile(r"(F-\d{2}) = (\d+\.\d+)")
    _EMPTY_FEATURES = "NONE"

    @classmethod
    def resolve(cls, artifact_state):
        """Return the next workflow and pipeline status for a validated graph."""
        if artifact_state.get("status") == "invalid":
            diagnostics = artifact_state.get("diagnostics", ())
            diagnostic = diagnostics[0] if diagnostics else {
                "code": "invalid_artifact_graph",
                "artifacts": [],
            }
            return cls._terminal(
                "HALTED",
                "rule_2_graph_contradiction",
                diagnostic["code"],
                diagnostic.get("artifacts", ()),
            )
        artifacts = artifact_state.get("artifacts", {})
        if not artifacts:
            return cls._active(
                "plan",
                "Project",
                "rule_1_bootstrap",
                entry_mode="bootstrap",
            )

        planning = artifacts.get("planning.md")
        if planning is None:
            return cls._terminal(
                "HALTED",
                "rule_2_graph_contradiction",
                "planning_missing_from_active_graph",
                cls._terminal_evidence(*artifacts.values()),
            )

        features = cls._planning_features(
            planning["metadata"].get("Feature IDs", "")
        )
        contradiction = cls._graph_contradiction(artifacts, features)
        if contradiction:
            return cls._terminal(
                "HALTED",
                "rule_2_graph_contradiction",
                contradiction["code"],
                contradiction["artifacts"],
            )

        blocked = [
            artifact
            for artifact in artifacts.values()
            if artifact["status"] == "BLOCKED"
            and cls._blocker_is_current(artifact, artifacts, planning, features)
        ]
        if blocked:
            feature_positions, slice_positions = cls._declared_positions(
                artifacts,
                features,
            )
            blocker = min(
                blocked,
                key=lambda artifact: cls._blocker_sort_key(
                    artifact,
                    feature_positions,
                    slice_positions,
                ),
            )
            metadata = blocker["metadata"]
            return cls._active(
                metadata["Blocker Owner"].lower(),
                metadata["Affected Scope"],
                "rule_3_persisted_blocker",
                blocker_category=metadata["Blocker Category"],
                entry_mode="recovery",
            )

        if not cls._planning_is_usable(planning, features):
            return cls._active("plan", "Project", "rule_4_planning_not_ready")
        if not features:
            return cls._terminal("COMPLETE", "rule_11_project_complete")

        requirements = {}
        for feature in features:
            artifact = artifacts.get(
                f"requirement-feature-{feature.removeprefix('F-')}.md"
            )
            if not cls._requirement_is_usable(
                artifact,
                feature,
                planning,
                features,
            ):
                return cls._active(
                    "grill", f"Feature: {feature}", "rule_5_requirement_required"
                )
            requirements[feature] = artifact["version"]

        solution = artifacts.get("solution-plan.md")
        if not cls._solution_is_usable(solution, requirements):
            return cls._active(
                "solution", "Project", "rule_6_solution_required"
            )

        slices_by_feature = {}
        for feature in features:
            artifact = artifacts.get(
                f"slice-plan-feature-{feature.removeprefix('F-')}.md"
            )
            if not cls._slice_plan_is_usable(
                artifact,
                feature,
                solution,
                features,
            ):
                return cls._active(
                    "slice", f"Feature: {feature}", "rule_7_slice_plan_required"
                )
            slices_by_feature[feature] = cls._identifier_list(
                artifact["metadata"].get("Slice IDs", ""), cls._SLICE
            )

        contradiction = cls._slice_contradiction(artifacts, slices_by_feature)
        if contradiction:
            return cls._terminal(
                "HALTED",
                "rule_2_graph_contradiction",
                contradiction["code"],
                contradiction["artifacts"],
            )

        for feature in features:
            slice_plan = artifacts[
                f"slice-plan-feature-{feature.removeprefix('F-')}.md"
            ]
            for slice_id in slices_by_feature[feature]:
                scope = f"Slice: {feature}/{slice_id}"
                artifact_scope = (
                    f"{feature.removeprefix('F-')}-slice-"
                    f"{slice_id.removeprefix('S-')}"
                )
                tdd = artifacts.get(f"tdd-feature-{artifact_scope}.md")
                if not cls._current_tdd(tdd, solution, slice_plan):
                    return cls._active("tdd", scope, "rule_10_tdd_required")
                review = cls._matching_review(
                    artifacts, artifact_scope, tdd, solution, slice_plan
                )
                if review is None:
                    return cls._active("review", scope, "rule_9_review_required")
                if review["metadata"]["Decision"] == "FAIL":
                    return cls._active(
                        review["metadata"]["Return Workflow"].lower(),
                        review["metadata"]["Return Scope"],
                        "rule_8_review_failure",
                        blocker_category="REVIEW_BLOCKER",
                    )

        return cls._terminal("COMPLETE", "rule_11_project_complete")

    @classmethod
    def _graph_contradiction(cls, artifacts, features):
        planning = artifacts["planning.md"]
        if features is None:
            return cls._contradiction(
                "invalid_planning_feature_order",
                planning,
            )
        downstream = sorted(name for name in artifacts if name != "planning.md")
        if not features and downstream:
            return cls._contradiction(
                "empty_planning_has_downstream_artifacts",
                planning,
                artifacts[downstream[0]],
            )
        planned = set(features)
        for artifact in artifacts.values():
            metadata = artifact["metadata"]
            feature = metadata.get("Feature ID")
            if feature is not None and feature not in planned:
                return cls._contradiction(
                    "artifact_feature_not_declared_in_planning",
                    planning,
                    artifact,
                )
            if artifact["status"] == "BLOCKED":
                scope = metadata.get("Affected Scope", "")
                scope_error = cls._scope_reference_error(
                    scope,
                    artifacts,
                    planned,
                )
                if scope_error is not None:
                    return cls._contradiction(
                        f"blocker_affected_scope_{scope_error}",
                        planning,
                        artifact,
                        *cls._scope_evidence(scope, artifacts),
                    )
            if (
                artifact["artifact_type"] == "Review Report"
                and metadata.get("Decision") == "FAIL"
            ):
                scope_error = cls._scope_reference_error(
                    metadata.get("Return Scope", ""),
                    artifacts,
                    planned,
                )
                if scope_error is not None:
                    return cls._contradiction(
                        f"review_return_scope_{scope_error}",
                        planning,
                        artifact,
                        *cls._scope_evidence(
                            metadata.get("Return Scope", ""), artifacts
                        ),
                    )
            if artifact["artifact_type"] == "Review Report":
                for finding in artifact.get("findings", ()):
                    scope_error = cls._scope_reference_error(
                        finding["affected_scope"],
                        artifacts,
                        planned,
                    )
                    if scope_error is not None:
                        return cls._contradiction(
                            f"review_finding_scope_{scope_error}",
                            planning,
                            artifact,
                            *cls._scope_evidence(
                                finding["affected_scope"], artifacts
                            ),
                        )
        return None

    @classmethod
    def _scope_reference_error(cls, scope, artifacts, planned):
        if scope == "Project":
            return None
        feature_match = cls._FEATURE_SCOPE.fullmatch(scope)
        if feature_match is not None:
            if feature_match.group(1) not in planned:
                return "feature_not_declared_in_planning"
            return None
        slice_match = cls._SLICE_SCOPE.fullmatch(scope)
        if slice_match is None:
            return "invalid_scope"
        feature, slice_id = slice_match.groups()
        if feature not in planned:
            return "feature_not_declared_in_planning"
        slice_plan = artifacts.get(
            f"slice-plan-feature-{feature.removeprefix('F-')}.md"
        )
        if slice_plan is None:
            return "slice_plan_missing"
        slice_ids = cls._identifier_list(
            slice_plan["metadata"].get("Slice IDs", ""),
            cls._SLICE,
        )
        if slice_ids is None or slice_id not in slice_ids:
            return "slice_not_declared_in_slice_plan"
        return None

    @classmethod
    def _slice_contradiction(cls, artifacts, slices_by_feature):
        planning = artifacts["planning.md"]
        for feature, slices in slices_by_feature.items():
            if slices is None:
                slice_plan = artifacts.get(
                    f"slice-plan-feature-{feature.removeprefix('F-')}.md"
                )
                return cls._contradiction(
                    "invalid_slice_order",
                    planning,
                    slice_plan,
                )
        for artifact in artifacts.values():
            metadata = artifact["metadata"]
            slice_id = metadata.get("Slice ID")
            if slice_id is None:
                continue
            feature = metadata["Feature ID"]
            if slice_id not in slices_by_feature.get(feature, ()):
                slice_plan = artifacts.get(
                    f"slice-plan-feature-{feature.removeprefix('F-')}.md"
                )
                return cls._contradiction(
                    "artifact_slice_not_declared_in_slice_plan",
                    planning,
                    slice_plan,
                    artifact,
                )
        return None

    @classmethod
    def _contradiction(cls, code, *artifacts):
        return {
            "code": code,
            "artifacts": cls._terminal_evidence(*artifacts),
        }

    @classmethod
    def _scope_evidence(cls, scope, artifacts):
        slice_match = cls._SLICE_SCOPE.fullmatch(scope)
        if slice_match is None:
            return ()
        feature = slice_match.group(1)
        slice_plan = artifacts.get(
            f"slice-plan-feature-{feature.removeprefix('F-')}.md"
        )
        return (slice_plan,) if slice_plan is not None else ()

    @staticmethod
    def _terminal_evidence(*artifacts):
        evidence = {}
        for artifact in artifacts:
            if artifact is None:
                continue
            filename = artifact.get("filename")
            if filename is None:
                filename = artifact["path"].rsplit("/", 1)[-1]
            evidence[filename] = {
                "filename": filename,
                "version": artifact["version"],
            }
        return [evidence[name] for name in sorted(evidence)]

    @staticmethod
    def _reason_code(reason):
        if reason == "artifact_root_is_not_a_directory":
            return "artifact_root_invalid"
        if reason in {
            "non_empty_artifact_root_without_valid_planning",
            "planning_missing_from_active_graph",
        }:
            return "planning_missing"
        if reason == "empty_planning_has_downstream_artifacts":
            return "empty_project_contradiction"
        if reason in {
            "artifact_feature_not_declared_in_planning",
            "artifact_slice_not_declared_in_slice_plan",
        }:
            return "identifier_reference_invalid"
        if reason.startswith(("blocker_affected_scope_", "review_")):
            return "routing_scope_invalid"
        return "artifact_invalid"

    @classmethod
    def _matching_review(cls, artifacts, artifact_scope, tdd, solution, slice_plan):
        attempt = int(tdd["metadata"]["Attempt"])
        filename = f"review-feature-{artifact_scope}-attempt-{attempt:02d}.md"
        review = artifacts.get(filename)
        if review is None:
            return None
        metadata = review["metadata"]
        if (
            metadata["Solution Version"] != solution["version"]
            or metadata["Slice Plan Version"] != slice_plan["version"]
        ):
            return None
        return review

    @staticmethod
    def _current_tdd(tdd, solution, slice_plan):
        if tdd is None or tdd["status"] != "READY_FOR_REVIEW":
            return False
        metadata = tdd["metadata"]
        return (
            metadata["Solution Version"] == solution["version"]
            and metadata["Slice Plan Version"] == slice_plan["version"]
        )

    @staticmethod
    def _identifier_list(value, pattern):
        entries = value.split("; ")
        if not entries or any(pattern.fullmatch(entry) is None for entry in entries):
            return None
        if len(set(entries)) != len(entries):
            return None
        return entries

    @classmethod
    def _planning_features(cls, value):
        if value == cls._EMPTY_FEATURES:
            return []
        return cls._identifier_list(value, cls._FEATURE)

    @classmethod
    def _version_map(cls, value):
        entries = value.split("; ")
        parsed = {}
        for entry in entries:
            match = cls._VERSION_ENTRY.fullmatch(entry)
            if match is None or match.group(1) in parsed:
                return None
            parsed[match.group(1)] = match.group(2)
        return parsed

    @classmethod
    def _declared_positions(cls, artifacts, features):
        feature_positions = {
            feature: position
            for position, feature in enumerate(features)
        }
        slice_positions = {}
        for feature in features:
            slice_plan = artifacts.get(
                f"slice-plan-feature-{feature.removeprefix('F-')}.md"
            )
            if slice_plan is None:
                continue
            slice_ids = cls._identifier_list(
                slice_plan["metadata"].get("Slice IDs", ""),
                cls._SLICE,
            )
            if slice_ids is None:
                continue
            slice_positions[feature] = {
                slice_id: position
                for position, slice_id in enumerate(slice_ids)
            }
        return feature_positions, slice_positions

    @staticmethod
    def _planning_is_usable(planning, features):
        return planning["status"] == "READY" and features is not None

    @classmethod
    def _requirement_is_usable(
        cls,
        requirement,
        feature,
        planning,
        features,
    ):
        return (
            cls._planning_is_usable(planning, features)
            and feature in features
            and requirement is not None
            and requirement["status"] == "READY"
            and requirement["metadata"]["Feature ID"] == feature
            and requirement["metadata"]["Planning Version"] == planning["version"]
        )

    @classmethod
    def _current_requirement_versions(cls, artifacts, planning, features):
        versions = {}
        for feature in features:
            requirement = artifacts.get(
                f"requirement-feature-{feature.removeprefix('F-')}.md"
            )
            if not cls._requirement_is_usable(
                requirement,
                feature,
                planning,
                features,
            ):
                return None
            versions[feature] = requirement["version"]
        return versions

    @classmethod
    def _solution_is_usable(cls, solution, requirement_versions):
        return (
            solution is not None
            and solution["status"] == "READY"
            and cls._version_map(
                solution["metadata"].get("Based On Requirements", "")
            )
            == requirement_versions
        )

    @classmethod
    def _slice_plan_is_usable(
        cls,
        slice_plan,
        feature,
        solution,
        features,
    ):
        return (
            feature in features
            and solution is not None
            and slice_plan is not None
            and slice_plan["status"] == "READY"
            and slice_plan["metadata"]["Feature ID"] == feature
            and slice_plan["metadata"]["Based On Solution"] == solution["version"]
            and cls._identifier_list(
                slice_plan["metadata"].get("Slice IDs", ""),
                cls._SLICE,
            )
            is not None
        )

    @classmethod
    def _blocker_sort_key(
        cls,
        artifact,
        feature_positions,
        slice_positions,
    ):
        metadata = artifact["metadata"]
        owner = cls._OWNER_ORDER.index(metadata["Blocker Owner"])
        feature_position = -1
        slice_position = -1
        affected_scope = metadata["Affected Scope"]
        feature_match = cls._FEATURE_SCOPE.fullmatch(affected_scope)
        slice_match = cls._SLICE_SCOPE.fullmatch(affected_scope)
        if feature_match is not None:
            feature = feature_match.group(1)
            feature_position = feature_positions.get(
                feature,
                len(feature_positions),
            )
        elif slice_match is not None:
            feature, slice_id = slice_match.groups()
            feature_position = feature_positions.get(
                feature,
                len(feature_positions),
            )
            feature_slices = slice_positions.get(feature, {})
            slice_position = feature_slices.get(
                slice_id,
                len(feature_slices),
            )
        return (
            owner,
            feature_position,
            slice_position,
            artifact.get("path", ""),
            artifact["artifact_type"],
            artifact["version"],
        )

    @classmethod
    def _blocker_is_current(cls, artifact, artifacts, planning, features):
        metadata = artifact["metadata"]
        artifact_type = artifact["artifact_type"]
        if artifact_type == "Planning":
            return True
        if not cls._planning_is_usable(planning, features):
            return False
        if artifact_type == "Requirement":
            return (
                metadata["Feature ID"] in features
                and metadata["Planning Version"] == planning["version"]
            )

        requirement_versions = cls._current_requirement_versions(
            artifacts,
            planning,
            features,
        )
        if requirement_versions is None:
            return False
        if artifact_type == "Solution Plan":
            return (
                cls._version_map(metadata.get("Based On Requirements", ""))
                == requirement_versions
            )

        solution = artifacts.get("solution-plan.md")
        if not cls._solution_is_usable(solution, requirement_versions):
            return False
        if artifact_type == "Slice Plan":
            return (
                metadata["Feature ID"] in features
                and metadata["Based On Solution"] == solution["version"]
            )
        if artifact_type == "TDD Record":
            feature = metadata["Feature ID"]
            slice_id = metadata["Slice ID"]
            slice_plan = artifacts.get(
                f"slice-plan-feature-{feature.removeprefix('F-')}.md"
            )
            if not cls._slice_plan_is_usable(
                slice_plan,
                feature,
                solution,
                features,
            ):
                return False
            slice_ids = cls._identifier_list(
                slice_plan["metadata"].get("Slice IDs", ""),
                cls._SLICE,
            )
            return (
                slice_id in slice_ids
                and metadata["Solution Version"] == solution["version"]
                and metadata["Slice Plan Version"] == slice_plan["version"]
            )
        return False

    @staticmethod
    def _active(
        workflow,
        scope,
        rule,
        blocker_category=None,
        entry_mode=None,
    ):
        result = {
            "pipeline_status": "ACTIVE",
            "current_workflow": workflow,
            "target_scope": scope,
            "resolution_rule": rule,
        }
        if blocker_category is not None:
            result["blocker_category"] = blocker_category
        if entry_mode is not None:
            result["entry_mode"] = entry_mode
        return result

    @staticmethod
    def _terminal(status, rule, reason=None, terminal_evidence=None):
        result = {
            "pipeline_status": status,
            "current_workflow": None,
            "target_scope": "Project",
            "resolution_rule": rule,
        }
        if reason:
            result["reason"] = reason
            if status == "HALTED":
                result["reason_code"] = StateResolver._reason_code(reason)
        if terminal_evidence is not None:
            result["terminal_evidence"] = list(terminal_evidence)
        return result
