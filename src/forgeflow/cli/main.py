"""ForgeFlow CLI - Python orchestrator for the ForgeFlow control protocol."""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from ..engine.runner import ForgeRunner
from ..engine.project_knowledge import ProjectKnowledgeBuilder
from ..scaffold import initialize_project
from ..logging_config import get_logger

logger = get_logger()

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INCOMPLETE = 2
EXIT_INTERRUPTED = 130


def _make_runner():
    """Create a new runner."""
    return ForgeRunner()


# --- CLI subcommands ---

def cmd_plan(args):
    """Execute Plan workflow."""
    intent = getattr(args, "intent", None)
    incremental = getattr(args, "incremental", False)
    if incremental and not (intent or "").strip():
        raise ValueError("--incremental requires --intent")
    logger.info(
        "Executing plan%s%s",
        " with User Intent" if intent else "",
        " (legacy --incremental alias)" if incremental else "",
    )
    runner = _make_runner()
    result = asyncio.run(
        runner.execute_single(
            "plan",
            user_input=intent,
            incremental=incremental,
            handoff_text=Path(args.handoff).read_text(encoding="utf-8") if getattr(args, "handoff", None) else None,
        )
    )
    print(result)
    return _single_exit_code(runner)


def cmd_workflow(args):
    """Execute one entry, or emit a read-only correction when authorization is absent."""
    runner = _make_runner()
    incoming = Path(args.handoff).read_text(encoding="utf-8") if args.handoff else None
    result = asyncio.run(runner.execute_single(args.command, handoff_text=incoming,
                                              confirm_inactive=args.confirm_inactive,
                                              feature=getattr(args, "feature", None)))
    print(result)
    return _single_exit_code(runner)


def cmd_run(args):
    """Start the ForgeFlow pipeline."""
    reset = getattr(args, "reset", False)
    intent = getattr(args, "intent", None)
    runner = _make_runner()

    if reset:
        rotation = runner.reset_artifacts()
        logger.info("[reset] %s", json.dumps(rotation))

    state = runner.get_state()
    run_mode = getattr(args, "run_mode", None) or state["config_mode"]
    logger.info(
          "ForgeFlow pipeline: mode=%s adapter=%s",
        run_mode, state["adapter"]
      )

    if run_mode == "auto":
        logger.info("[auto-mode] Starting... Ctrl+C to pause.")
        try:
            result = asyncio.run(runner.run(initial_intent=intent))
            print(f"\nPipeline result: {result}")
            print("\nExecution History:")
            runner.print_history()
            return _pipeline_exit_code(result)
        except KeyboardInterrupt:
            logger.info("[auto-mode] Paused by user.")
            state = runner.get_state()
            print(json.dumps(state, indent=2))
            return EXIT_INTERRUPTED
    else:
        logger.info("[manual-mode] Running Plan workflow...")
        result = asyncio.run(
            runner.execute_single("plan", user_input=intent)
        )
        print(result)
        return _single_exit_code(runner)


def cmd_status(args):
    """Show current pipeline state and artifacts."""
    runner = _make_runner()
    state = runner.get_state()
    logger.info("Status: %s", json.dumps(state, indent=2))
    print(json.dumps(state, indent=2))
    return EXIT_SUCCESS


def cmd_knowledge(args):
    """Query the derived, non-authoritative project knowledge view."""
    state = _make_runner().get_state(include_history=getattr(args, "history", False))
    view = ProjectKnowledgeBuilder.select(
        state["project_knowledge"],
        feature_id=getattr(args, "feature", None),
        slice_scope=getattr(args, "slice_scope", None),
        include_history=getattr(args, "history", False),
        impact_feature=getattr(args, "impact", None),
        component_id=getattr(args, "component", None),
    )
    if getattr(args, "format", "json") == "markdown":
        print(ProjectKnowledgeBuilder.render_markdown(view), end="")
    else:
        print(json.dumps(view, ensure_ascii=False, indent=2))
    return EXIT_SUCCESS


def cmd_reset(args):
    """Rotate active project evidence."""
    force = getattr(args, "force", False)
    if force:
        rotation = _make_runner().reset_artifacts()
        logger.info("[reset] %s", json.dumps(rotation))
        print(json.dumps(rotation, indent=2))
    else:
        logger.info("[reset] Dry-run mode. Use --force to rotate.")
        print("[info] Use --force to rotate active artifacts and reports.")
    return EXIT_SUCCESS


def cmd_init(args):
    """Initialize a new ForgeFlow project."""
    adapter = getattr(args, "adapter", None) or "copilot"
    logger.info("Initializing ForgeFlow project with adapter=%s", adapter)
    result = initialize_project(
        project_root=os.getcwd(),
        adapter=adapter,
        force=getattr(args, "force", False),
    )
    logger.info("[init] %s", json.dumps(result))
    print(json.dumps(result, indent=2))
    return EXIT_SUCCESS

def cmd_handoff(args):
    """Display the latest handoff produced by the CLI runner."""
    runner = _make_runner()
    handoff = runner.get_latest_handoff()
    if handoff is None:
        print("[info] No valid runtime handoff found.")
        return EXIT_ERROR
    print(json.dumps(handoff, ensure_ascii=False, indent=2))
    return EXIT_SUCCESS


