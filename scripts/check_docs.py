#!/usr/bin/env python3
"""Check repository Markdown links and documented Python CLI/config names.

No network or third-party dependencies. Checks public Markdown (outside .forgeflow)
using Git's tracked/unignored file list. Supports inline links, explicit reference
links, ATX/setext headings and explicit HTML anchors; this is not a Markdown renderer.
External URLs are deliberately not requested. Targets inside .forgeflow are read only.
"""
import html
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def prose(text):
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            mark = match.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            result.append("")
        else:
            result.append(line if fence is None else "")
    return "\n".join(result)


def anchors(text):
    text = prose(text)
    used = set()
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        title = match.group(1) if match else None
        if title is None and index + 1 < len(lines) and line.strip():
            if re.fullmatch(r" {0,3}(?:=+|-+)\s*", lines[index + 1]):
                title = line.strip()
        if title is None:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", title)
        title = html.unescape(re.sub(r"<[^>]+>", "", title)).lower()
        base = re.sub(r"[^\w\- ]", "", title).replace(" ", "-")
        slug, suffix = base, 0
        while slug in used:
            suffix += 1
            slug = f"{base}-{suffix}"
        used.add(slug)
    used.update(re.findall(r'<(?:a|h[1-6])\b[^>]*(?:id|name)=["\']([^"\']+)', text))
    return used


def check_links(paths, root):
    errors, count = [], 0
    cache = {}
    for source in paths:
        text = prose(source.read_text(encoding="utf-8"))
        definitions = dict(re.findall(r'^ {0,3}\[([^]]+)\]:\s*<?([^\s>]+)>?', text, re.M))
        definitions = {key.casefold(): value for key, value in definitions.items()}
        destinations = re.findall(r'\]\(<?([^\s)>]+)>?(?:\s+["\'][^\n]*?["\'])?\)', text)
        for label, ref in re.findall(r'\[([^]\n]+)\]\[([^]\n]*)\]', text):
            key = (ref or label).casefold()
            if key not in definitions:
                errors.append(f"{source.relative_to(root)}: undefined reference [{key}]")
            else:
                destinations.append(definitions[key])
        for destination in destinations:
            url = urlsplit(destination)
            if url.scheme or url.netloc:
                continue
            count += 1
            target = (source.parent / unquote(url.path)).resolve() if url.path else source.resolve()
            if url.path.startswith("/"):
                target = (root / unquote(url.path).lstrip("/")).resolve()
            reason = None
            if not target.exists():
                reason = "missing target"
            elif url.fragment and target.suffix.lower() == ".md":
                if target not in cache:
                    cache[target] = anchors(target.read_text(encoding="utf-8"))
                if unquote(url.fragment) not in cache[target]:
                    reason = "missing Markdown anchor"
            if reason:
                errors.append(f"{source.relative_to(root)}: {reason}: {destination}")
    return errors, count


def check_reference(root):
    reference = (root / "docs/reference/cli.md").read_text(encoding="utf-8")
    env = {**os.environ, "PYTHONPATH": str(root / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
    env.pop("FORGEFLOW_LOG_DIR", None)

    def help_text(*args):
        return subprocess.check_output(
            [sys.executable, "-m", "forgeflow", *args, "--help"],
            cwd=root, env=env, text=True,
        )

    commands = re.search(r"\{([a-z,]+)\}", help_text()).group(1).split(",")
    errors = []
    for command in commands:
        row = next((line for line in reference.splitlines()
                    if line.startswith(f"| `forge {command}` |")), "")
        if not row:
            errors.append(f"CLI reference: missing command {command}")
        for option in set(re.findall(r"(?<!\w)--[a-z][a-z-]*", help_text(command))) - {"--help"}:
            if f"`{option}`" not in row:
                errors.append(f"CLI reference: missing {command} option {option}")

    sys.path.insert(0, str(root / "src"))
    from forgeflow.engine.yaml_parser import YAMLParser
    for field in YAMLParser._ALLOWED:
        if not re.search(rf"^\| `{re.escape(field)}` \|", reference, re.M):
            errors.append(f"CLI reference: missing config field {field}")
    return errors


def main():
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    ).decode().split("\0")
    paths = [ROOT / name for name in sorted(set(names))
             if name.endswith(".md") and not name.startswith(".forgeflow/")
             and (ROOT / name).is_file()]
    errors, count = check_links(paths, ROOT)
    errors.extend(check_reference(ROOT))
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Documentation: {len(paths)} Markdown files, {count} local links, "
          f"CLI/config name coverage, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
