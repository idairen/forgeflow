"""Project scaffolding from the framework bundled with ForgeFlow."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

from .engine.yaml_parser import YAMLParser


FRAMEWORK_ENTRIES = (
    "forgeflow.md",
    "forgeflow.schema.json",
    "adapter",
    "protocol",
    "rules",
    "workflow",
)
LEGACY_MANAGED_ENTRIES = ("compatibility.md", "conformance", "workflow/tdd.md",
                          "adapter/codex/forge-tdd.prompt.md", "adapter/copilot/forge-tdd.prompt.md")


def initialize_project(project_root, adapter, force=False):
    """Install or refresh ForgeFlow framework files in a project."""
    project = Path(project_root).resolve()
    project.mkdir(parents=True, exist_ok=True)
    template = _template_root()
    framework_source = template / ".forgeflow"
    config_source = template / "forgeflow.json"
    framework_target = project / ".forgeflow"
    config_target = project / "forgeflow.json"

    conflicts = [
        str(path)
        for path in (framework_target, config_target)
        if path.exists() or path.is_symlink()
    ]
    if conflicts and not force:
        raise FileExistsError(
            "ForgeFlow project files already exist; use --force to refresh: "
            + ", ".join(conflicts)
        )
    if framework_target.is_symlink():
        raise RuntimeError(
            f"Refusing to initialize through symbolic link: {framework_target}"
        )
    if force and framework_target.is_dir():
        _reject_nested_symlinks(framework_target)

    config = _load_config(config_source)
    if force and config_target.is_file():
        existing_config = _load_config(config_target)
        for key in config:
            if key in existing_config:
                config[key] = existing_config[key]
    config["adapter"] = adapter
    YAMLParser.validate(config)

    if framework_source.resolve() != framework_target.resolve():
        if framework_target.exists():
            _copy_framework(framework_source, framework_target)
            framework_action = "refreshed"
        else:
            staging = project / f".forgeflow.init-{uuid.uuid4().hex}"
            try:
                _copy_framework(framework_source, staging)
                staging.rename(framework_target)
            except Exception:
                shutil.rmtree(staging, ignore_errors=True)
                raise
            framework_action = "created"
    else:
        framework_action = "source"

    if force:
        _remove_legacy_managed_entries(framework_target)

    _write_json_atomic(config_target, config)

    return {
        "project_root": str(project),
        "framework": framework_action,
        "config": str(config_target),
        "adapter": adapter,
        "framework_files": _framework_file_count(framework_target),
    }


def _template_root():
    package_template = Path(__file__).parent / "_template"
    if (package_template / ".forgeflow" / "forgeflow.md").is_file():
        return package_template
    source_root = Path(__file__).resolve().parents[2]
    if (source_root / ".forgeflow" / "forgeflow.md").is_file():
        return source_root
    raise RuntimeError("Bundled ForgeFlow framework resources are missing")


def _copy_framework(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for entry in FRAMEWORK_ENTRIES:
        source_path = source / entry
        target_path = target / entry
        if source_path.is_dir():
            shutil.copytree(
                source_path,
                target_path,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".DS_Store"),
            )
        else:
            shutil.copy2(source_path, target_path)


def _load_config(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Invalid ForgeFlow configuration at {path}: {error}"
        ) from error
    if not isinstance(data, dict):
        raise ValueError(f"ForgeFlow configuration must be an object: {path}")
    return data


def _remove_legacy_managed_entries(framework_root):
    for relative in LEGACY_MANAGED_ENTRIES:
        path = framework_root / relative
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists() or path.is_symlink():
            path.unlink()


def _reject_nested_symlinks(framework_root):
    for path in framework_root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(
                f"Refusing to refresh framework containing symbolic link: {path}"
            )


def _write_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _framework_file_count(root):
    count = 0
    for entry in FRAMEWORK_ENTRIES:
        path = root / entry
        if path.is_file():
            count += 1
        else:
            count += sum(1 for child in path.rglob("*") if child.is_file())
    return count
