import unittest

from forgeflow.engine.project_impact import ProjectImpactAnalyzer


def impact_model():
    return ProjectImpactAnalyzer.build(
        ["F-01", "F-02", "F-03", "F-04"],
        {
            "Shared Component IDs": "SC-01; SC-02",
            "Feature Dependencies": (
                "F-01 = F-02; F-02 = F-03; F-03 = NONE; F-04 = NONE"
            ),
            "Feature Shared Components": (
                "F-01 = SC-01; F-02 = SC-01; F-03 = SC-02; F-04 = NONE"
            ),
            "Feature Decision References": (
                "F-01 = ED-01; F-02 = ED-01, ED-02; "
                "F-03 = ED-02; F-04 = NONE"
            ),
            "Cross-Feature Impact": (
                "F-01 = INDIRECT; F-02 = DIRECT; "
                "F-03 = DIRECT; F-04 = UNAFFECTED"
            ),
        },
    )


class ProjectImpactAnalyzerTests(unittest.TestCase):
    def test_builds_forward_reverse_and_component_indexes(self):
        model = impact_model()

        self.assertEqual(model["status"], "available")
        self.assertEqual(model["dependencies"]["F-01"], ["F-02"])
        self.assertEqual(model["reverse_dependencies"]["F-03"], ["F-02"])
        self.assertEqual(model["component_features"]["SC-01"], ["F-01", "F-02"])

    def test_feature_query_preserves_order_and_separates_component_peers(self):
        selected = ProjectImpactAnalyzer.select(impact_model(), feature_id="F-03")
        query = selected["query"]

        self.assertEqual(query["direct_dependents"], ["F-02"])
        self.assertEqual(query["transitive_dependents"], ["F-01"])
        self.assertEqual(query["affected_features"], ["F-01", "F-02", "F-03"])
        self.assertEqual(query["component_peers"], [])

    def test_component_query_and_invalid_filters(self):
        selected = ProjectImpactAnalyzer.select(
            impact_model(), component_id="SC-01"
        )
        self.assertEqual(selected["query"]["features"], ["F-01", "F-02"])

        with self.assertRaisesRegex(ValueError, "F-XX"):
            ProjectImpactAnalyzer.select(impact_model(), feature_id="feature-1")
        with self.assertRaisesRegex(ValueError, "not active"):
            ProjectImpactAnalyzer.select(impact_model(), component_id="SC-99")

    def test_legacy_solution_has_explicitly_unavailable_impact(self):
        model = ProjectImpactAnalyzer.build(
            ["F-01"],
            {"Feature Engineering Versions": "F-01 = 1.0"},
        )

        self.assertEqual(model["status"], "unavailable")
        self.assertEqual(
            model["reason"],
            "solution_without_structured_impact_metadata",
        )
        with self.assertRaisesRegex(ValueError, "unavailable"):
            ProjectImpactAnalyzer.select(model, feature_id="F-01")


if __name__ == "__main__":
    unittest.main()
