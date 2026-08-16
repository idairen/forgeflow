"""ForgeFlow CLI - AI-driven development workflow orchestrator."""
import argparse
import asyncio
import json
import os
import shutil
import sys

from ..engine.runner import ForgeRunner
from ..engine.config import EngineConfig, ForgeflowLoader
from ..logging_config import get_logger

logger = get_logger()


def _make_runner():
    """Create a new runner."""
    return ForgeRunner()


# --- CLI subcommands ---

def cmd_plan(args):
    """Execute Plan workflow."""
    logger.info("Executing plan%s",
                  f" with intent={args.intent}" if getattr(args, "intent", None) else "")
    runner = _make_runner()
    try:
        result = asyncio.run(runner._execute_llm("plan"))
        print(result)
    except Exception as e:
        logger.error("[plan] Failed: %s", e)
        print(f"[ERROR] Plan failed: {e}", file=sys.stderr)


def cmd_run(args):
    """Start the ForgeFlow pipeline."""
    reset = getattr(args, "reset", False)
    no_auto = getattr(args, "no_auto", False)
    auto_mode = not no_auto

    if reset:
        artifacts_dir = ".forgeflow/artifacts"
        if os.path.exists(artifacts_dir):
            shutil.rmtree(artifacts_dir)
        os.makedirs(artifacts_dir, exist_ok=True)
        logger.info("[reset] Cleaned artifacts/")

    runner = _make_runner()
    state = runner.get_state()
    logger.info(
          "ForgeFlow pipeline: mode=%s adapter=%s",
        state["config_mode"], state["adapter"]
      )

    if auto_mode:
        logger.info("[auto-mode] Starting... Ctrl+C to pause.")
        try:
            result = asyncio.run(runner.run())
            print(f"\nPipeline result: {result}")
            print("\nExecution History:")
            runner.print_history()
        except KeyboardInterrupt:
            logger.info("[auto-mode] Paused by user.")
            state = runner.get_state()
            print(json.dumps(state, indent=2))
        except Exception as e:
            logger.error("[auto-mode] Pipeline crashed: %s", e)
            print(f"[ERROR] Pipeline crashed: {e}", file=sys.stderr)
    else:
        logger.info("[manual-mode] Running Plan workflow...")
        try:
            result = asyncio.run(runner._execute_llm("plan"))
            print(result)
        except Exception as e:
            logger.error("[manual-mode] Failed: %s", e)
            print(f"[ERROR] Plan failed: {e}", file=sys.stderr)


def cmd_status(args):
    """Show current pipeline state and artifacts."""
    runner = _make_runner()
    state = runner.get_state()
    logger.info("Status: %s", json.dumps(state, indent=2))
    print(json.dumps(state, indent=2))


def cmd_reset(args):
    """Clean up artifacts/."""
    force = getattr(args, "force", False)
    if force:
        artifacts_dir = ".forgeflow/artifacts"
        if os.path.exists(artifacts_dir):
            shutil.rmtree(artifacts_dir)
        os.makedirs(artifacts_dir, exist_ok=True)
        logger.info("[reset] artifacts/ cleaned.")
        print("[reset] artifacts/ cleaned.")
    else:
        logger.info("[reset] Dry-run mode. Use --force to clean.")
        print("   [info] Use --force to actually clean.")


def cmd_init(args):
    """Initialize a new ForgeFlow project."""
    adapter = getattr(args, "adapter", None) or "copilot"
    logger.info("Initializing ForgeFlow project with adapter=%s", adapter)
    
    # Set adapter in forgeflow.json (single data source)
    ForgeflowLoader.set_adapter(adapter)
    logger.info("[init] Adapter set to %s in forgeflow.json", adapter)
    
    print(f"[success] ForgeFlow project initialized with adapter={adapter}.")




def cmd_handoff(args):
    """Display the latest handoff from artifacts/."""
    runner = _make_runner()
    import pathlib
    root = pathlib.Path(runner.artifacts_dir)
    if not root.exists():
        print("[info] No artifacts directory found.")
        return
    try:
        for f in sorted(root.rglob("*.md"), key=os.path.getmtime, reverse=True):
            ct = f.read_text(encoding="utf-8")
            if "Handoff" in ct or "handoff" in ct.lower():
                print(f"Latest handoff: {f.name}")
                hlines = [l for l in ct.split("\n") if not l.startswith("#") and l.strip()]
                print("\n".join(hlines[:30]))
                return
        print("[info] No handoff files found.")
    except Exception as e:
        logger.error("Failed to read latest handoff: %s", e)
        print(f"[error] {e}")


# --- CLI entry point ---

def main_cli():
    """ForgeFlow CLI - plan, run, status, reset, init."""
    parser = argparse.ArgumentParser(
        prog="forge",
        description="ForgeFlow CLI - AI-driven development workflow orchestrator"
      )
    subparsers = parser.add_subparsers(dest="command")

    # plan
    p_plan = subparsers.add_parser("plan", help="Execute Plan workflow")
    p_plan.add_argument("--intent", "-i", help="Project intent description")
    p_plan.set_defaults(func=cmd_plan)

    # run
    p_run = subparsers.add_parser("run", help="Start the ForgeFlow pipeline")
    p_run.add_argument(
        "--auto-mode", action="store_true", default=True,
        help="Auto-mode: loop until blocked. Manual: one step at a time."
     )
    p_run.add_argument(
        "--no-auto", action="store_true", default=False,
        help="Disable auto-mode (manual mode)"
     )
    p_run.add_argument(
        "--reset", action="store_true", default=False,
        help="Reset artifacts/ before running"
     )
    p_run.set_defaults(func=cmd_run)

    # status
    p_status = subparsers.add_parser(
        "status", help="Show current pipeline state and artifacts"
     )
    p_status.set_defaults(func=cmd_status)

    # reset
    p_reset = subparsers.add_parser("reset", help="Clean up artifacts/")
    p_reset.add_argument(
        "--force", action="store_true", default=False,
        help="Remove all artifacts/"
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
        help="Overwrite existing config"
     )
    p_init.set_defaults(func=cmd_init)

    # handoff (NEW - debug tool)
    p_handoff = subparsers.add_parser(
        "handoff", help="Show the latest handoff from artifacts/"
     )
    p_handoff.set_defaults(func=cmd_handoff)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except Exception as e:
        logger.error("[cli] Unhandled error: %s", e)
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
