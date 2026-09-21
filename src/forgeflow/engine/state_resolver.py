"""Deterministic runtime projection from the active Artifact Graph."""
import re


class StateResolver:
    """Apply the ordered Transition Protocol rules and evidence projections."""

    _OWNER_ORDER = ("Plan", "Grill", "Solution", "Slice", "Implement")
    _FEATURE = re.compile(r"F-(?:0[1-9]|[1-9][0-9]+)")
    _SLICE = re.compile(r"S-(?:0[1-9]|[1-9][0-9]+)")
    _FEATURE_SCOPE = re.compile(r"Feature: (F-(?:0[1-9]|[1-9][0-9]+))")
    _SLICE_SCOPE = re.compile(r"Slice: (F-(?:0[1-9]|[1-9][0-9]+))/(S-(?:0[1-9]|[1-9][0-9]+))")
    _VERSION_ENTRY = re.compile(r"(F-(?:0[1-9]|[1-9][0-9]+)) = (\d+\.\d+)")
    _EMPTY_FEATURES = "NONE"

    @classmethod
    def resolve(cls, artifact_state):
        result = cls._resolve(artifact_state)
        result["input_artifacts"] = cls.input_projection(artifact_state, result)
        return result

    @classmethod
    def _resolve(cls, artifact_state):
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

        slices = {f: cls._identifier_list(a["metadata"].get("Slice IDs", ""), cls._SLICE)
                  for f in features for a in [artifacts.get(f"slice-plan-feature-{f[2:]}.md")] if a}
        contradiction = cls._slice_contradiction(artifacts, slices)
        if contradiction:
            return cls._terminal("HALTED", "rule_2_graph_contradiction", contradiction["code"], contradiction["artifacts"])
        lane_state = cls._lanes(artifacts, planning, features)
        if lane_state.get("error"):
            return cls._terminal("HALTED", "rule_2_graph_contradiction", "artifact_invalid", cls._terminal_evidence(planning, lane_state["error"]))

        blocked = [
            artifact
            for artifact in artifacts.values()
            if artifact["status"] == "BLOCKED"
            and cls._blocker_is_current(artifact, artifacts, planning, features)
        ]
        blocked = [a for a in blocked if not (
            a["metadata"]["Blocker Category"] == "BUSINESS_GAP"
            and any(f != a["metadata"]["Affected Scope"].removeprefix("Feature: ")
                    and a["metadata"]["Affected Scope"].removeprefix("Feature: ") not in lane_state["closure"].get(f, ())
                    for f in lane_state["eligible"] + lane_state["progress_active"])
        )]
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
            result = cls._active(
                metadata["Blocker Owner"].lower(),
                metadata["Affected Scope"],
                "rule_3_persisted_blocker",
                blocker_category=metadata["Blocker Category"],
                entry_mode="recovery",
            )
            result["blocker_filename"] = blocker["filename"]
            return result

        if not cls._planning_is_usable(planning, features):
            return cls._active("plan", "Project", "rule_4_planning_not_ready")
        if not features:
            return cls._terminal("COMPLETE", "rule_11_project_complete")

        if lane_state["eligible"]:
            result = cls._active("grill", f"Feature: {lane_state['eligible'][0]}", "rule_5_requirement_required")
            result["eligible_features"] = lane_state["eligible"]
            return result
        if lane_state["active"]:
            return {"pipeline_status": "WAITING", "current_workflow": None,
                    "target_scope": "Project", "resolution_rule": "rule_5_join_pending",
                    "active_lanes": lane_state["active"]}

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
        if not cls._solution_is_usable(solution, requirements, features):
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

        # Rule 8 precedes Rules 9 and 10 across the complete delivery graph.
        for feature in features:
            sp = artifacts[f"slice-plan-feature-{feature[2:]}.md"]
            for sid in slices_by_feature[feature]:
                scope_id = f"{feature[2:]}-slice-{sid[2:]}"
                record = artifacts.get(f"implement-feature-{scope_id}.md")
                if not cls._current_implement(record, solution, sp, feature):
                    continue
                report = cls._matching_review(artifacts, scope_id, record, solution, sp, feature)
                if report and report["metadata"]["Decision"] == "FAIL":
                    result = cls._active(report["metadata"]["Return Workflow"].lower(), report["metadata"]["Return Scope"], "rule_8_review_failure", blocker_category="REVIEW_BLOCKER")
                    result["review_filename"] = report["filename"]
                    return result


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
                implement = artifacts.get(f"implement-feature-{artifact_scope}.md")
                if implement and implement.get("review_disposed"):
                    return cls._active("implement", scope, "rule_10_implement_required")
                if not cls._current_implement(implement, solution, slice_plan, feature):
                    return cls._active("implement", scope, "rule_10_implement_required")
                review = cls._matching_review(
                    artifacts,
                    artifact_scope,
                    implement,
                    solution,
                    slice_plan,
                    feature,
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
    def has_current_failed_review(cls, artifact_state):
        """Return whether any active Feature has a current FAIL Review."""
        if artifact_state.get("status") == "invalid":
            return False
        artifacts = artifact_state.get("artifacts", {})
        planning = artifacts.get("planning.md")
        if planning is None:
            return False
        features = cls._planning_features(
            planning["metadata"].get("Feature IDs", "")
        )
        if not cls._planning_is_usable(planning, features) or not features:
            return False
        requirement_versions = cls._current_requirement_versions(
            artifacts,
            planning,
            features,
        )
        if requirement_versions is None:
            return False
        solution = artifacts.get("solution-plan.md")
        if not cls._solution_is_usable(
            solution,
            requirement_versions,
            features,
        ):
            return False

        for feature in features:
            slice_plan = artifacts.get(
                f"slice-plan-feature-{feature.removeprefix('F-')}.md"
            )
            if not cls._slice_plan_is_usable(
                slice_plan,
                feature,
                solution,
                features,
            ):
                continue
            slice_ids = cls._identifier_list(
                slice_plan["metadata"].get("Slice IDs", ""),
                cls._SLICE,
            )
            for slice_id in slice_ids:
                artifact_scope = (
                    f"{feature.removeprefix('F-')}-slice-"
                    f"{slice_id.removeprefix('S-')}"
                )
                implement = artifacts.get(f"implement-feature-{artifact_scope}.md")
                if not cls._current_implement(implement, solution, slice_plan, feature):
                    continue
                review = cls._matching_review(
                    artifacts,
                    artifact_scope,
                    implement,
                    solution,
                    slice_plan,
                    feature,
                )
                if review is not None and review["metadata"]["Decision"] == "FAIL":
                    return True
        return False

    @classmethod
    def _lanes(cls, artifacts, planning, features):
        dependencies = planning.get("dependencies", {f: [] for f in features})
        closure = {}
        for feature in features:
            seen, pending = set(), list(dependencies.get(feature, []))
            while pending:
                item = pending.pop()
                if item == feature or item not in features:
                    return {"error": planning}
                if item not in seen:
                    seen.add(item)
                    pending.extend(dependencies.get(item, []))
            closure[feature] = [f for f in features if f in seen]
        usable = {f: cls._requirement_is_usable(artifacts.get(f"requirement-feature-{f[2:]}.md"), f, planning, features) for f in features}
        blocked = set()
        for artifact in artifacts.values():
            if artifact["status"] == "BLOCKED" and artifact["metadata"].get("Blocker Category") == "BUSINESS_GAP" and cls._blocker_is_current(artifact, artifacts, planning, features):
                blocked.add(artifact["metadata"]["Affected Scope"].removeprefix("Feature: "))
        active, complete = [], []
        for feature in features:
            lane = artifacts.get(f"lane-feature-{feature[2:]}.md")
            if lane is None:
                continue
            metadata = lane["metadata"]
            expected = {f: artifacts[f"requirement-feature-{f[2:]}.md"]["version"] for f in closure[feature] if usable[f]}
            value = metadata.get("Dependency Requirement Versions", "")
            actual = {} if value == "NONE" else cls._version_map(value)
            current = (metadata.get("Feature Contract Version") == cls._feature_contract_version(planning, feature)
                       and all(usable[f] for f in closure[feature]) and actual == expected
                       and list(actual or {}) == list(expected))
            if lane["status"] == "ACTIVE":
                if not current or usable[feature]:
                    return {"error": lane}
                active.append(feature)
            elif current and not usable[feature]:
                return {"error": lane}
            elif current:
                complete.append(feature)
        eligible = [f for f in features if planning["status"] == "READY" and not usable[f]
                    and f not in active and all(usable[d] for d in closure[f])
                    and not ({f, *closure[f]} & blocked)]
        progress_active = [f for f in active if not ({f, *closure[f]} & blocked)]
        return {"eligible": eligible, "active": active, "complete": complete, "progress_active": progress_active, "closure": closure}

    @classmethod
    def grill_entry(cls, state, feature, confirm_inactive=False):
        """Validate an explicit Lane or interrupted/blocker Recovery request."""
        result = cls.resolve(state)
        if result["pipeline_status"] == "HALTED" or cls._FEATURE.fullmatch(feature) is None:
            raise ValueError("Grill entry requires a valid graph and canonical Feature")
        artifacts = state["artifacts"]
        planning = artifacts.get("planning.md")
        features = cls._planning_features(planning["metadata"].get("Feature IDs", "")) if planning else []
        if not planning or planning["status"] != "READY" or feature not in features:
            raise ValueError("Grill entry requires a declared Feature and READY Planning")
        lanes = cls._lanes(artifacts, planning, features)
        blockers = [a for a in artifacts.values() if a["status"] == "BLOCKED" and cls._blocker_is_current(a, artifacts, planning, features)]
        project_blocker = any(a["metadata"]["Affected Scope"] == "Project" for a in blockers)
        lane = artifacts.get(f"lane-feature-{feature[2:]}.md")
        active = lane and lane["status"] == "ACTIVE"
        if active and not confirm_inactive:
            raise ValueError("explicit confirmation of this Lane execution's inactivity is required")
        scoped_blockers = [a for a in blockers if a["metadata"]["Affected Scope"] == f"Feature: {feature}"]
        own_business = [a for a in scoped_blockers if a["metadata"]["Blocker Category"] == "BUSINESS_GAP"]
        dependency_blocker = any(a["metadata"]["Affected Scope"] in {f"Feature: {f}" for f in lanes["closure"][feature]} for a in blockers)
        release_only = bool(project_blocker and active)
        if dependency_blocker or (project_blocker and not release_only):
            raise ValueError("an upstream blocker must be handled first")
        if not active and not own_business and feature not in lanes["eligible"]:
            raise ValueError("Feature is not eligible for Lane Entry")
        if active and not release_only and scoped_blockers and not own_business:
            raise ValueError("exact blocker recovery is required")
        # _lanes already checked frozen dependency versions and no usable target Requirement.
        if active and not all(cls._requirement_is_usable(artifacts.get(f"requirement-feature-{f[2:]}.md"), f, planning, features) for f in lanes["closure"][feature]):
            raise ValueError("Lane dependencies are not usable")
        entry = cls._active("grill", f"Feature: {feature}", "rule_3_persisted_blocker" if own_business else "interrupted_lane_recovery" if active else "rule_5_requirement_required", entry_mode="recovery" if active or own_business else "lane")
        if own_business:
            entry.update(blocker_category="BUSINESS_GAP", blocker_filename=sorted(own_business, key=lambda a: a["filename"])[0]["filename"])
        if active:
            entry["confirmed_inactive_claim"] = {"filename": lane["filename"], "version": lane["version"], "attempt": lane["metadata"]["Attempt"]}
        entry["release_only"] = release_only
        entry["input_artifacts"] = []
        return entry

    @classmethod
    def input_projection(cls, state, resolution):
        """Exact ordered Transition input evidence, independent of renderer."""
        if resolution["pipeline_status"] == "HALTED":
            return resolution.get("terminal_evidence", [])
        artifacts = state.get("artifacts", {})
        planning = artifacts.get("planning.md")
        if not planning or resolution.get("resolution_rule") in {"rule_1_bootstrap", "rule_5_join_pending"}:
            return []
        features = cls._planning_features(planning["metadata"].get("Feature IDs", "")) or []
        names = ["planning.md"]
        rule = resolution["resolution_rule"]
        scope = resolution["target_scope"]
        if rule == "rule_4_planning_not_ready" or not features:
            pass
        elif rule == "rule_5_requirement_required":
            f = scope.removeprefix("Feature: ")
            lane = cls._lanes(artifacts, planning, features)
            names += [f"requirement-feature-{d[2:]}.md" for d in lane["closure"][f]]
            names += [f"lane-feature-{f[2:]}.md", f"requirement-feature-{f[2:]}.md"]
        elif rule == "rule_3_persisted_blocker":
            selected = artifacts.get(resolution.get("blocker_filename"))
            if not selected:
                return []
            kind = selected["artifact_type"]
            f = selected["metadata"].get("Feature ID", "")
            if kind == "Requirement":
                names += [f"lane-feature-{f[2:]}.md"]
            elif kind not in {"Planning", "Requirement"}:
                names += [f"requirement-feature-{d[2:]}.md" for d in features]
                if kind != "Solution Plan":
                    names += ["solution-plan.md"]
                if kind == "Implement Record":
                    names += [f"slice-plan-feature-{f[2:]}.md"]
            names += [selected["filename"]]
        else:
            names += [f"requirement-feature-{f[2:]}.md" for f in features]
            if rule == "rule_6_solution_required":
                names += [f"lane-feature-{f[2:]}.md" for f in cls._lanes(artifacts, planning, features)["complete"]]
                names += ["solution-plan.md"]
            else:
                names += ["solution-plan.md"]
                for f in features:
                    names.append(f"slice-plan-feature-{f[2:]}.md")
                    if rule == "rule_7_slice_plan_required" and scope == f"Feature: {f}":
                        break
                if rule == "rule_8_review_failure":
                    review = artifacts.get(resolution.get("review_filename"))
                    if review:
                        m = review["metadata"]
                        names += [f"implement-feature-{m['Feature ID'][2:]}-slice-{m['Slice ID'][2:]}.md", review["filename"]]
                elif rule in {"rule_9_review_required", "rule_10_implement_required", "rule_11_project_complete"}:
                    done = False
                    for f in features:
                        sp = artifacts.get(f"slice-plan-feature-{f[2:]}.md")
                        for sid in (sp["metadata"].get("Slice IDs", "").split("; ") if sp else []):
                            name = f"implement-feature-{f[2:]}-slice-{sid[2:]}.md"
                            names.append(name)
                            if scope == f"Slice: {f}/{sid}":
                                done = True
                                break
                            record = artifacts.get(name)
                            if record:
                                names.append(f"review-feature-{f[2:]}-slice-{sid[2:]}-attempt-{int(record['metadata']['Attempt']):02d}.md")
                        if done:
                            break
        return [{"filename": n, "version": artifacts[n]["version"]}
                for n in dict.fromkeys(names) if n in artifacts]

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
    def _matching_review(
        cls,
        artifacts,
        artifact_scope,
        implement,
        solution,
        slice_plan,
        feature,
    ):
        attempt = int(implement["metadata"]["Attempt"])
        filename = f"review-feature-{artifact_scope}-attempt-{attempt:02d}.md"
        review = artifacts.get(filename)
        if review is None:
            return None
        metadata = review["metadata"]
        engineering_version = cls._feature_engineering_version(solution, feature)
        if (
            metadata["Solution Version"] != engineering_version
            or metadata["Slice Plan Version"] != slice_plan["version"]
        ):
            return None
        return review

    @classmethod
    def _current_implement(cls, implement, solution, slice_plan, feature):
        if implement is None or implement["status"] != "READY_FOR_REVIEW":
            return False
        metadata = implement["metadata"]
        return (
            metadata["Solution Version"]
            == cls._feature_engineering_version(solution, feature)
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

    @classmethod
    def _planning_is_usable(cls, planning, features):
        if planning["status"] != "READY" or features is None:
            return False
        versions = planning["metadata"].get("Feature Contract Versions", "")
        if not features:
            return versions == cls._EMPTY_FEATURES
        parsed = cls._version_map(versions)
        return parsed is not None and list(parsed) == features

    @classmethod
    def _feature_contract_version(cls, planning, feature):
        versions = cls._version_map(
            planning["metadata"].get("Feature Contract Versions", "")
        )
        return versions.get(feature) if versions is not None else None

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
            and requirement["metadata"]["Planning Version"]
            == cls._feature_contract_version(planning, feature)
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
    def _solution_is_usable(cls, solution, requirement_versions, features):
        if solution is None or solution["status"] != "READY":
            return False
        based_on = cls._version_map(
            solution["metadata"].get("Based On Requirements", "")
        )
        engineering_versions = cls._version_map(
            solution["metadata"].get("Feature Engineering Versions", "")
        )
        return (
            based_on == requirement_versions
            and engineering_versions is not None
            and list(engineering_versions) == features
        )

    @classmethod
    def _feature_engineering_version(cls, solution, feature):
        versions = cls._version_map(
            solution["metadata"].get("Feature Engineering Versions", "")
        )
        return versions.get(feature) if versions is not None else None

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
            and slice_plan.get("verification_actionable", False)
            and slice_plan["metadata"]["Feature ID"] == feature
            and slice_plan["metadata"]["Based On Solution"]
            == cls._feature_engineering_version(solution, feature)
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
            feature = metadata["Feature ID"]
            lane = artifacts.get(f"lane-feature-{feature[2:]}.md")
            if lane and lane["metadata"].get("Feature Contract Version") != metadata["Planning Version"]:
                return False
            return (
                feature in features
                and metadata["Planning Version"]
                == cls._feature_contract_version(planning, feature)
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
        if not cls._solution_is_usable(solution, requirement_versions, features):
            return False
        if artifact_type == "Slice Plan":
            feature = metadata["Feature ID"]
            return (
                feature in features
                and metadata["Based On Solution"]
                == cls._feature_engineering_version(solution, feature)
            )
        if artifact_type == "Implement Record":
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
                and metadata["Solution Version"]
                == cls._feature_engineering_version(solution, feature)
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
