import json
import re
import unittest
from pathlib import Path

from forgeflow.engine.artifact_parser import ArtifactParser
from forgeflow.engine.state_resolver import StateResolver


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = {"plan", "grill", "solution", "slice", "implement", "review"}


class RepositoryContractTests(unittest.TestCase):
    def test_repository_uses_segmented_public_layout(self):
        required_paths = {
            "src/forgeflow/__init__.py",
            "src/forgeflow/engine/project_impact.py",
            "tests/unit/test_artifact_parser.py",
            "tests/unit/test_project_knowledge.py",
            "tests/unit/test_project_impact.py",
            "tests/unit/test_ide_acceptance_manager.py",
            "tests/integration/test_runner_protocol.py",
            "tests/integration/test_cli_knowledge.py",
            "tests/contracts/test_repository_contracts.py",
            "tests/acceptance/ide/manage.py",
            "docs/guides/concept-and-architecture.md",
            "docs/testing/ide-test-plan.zh-CN.md",
            "docs/testing/cli-knowledge-test-plan.md",
            "docs/presentations/forgeflow-enterprise-roadshow.pdf",
            "docs/presentations/forgeflow-executive-architecture-brief.en.pdf",
            "docs/presentations/forgeflow-executive-architecture-brief.zh-CN.pdf",
            "docs/presentations/forgeflow-engineering-protocol.en.md",
            "docs/presentations/forgeflow-engineering-protocol.zh-CN.md",
            "scripts/build_executive_brief.py",
            "ARCHITECTURE.zh-CN.md",
            "CODE_OF_CONDUCT.md",
            "GOVERNANCE.md",
            "ROADMAP.md",
            "SUPPORT.md",
            "SECURITY.md",
            "CONTRIBUTING.md",
            ".github/CODEOWNERS",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/protocol_change.yml",
            ".github/dependabot.yml",
            "docs/maintainers/releasing.md",
        }
        removed_paths = {
            "forgeflow",
            "tests/ide",
            "docs/forgeflow-concept-and-architecture-guide.md",
            "docs/forgeflow-ide-test-plan.zh-CN.md",
            "output",
        }

        for relative in required_paths:
            self.assertTrue((ROOT / relative).exists(), relative)
        for relative in removed_paths:
            self.assertFalse((ROOT / relative).exists(), relative)

    def test_executive_briefs_are_bilingual_pdf_outputs(self):
        briefs = {
            "en": ROOT
            / "docs/presentations/forgeflow-executive-architecture-brief.en.pdf",
            "zh-CN": ROOT
            / "docs/presentations/forgeflow-executive-architecture-brief.zh-CN.pdf",
        }
        for locale, path in briefs.items():
            with self.subTest(locale=locale):
                self.assertGreater(path.stat().st_size, 100_000)
                self.assertEqual(path.read_bytes()[:5], b"%PDF-")

        generator = (ROOT / "scripts/build_executive_brief.py").read_text(
            encoding="utf-8"
        )
        for concept in (
            "Artifact Graph",
            "Agent-agnostic Core",
            "HANDOFF & RETURN PROTOCOL",
            "FEATURE / SLICE",
            "FROM SDLC TO AI ENGINEERING PROTOCOL",
            "AGENT INDEPENDENCE",
            "方向，不是当前能力声明",
        ):
            self.assertIn(concept, generator)

    def test_engineering_protocol_presentations_are_bilingual_and_current(self):
        presentations = {
            "en": ROOT / "docs/presentations/forgeflow-engineering-protocol.en.md",
            "zh-CN": ROOT
            / "docs/presentations/forgeflow-engineering-protocol.zh-CN.md",
        }
        required_concepts = {
            "Agent-Agnostic Engineering Protocol",
            "Artifact Graph",
            "Return",
            "Recovery",
            "Codex",
            "Copilot",
            "GitHub Spec Kit",
            "OpenSpec",
            "BMAD Method",
            "SpecDD",
            "Plugin-Based Review",
        }
        for locale, path in presentations.items():
            content = path.read_text(encoding="utf-8")
            with self.subTest(locale=locale):
                self.assertEqual(content.count("```mermaid"), 4)
                for concept in required_concepts:
                    self.assertIn(concept, content)
                if locale == "en":
                    self.assertIn("What makes ForgeFlow distinctive", content)
                    self.assertIn("Recommended adoption path", content)
                    self.assertIn("not a current validated-integration claim", content)
                else:
                    self.assertIn("ForgeFlow 与众不同的地方", content)
                    self.assertIn("建议采用路径", content)
                    self.assertIn("不是当前已验证集成", content)

    def test_json_documents_are_parseable(self):
        for relative in (
            "forgeflow.json",
            "package.json",
            ".forgeflow/forgeflow.schema.json",
        ):
            with self.subTest(path=relative):
                parsed = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)

    def test_distribution_versions_are_synchronized(self):
        package_version = json.loads(
            (ROOT / "package.json").read_text(encoding="utf-8")
        )["version"]
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        package_init = (ROOT / "src/forgeflow/__init__.py").read_text(
            encoding="utf-8"
        )
        pyproject_version = re.search(
            r'^version = "([^"]+)"$', pyproject, re.MULTILINE
        )
        module_version = re.search(
            r'^__version__ = "([^"]+)"$', package_init, re.MULTILINE
        )

        self.assertIsNotNone(pyproject_version)
        self.assertIsNotNone(module_version)
        self.assertEqual(pyproject_version.group(1), package_version)
        self.assertEqual(module_version.group(1), package_version)

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
            ".forgeflow/protocol/transition.md",
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

    def test_runtime_workflow_owners_match_framework(self):
        from forgeflow.engine.runner import ForgeRunner
        from forgeflow.engine.handoff_parser import HandoffParser
        from forgeflow.engine.verification import STRATEGIES
        self.assertEqual(set(ForgeRunner._WORKFLOW_TITLES), WORKFLOWS)
        self.assertEqual({name.lower() for name in HandoffParser._WORKFLOW_SCOPES}, WORKFLOWS)
        self.assertEqual({owner.lower() for _, _, owner in ArtifactParser._FILE_RULES}, WORKFLOWS)
        contract = (ROOT / ".forgeflow/protocol/artifact.md").read_text()
        registry = contract.split("| Strategy | Required execution pattern and evidence |", 1)[1].split("TDD is the default candidate", 1)[0]
        names = re.findall(r"^\| ([A-Z_]+) \|", registry, re.M)
        self.assertEqual(list(STRATEGIES), names)

    def test_current_protocols_are_packaged(self):
        from forgeflow.scaffold import FRAMEWORK_ENTRIES
        self.assertIn("protocol", FRAMEWORK_ENTRIES)
        for name in ("artifact", "transition", "handoff", "review-recovery"):
            self.assertTrue((ROOT / f".forgeflow/protocol/{name}.md").is_file())
        self.assertFalse((ROOT / ".forgeflow/workflow/tdd.md").exists())
        self.assertTrue((ROOT / ".forgeflow/workflow/implement.md").is_file())

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

    def test_architecture_links_current_authorities_and_discloses_limits(self):
        for filename in ("ARCHITECTURE.md", "ARCHITECTURE.zh-CN.md"):
            text = (ROOT / filename).read_text()
            for path in ("forgeflow.md", "protocol/artifact.md", "protocol/transition.md", "protocol/handoff.md"):
                self.assertIn("./.forgeflow/" + path, text)
            self.assertIn("Technical Preview", text)
            self.assertIn("Implement", text)
        self.assertIn("cannot establish whether execution", (ROOT / "ARCHITECTURE.md").read_text())


if __name__ == "__main__":
    unittest.main()
