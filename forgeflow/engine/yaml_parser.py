"""Strict ForgeFlow JSON configuration parser."""
from dataclasses import dataclass
import json
from pathlib import Path


class ConfigError(ValueError):
    """A missing or invalid ForgeFlow project configuration."""


@dataclass(frozen=True)
class ForgeflowConfig:
    mode: str
    adapter: str
    root_artifact_dir: str
    model: str | None = None
    execution_timeout_seconds: int | float = 900


class YAMLParser:
    """Compatibility name for the strict forgeflow.json parser."""

    _REQUIRED = {"mode", "adapter", "root_artifact_dir"}
    _ALLOWED = _REQUIRED | {"model", "execution_timeout_seconds"}

    @classmethod
    def load(cls, path):
        """Load and validate an initialized project's forgeflow.json."""
        if path is None:
            raise ConfigError("A forgeflow.json path is required")
        config_path = Path(path)
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise ConfigError(
                f"ForgeFlow configuration not found at {config_path}; "
                "run 'forge init' first"
            ) from error
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ConfigError(
                f"Unable to read ForgeFlow configuration at {config_path}: {error}"
            ) from error

        return cls.validate(data)

    @classmethod
    def validate(cls, data):
        """Validate already-decoded configuration data."""

        if not isinstance(data, dict):
            raise ConfigError("forgeflow.json must contain a JSON object")
        missing = sorted(cls._REQUIRED - data.keys())
        if missing:
            raise ConfigError(
                "forgeflow.json is missing required fields: " + ", ".join(missing)
            )
        unknown = sorted(data.keys() - cls._ALLOWED)
        if unknown:
            raise ConfigError(
                "forgeflow.json contains unsupported fields: " + ", ".join(unknown)
            )

        mode = data["mode"]
        if mode not in {"auto", "manual"}:
            raise ConfigError("mode must be 'auto' or 'manual'")
        adapter = data["adapter"]
        if adapter not in {"codex", "copilot"}:
            raise ConfigError("adapter must be 'codex' or 'copilot'")
        artifact_root = data["root_artifact_dir"]
        if artifact_root != ".forgeflow/artifacts":
            raise ConfigError(
                "root_artifact_dir must be the canonical '.forgeflow/artifacts'"
            )

        model = data.get("model")
        if model is not None and (
            not isinstance(model, str) or not model.strip()
        ):
            raise ConfigError("model must be a non-empty string or null")
        timeout = data.get("execution_timeout_seconds", 900)
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise ConfigError("execution_timeout_seconds must be a positive number")

        return ForgeflowConfig(
            mode=mode,
            adapter=adapter,
            root_artifact_dir=artifact_root,
            model=model,
            execution_timeout_seconds=timeout,
        )