def _pipeline_exit_code(result):
    try:
        summary = json.loads(result)
    except (TypeError, json.JSONDecodeError) as error:
        raise RuntimeError("Runner returned an invalid pipeline summary") from error
    if summary.get("result") == "PIPELINE_COMPLETE":
        return EXIT_SUCCESS
    return EXIT_INCOMPLETE


def _single_exit_code(runner):
    if not runner.history:
        raise RuntimeError("Runner did not record the single workflow execution")
    result = runner.history[-1].get("result")
    if result in {"STEP_COMPLETE", "PIPELINE_COMPLETE"}:
        return EXIT_SUCCESS
    return EXIT_INCOMPLETE


# --- CLI entry point ---

def main_cli(argv=None):
    """ForgeFlow CLI - execution, state, and knowledge commands."""
    parser = argparse.ArgumentParser(
        prog="forge",
        description="ForgeFlow CLI - repository-native AI delivery orchestrator"
      )
    subparsers = parser.add_subparsers(dest="command")

    # plan
    p_plan = subparsers.add_parser("plan", help="Execute Plan workflow")
    p_plan.add_argument("--intent", "-i", help="Project intent description")
    p_plan.add_argument("--handoff", help="File containing a canonical Plan Handoff")
    p_plan.add_argument(
        "--incremental",
        action="store_true",
        default=False,
        help=(
            "Deprecated compatibility flag; --intent already starts a subsequent "
            "Plan change when Planning exists"
        ),
    )
    p_plan.set_defaults(func=cmd_plan)

    for workflow in ("grill", "solution", "slice", "implement", "review"):
        command = subparsers.add_parser(workflow, help=f"Execute one authorized {workflow.capitalize()} scope")
        command.add_argument("--handoff", help="File containing the complete canonical Handoff from a prior invocation")
        if workflow == "grill":
            command.add_argument("--feature", help="Explicit no-Handoff Lane/Recovery entry for one Feature, e.g. F-01")
        command.add_argument("--confirm-inactive", action="store_true", help="Confirm the exact prior Grill blocker claim's execution has stopped")
        command.set_defaults(func=cmd_workflow)

    # run
    p_run = subparsers.add_parser("run", help="Start the ForgeFlow pipeline")
    mode_group = p_run.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--auto", "--auto-mode",
        dest="run_mode",
        action="store_const",
        const="auto",
        help="Run automatically until complete, blocked, or halted"
     )
    mode_group.add_argument(
        "--manual", "--no-auto",
        dest="run_mode",
        action="store_const",
        const="manual",
        help="Execute only the Plan workflow"
     )
    p_run.add_argument(
        "--reset", action="store_true", default=False,
        help="Rotate active artifacts and supplemental reports before running"
     )
    p_run.add_argument(
        "--intent", "-i",
        help="User Intent supplied to the initial Plan invocation"
     )
    p_run.set_defaults(func=cmd_run)

    # status
    p_status = subparsers.add_parser(
        "status", help="Show current pipeline state and artifacts"
     )
    p_status.set_defaults(func=cmd_status)

    # knowledge
    p_knowledge = subparsers.add_parser(
        "knowledge",
        help="Query the derived Project Knowledge View",
    )
    p_knowledge.add_argument(
        "--feature",
        help="Limit output to one active Feature using F-XX",
    )
    p_knowledge.add_argument(
        "--slice",
        dest="slice_scope",
        help="Limit output to one active Slice using F-XX/S-XX",
    )
    p_knowledge.add_argument(
        "--history",
        action="store_true",
        default=False,
        help="Include historical indexes and contract timeline entries",
    )
    p_knowledge.add_argument(
        "--impact",
        help="Analyze dependents and shared-component relationships for F-XX",
    )
    p_knowledge.add_argument(
        "--component",
        help="List active Features mapped to one shared component using SC-XX",
    )
    p_knowledge.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    p_knowledge.set_defaults(func=cmd_knowledge)

    # reset
    p_reset = subparsers.add_parser(
        "reset", help="Rotate active artifacts and supplemental reports"
    )
    p_reset.add_argument(
        "--force", action="store_true", default=False,
        help="Archive active project evidence and create empty evidence roots"
     )
    p_reset.set_defaults(func=cmd_reset)

    # init (NEW)
    p_init = subparsers.add_parser("init", help="Initialize a new ForgeFlow project")
    p_init.add_argument(
        "--adapter", "-a", choices=["copilot", "codex"], default="copilot",
        help="IDE adapter to use (default: copilot)"
     )
    p_init.add_argument(
        "--force", action="store_true", default=False,
        help="Refresh managed framework files and preserve project artifacts"
     )
    p_init.set_defaults(func=cmd_init)

    # handoff (debug tool)
    p_handoff = subparsers.add_parser(
        "handoff", help="Show the latest handoff produced by the CLI runner"
     )
    p_handoff.set_defaults(func=cmd_handoff)

    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return EXIT_SUCCESS

    try:
        result = args.func(args)
        return result if isinstance(result, int) else EXIT_SUCCESS
    except KeyboardInterrupt:
        logger.info("[cli] Interrupted by user.")
        return EXIT_INTERRUPTED
    except Exception as e:
        logger.error("[cli] Unhandled error: %s", e)
        print(f"[ERROR] {e}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main_cli())
