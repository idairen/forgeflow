"""Bounded implementation counter and invalid-Review disposition evidence."""
import hashlib
import re
from pathlib import Path

from .verification import table


def inspect_attempts(root, record, artifacts, parse_metadata):
    root = Path(root)
    meta = record["metadata"]
    feature, slice_id = meta["Feature ID"][2:], meta["Slice ID"][2:]
    current = int(meta["Attempt"])
    used = {current}
    prefix = f"feature-{feature}-slice-{slice_id}"
    history = root / "history"
    for folder in (history, history / "legacy-tdd", history / "invalid-review"):
        if folder.is_symlink():
            raise ValueError("counter history must not be a symbolic link")
    paths = list(history.glob(f"implement-{prefix}-attempt-*.md"))
    paths += list(history.glob(f"tdd-{prefix}-attempt-*.md"))
    paths += list((history / "legacy-tdd").glob(f"*-{prefix}*.md"))
    records = {("implement", current): Path(record["path"]).read_bytes()}
    for path in paths:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"invalid counter evidence: {path.name}")
        data, errors = parse_metadata(path.read_text(encoding="utf-8"))
        attempt = data.get("Attempt", "")
        if errors or not attempt.isdigit() or int(attempt) <= 0 or data.get("Feature ID") != meta["Feature ID"] or data.get("Slice ID") != meta["Slice ID"]:
            raise ValueError(f"invalid counter identity: {path.name}")
        if "-attempt-" in path.name and not path.name.endswith(f"-attempt-{int(attempt):02d}.md"):
            raise ValueError(f"counter filename mismatch: {path.name}")
        key = (path.name.split("-", 1)[0], int(attempt))
        content = path.read_bytes()
        if key in records and records[key] != content:
            raise ValueError(f"conflicting Attempt history: {path.name}")
        records[key] = content
        used.add(int(attempt))
    for a in artifacts.values():
        m = a["metadata"]
        if a["artifact_type"] == "Review Report" and m.get("Feature ID") == meta["Feature ID"] and m.get("Slice ID") == meta["Slice ID"]:
            used.add(int(m["Attempt"]))
    folder = history / "invalid-review"
    names = set()
    for path in folder.glob(f"review-{prefix}-attempt-*.md"):
        names.add(path.name.replace(".receipt.md", ".md"))
    disposed = False
    for name in sorted(names):
        match = re.fullmatch(r"review-" + re.escape(prefix) + r"-attempt-(0[1-9]|[1-9][0-9]+)\.md", name)
        if not match:
            raise ValueError(f"invalid disposition filename: {name}")
        attempt = int(match.group(1))
        original, receipt = folder / name, folder / name.replace(".md", ".receipt.md")
        if any(p.is_symlink() or not p.is_file() for p in (original, receipt)):
            raise ValueError(f"incomplete invalid-Review pair: {name}")
        content = receipt.read_text(encoding="utf-8")
        # Receipts deliberately have no Artifact Metadata section.
        lines = content.splitlines()
        if not lines or not re.fullmatch(r"# \S.*", lines[0]):
            raise ValueError("invalid recovery receipt title")
        rows = table("## Receipt\n" + "\n".join(lines[1:]), "Receipt", ("Field", "Value"))
        fields = ("Source Filename", "SHA256", "Feature ID", "Slice ID", "Attempt", "Implement Version", "Authorization", "Reason")
        if [r["Field"] for r in rows] != list(fields):
            raise ValueError("invalid recovery receipt fields")
        data = {r["Field"]: r["Value"] for r in rows}
        if data["Source Filename"] != name or data["SHA256"] != hashlib.sha256(original.read_bytes()).hexdigest() or data["Feature ID"] != meta["Feature ID"] or data["Slice ID"] != meta["Slice ID"] or data["Attempt"] != str(attempt):
            raise ValueError("invalid recovery receipt identity or digest")
        if name in artifacts:
            raise ValueError("canonical Review coexists with invalid-Review history")
        if attempt == current:
            if data["Implement Version"] != record["version"]:
                raise ValueError("invalid recovery Implement Version")
            disposed = True
        else:
            prior = history / f"implement-{prefix}-attempt-{attempt:02d}.md"
            if prior.is_symlink() or not prior.is_file():
                raise ValueError("missing archived Implement for disposition")
            prior_meta, errors = parse_metadata(prior.read_text(encoding="utf-8"))
            if errors or prior_meta.get("Version") != data["Implement Version"]:
                raise ValueError("invalid archived Implement for disposition")
        used.add(attempt)
    if max(used) > current:
        raise ValueError("canonical Implement is older than consumed Attempt evidence")
    return {"used_attempts": sorted(used), "next_attempt": max(used) + 1, "review_disposed": disposed}
