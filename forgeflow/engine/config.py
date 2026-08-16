"""ForgeFlow Engine Configuration & Host CLI Auto-detection."""
import json
import os


class ForgeflowLoader:
    """Load adapter from forgeflow.json (single data source)."""
    
    DEFAULT_ADAPTER = "copilot"
    
    @staticmethod
    def get_adapter():
        try:
            path = os.path.join(os.getcwd(), "forgeflow.json")
            if not os.path.exists(path):
                return ForgeflowLoader.DEFAULT_ADAPTER
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("adapter", ForgeflowLoader.DEFAULT_ADAPTER)
        except (FileNotFoundError, json.JSONDecodeError):
            return ForgeflowLoader.DEFAULT_ADAPTER

    @staticmethod
    def set_adapter(adapter_name):
        try:
            path = os.path.join(os.getcwd(), "forgeflow.json")
            if not os.path.exists(path):
                data = {}
            else:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data["adapter"] = adapter_name
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: failed to update forgeflow.json: {e}")


class EngineConfig:
    _ENV_SIGS = {
        "copilot": ["GITHUB_TOKEN", "VS_CODE_EXTENSION"],
        "codex": ["CODEX_CLI", "CODEX_HOME"],
        "gemini": ["GOOGLE_API_KEY", "GEMINI_CLI"],
        "claude": ["ANTHROPIC_API_KEY", "CLAUDE_CLI"],
    }

    @classmethod
    def detect_host(cls):
        for host, keys in cls._ENV_SIGS.items():
            if any(os.environ.get(k) for k in keys):
                return host
        return None

    @staticmethod
    def get_adapter_dir():
        """Get adapter from forgeflow.json (single data source)."""
        adapter = ForgeflowLoader.get_adapter()
        user_override = os.environ.get("FORGEFLOW_ADAPTER")
        if user_override:
            return user_override.lower()
        if adapter and adapter != "copilot":
            return adapter
        host = EngineConfig.detect_host()
        if host:
            return host
        return "copilot"


class PromptResolver:
    def __init__(self, project_root=None):
        self.project_root = project_root or os.getcwd()
        self.adapter_name = EngineConfig.get_adapter_dir()

    def resolve(self, workflow_name, ext=".prompt.md"):
        adapter_path = os.path.join(
            ".forgeflow", "adapter", self.adapter_name
        )
        return os.path.join(adapter_path, f"{workflow_name}{ext}")

    def get_adapter_name(self):
        return self.adapter_name
