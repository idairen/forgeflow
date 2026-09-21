"""Derived, non-authoritative ForgeFlow project knowledge views."""
import copy
import pathlib
import re

from .artifact_parser import ArtifactParser
from .project_impact import ProjectImpactAnalyzer


class ProjectKnowledgeBuilder:
    """Build and render a queryable projection over ForgeFlow evidence."""

    _FEATURE = re.compile(r"F-(?:0[1-9]|[1-9][0-9]+)")
    _SLICE_SCOPE = re.compile(r"(F-(?:0[1-9]|[1-9][0-9]+))/(S-(?:0[1-9]|[1-9][0-9]+))")
    _HISTORICAL_CONTRACTS = (
        (re.compile(r"planning-v(\d+\.\d+)\.md"), "planning"),
        (re.compile(r"solution-plan-v(\d+\.\d+)\.md"), "solution"),
    )

    @classmethod
    def build(cls, artifact_state, reports_dir=None, include_history=False):
        artifact_root = pathlib.Path(artifact_state.get("root", ""))
        graph_is_invalid = artifact_state.get("status") == "invalid"
        artifacts = artifact_state.get("artifacts", {})
        history = cls._knowledge_history(artifact_root, reports_dir) if include_history else {
            "artifact_history": [], "supplemental_reports": [], "report_history": [], "rotated_evidence_roots": []}
        timeline, warnings = cls._contract_timeline(
            artifact_root,
            {} if graph_is_invalid else artifacts,
            include_history=include_history,
        )
        base = {
            "schema_version": 1,
            "authority": "derived_non_authoritative",
            "timeline": timeline,
            "history": history,
            "warnings": warnings,
        }
        if graph_is_invalid:
            return {
                **base,
                "status": "unavailable",
                "reason": "invalid_artifact_graph",
                "impact": {
                    "schema_version": 1,
                    "authority": "derived_non_authoritative",
                    "status": "unavailable",
                    "reason": "invalid_artifact_graph",
                },
            }

        planning = artifacts.get("planning.md")
        if planning is None:
            return {
                **base,
                "status": "empty",
                "planning": None,
                "solution": None,
                "features": [],
                "impact": ProjectImpactAnalyzer.build([], None),
            }

        planning_metadata = planning["metadata"]
        feature_ids = cls._identifier_values(planning_metadata.get("Feature IDs"))
        contract_versions = cls._version_map_values(
            planning_metadata.get("Feature Contract Versions")
        )
        solution = artifacts.get("solution-plan.md")
        solution_metadata = solution["metadata"] if solution else {}
        impact = ProjectImpactAnalyzer.build(feature_ids, solution_metadata)
        requirement_versions = cls._version_map_values(
            solution_metadata.get("Based On Requirements")
        )
        engineering_versions = cls._version_map_values(
            solution_metadata.get("Feature Engineering Versions")
        )

        features = []
        for feature_id in feature_ids:
            feature_number = feature_id.removeprefix("F-")
            requirement = artifacts.get(f"requirement-feature-{feature_number}.md")
            slice_plan = artifacts.get(f"slice-plan-feature-{feature_number}.md")
            slice_ids = (
                cls._identifier_values(slice_plan["metadata"].get("Slice IDs"))
                if slice_plan
                else []
            )
            features.append(
                {
                    "feature_id": feature_id,
                    "contract_version": contract_versions.get(feature_id),
                    "lane": cls._artifact_reference(artifacts.get(f"lane-feature-{feature_number}.md"), extra_fields=("Attempt", "Feature Contract Version", "Dependency Requirement Versions", "Claim Evidence")),
                    "requirement": cls._artifact_reference(
                        requirement,
                        extra_fields=("Planning Version",),
                    ),
                    "solution_requirement_version": requirement_versions.get(
                        feature_id
                    ),
                    "engineering_version": engineering_versions.get(feature_id),
                    "slice_plan": cls._artifact_reference(
                        slice_plan,
                        extra_fields=("Based On Solution", "Slice IDs"),
                    ),
                    "slices": [
                        cls._slice_knowledge(artifacts, feature_id, slice_id)
                        for slice_id in slice_ids
                    ],
                }
            )

        return {
            **base,
            "status": "available",
            "planning": cls._artifact_reference(
                planning,
                extra_fields=("Change Set", "Feature IDs"),
            ),
            "solution": cls._artifact_reference(
                solution,
                extra_fields=(
                    "Based On Requirements",
                    "Feature Engineering Versions",
                ),
            ),
            "features": features,
            "impact": impact,
        }

    @classmethod
    def select(
        cls,
        view,
        feature_id=None,
        slice_scope=None,
        include_history=False,
        impact_feature=None,
        component_id=None,
    ):
        selected = copy.deepcopy(view)
        if (
            impact_feature is not None
            and (feature_id is not None or slice_scope is not None or component_id is not None)
        ) or (
            component_id is not None
            and (feature_id is not None or slice_scope is not None)
        ):
            raise ValueError(
                "--feature, --slice, --impact, and --component are mutually exclusive"
            )
        if slice_scope is not None:
            match = cls._SLICE_SCOPE.fullmatch(slice_scope)
            if match is None:
                raise ValueError("--slice must use F-XX/S-XX")
            slice_feature, slice_id = match.groups()
            if feature_id is not None and feature_id != slice_feature:
                raise ValueError("--feature does not match --slice")
            feature_id = slice_feature
        elif feature_id is not None and cls._FEATURE.fullmatch(feature_id) is None:
            raise ValueError("--feature must use F-XX")

        if feature_id is not None:
            features = [
                feature
                for feature in selected.get("features", [])
                if feature["feature_id"] == feature_id
            ]
            if not features:
                raise ValueError(f"Feature is not active: {feature_id}")
            selected["features"] = features
        if slice_scope is not None:
            slices = [
                item
                for item in selected["features"][0]["slices"]
                if item["slice_id"] == slice_id
            ]
            if not slices:
                raise ValueError(f"Slice is not active: {slice_scope}")
            selected["features"][0]["slices"] = slices

        selected["impact"] = ProjectImpactAnalyzer.select(
            selected.get(
                "impact",
                {
                    "schema_version": 1,
                    "authority": "derived_non_authoritative",
                    "status": "unavailable",
                    "reason": "impact_model_not_present",
                },
            ),
            feature_id=impact_feature,
            component_id=component_id,
        )

        if not include_history:
            selected.pop("history", None)
            selected["timeline"] = {
                key: [entry for entry in entries if entry["source"] == "current"]
                for key, entries in selected.get("timeline", {}).items()
            }
        return selected

    @classmethod
    def render_markdown(cls, view):
        lines = [
            "# ForgeFlow Project Knowledge",
            "",
            f"- Status: `{view.get('status', 'unknown')}`",
            f"- Authority: `{view.get('authority', 'unknown')}`",
        ]
        if view.get("reason"):
            lines.append(f"- Reason: `{view['reason']}`")
        planning = view.get("planning")
        solution = view.get("solution")
        lines.extend(["", "## Active Baseline", ""])
        lines.append(cls._reference_line("Planning", planning))
        lines.append(cls._reference_line("Solution", solution))

        for feature in view.get("features", []):
            lines.extend(
                [
                    "",
                    f"## {feature['feature_id']}",
                    "",
                    f"- Feature Contract Version: `{feature.get('contract_version') or 'NONE'}`",
                    cls._reference_line("Requirement", feature.get("requirement")),
                    f"- Feature Engineering Version: `{feature.get('engineering_version') or 'NONE'}`",
                    cls._reference_line("Slice Plan", feature.get("slice_plan")),
                ]
            )
            for slice_item in feature.get("slices", []):
                lines.extend(
                    [
                        "",
                        f"### {feature['feature_id']}/{slice_item['slice_id']}",
                        "",
                        cls._reference_line("Implement", slice_item.get("implement")),
                    ]
                )
                for review in slice_item.get("reviews", []):
                    lines.append(cls._reference_line("Review", review))

        impact = view.get("impact")
        if impact is not None:
            lines.extend(
                [
                    "",
                    "## Project Impact View",
                    "",
                    f"- Status: `{impact.get('status', 'unknown')}`",
                ]
            )
            if impact.get("reason"):
                lines.append(f"- Reason: `{impact['reason']}`")
            query = impact.get("query")
            if query and query["type"] == "feature_impact":
                lines.extend(
                    [
                        f"- Feature: `{query['feature_id']}`",
                        cls._list_line("Depends On", query["depends_on"]),
                        cls._list_line(
                            "Direct Dependents", query["direct_dependents"]
                        ),
                        cls._list_line(
                            "Transitive Dependents",
                            query["transitive_dependents"],
                        ),
                        cls._list_line(
                            "Affected Features", query["affected_features"]
                        ),
                        cls._list_line(
                            "Shared Components", query["shared_components"]
                        ),
                        cls._list_line("Component Peers", query["component_peers"]),
                        cls._list_line(
                            "Decision References", query["decision_references"]
                        ),
                        "- Current Change Classification: "
                        f"`{query.get('current_change_classification') or 'NONE'}`",
                    ]
                )
            elif query and query["type"] == "shared_component":
                lines.extend(
                    [
                        f"- Shared Component: `{query['component_id']}`",
                        cls._list_line("Features", query["features"]),
                    ]
                )

        timeline = view.get("timeline", {})
        if any(timeline.values()):
            lines.extend(["", "## Contract Timeline", ""])
            for kind, entries in timeline.items():
                lines.append(f"### {kind.title()}")
                for entry in entries:
                    summary = (
                        f" — {entry['summary']}" if entry.get("summary") else ""
                    )
                    lines.append(
                        f"- `{entry['version']}` ({entry['source']}, "
                        f"`{entry['path']}`){summary}"
                    )
                if not entries:
                    lines.append("- `NONE`")
                lines.append("")

        if "history" in view:
            lines.extend(["", "## History Index", ""])
            for key, paths in view["history"].items():
                lines.append(f"### {key.replace('_', ' ').title()}")
                lines.extend(f"- `{path}`" for path in paths)
                if not paths:
                    lines.append("- `NONE`")
                lines.append("")
        if view.get("warnings"):
            lines.extend(["## Warnings", ""])
            lines.extend(f"- {warning}" for warning in view["warnings"])
        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _reference_line(label, reference):
        if reference is None:
            return f"- {label}: `NONE`"
        suffix = ""
        if reference.get("Attempt"):
            suffix += f", attempt {reference['Attempt']}"
        if reference.get("Decision"):
            suffix += f", {reference['Decision']}"
        return (
            f"- {label}: `{reference['filename']} = {reference['version']}` "
            f"({reference['status']}{suffix})"
        )

    @staticmethod
    def _list_line(label, values):
        rendered = ", ".join(f"`{value}`" for value in values) or "`NONE`"
        return f"- {label}: {rendered}"

    @classmethod
    def _slice_knowledge(cls, artifacts, feature_id, slice_id):
        feature_number = feature_id.removeprefix("F-")
        slice_number = slice_id.removeprefix("S-")
        implement = artifacts.get(f"implement-feature-{feature_number}-slice-{slice_number}.md")
        review_prefix = f"review-feature-{feature_number}-slice-{slice_number}-attempt-"
        reviews = sorted(
            (
                artifact
                for filename, artifact in artifacts.items()
                if filename.startswith(review_prefix)
            ),
            key=lambda artifact: int(artifact["metadata"]["Attempt"]),
        )
        return {
            "slice_id": slice_id,
            "implement": cls._artifact_reference(
                implement,
                extra_fields=("Attempt", "Solution Version", "Slice Plan Version"),
            ),
            "reviews": [
                cls._artifact_reference(
                    review,
                    extra_fields=(
                        "Attempt",
                        "Decision",
                        "Solution Version",
                        "Slice Plan Version",
                    ),
                )
                for review in reviews
            ],
        }

    @staticmethod
    def _artifact_reference(artifact, extra_fields=()):
        if artifact is None:
            return None
        reference = {
            "filename": artifact["filename"],
            "version": artifact["version"],
            "status": artifact["status"],
        }
        for field in extra_fields:
            value = artifact["metadata"].get(field)
            if value is not None:
                reference[field] = value
        return reference

    @staticmethod
    def _identifier_values(value):
        if not value or value == "NONE":
            return []
        return value.split("; ")

    @staticmethod
    def _version_map_values(value):
        if not value or value == "NONE":
            return {}
        return dict(entry.split(" = ", 1) for entry in value.split("; "))

    @classmethod
    def _knowledge_history(cls, artifact_root, reports_dir):
        reports_root = pathlib.Path(reports_dir) if reports_dir else None
        return {
            "artifact_history": cls._relative_files(artifact_root / "history"),
            "supplemental_reports": cls._relative_files(
                reports_root,
                excluded_top_level={"history"},
            ),
            "report_history": cls._relative_files(
                reports_root / "history" if reports_root else None
            ),
            "rotated_evidence_roots": cls._rotated_evidence_roots(
                artifact_root,
                reports_root,
            ),
        }

    @classmethod
    def _contract_timeline(cls, artifact_root, artifacts, include_history=False):
        timeline = {"planning": [], "solution": []}
        warnings = []
        current = (
            ("planning", artifacts.get("planning.md"), "Change Set"),
            ("solution", artifacts.get("solution-plan.md"), None),
        )
        for kind, artifact, summary_field in current:
            if artifact is None:
                continue
            entry = {
                "version": artifact["version"],
                "source": "current",
                "path": artifact["filename"],
            }
            if summary_field and artifact["metadata"].get(summary_field):
                entry["summary"] = artifact["metadata"][summary_field]
            timeline[kind].append(entry)

        history_root = artifact_root / "history"
        if include_history and history_root.is_dir() and not history_root.is_symlink():
            for path in sorted(history_root.rglob("*.md")):
                if not path.is_file() or path.is_symlink():
                    continue
                for pattern, kind in cls._HISTORICAL_CONTRACTS:
                    match = pattern.fullmatch(path.name)
                    if match is None:
                        continue
                    try:
                        text = path.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        warnings.append(f"unreadable history: {path.name}")
                        break
                    metadata, errors = ArtifactParser._parse_metadata(text)
                    if errors or metadata.get("Version") != match.group(1):
                        warnings.append(f"invalid history metadata: {path.name}")
                        break
                    entry = {
                        "version": match.group(1),
                        "source": "history",
                        "path": path.relative_to(artifact_root).as_posix(),
                    }
                    if kind == "planning" and metadata.get("Change Set"):
                        entry["summary"] = metadata["Change Set"]
                    timeline[kind].append(entry)
                    break
        for entries in timeline.values():
            entries.sort(
                key=lambda entry: tuple(int(part) for part in entry["version"].split("."))
            )
        return timeline, warnings

    @staticmethod
    def _relative_files(root, excluded_top_level=None):
        if root is None or not root.is_dir() or root.is_symlink():
            return []
        excluded = excluded_top_level or set()
        files = []
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if relative.parts and relative.parts[0] in excluded:
                continue
            if path.is_file() and not path.is_symlink():
                files.append(relative.as_posix())
        return sorted(files)

    @staticmethod
    def _rotated_evidence_roots(artifact_root, reports_root):
        roots = []
        for root in (artifact_root, reports_root):
            if root is None or not root.parent.is_dir():
                continue
            prefix = root.name + "."
            roots.extend(
                path.name
                for path in root.parent.iterdir()
                if path.name.startswith(prefix)
                and path.is_dir()
                and not path.is_symlink()
            )
        return sorted(set(roots))
