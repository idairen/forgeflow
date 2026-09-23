import json
import tempfile
import unittest
from pathlib import Path

from forgeflow.engine.yaml_parser import ConfigError, YAMLParser


class ConfigTests(unittest.TestCase):
    def test_loads_canonical_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "forgeflow.json"
            path.write_text(
                json.dumps(
                    {
                        "mode": "manual",
                        "adapter": "codex",
                        "root_artifact_dir": ".forgeflow/artifacts",
                        "model": "example-model",
                        "execution_timeout_seconds": 30,
                    }
                ),
                encoding="utf-8",
            )

            config = YAMLParser.load(path)

        self.assertEqual(config.mode, "manual")
        self.assertEqual(config.adapter, "codex")
        self.assertEqual(config.execution_timeout_seconds, 30)

    def test_rejects_unknown_missing_and_invalid_fields(self):
        valid = {
            "mode": "auto",
            "adapter": "copilot",
            "root_artifact_dir": ".forgeflow/artifacts",
        }
        invalid = [
            {**valid, "unknown": True},
            {key: value for key, value in valid.items() if key != "adapter"},
            {**valid, "mode": "automatic"},
            {**valid, "adapter": "claude"},
            {**valid, "root_artifact_dir": "artifacts"},
            {**valid, "execution_timeout_seconds": 0},
            {**valid, "model": ""},
        ]

        for candidate in invalid:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ConfigError):
                    YAMLParser.validate(candidate)

    def test_missing_and_malformed_files_raise_config_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(ConfigError):
                YAMLParser.load(root / "missing.json")
            malformed = root / "forgeflow.json"
            malformed.write_text("{", encoding="utf-8")
            with self.assertRaises(ConfigError):
                YAMLParser.load(malformed)


if __name__ == "__main__":
    unittest.main()
