#!/usr/bin/env python3
"""Check local release archives against this checkout without extracting them."""
import argparse
import hashlib
import json
import stat
from pathlib import Path, PurePosixPath
import tarfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def load_archive(path):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            entries = []
            for item in archive.infolist():
                if stat.S_ISLNK(item.external_attr >> 16):
                    raise ValueError(f"Non-regular archive member: {item.filename}")
                if not item.is_dir():
                    entries.append((item.filename, archive.read(item)))
    else:
        with tarfile.open(path, "r:gz") as archive:
            entries = []
            for item in archive.getmembers():
                if item.isdir():
                    continue
                if not item.isfile():
                    raise ValueError(f"Non-regular archive member: {item.name}")
                entries.append((item.name, archive.extractfile(item).read()))
    files = {}
    for name, data in entries:
        parts = PurePosixPath(name).parts
        if name.startswith("/") or ".." in parts or "\\" in name or name in files:
            raise ValueError(f"Unsafe/duplicate archive member: {name}")
        if any(part in {".git", ".venv", "__pycache__", ".DS_Store", ".env"}
               or part.startswith(".env.") for part in parts):
            raise ValueError(f"Local-only archive member: {name}")
        if any(part in {"artifacts", "reports", "runtime"}
               or part.startswith(("artifacts.", "reports.")) for part in parts):
            raise ValueError(f"Project evidence in distribution: {name}")
        files[name] = data
    return files


def verify(path, kind, version):
    files = load_archive(path)
    prefix = {"wheel": "forgeflow/_template/", "sdist": f"forgeflow-{version}/",
              "npm": "package/"}[kind]
    expected = [ROOT / "forgeflow.json", ROOT / ".forgeflow/forgeflow.md",
                ROOT / ".forgeflow/forgeflow.schema.json"]
    for directory in ("adapter", "protocol", "rules", "workflow"):
        expected.extend(sorted((ROOT / ".forgeflow" / directory).rglob("*.md")))
    expected_names = set()
    for source in expected:
        name = prefix + source.relative_to(ROOT).as_posix()
        expected_names.add(name)
        if files.get(name) != source.read_bytes():
            raise ValueError(f"Missing/stale bundled file: {name}")
    framework_names = {name for name in files if name.startswith(prefix + ".forgeflow/")}
    if framework_names != {name for name in expected_names if "/.forgeflow/" in name}:
        raise ValueError(f"Unexpected framework template files in {path.name}")
    if not any(PurePosixPath(name).name == "LICENSE" and data == (ROOT / "LICENSE").read_bytes()
               for name, data in files.items()):
        raise ValueError(f"Missing or changed MIT license in {path.name}")
    if kind == "npm":
        package = json.loads(files["package/package.json"])
        if package["version"] != version or package["bin"] != {"forgeflow": "npm/bin/forgeflow.js"}:
            raise ValueError("npm version/entrypoint mismatch")
        if any(name.startswith("package/src/") for name in files):
            raise ValueError("npm must remain installer-only")
    else:
        source_prefix = "forgeflow/" if kind == "wheel" else prefix + "src/forgeflow/"
        for source in (ROOT / "src/forgeflow").rglob("*.py"):
            name = source_prefix + source.relative_to(ROOT / "src/forgeflow").as_posix()
            if files.get(name) != source.read_bytes():
                raise ValueError(f"Missing/stale Python source: {name}")
    return {"artifact": path.name, "files": len(files), "status": "PASS",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for kind in ("wheel", "sdist", "npm"):
        parser.add_argument("--" + kind, required=True, type=Path)
    args = parser.parse_args()
    version = json.loads((ROOT / "package.json").read_text())["version"]
    reports = [verify(getattr(args, kind), kind, version) for kind in ("wheel", "sdist", "npm")]
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
