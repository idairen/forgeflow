"""ForgeFlow YAML/JSON config parser."""
import json
import os
from typing import Any

from ..logging_config import get_logger

logger = get_logger()


class WorkflowConfig:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.title = kwargs.get("title", "")
        self.prompt_file = kwargs.get("prompt_file", "")
        self.artifact = kwargs.get("artifact", "")
        self.scope = kwargs.get("scope", "")
        self.auto_next = kwargs.get("auto_next")
        self.loops = kwargs.get("loops", False)
        self.on_blocker_return = kwargs.get("on_blocker_return", {})


class TransitionRule:
    def __init__(self, **kwargs):
        self.rule_id = kwargs.get("rule_id", "")
        self.condition = kwargs.get("condition", "")
        self.forward = kwargs.get("forward")
        self.return_to = kwargs.get("return_to")
        self.loops_back = kwargs.get("loops_back", False)


class ForgeflowConfig:
    def __init__(self, **kwargs):
        self.mode = kwargs.get("mode", "manual")
        self.adapter = kwargs.get("adapter", "copilot")
        self.auto_parallel = kwargs.get("auto_parallel", False)
        self.blocker_timeout_minutes = kwargs.get("blocker_timeout_minutes", 30)
        self.root_artifact_dir = kwargs.get("root_artifact_dir", ".forgeflow/artifacts")
        self.workflows = kwargs.get("workflows", {})
        self.transitions = kwargs.get("transitions", [])
        self.artifacts_cfg = kwargs.get("artifacts", {})
        self.aliases = kwargs.get("aliases", {})

    def get_workflow(self, name):
        return self.workflows.get(name) or WorkflowConfig()


class YAMLParser:
    @staticmethod
    def load(path=None):
        """Load config from forgeflow.json (or default empty config)."""
        if path is None:
            engine_dir = os.path.dirname(__file__)
            proj_root = os.path.abspath(os.path.join(engine_dir, ".."))
            cands = [os.path.join(proj_root, "forgeflow.json")]
            for c in cands:
                if os.path.exists(c):
                    path = c
                    break
            if path is None:
                logger.debug("No forgeflow.json found; using empty config")
                return ForgeflowConfig()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Failed to load forgeflow.json: %s", e)
            return ForgeflowConfig()
        workflows = {}
        for name, wf in data.get("workflows", {}).items():
            try:
                workflows[name] = WorkflowConfig(**wf)
            except TypeError as e:
                logger.warning("Skipping invalid workflow: %s", e)
        transitions = []
        for tr in data.get("transitions", []):
            try:
                transitions.append(TransitionRule(**tr))
            except TypeError as e:
                logger.warning("Skipping invalid transition rule: %s", e)
        return ForgeflowConfig(
            mode=data.get("mode", "manual"),
            adapter=data.get("adapter", "copilot"),
            auto_parallel=data.get("auto_parallel", False),
            blocker_timeout_minutes=data.get("blocker_timeout_minutes", 30),
            root_artifact_dir=data.get("root_artifact_dir", ".forgeflow/artifacts"),
            workflows=workflows,
            transitions=transitions,
            artifacts_cfg=data.get("artifacts", {}),
            aliases=data.get("aliases", {}),
        )

    @staticmethod
    def match_transition_rule(context=None):
        if not context:
            return None
        return None
