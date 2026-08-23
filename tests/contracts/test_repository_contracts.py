import json
import re
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

    def test_bootstrap_entry_uses_handoff_root_contract(self):
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")

        for rule in (
            "the Artifact Root is absent or empty, and the\n"
            "supplemental Reports Root is absent or empty",
            "An empty Artifact\nRoot with a non-empty Reports Root is residual project evidence",
            "Rule 1 does not\nmatch, Bootstrap Entry is not authorized",
        ):
            self.assertIn(rule, handoff)
        self.assertIn(
            "Bootstrap Entry conditions are defined only by the Handoff Protocol",
            plan,
        )
        self.assertNotIn(
            "Bootstrap Entry** requires both Artifact Root and Reports Root",
            plan,
        )

    def test_plugin_registry_owns_canonical_md_and_csv_reports(self):
        registry = (ROOT / ".forgeflow/rules/reviews/_index.md").read_text(
            encoding="utf-8"
        )
        review = (ROOT / ".forgeflow/workflow/review.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("### Canonical Report Serialization", registry)
        self.assertIn("#### Markdown Template", registry)
        self.assertIn(
            "| Rule ID | Description | Severity | Verdict | Disposition | Evidence |",
            registry,
        )
        self.assertIn("#### CSV Template", registry)
        self.assertIn(
            "Plugin,Rules Version,Feature ID,Slice ID,Attempt,Overall Verdict,"
            "PASS Count,VIOLATION Count,UNKNOWN Count,N/A Count,BLOCKING Count,"
            "NON_BLOCKING Count,Rule ID,Description,Severity,Verdict,Disposition,Evidence",
            registry,
        )
        self.assertIn("same rules, verdicts, dispositions", registry)
        self.assertIn("sole registry and execution contract", review)
        self.assertIn("MUST NOT duplicate, infer, reorder, or locally redefine", review)

    def test_scoped_workflows_cannot_preconsume_future_scope(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        principle = (
            "A workflow execution MUST NOT consume a future execution scope\n"
            "unless that scope is explicitly provided by the incoming Canonical Handoff "
            "or a\nvalidated Feature Lane Entry."
        )
        self.assertIn(principle, framework)
        self.assertIn(principle, handoff)

        workflow_rules = {
            "grill": "more than one Feature is\nnon-conforming",
            "slice": "does not continue work inside this execution",
            "tdd": "does not authorize Review or the next Slice",
            "review": "MUST only emit that Handoff and stop",
        }
        for workflow, rule in workflow_rules.items():
            spec = (ROOT / f".forgeflow/workflow/{workflow}.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(rule, spec)

    def test_subsequent_plan_is_default_and_solution_is_project_coherent(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")
        solution = (ROOT / ".forgeflow/workflow/solution.md").read_text(
            encoding="utf-8"
        )

        for contract in (framework, handoff, plan):
            self.assertIn("Subsequent Plan Entry", contract)
        self.assertIn("Semantic similarity", plan)
        self.assertIn("MUST NOT be used to infer a different\n     project", plan)
        self.assertIn("every current\nactive business contract", solution)
        self.assertIn("Shared Components and Utilities", solution)
        self.assertIn("Cross-Feature Impact", solution)

    def test_project_knowledge_is_derived_and_traceable(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        workflows = {
            name: (ROOT / f".forgeflow/workflow/{name}.md").read_text(
                encoding="utf-8"
            )
            for name in WORKFLOWS
        }

        self.assertIn("Project Knowledge View", framework)
        self.assertIn("Project Knowledge View", artifact)
        self.assertIn("not an Artifact Type", artifact)
        self.assertIn("Planning Change Set", artifact)
        self.assertIn("intent-evolution summary", workflows["plan"])
        self.assertIn("Planning Change Set context", workflows["grill"])
        self.assertIn("Engineering Decision Register", workflows["solution"])
        self.assertIn("shared components or utilities", workflows["slice"])
        self.assertIn("implemented engineering decisions", workflows["tdd"])
        self.assertIn("complete knowledge", workflows["review"])

    def test_structured_impact_model_remains_non_authoritative(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        solution = (ROOT / ".forgeflow/workflow/solution.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Project Impact View", framework)
        self.assertIn("MUST NOT authorize a Workflow", framework)
        for field in (
            "Shared Component IDs",
            "Feature Dependencies",
            "Feature Shared Components",
            "Feature Shared Component Access",
            "Feature Decision References",
            "Cross-Feature Impact",
        ):
            self.assertIn(field, artifact)
            self.assertIn(field, solution)

    def test_feature_lanes_are_dependency_and_access_aware(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        solution = (ROOT / ".forgeflow/workflow/solution.md").read_text(
            encoding="utf-8"
        )
        scoped_workflows = {
            name: (ROOT / f".forgeflow/workflow/{name}.md").read_text(
                encoding="utf-8"
            )
            for name in ("slice", "tdd", "review")
        }

        self.assertIn("LANE_READY(F)", framework)
        self.assertIn("LANE_DELIVERY_READY(F)", framework)
        self.assertIn("Planning order is\nnot an execution dependency", framework)
        self.assertIn("### Feature Lane State and Selection", handoff)
        self.assertIn("Feature Lane Ready Set", handoff)
        self.assertIn("There are exactly five entry modes", handoff)
        self.assertIn("Feature Lane Entry", handoff)
        self.assertIn("Feature Shared Component Access", artifact)
        self.assertIn("Feature Shared Component Access", solution)
        self.assertIn("`READ`/`READ`", artifact)
        self.assertIn("WRITE", artifact)
        self.assertIn("union", artifact)
        for workflow in scoped_workflows.values():
            self.assertIn("Feature Lane Entry", workflow)
            self.assertIn("re-read", workflow.lower())

        all_contracts = "\n".join(
            [framework, artifact, handoff, solution, *scoped_workflows.values()]
        )
        self.assertNotIn(
            "TDD is forbidden until every planned Feature has a usable current Slice Plan",
            all_contracts,
        )
        self.assertNotIn("TDD MUST NOT start before `DELIVERY_READY`", all_contracts)
        self.assertNotIn("A later Feature's Slice MUST NOT start", all_contracts)

    def test_source_and_test_placement_are_upstream_engineering_contracts(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        workflows = {
            name: (ROOT / f".forgeflow/workflow/{name}.md").read_text(
                encoding="utf-8"
            )
            for name in ("solution", "slice", "tdd", "review")
        }
        architecture_rules = (
            ROOT / ".forgeflow/rules/reviews/architecture/rules.md"
        ).read_text(encoding="utf-8")

        self.assertIn("not local TDD preferences", framework)
        for section in (
            "## Implementation Structure",
            "## Test Structure",
            "Planned File Placement",
            "File Placement\nConformance",
        ):
            self.assertIn(section, artifact)
        self.assertIn("package-by-Feature", workflows["solution"])
        self.assertIn("Planned File Placement", workflows["slice"])
        self.assertIn("MUST NOT\n   choose a new package", workflows["tdd"])
        self.assertIn("TDD File\n   Placement Conformance", workflows["review"])
        self.assertIn(
            "ARC-003 | Contracted Source Structure Conformance | P1",
            architecture_rules,
        )
        self.assertIn(
            "ARC-009 | Contracted Test Structure Conformance | P1",
            architecture_rules,
        )
        self.assertIn(
            "ARC-008 | General Package/Module Cohesion | P2",
            architecture_rules,
        )

    def test_ide_invocations_stop_at_handoffs_and_artifacts_are_not_split(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")
        grill = (ROOT / ".forgeflow/workflow/grill.md").read_text(
            encoding="utf-8"
        )
        solution = (ROOT / ".forgeflow/workflow/solution.md").read_text(
            encoding="utf-8"
        )
        schema = json.loads(
            (ROOT / ".forgeflow/forgeflow.schema.json").read_text(encoding="utf-8")
        )

        self.assertIn("Invocation termination barrier", framework)
        self.assertIn("direct IDE launcher invocation is manual", framework)
        self.assertIn("Emission-consumption boundary", handoff)
        self.assertIn("MUST NOT consume its own Handoff", handoff)
        self.assertIn("do not start Grill", plan)
        self.assertIn("Requirement mutation set", grill)
        self.assertNotIn("Artifact Protocol Version", artifact)
        for section in ArtifactParser._PLANNING_SECTIONS:
            self.assertIn(f"`## {section}`", artifact)
        self.assertIn("## Solution Summary", solution)
        self.assertIn("`solution-plan-summary.md`", solution)
        self.assertIn("standalone summary file", solution)
        self.assertIn("CLI orchestration only", schema["properties"]["mode"]["description"])

    def test_plan_clarifies_business_scope_without_preloading_future_workflows(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")

        self.assertIn("Authoritative loading and workspace boundary", framework)
        self.assertIn("Framework, Artifact Protocol, Handoff Protocol", framework)
        self.assertIn("MUST NOT load another Workflow specification", framework)
        self.assertIn("MUST NOT inspect user-level agent configuration", framework)
        self.assertIn("## Planning clarification", plan)
        for concept in (
            "approved project scope",
            "Feature set",
            "cross-Feature actor",
            "contract between two or more Features",
            "ask the user during this invocation",
            "Every other business question",
            "Grill-owned",
        ):
            self.assertIn(concept, plan)
        self.assertIn("Assumptions", artifact)
        self.assertIn("silence is not exclusion", artifact)
        self.assertIn("Dependencies in the Features", artifact)

    def test_authoritative_files_require_complete_read_through_eof(self):
        framework_path = ROOT / ".forgeflow/forgeflow.md"
        framework = framework_path.read_text(encoding="utf-8")
        authoritative_paths = (
            ".forgeflow/forgeflow.md",
            ".forgeflow/protocol/artifact.md",
            ".forgeflow/protocol/handoff.md",
            *(f".forgeflow/workflow/{workflow}.md" for workflow in sorted(WORKFLOWS)),
        )

        for requirement in (
            "Authoritative Read Completion Procedure",
            "current physical end",
            "contiguous ranges",
            "path-specific marker",
            "internal read receipt",
            "MUST continue from the next unread line",
        ):
            self.assertIn(requirement, framework)

        for relative_path in authoritative_paths:
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertEqual(
                content.rstrip().splitlines()[-1],
                f"<!-- forgeflow-eof: {relative_path} -->",
            )

    def test_plan_uses_canonical_persisted_planning_and_handoff_rendering(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")

        self.assertIn("Canonical Planning rendering envelope", artifact)
        self.assertIn("Planning serialization validation", artifact)
        for section in ArtifactParser._PLANNING_SECTIONS:
            self.assertIn(f"## {section}", artifact)
        for prohibition in (
            "repeated `# Planning`",
            "Feature status table",
            "per-Feature contract-summary subsection",
            "Project scaffolding",
            "database setup",
        ):
            self.assertIn(prohibition, artifact)

        self.assertIn("## Planning conformance gate", plan)
        self.assertIn("reparsed persisted artifact", plan)
        self.assertIn("Source Scope` is always `Project", plan)
        self.assertIn("`<transition>` wrapper", plan)
        self.assertIn("Markdown structures are protocol data", framework)
        self.assertIn("presentational\nsuggestions", framework)
        self.assertIn("XML or HTML elements such as `<transition>`", handoff)
        self.assertIn("compare the candidate block", handoff)
        self.assertIn("Metadata `READY` value alone", handoff)
        self.assertIn("is insufficient", handoff)

    def test_plan_has_no_shadow_state_and_handoff_is_the_final_action(self):
        framework = (ROOT / ".forgeflow/forgeflow.md").read_text(encoding="utf-8")
        artifact = (ROOT / ".forgeflow/protocol/artifact.md").read_text(
            encoding="utf-8"
        )
        handoff = (ROOT / ".forgeflow/protocol/handoff.md").read_text(
            encoding="utf-8"
        )
        plan = (ROOT / ".forgeflow/workflow/plan.md").read_text(encoding="utf-8")

        self.assertIn("### Workflow persistence boundary", framework)
        for phrase in (
            "database table",
            "shadow state",
            "Tool availability does not grant mutation authority",
            "does not forbid application persistence implemented by",
            "database schemas, migrations, tables, indexes",
        ):
            self.assertIn(phrase, framework)
        for phrase in (
            "only permitted persistent mutations",
            "MUST NOT execute SQL DDL or DML",
            "## Execution boundary",
            "MUST NOT invoke an SQL or database tool",
            "task, memory, planning, agent-management",
            "Plan has no such",
            "exception",
            "separate decision",
            "minimum question",
        ):
            self.assertIn(phrase, plan)
        self.assertIn("assignment and", plan)
        self.assertIn("collaboration rules", plan)
        self.assertIn("decomposition is its only product-definition responsibility", plan)
        self.assertIn("Every other business question is", plan)
        self.assertIn("forbidden in Plan", plan)
        self.assertIn("## Decomposition readiness gate", plan)
        self.assertIn("domain-independent procedure", plan)
        self.assertIn("five universal dimensions", plan)
        self.assertIn("applies identically to every domain and User Intent", plan)
        for phrase in (
            "approved business decision is a contract",
            "No Planning section may contradict another",
            "Dependency validation is exhaustive",
            "role cardinalities",
            "#### Decomposition readiness evidence",
            "project inclusion and exclusion boundaries",
            "lifecycle transfers, returns, or resumptions",
            "shared data meanings, measurements, aggregations",
            "zero Plan questions is valid",
        ):
            self.assertIn(phrase, artifact)
        self.assertIn("A transitive", artifact)
        self.assertIn("path through another Feature", artifact)
        self.assertIn("final action, not only its final visible paragraph", handoff)
        self.assertIn("MUST NOT invoke any tool", handoff)
        self.assertIn("execute SQL", handoff)

        tdd = (ROOT / ".forgeflow/workflow/tdd.md").read_text(encoding="utf-8")
        self.assertIn("application database schemas, migrations, tables", tdd)
        self.assertIn("SQL records required by the targeted Slice", tdd)
        self.assertIn("MUST NOT use an", tdd)
        self.assertIn("application database or SQL tool to persist ForgeFlow", tdd)

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
            "agent-agnostic by design",
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
            "规范核心在设计上是 **Agent-agnostic**",
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
