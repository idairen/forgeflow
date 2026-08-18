import json
import unittest
from pathlib import Path

from forgeflow.engine.artifact_parser import ArtifactParser
from forgeflow.engine.state_resolver import StateResolver


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {"plan", "grill", "solution", "slice", "tdd", "review"}


class RepositoryContractTests(unittest.TestCase):
    def test_repository_uses_segmented_public_layout(self):
        required_paths = {
            "src/forgeflow/__init__.py",
            "tests/unit/test_artifact_parser.py",
            "tests/integration/test_runner_protocol.py",
            "tests/contracts/test_repository_contracts.py",
            "tests/acceptance/ide/manage.py",
            "docs/guides/concept-and-architecture.md",
            "docs/testing/ide-test-plan.zh-CN.md",
            "docs/presentations/forgeflow-enterprise-roadshow.pdf",
            "ARCHITECTURE.zh-CN.md",
        }
        removed_paths = {
            "forgeflow",
            "tests/ide",
            "output",
            "docs/forgeflow-concept-and-architecture-guide.md",
            "docs/forgeflow-ide-test-plan.zh-CN.md",
        }

        for relative in required_paths:
            self.assertTrue((ROOT / relative).exists(), relative)
        for relative in removed_paths:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_json_documents_are_parseable(self):
        for relative in (
            "forgeflow.json",
            "package.json",
            ".forgeflow/forgeflow.schema.json",
        ):
            with self.subTest(path=relative):
                parsed = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)

    def test_workflow_and_adapter_sets_are_symmetric(self):
        workflows = {
            path.stem for path in (ROOT / ".forgeflow" / "workflow").glob("*.md")
        }
        self.assertEqual(workflows, WORKFLOWS)

        for adapter in ("codex", "copilot"):
            launchers = {
                path.name.removeprefix("forge-").removesuffix(".prompt.md")
                for path in (ROOT / ".forgeflow" / "adapter" / adapter).glob(
                    "forge-*.prompt.md"
                )
            }
            self.assertEqual(launchers, WORKFLOWS)

    def test_launchers_reference_authoritative_framework_files(self):
        required = {
            ".forgeflow/forgeflow.md",
            ".forgeflow/protocol/artifact.md",
            ".forgeflow/protocol/handoff.md",
        }
        for adapter in ("codex", "copilot"):
            for workflow in WORKFLOWS:
                path = (
                    ROOT
                    / ".forgeflow"
                    / "adapter"
                    / adapter
                    / f"forge-{workflow}.prompt.md"
                )
                content = path.read_text(encoding="utf-8")
                expected = required | {f".forgeflow/workflow/{workflow}.md"}
                with self.subTest(adapter=adapter, workflow=workflow):
                    for reference in expected:
                        self.assertIn(reference, content)

    def test_removed_protocol_files_do_not_return(self):
        protocol = ROOT / ".forgeflow" / "protocol"
        self.assertFalse((protocol / "compatibility.md").exists())
        self.assertFalse((protocol / "conformance.md").exists())
        self.assertFalse((protocol / "transition.md").exists())

    def test_npm_package_remains_installer_only(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertEqual(package["bin"], {"forgeflow": "npm/bin/forgeflow.js"})
        self.assertNotIn("src/forgeflow/engine", package["files"])
        self.assertNotIn("src/forgeflow/cli", package["files"])

    def test_sample_project_uses_current_protocol_without_framework_copy(self):
        sample = ROOT / "examples" / "sample-project"
        expected = sample / "expected-artifacts"

        self.assertFalse((sample / ".forgeflow").exists())
        self.assertEqual(
            {path.name for path in expected.glob("*.md")},
            {"planning.md", "requirement-feature-01.md"},
        )
        artifact_state = ArtifactParser.detect_artifact_state(expected)
        self.assertEqual(artifact_state["status"], "active")
        self.assertEqual(artifact_state["errors"], [])

        resolution = StateResolver.resolve(artifact_state)
        self.assertEqual(resolution["pipeline_status"], "ACTIVE")
        self.assertEqual(resolution["current_workflow"], "grill")
        self.assertEqual(resolution["target_scope"], "Feature: F-02")

    def test_architecture_declares_current_sources_comparison_and_boundaries(self):
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        chinese_architecture = (ROOT / "ARCHITECTURE.zh-CN.md").read_text(
            encoding="utf-8"
        )
        required_references = {
            "./.forgeflow/forgeflow.md",
            "./.forgeflow/protocol/artifact.md",
            "./.forgeflow/protocol/handoff.md",
            "https://github.com/github/spec-kit",
            "https://github.com/Fission-AI/OpenSpec",
            "https://github.com/bmad-code-org/BMAD-METHOD",
            "https://github.com/specdd/specdd",
            "https://github.com/specd-sdd/SpecD",
        }
        required_boundaries = {
            "Technical Preview",
            "A Handoff does not make an Artifact true",
            "There is currently no separate `update` command.",
            "does not currently ship or claim validated dedicated integrations",
            "real IDE acceptance",
        }

        for reference in required_references:
            self.assertIn(reference, architecture)
            self.assertIn(reference, chinese_architecture)
        for boundary in required_boundaries:
            self.assertIn(boundary, architecture)

        chinese_boundaries = {
            "Technical Preview",
            "Handoff 不会让 Artifact 自动变为真实",
            "当前没有独立的 `update` 命令。",
            "不提供、也不宣称已经验证它们的专用集成",
            "真实 IDE Acceptance",
        }
        for boundary in chinese_boundaries:
            self.assertIn(boundary, chinese_architecture)

        expected_sections = [str(number) for number in range(1, 19)]
        english_sections = [
            line.split(".", 1)[0].removeprefix("## ")
            for line in architecture.splitlines()
            if line.startswith("## ") and line.removeprefix("## ")[:1].isdigit()
        ]
        chinese_sections = [
            line.split(".", 1)[0].removeprefix("## ")
            for line in chinese_architecture.splitlines()
            if line.startswith("## ") and line.removeprefix("## ")[:1].isdigit()
        ]
        self.assertEqual(english_sections, expected_sections)
        self.assertEqual(chinese_sections, expected_sections)


if __name__ == "__main__":
    unittest.main()
