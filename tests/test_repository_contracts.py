import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = {"plan", "grill", "solution", "slice", "tdd", "review"}


class RepositoryContractTests(unittest.TestCase):
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
        self.assertNotIn("forgeflow/engine", package["files"])
        self.assertNotIn("forgeflow/cli", package["files"])


if __name__ == "__main__":
    unittest.main()
