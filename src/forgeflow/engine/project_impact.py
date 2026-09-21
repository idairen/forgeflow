"""Derived dependency and impact analysis for ForgeFlow project knowledge."""
import copy
import re


class ProjectImpactAnalyzer:
    """Build and query a non-authoritative impact model from Solution metadata."""

    _FEATURE = re.compile(r"F-(?:0[1-9]|[1-9][0-9]+)")
    _COMPONENT = re.compile(r"SC-(?:0[1-9]|[1-9][0-9]+)")
    _FIELDS = (
        "Shared Component IDs",
        "Feature Dependencies",
        "Feature Shared Components",
        "Feature Decision References",
        "Cross-Feature Impact",
    )

    @classmethod
    def build(cls, feature_ids, solution_metadata):
        base = {
            "schema_version": 1,
            "authority": "derived_non_authoritative",
        }
        if not solution_metadata:
            return {**base, "status": "unavailable", "reason": "no_current_solution"}
        present = [field for field in cls._FIELDS if field in solution_metadata]
        if not present:
            return {
                **base,
                "status": "unavailable",
                "reason": "solution_without_structured_impact_metadata",
            }
        if len(present) != len(cls._FIELDS):
            return {
                **base,
                "status": "unavailable",
                "reason": "invalid_structured_impact_metadata",
            }

        dependencies = cls._relation_map(solution_metadata["Feature Dependencies"])
        feature_components = cls._relation_map(
            solution_metadata["Feature Shared Components"]
        )
        feature_decisions = cls._relation_map(
            solution_metadata["Feature Decision References"]
        )
        current_impact = {
            feature_id: values[0]
            for feature_id, values in cls._relation_map(
                solution_metadata["Cross-Feature Impact"]
            ).items()
        }
        reverse_dependencies = {feature_id: [] for feature_id in feature_ids}
        for source in feature_ids:
            for target in dependencies.get(source, []):
                reverse_dependencies.setdefault(target, []).append(source)

        component_ids = cls._identifier_list(solution_metadata["Shared Component IDs"])
        component_features = {component_id: [] for component_id in component_ids}
        for feature_id in feature_ids:
            for component_id in feature_components.get(feature_id, []):
                component_features.setdefault(component_id, []).append(feature_id)

        return {
            **base,
            "status": "available",
            "feature_order": list(feature_ids),
            "dependencies": dependencies,
            "reverse_dependencies": reverse_dependencies,
            "feature_components": feature_components,
            "component_features": component_features,
            "feature_decisions": feature_decisions,
            "current_change_impact": current_impact,
        }

    @classmethod
    def select(cls, model, feature_id=None, component_id=None):
        if feature_id is not None and component_id is not None:
            raise ValueError("--impact and --component cannot be combined")
        selected = copy.deepcopy(model)
        if feature_id is None and component_id is None:
            return selected
        if model.get("status") != "available":
            raise ValueError(
                "Project impact model is unavailable: "
                + model.get("reason", "unknown_reason")
            )

        if feature_id is not None:
            if cls._FEATURE.fullmatch(feature_id) is None:
                raise ValueError("--impact must use F-XX")
            if feature_id not in model["feature_order"]:
                raise ValueError(f"Feature is not active: {feature_id}")
            direct = model["reverse_dependencies"].get(feature_id, [])
            transitive = cls._transitive_dependents(model, feature_id)
            affected = [
                candidate
                for candidate in model["feature_order"]
                if candidate == feature_id or candidate in transitive
            ]
            components = model["feature_components"].get(feature_id, [])
            component_peers = [
                candidate
                for candidate in model["feature_order"]
                if candidate != feature_id
                and any(
                    candidate in model["component_features"].get(component_id, [])
                    for component_id in components
                )
            ]
            selected["query"] = {
                "type": "feature_impact",
                "feature_id": feature_id,
                "depends_on": model["dependencies"].get(feature_id, []),
                "direct_dependents": direct,
                "transitive_dependents": [
                    candidate
                    for candidate in model["feature_order"]
                    if candidate in transitive and candidate not in direct
                ],
                "affected_features": affected,
                "shared_components": components,
                "component_peers": component_peers,
                "decision_references": model["feature_decisions"].get(
                    feature_id, []
                ),
                "current_change_classification": model[
                    "current_change_impact"
                ].get(feature_id),
            }
            return selected

        if cls._COMPONENT.fullmatch(component_id) is None:
            raise ValueError("--component must use SC-XX")
        if component_id not in model["component_features"]:
            raise ValueError(f"Shared component is not active: {component_id}")
        selected["query"] = {
            "type": "shared_component",
            "component_id": component_id,
            "features": model["component_features"][component_id],
        }
        return selected

    @staticmethod
    def _identifier_list(value):
        return [] if not value or value == "NONE" else value.split("; ")

    @staticmethod
    def _relation_map(value):
        result = {}
        for entry in value.split("; "):
            source, targets_value = entry.split(" = ", 1)
            result[source] = (
                [] if targets_value == "NONE" else targets_value.split(", ")
            )
        return result

    @staticmethod
    def _transitive_dependents(model, feature_id):
        pending = list(model["reverse_dependencies"].get(feature_id, []))
        visited = set()
        while pending:
            candidate = pending.pop(0)
            if candidate in visited:
                continue
            visited.add(candidate)
            pending.extend(model["reverse_dependencies"].get(candidate, []))
        return visited
