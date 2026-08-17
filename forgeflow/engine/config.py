"""Project-root-relative ForgeFlow prompt resolution."""
import os


class PromptResolver:
    def __init__(self, project_root, adapter_name):
        if adapter_name not in {"codex", "copilot"}:
            raise ValueError("adapter_name must be 'codex' or 'copilot'")
        self.project_root = os.path.abspath(project_root)
        self.adapter_name = adapter_name

    def resolve(self, workflow_name, ext=".prompt.md"):
        adapter_path = os.path.join(
            self.project_root, ".forgeflow", "adapter", self.adapter_name
        )
        return os.path.join(adapter_path, f"forge-{workflow_name}{ext}")

    def get_adapter_name(self):
        return self.adapter_name
