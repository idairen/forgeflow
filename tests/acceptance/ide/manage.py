#!/usr/bin/env python3
"""Prepare and inspect ForgeFlow IDE acceptance-test workspaces."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = REPOSITORY_ROOT / "docs" / "testing" / "ide-test-plan.zh-CN.md"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "python-project"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "current"
FRAMEWORK_ENTRIES = (
    "forgeflow.md",
    "forgeflow.schema.json",
    "adapter",
    "protocol",
    "rules",
    "workflow",
)
WORKFLOWS = ("plan", "grill", "solution", "slice", "implement", "review")
AREA_BASELINES = {
    "INV": "S0-CLEAN",
    "PLAN": "S0-CLEAN or case-specific",
    "GRILL": "S1-PLANNED",
    "SOL": "S2-BUSINESS",
    "SLICE": "S3-ENGINEERING",
    "TDD": "S4-DELIVERY or case-specific",
    "REV": "S5-REVIEW or S6-FAIL",
    "HO": "case-specific",
    "BLK": "case-specific blocker snapshot",
    "INC": "S7-COMPLETE or case-specific",
    "HIS": "case-specific",
    "GRAPH": "copy of a valid snapshot",
    "VER": "case-specific valid snapshot",
    "ORD": "declared-order variant",
    "RST": "case-specific valid snapshot",
    "PAR": "matched Codex/Copilot snapshot pair",
}
AREA_NAMES = {
    "INV": "Prompt 发现与宿主隔离",
    "PLAN": "Plan 与项目入口",
    "GRILL": "Grill",
    "SOL": "Solution",
    "SLICE": "Slice",
    "TDD": "Implement strategies",
    "REV": "Review 与插件",
    "HO": "Handoff 与转换",
    "BLK": "Blocker 与 Recovery",
    "INC": "后续需求与增量演进",
    "HIS": "历史、报告与轮换",
    "GRAPH": "无效 Artifact Graph",
    "VER": "版本新鲜度",
    "ORD": "声明顺序",
    "RST": "会话重启",
    "PAR": "Adapter 一致性",
}
CSV_HEADERS = (
    "用例编号",
    "测试域",
    "优先级",
    "适配器",
    "推荐前置快照",
    "场景与操作",
    "期望结果",
    "状态",
    "证据",
    "缺陷编号",
    "备注",
)
RESULT_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT RUN")


@dataclass(frozen=True)
class Case:
    case_id: str
    area: str
    priority: str
    action: str
    expected: str

    @property
    def baseline(self) -> str:
        return AREA_BASELINES[self.area]


@dataclass(frozen=True)
class Result:
    case_id: str
    adapter: str
    status: str
    defect_id: str
    path: Path


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def load_cases() -> dict[str, Case]:
    lines = PLAN_PATH.read_text(encoding="utf-8").splitlines()
    cases: dict[str, Case] = {}
    index = 0

    while index < len(lines):
        if not lines[index].startswith("|"):
            index += 1
            continue

        table: list[list[str]] = []
        while index < len(lines) and lines[index].startswith("|"):
            table.append(_cells(lines[index]))
            index += 1

        if len(table) < 3 or "ID" not in table[0] or not _is_separator(table[1]):
            continue

        headers = table[0]
        for row in table[2:]:
            if len(row) != len(headers):
                raise ValueError(f"Malformed case table row: {row}")
            values = dict(zip(headers, row))
            case_id = values.get("ID", "")
            priority = values.get("优先级", "")
            if not case_id.startswith("IDE-") or priority not in {"P0", "P1", "P2"}:
                continue

            parts = case_id.split("-")
            if len(parts) != 3 or parts[1] not in AREA_BASELINES:
                raise ValueError(f"Unsupported case identifier: {case_id}")
            area = parts[1]

            expected_headers = [
                header
                for header in headers
                if "期望" in header or header == "一致性要求"
            ]
            expected = "; ".join(values[header] for header in expected_headers)
            action_parts = [
                f"{header}: {values[header]}"
                for header in headers
                if header not in {"ID", "优先级", *expected_headers}
            ]
            action = "; ".join(action_parts)
            if case_id in cases:
                raise ValueError(f"Duplicate case identifier: {case_id}")
            cases[case_id] = Case(case_id, area, priority, action, expected)

    return cases


def reject_symlinks(root: Path) -> None:
    if root.is_symlink():
        raise ValueError(f"Symbolic-link roots are not supported: {root}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not supported: {path}")


def ensure_new_directory(path: Path) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"Destination already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_workspace(source: Path, destination: Path) -> None:
    source = source.resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"Workspace source is not a directory: {source}")
    reject_symlinks(source)
    ensure_new_directory(destination)

    def ignore(directory: str, names: list[str]) -> set[str]:
        ignored = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}
        if Path(directory).name == ".forgeflow":
            ignored.add("runtime")
        return ignored.intersection(names)

    shutil.copytree(source, destination, ignore=ignore)


def install_framework(project: Path) -> None:
    source = REPOSITORY_ROOT / ".forgeflow"
    target = project / ".forgeflow"
    target.mkdir(parents=True, exist_ok=True)
    for entry in FRAMEWORK_ENTRIES:
        source_path = source / entry
        target_path = target / entry
        if source_path.is_dir():
            shutil.copytree(source_path, target_path)
        else:
            shutil.copy2(source_path, target_path)
    (target / "artifacts").mkdir()
    (target / "reports").mkdir()


def write_copilot_settings(project: Path) -> None:
    settings_path = project / ".vscode" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings = {
        "chat.promptFilesLocations": {
            ".github/prompts": True,
            ".forgeflow/adapter/copilot": True,
        }
    }
    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def render_result(case: Case, adapter: str) -> str:
    version = re.search(r"^Version: (.+)$", (REPOSITORY_ROOT / ".forgeflow/forgeflow.md").read_text(), re.M).group(1)
    return f"""# {case.case_id} Test Result

