#!/usr/bin/env python3
"""Prepare and inspect ForgeFlow IDE acceptance-test workspaces."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PLAN_PATH = REPOSITORY_ROOT / "docs" / "forgeflow-ide-test-plan.zh-CN.md"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "python-project"
FRAMEWORK_ENTRIES = (
    "forgeflow.md",
    "forgeflow.schema.json",
    "adapter",
    "protocol",
    "rules",
    "workflow",
)
WORKFLOWS = ("plan", "grill", "solution", "slice", "tdd", "review")
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
    "TDD": "TDD",
    "REV": "Review 与插件",
    "HO": "Handoff 与转换",
    "BLK": "Blocker 与 Recovery",
    "INC": "同项目增量",
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
    return f"""# {case.case_id} Test Result

## Case

| Field | Value |
|---|---|
| Area | {AREA_NAMES[case.area]} |
| Priority | {case.priority} |
| Adapter | {adapter} |
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
        else output.parent / f"{output.name}.{case.case_id}.result.md"
    )
    if result_path.exists() or result_path.is_symlink():
        raise FileExistsError(f"Result file already exists: {result_path}")
    result_path.write_text(render_result(case, args.adapter), encoding="utf-8")
    print(f"Prepared case workspace: {output}")
    print(f"Created result record: {result_path}")
    print(f"Recommended baseline: {case.baseline}")


def command_verify(cases: dict[str, Case]) -> None:
    if len(cases) != 215:
        raise ValueError(f"Expected 215 cases, found {len(cases)}")

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
        "Verified 215 IDE cases and 12 workflow Prompts "
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
