"""ForgeFlow Handoff parser."""
import os
import pathlib
from typing import Any

from ..logging_config import get_logger

logger = get_logger()


class HandoffParser:
    @staticmethod
    def parse(text):
        """Parse a handoff block. Returns None if invalid."""
        if "### Handoff" not in text:
            logger.debug("No ### Handoff marker found")
            return None
        result = {}
        for line in text.splitlines():
            stripped = line.strip()
            # Skip the ### Handoff marker and separator rows
             # Skip separator rows (|---|) in addition to ### marker
            if stripped == "### Handoff":
                continue
             # Match separator: line is only pipes, dashes, and spaces
            if all(c in "| -" for c in stripped):
                continue
            # Parse data rows: skip header row (Field | Value)
            if "|" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                # Skip header row -- real keys won't match "field" or "value"
                if len(parts) == 2 and parts[0].lower() not in ("field", "value"):
                    result[parts[0].lower()] = parts[1]
        trans_type = result.get("transition", "").upper()
        if trans_type not in ("FORWARD", "RETURN", "TERMINAL"):
            logger.debug("Invalid transition: %s", trans_type)
            return None
        norm = dict(result.items())
        if "next_workflow" in norm:
            norm["next_wf"] = norm.pop("next_workflow").lower()
        norm["transition_type"] = trans_type
        logger.debug("Parsed handoff: transition=%s", trans_type)
        return norm

    @staticmethod
    def detect_artifact_state(root_dir):
        """Detect what artifacts exist under the root dir."""
        root_path = pathlib.Path(root_dir)
        if not root_path.exists():
            logger.debug("Artifacts directory does not exist: %s", root_dir)
            return {"status": "empty", "root": root_dir, "artifacts": {}}
        artifacts = {}
        for item in sorted(root_path.rglob("*")):
            if item.is_file():
                name = item.name
                artifacts[name] = {"exists": True, "path": str(item),
                                     "status": _guess_status(item)}
        logger.debug("Detected %d artifact(s) in %s", len(artifacts), root_dir)
        if not artifacts:
            return {"status": "empty", "root": root_dir, "artifacts": {}}
        return {"status": "active", "root": root_dir, "artifacts": artifacts}


def _guess_status(path):
    import pathlib
    name = path.name
    if "Plan" in name:
        return "ready"
    if "DONE" in name.upper() or "SUCCESS" in name.upper():
        return "completed"
    return "in_progress"

    @staticmethod
    def check_artifact_exists(artifacts_dir, artifact_name):
        root = pathlib.Path(artifacts_dir)
        for f in root.rglob("*"):
            if f.is_file() and f.name == artifact_name:
                return True
        return False

    @staticmethod
    def get_latest_handoff(artifacts_dir):
        root = pathlib.Path(artifacts_dir)
        if not root.exists():
            return None
        for f in sorted(root.rglob("*.md"), key=os.path.getmtime, reverse=True):
            ct = f.read_text(encoding="utf-8")
            if "Handoff" in ct or "handoff" in ct.lower():
                logger.debug("Found latest handoff at %s", f)
                return HandoffParser.parse(ct)
        logger.debug("No handoff files found in %s", artifacts_dir)
        return None
