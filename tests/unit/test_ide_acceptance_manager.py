import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANAGER_PATH = ROOT / "tests" / "acceptance" / "ide" / "manage.py"
SPEC = importlib.util.spec_from_file_location("forgeflow_ide_acceptance", MANAGER_PATH)
MANAGER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MANAGER
SPEC.loader.exec_module(MANAGER)


class IdeAcceptanceManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = MANAGER.load_cases()

    @staticmethod
    def _write_result(root, case, adapter, status="PASS", suffix=""):
        content = MANAGER.render_result(case, adapter)
        content = content.replace("| Status | NOT RUN |", f"| Status | {status} |")
        if status == "PASS":
            content = content.replace("TODO", "recorded")
        path = root / f"{case.case_id}.{adapter}{suffix}.result.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_pass_result_requires_complete_evidence(self):
        case = self.cases["IDE-INV-001"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "incomplete.result.md"
            content = MANAGER.render_result(case, "copilot").replace(
                "| Status | NOT RUN |", "| Status | PASS |"
            )
            path.write_text(content, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "still contains TODO placeholders"):
                MANAGER.load_results(root, self.cases)

    def test_pass_result_allows_todo_text_inside_recorded_evidence(self):
        case = self.cases["IDE-INV-001"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self._write_result(root, case, "copilot")
            content = path.read_text(encoding="utf-8").replace(
                "| Notes | recorded |", "| Notes | Agent output mentioned TODO code |"
            )
            path.write_text(content, encoding="utf-8")

            results = MANAGER.load_results(root, self.cases)

            self.assertEqual(results[0].status, "PASS")

    def test_duplicate_case_adapter_results_are_rejected(self):
        case = self.cases["IDE-INV-001"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_result(root, case, "copilot", suffix=".first")
            self._write_result(root, case, "copilot", suffix=".second")

            with self.assertRaisesRegex(ValueError, "Duplicate result"):
                MANAGER.load_results(root, self.cases)

    def test_release_gate_requires_every_p0_case(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_case = self.cases["IDE-INV-001"]
            self._write_result(root, first_case, "copilot")
            args = type("Args", (), {"results": root})()

            with contextlib.redirect_stdout(io.StringIO()):
                result = MANAGER.command_release_gate(args, self.cases)

            self.assertEqual(result, 1)

    def test_one_adapter_pass_does_not_cover_a_two_adapter_case(self):
        case = next(c for c in self.cases.values() if "," in MANAGER.case_adapters(c))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_result(root, case, "copilot")
            results = MANAGER.load_results(root, self.cases)
        self.assertEqual(MANAGER.case_outcomes(self.cases, results)[case.case_id], "NOT RUN")

    def test_release_gate_passes_complete_p0_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for case in self.cases.values():
                if case.priority != "P0":
                    continue
                for adapter in MANAGER.case_adapters(case).split(","):
                    self._write_result(root, case, adapter)
            args = type("Args", (), {"results": root})()

            with contextlib.redirect_stdout(io.StringIO()):
                result = MANAGER.command_release_gate(args, self.cases)

            self.assertEqual(result, 0)

    def test_recorded_p1_blocker_blocks_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for case in self.cases.values():
                if case.priority == "P0":
                    for adapter in MANAGER.case_adapters(case).split(","):
                        self._write_result(root, case, adapter)
            p1_case = next(
                case for case in self.cases.values() if case.priority == "P1"
            )
            adapter = MANAGER.case_adapters(p1_case).split(",")[0]
            self._write_result(root, p1_case, adapter, status="BLOCKED")
            args = type("Args", (), {"results": root})()

            with contextlib.redirect_stdout(io.StringIO()):
                result = MANAGER.command_release_gate(args, self.cases)

            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
