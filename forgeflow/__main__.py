"""Allow `python -m forgeflow` invocation."""
from forgeflow.cli.main import main_cli

raise SystemExit(main_cli())