## Case

| Field | Value |
|---|---|
| Area | {AREA_NAMES[case.area]} |
| Priority | {case.priority} |
| Adapter | {adapter} |
| Framework Version | {version} |
| Recommended baseline | {case.baseline} |
| Action | {case.action} |
| Expected | {case.expected} |

## Environment

| Field | Value |
|---|---|
| Operating system | TODO |
| IDE and version | TODO |
| AI extension and version | TODO |
| Selected model | TODO |
| Selected chat mode/agent | TODO |
| Prompt search-path configuration | TODO |
| ForgeFlow Git SHA | TODO |
| Project Git SHA | TODO |

## Execution Evidence

- Prompt selected from command menu: TODO
- Prompt source shown by IDE: TODO
- User input: TODO
- Response transcript or screenshot: TODO
- Pre-execution file inventory/checksums: TODO
- Post-execution `git diff`: TODO
- Artifact evidence: TODO
- Report evidence: TODO
- Handoff evidence, or reason none is expected: TODO

## Result

| Field | Value |
|---|---|
| Status | NOT RUN |
| Defect ID | NONE |
| Notes | TODO |
"""


def _result_table_value(content: str, field: str, path: Path) -> str:
    pattern = re.compile(
        rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|$",
        re.MULTILINE,
    )
    values = pattern.findall(content)
    if len(values) != 1:
        raise ValueError(f"Expected one {field!r} field in result: {path}")
    return values[0].strip()


def load_results(root: Path, cases: dict[str, Case]) -> list[Result]:
    if not root.exists():
        return []
    if not root.is_dir():
        raise ValueError(f"Results root is not a directory: {root}")

    results: list[Result] = []
    seen: set[tuple[str, str]] = set()
    for path in sorted(root.rglob("*.result.md")):
        content = path.read_text(encoding="utf-8")
        heading = re.search(r"^# (IDE-[A-Z]+-\d{3}) Test Result$", content, re.MULTILINE)
        if heading is None:
            raise ValueError(f"Missing canonical result heading: {path}")
        case_id = heading.group(1)
        case = cases.get(case_id)
        if case is None:
            raise ValueError(f"Unknown case in result {path}: {case_id}")

        adapter = _result_table_value(content, "Adapter", path).lower()
        if adapter not in case_adapters(case).split(","):
            raise ValueError(
                f"Adapter {adapter!r} is not applicable to {case_id}: {path}"
            )
        status = _result_table_value(content, "Status", path).upper()
        if status not in RESULT_STATUSES:
            raise ValueError(f"Unsupported result status {status!r}: {path}")
        defect_id = _result_table_value(content, "Defect ID", path)
        if status == "PASS":
            current_version = re.search(r"^Version: (.+)$", (REPOSITORY_ROOT / ".forgeflow/forgeflow.md").read_text(), re.M).group(1)
            if _result_table_value(content, "Framework Version", path) != current_version:
                raise ValueError(f"PASS result is from another Framework version: {path}")
            unresolved_table_value = re.search(
                r"^\|\s*[^|]+\s*\|\s*TODO\s*\|$", content, re.MULTILINE
            )
            unresolved_evidence = re.search(
                r"^- [^:\n]+: TODO$", content, re.MULTILINE
            )
            if unresolved_table_value or unresolved_evidence:
                raise ValueError(
                    f"PASS result still contains TODO placeholders: {path}"
                )
            if defect_id.upper() != "NONE":
                raise ValueError(f"PASS result must use Defect ID NONE: {path}")

        key = (case_id, adapter)
        if key in seen:
            raise ValueError(
                f"Duplicate result for {case_id} and {adapter} under {root}"
            )
        seen.add(key)
        results.append(Result(case_id, adapter, status, defect_id, path))
    return results


def case_outcomes(
    cases: dict[str, Case], results: list[Result]
) -> dict[str, str]:
    by_case: dict[str, list[str]] = {}
    for result in results:
        by_case.setdefault(result.case_id, []).append(result.status)

    outcomes: dict[str, str] = {}
    for case_id in cases:
        statuses = by_case.get(case_id, [])
        if "FAIL" in statuses:
            outcomes[case_id] = "FAIL"
        elif "BLOCKED" in statuses:
            outcomes[case_id] = "BLOCKED"
        elif all(any(r.case_id == case_id and r.adapter == adapter and r.status == "PASS" for r in results)
                 for adapter in case_adapters(cases[case_id]).split(",")):
            outcomes[case_id] = "PASS"
        else:
            outcomes[case_id] = "NOT RUN"
    return outcomes


def print_summary(cases: dict[str, Case], results: list[Result]) -> None:
    outcomes = case_outcomes(cases, results)
    for priority in ("P0", "P1", "P2"):
        selected = [
            outcomes[case.case_id]
            for case in cases.values()
            if case.priority == priority
        ]
        counts = {status: selected.count(status) for status in RESULT_STATUSES}
        print(
            f"{priority}: total={len(selected)} pass={counts['PASS']} "
            f"fail={counts['FAIL']} blocked={counts['BLOCKED']} "
            f"not_run={counts['NOT RUN']}"
        )

    for adapter in ("copilot", "codex"):
        selected = [result for result in results if result.adapter == adapter]
        passed = sum(result.status == "PASS" for result in selected)
        print(f"{adapter}: recorded={len(selected)} pass={passed}")


def command_summary(args: argparse.Namespace, cases: dict[str, Case]) -> None:
    results = load_results(args.results.resolve(), cases)
    print_summary(cases, results)


def command_release_gate(args: argparse.Namespace, cases: dict[str, Case]) -> int:
    results = load_results(args.results.resolve(), cases)
    outcomes = case_outcomes(cases, results)
    print_summary(cases, results)

    incomplete_p0 = [
        case_id
        for case_id, case in cases.items()
        if case.priority == "P0" and outcomes[case_id] != "PASS"
    ]
    recorded_p1_failures = [
        case_id
        for case_id, case in cases.items()
        if case.priority == "P1" and outcomes[case_id] in {"FAIL", "BLOCKED"}
    ]
    if incomplete_p0 or recorded_p1_failures:
        print("RELEASE GATE: BLOCKED")
        if incomplete_p0:
            print(
                f"P0 cases not passed ({len(incomplete_p0)}): "
                + _format_case_ids(incomplete_p0)
            )
        if recorded_p1_failures:
            print(
                "Recorded P1 failures/blockers "
                f"({len(recorded_p1_failures)}): "
                + _format_case_ids(recorded_p1_failures)
            )
        return 1

    print("RELEASE GATE: PASS")
    return 0


def _format_case_ids(case_ids: list[str], limit: int = 20) -> str:
    visible = case_ids[:limit]
    suffix = "" if len(case_ids) <= limit else f", ... (+{len(case_ids) - limit} more)"
    return ", ".join(visible) + suffix


def command_list(args: argparse.Namespace, cases: dict[str, Case]) -> None:
    selected = sorted(cases.values(), key=lambda case: case.case_id)
    if args.area:
        selected = [case for case in selected if case.area == args.area.upper()]
    if args.priority:
        selected = [case for case in selected if case.priority == args.priority]
    for case in selected:
        print(
            f"{case.case_id}\t{case.priority}\t{case.baseline}\t{case.action}",
        )
    print(f"Total: {len(selected)}", file=sys.stderr)


def command_show(args: argparse.Namespace, cases: dict[str, Case]) -> None:
    case = cases.get(args.case_id.upper())
    if case is None:
        raise KeyError(f"Unknown case: {args.case_id}")
    print(f"ID: {case.case_id}")
    print(f"Area: {AREA_NAMES[case.area]}")
    print(f"Priority: {case.priority}")
    print(f"Recommended baseline: {case.baseline}")
    print(f"Action: {case.action}")
    print(f"Expected: {case.expected}")


def case_adapters(case: Case) -> str:
    if case.case_id == "IDE-INV-007":
        return "codex"
    if case.area == "INV":
        return "copilot"
    return "copilot,codex"


def command_export(cases: dict[str, Case]) -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(CSV_HEADERS)
    for case in cases.values():
        writer.writerow(
            (
                case.case_id,
                AREA_NAMES[case.area],
                case.priority,
                case_adapters(case),
                case.baseline,
                case.action,
                case.expected,
                "NOT RUN",
                "",
                "",
                "",
            )
        )


def command_init(args: argparse.Namespace) -> None:
    output = args.output.resolve()
    ensure_new_directory(output)
    shutil.copytree(FIXTURE_PATH, output)
    install_framework(output)
    if args.adapter == "copilot":
        write_copilot_settings(output)
    print(f"Initialized clean {args.adapter} IDE workspace: {output}")
    if args.adapter == "codex":
        print(
            "Configure the Codex host to discover "
            ".forgeflow/adapter/codex before running a case."
        )


def command_snapshot(args: argparse.Namespace) -> None:
    destination = args.output.resolve()
    copy_workspace(args.source, destination)
    print(f"Captured IDE-generated snapshot: {destination}")


def command_prepare(args: argparse.Namespace, cases: dict[str, Case]) -> None:
    case = cases.get(args.case_id.upper())
    if case is None:
        raise KeyError(f"Unknown case: {args.case_id}")

    output = args.output.resolve()
    copy_workspace(args.source, output)
    result_path = (
        args.result.resolve()
        if args.result
        else RESULTS_PATH / f"{case.case_id}.{args.adapter}.result.md"
    )
    if result_path.exists() or result_path.is_symlink():
        raise FileExistsError(f"Result file already exists: {result_path}")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(render_result(case, args.adapter), encoding="utf-8")
    print(f"Prepared case workspace: {output}")
    print(f"Created result record: {result_path}")
    print(f"Recommended baseline: {case.baseline}")


def command_verify(cases: dict[str, Case]) -> None:
    if not cases:
        raise ValueError("Acceptance catalog must not be empty")

    for adapter in ("codex", "copilot"):
        for workflow in WORKFLOWS:
            path = (
                REPOSITORY_ROOT
                / ".forgeflow"
                / "adapter"
                / adapter
                / f"forge-{workflow}.prompt.md"
            )
            text = path.read_text(encoding="utf-8")
            if f"name: forge-{workflow}\n" not in text:
                raise ValueError(f"Prompt name mismatch: {path}")
            if f".forgeflow/workflow/{workflow}.md" not in text:
                raise ValueError(f"Workflow target mismatch: {path}")
            if adapter == "copilot" and "agent: agent\n" not in text:
                raise ValueError(f"Copilot Prompt does not force Agent mode: {path}")
            if adapter == "codex" and "agent:" in text:
                raise ValueError(f"Codex Prompt contains Copilot agent metadata: {path}")

    priorities = {priority: 0 for priority in ("P0", "P1", "P2")}
    for case in cases.values():
        priorities[case.priority] += 1
    print(
        f"Verified {len(cases)} IDE cases and 12 workflow Prompts "
        f"(P0={priorities['P0']}, P1={priorities['P1']}, P2={priorities['P2']})."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List cases from the test plan")
    list_parser.add_argument("--area", choices=sorted(AREA_BASELINES))
    list_parser.add_argument("--priority", choices=("P0", "P1", "P2"))

    show_parser = subparsers.add_parser("show", help="Show one case")
    show_parser.add_argument("case_id")

    subparsers.add_parser("export", help="Export all cases as UTF-8 CSV")

    init_parser = subparsers.add_parser(
        "init", help="Create a clean IDE test workspace"
    )
    init_parser.add_argument("--adapter", choices=("copilot", "codex"), required=True)
    init_parser.add_argument("--output", type=Path, required=True)

    snapshot_parser = subparsers.add_parser(
        "snapshot", help="Capture a real IDE-generated workspace state"
    )
    snapshot_parser.add_argument("--source", type=Path, required=True)
    snapshot_parser.add_argument("--output", type=Path, required=True)

    prepare_parser = subparsers.add_parser(
        "prepare", help="Clone a snapshot for one destructive test case"
    )
    prepare_parser.add_argument("case_id")
    prepare_parser.add_argument("--adapter", choices=("copilot", "codex"), required=True)
    prepare_parser.add_argument("--source", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.add_argument("--result", type=Path)

    summary_parser = subparsers.add_parser(
        "summary", help="Summarize recorded real-host results"
    )
    summary_parser.add_argument("--results", type=Path, default=RESULTS_PATH)

    gate_parser = subparsers.add_parser(
        "release-gate", help="Require all P0 real-host cases to pass"
    )
    gate_parser.add_argument("--results", type=Path, default=RESULTS_PATH)

    subparsers.add_parser("verify", help="Verify the case catalog and Prompt set")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        cases = load_cases()
        if args.command == "list":
            command_list(args, cases)
        elif args.command == "show":
            command_show(args, cases)
        elif args.command == "export":
            command_export(cases)
        elif args.command == "init":
            command_init(args)
        elif args.command == "snapshot":
            command_snapshot(args)
        elif args.command == "prepare":
            command_prepare(args, cases)
        elif args.command == "summary":
            command_summary(args, cases)
        elif args.command == "release-gate":
            return command_release_gate(args, cases)
        elif args.command == "verify":
            command_verify(cases)
        else:
            parser.error(f"Unsupported command: {args.command}")
    except (FileExistsError, FileNotFoundError, KeyError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
