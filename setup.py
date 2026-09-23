"""Build hooks for embedding the ForgeFlow Markdown framework."""
from pathlib import Path
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


FRAMEWORK_ENTRIES = (
    "forgeflow.md",
    "forgeflow.schema.json",
    "adapter",
    "protocol",
    "rules",
    "workflow",
)


class BuildPy(_build_py):
    def run(self):
        super().run()
        project_root = Path(__file__).parent
        target_root = Path(self.build_lib) / "forgeflow" / "_template"
        if target_root.exists():
            shutil.rmtree(target_root)
        framework_target = target_root / ".forgeflow"
        framework_target.mkdir(parents=True, exist_ok=True)
        for entry in FRAMEWORK_ENTRIES:
            source = project_root / ".forgeflow" / entry
            target = framework_target / entry
            if source.is_dir():
                shutil.copytree(
                    source,
                    target,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".DS_Store"),
                )
            else:
                shutil.copy2(source, target)
        shutil.copy2(project_root / "forgeflow.json", target_root / "forgeflow.json")


setup(cmdclass={"build_py": BuildPy})
