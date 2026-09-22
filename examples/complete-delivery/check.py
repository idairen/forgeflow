#!/usr/bin/env python3
"""Run actual tutorial checks; never generate ForgeFlow Review/IDE evidence."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def run():
    with tempfile.TemporaryDirectory(prefix="forgeflow-example-") as directory:
        target = Path(directory)
        shutil.copytree(ROOT / "tests", target / "tests")
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        environment.pop("PYTHONPATH", None)
        for stage in ("starter", "reference"):
            shutil.copy2(ROOT / stage / "inventory.py", target / "inventory.py")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                cwd=target, env=environment, text=True, capture_output=True,
                timeout=30,
            )
            print(f"\n=== {stage}: exit={result.returncode} ===", flush=True)
            print(result.stdout + result.stderr, end="", flush=True)
            if stage == "starter":
                expected = ("test_insufficient_stock_leaves_every_balance_unchanged",
                            "test_unknown_source_does_not_create_a_balance")
                if result.returncode != 1 or "FAILED (failures=2)" not in result.stderr:
                    raise SystemExit("Starter did not fail in the expected behavioral checks")
                if not all(f"FAIL: {name}" in result.stderr for name in expected):
                    raise SystemExit("Unexpected starter failure")
            elif result.returncode != 0 or "Ran 8 tests" not in result.stderr:
                raise SystemExit("Reference implementation did not pass all checks")
    print("Example checks passed: two expected starter failures, eight reference successes.")
    print("This is executable teaching material, not independent Review or IDE acceptance.")


if __name__ == "__main__":
    run()
