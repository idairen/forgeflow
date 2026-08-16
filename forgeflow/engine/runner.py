"""ForgeFlow Auto-mode Runner."""
import asyncio
import json
import os
import shutil
from datetime import datetime, timezone
import pathlib as plib

from .yaml_parser import YAMLParser, ForgeflowConfig, WorkflowConfig, TransitionRule
from .handoff_parser import HandoffParser
from .config import EngineConfig, PromptResolver
from ..logging_config import get_logger

logger = get_logger()


class ForgeRunner:
    def __init__(self, config_path=None):
        self._config_path = config_path or os.path.join(
            os.getcwd(), "forgeflow.json")
        self.config: ForgeflowConfig = YAMLParser.load(self._config_path)
        self.handoff_parser = HandoffParser()
        self.current_workflow = "plan"
        self.history = []
        self.artifacts_dir = self.config.root_artifact_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

        resolver = PromptResolver()
        self.adapter_name = resolver.get_adapter_name()
        logger.info(
              "[forgeflow] Auto-mode initialized | adapter=%s | mode=%s",
            self.adapter_name, self.config.mode,
           )

    async def run(self):
        """Auto-mode pipeline: loop until TERMINAL or max iterations.

        Each iteration:
           1. Detect artifact state for the current workflow.
           2. Execute the workflow via LLM (with retries).
           3. Parse handoff from output.
           4. Apply transition rules (FORWARD / RETURN / TERMINAL).
           5. On persistent failure -> fall back to forgeflow.json rules.

        Returns a JSON summary of the final state.
        """
        logger.info(
              "[forgeflow] Starting auto-mode pipeline "
              "(adapter=%s, max_steps=%d)",
            self.adapter_name, self._max_total_steps(),
           )

        total_max = self._max_total_steps()
        per_wf_max = self._max_failures_per_workflow()

        for step in range(total_max):
            wf_config = await self._get_workflow()
            artifact_state = HandoffParser.detect_artifact_state(
                self.artifacts_dir,
               )

            logger.info(
                  "[%s/%d] Executing: %s (%s) "
                  "| adapter=%s | artifacts=%s",
                  "auto",
                step + 1,
                self.current_workflow,
                wf_config.title,
                self.adapter_name,
                artifact_state.get("status", "?"),
               )

            # --- Execute LLM with retry loop ---------------------------
            llm_output = None
            exec_failures = 0

            while exec_failures < per_wf_max:
                try:
                    llm_output = await self._execute_llm(
                        self.current_workflow,
                       )
                except Exception as e:
                    exec_failures += 1
                    logger.warning(
                          "[retry] Step %d failed (%d/%d): %s",
                        step + 1,
                        exec_failures,
                        per_wf_max,
                        e,
                       )
                    if exec_failures >= per_wf_max:
                        logger.warning(
                              "[%s] %d consecutive failures "
                              "-> using forgeflow.json rules",
                            self.current_workflow,
                             exec_failures,
                           )

                if llm_output is None or not isinstance(llm_output, str):
                    exec_failures += 1
                    logger.warning(
                          "[retry] Empty/null output (%d/%d)",
                        exec_failures,
                        per_wf_max,
                       )
                    continue

                # Try parsing handoff
                handoff = self.handoff_parser.parse(llm_output)
                if handoff is not None:
                    break    # success -> proceed to transition

                exec_failures += 1
                logger.warning(
                      "[retry] Invalid handoff (%d/%d) for %s",
                    exec_failures,
                    per_wf_max,
                    self.current_workflow,
                   )

            # --- Decision point: parse succeeded or fell through -------
            log_entry = {
                  "iteration": step + 1,
                  "workflow": self.current_workflow,
                  "timestamp": datetime.now(timezone.utc).isoformat(),
                 }

            if exec_failures >= per_wf_max:
                # Exhausted retries -> use fallback from forgeflow.json
                logger.warning(
                      "[%s] Using transition rules (fallback)",
                    self.current_workflow,
                   )
                trans_result = self._apply_fallback_transitions(
                    self.current_workflow,
                   )
                log_entry["transition_method"] = "fallback_rules"
                log_entry["fallback_reason"] = (
                    f"{per_wf_max} consecutive execution/handoff failures"
                   )

                if trans_result is None:
                    # No valid fallback -> pipeline ends
                    log_entry["result"] = "PIPELINE_BLOCKED"
                    log_entry["blocker"] = (
                        f"No transition rules matched for "
                        f"'{self.current_workflow}' under failure conditions"
                         )
                    await self._save_step_summary(log_entry)
                    logger.error(
                          "[forgeflow] Pipeline blocked: %s",
                        log_entry["blocker"],
                         )
                    return json.dumps(log_entry, indent=2)

                trans = trans_result.get("transition", "").upper()
                if trans == "FORWARD":
                    next_wf = trans_result.get("next_workflow", "")
                    if next_wf:
                        self.current_workflow = next_wf
                        log_entry["handoff"] = {
                              "transition": "FORWARD",
                              "next_workflow": next_wf,
                             }
                        logger.info(
                              "[%s] -> FORWARD (fallback) to %s",
                            next_wf,
                             )
                    else:
                        log_entry["result"] = "PIPELINE_BLOCKED"
                        await self._save_step_summary(log_entry)
                        return json.dumps(log_entry, indent=2)

                elif trans == "RETURN":
                    target = (
                        trans_result.get("target_workflow", "")
                        or trans_result.get("return_to", "")
                        or "plan"
                         )
                    self.current_workflow = target
                    blocker_cat = trans_result.get(
                              "blocker_category", "FALLBACK_BLOCKER"
                             )
                    log_entry["handoff"] = {
                              "transition": "RETURN",
                              "blocker_category": blocker_cat,
                              "target_workflow": target,
                             }
                    logger.info(
                              "[%s] -> RETURN (fallback) (%s) back to %s",
                            blocker_cat,
                            target,
                             )

                elif trans == "TERMINAL":
                    log_entry["result"] = "PIPELINE_TERMINATED"
                    await self._save_step_summary(log_entry)
                    logger.info("[forgeflow] PIPELINE TERMINATED (fallback)")
                    return json.dumps(log_entry, indent=2)

                else:
                    log_entry["error"] = f"unknown_transition:{trans}"
                    await self._save_step_summary(log_entry)
            else:
                # Handoff parsed successfully -> normal transition flow
                handoff = (
                    self.handoff_parser.parse(llm_output)
                    if llm_output
                    else None
                     )
                if handoff is not None:
                    log_entry["handoff"] = handoff
                    trans = handoff.get("transition", "").upper()

                    if trans == "FORWARD":
                        next_wf = handoff.get("next_workflow", "")
                        if next_wf:
                            self.current_workflow = next_wf
                            logger.info(
                                  "[%s] -> FORWARD to %s", next_wf,
                                 )
                        else:
                            log_entry["error"] = "FORWARD without target"
                            await self._save_step_summary(log_entry)
                            return json.dumps(log_entry, indent=2)

                    elif trans == "RETURN":
                        blocker_cat = handoff.get(
                                  "blocker_category", "UNKNOWN"
                                 )
                        target = (
                            handoff.get("target_workflow", "")
                            or handoff.get("return_to", "")
                            or "plan"
                             )
                        self.current_workflow = target
                        logger.info(
                                  "[%s] -> RETURN (%s) back to %s",
                                blocker_cat,
                                target,
                                 )

                    elif trans == "TERMINAL":
                        log_entry["result"] = "PIPELINE_COMPLETE"
                        await self._save_step_summary(log_entry)
                        logger.info("[forgeflow] PIPELINE COMPLETE")
                        return json.dumps(log_entry, indent=2)

                    else:
                        log_entry["error"] = f"unknown_transition:{trans}"
                        await self._save_step_summary(log_entry)
                else:
                    # This branch should not be reached (handled above),
                    # but be safe
                    log_entry["error"] = "no_valid_handoff"
                    logger.warning(
                          "[%s] WARNING: no valid handoff",
                        self.current_workflow,
                         )

            # Persist history entry
            self.history.append(log_entry)

        # Exhausted total iterations
        logger.warning(
              "[forgeflow] Reached MAX_ITERATIONS (%d)",
            total_max,
             )
        return json.dumps(
              {"result": "MAX_ITERATIONS_REACHED", "iterations": total_max,
               "final_workflow": self.current_workflow},
            indent=2,
             )

    async def execute_single(self, workflow_name):
        """Manual-mode: execute one workflow."""
        self.current_workflow = workflow_name
        wf_config = self.config.get_workflow(workflow_name)
        title = wf_config.title if wf_config else "N/A"

        logger.info(
              "[manual] Executing %s (%s)", workflow_name, title,
             )

        artifact_state = HandoffParser.detect_artifact_state(
            self.artifacts_dir,
             )
        status = artifact_state.get("status", "unknown")
        logger.debug("Artifacts status: %s", status)

        try:
            llm_output = await self._execute_llm(workflow_name)
        except Exception as e:
            logger.error("[manual] Execution error: %s", e)
            raise

        handoff = self.handoff_parser.parse(llm_output) if llm_output else None
        if handoff:
            trans = handoff.get("transition", "").upper()
            if trans == "FORWARD":
                logger.info(
                      "  Suggests FORWARD to: %s",
                    handoff.get("next_workflow", ""),
                     )
            elif trans == "RETURN":
                target = (
                    handoff.get("target_workflow", "")
                    or handoff.get("return_to", "")
                    or "plan"
                     )
                cat = handoff.get("blocker_category", "UNKNOWN")
                logger.info("  BLOCKER (%s) RETURN to: %s", cat, target)
            elif trans == "TERMINAL":
                logger.info("    PIPELINE TERMINATED")
            else:
                logger.info("   Transition type: %s", trans)
        else:
            logger.warning("     No valid handoff detected.")

        self.history.append(
              {
                  "iteration": len(self.history) + 1,
                  "workflow": workflow_name,
                  "result": "single_step",
              },
             )
        return llm_output or ""

    def get_state(self):
        """Return current runner state as dict."""
        return {
              "current_workflow": self.current_workflow,
              "history_len": len(self.history),
              "artifacts_dir": self.artifacts_dir,
              "config_mode": self.config.mode,
              "adapter": self.adapter_name,
             }

    def print_history(self):
        if not self.history:
            print("         (empty)")
            return
        for i, e in enumerate(self.history, 1):
            wf = e.get("workflow", "?")
            ts = e.get("timestamp", "")
            extra = f" @ {ts}" if ts else ""
            print(f"           {i:3d}. {wf}{extra}")

    def reset_artifacts(self):
        """Clean artifacts/."""
        root = plib.Path(self.artifacts_dir)
        if root.exists():
            shutil.rmtree(str(root))
        root.mkdir(parents=True, exist_ok=True)
        logger.info("[reset] Cleaned %s/", self.artifacts_dir)

    # --- internal helpers ---

    async def _get_workflow(self):
        return (
            self.config.get_workflow(self.current_workflow)
            or WorkflowConfig()
             )

    async def _execute_llm(self, name):
        """Read prompt from the selected adapter with retry logic.

        Retry policy:
           - max_retries = 3
           - backoff: 0.5s, 1.0s, 2.0s (exponential)
        """
        max_retries = 3
        backoff_base = 0.5

        for attempt in range(max_retries + 1):
            try:
                logger.debug(
                      "[LLM] Loading prompt for %s "
                      "(attempt %d/%d, adapter=%s)",
                    name,
                    attempt + 1,
                    max_retries + 1,
                    self.adapter_name,
                     )

                resolver = PromptResolver()
                prompt_path = resolver.resolve(name)

                if not os.path.exists(prompt_path):
                    err_msg = (
                        f"Prompt file not found at {prompt_path} "
                        f"for adapter {self.adapter_name}. "
                          "Fix: edit forgeflow.json or set "
                          "FORGEFLOW_ADAPTER env var. "
                          "Available adapters: .forgeflow/adapter/codex/, "
                          ".forgeflow/adapter/copilot/"
                         )
                    logger.error("[LLM] %s", err_msg)
                    raise FileNotFoundError(err_msg)

                prompt_text = plib.Path(prompt_path).read_text(
                    encoding="utf-8",
                     )
                logger.debug(
                      "[LLM] Loaded %d chars from %s",
                    len(prompt_text),
                    prompt_path,
                     )
                return prompt_text

            except Exception as e:
                if attempt < max_retries:
                    wait = backoff_base * (2 ** attempt)
                    logger.warning(
                          "[LLM] Retry %d/%d after %.1fs: %s",
                        attempt + 1,
                        max_retries,
                        wait,
                        e,
                         )
                    await asyncio.sleep(wait)
                else:
                    logger.error(
                          "[LLM] All %d attempts failed for %s: %s",
                        max_retries + 1,
                        name,
                        e,
                         )
                    raise

    async def _save_step_summary(self, entry):
        """Persist a step summary to artifacts/."""
        try:
            ts = entry.get(
                  "timestamp",
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                 )
            wf = entry.get("workflow", "unknown")
            filename_safe = ts.replace(":", "").replace("+", "")
            handoff_lines = [
                  "# Step Summary",
                f"## Workflow: {wf}",
                  "",
                 ]
            for k, v in entry.items():
                if k == "workflow":
                    continue
                val_str = json.dumps(v, ensure_ascii=False)
                handoff_lines.append(f"- **{k}**: {val_str}")
            target = (
                plib.Path(self.artifacts_dir)
                  / f"{wf}-step-{filename_safe}.md"
                 )
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(handoff_lines), encoding="utf-8")
            logger.debug("[save] %s", target)
        except Exception as e:
            logger.error("[save] Failed to persist summary: %s", e)

    # --- fallback transition engine ---

    def _max_total_steps(self):
        """Maximum total iterations across the entire pipeline."""
        return 50

    def _max_failures_per_workflow(self):
        """Max consecutive failures before triggering fallback rules."""
        return 3

    def _apply_fallback_transitions(
        self, wf_name,
         ):
        """Determine next workflow when handoff parsing fails.

        Priority order:
           1. Check auto_next from forgeflow.json for the current workflow
           2. Match against transition rules from forgeflow.json
           3. Return None if nothing matches (pipeline blocked)

        Returns a dict with keys: transition, next_workflow/target_workflow,
                                  blocker_category
        """
        wf_cfg = self.config.get_workflow(wf_name)

        # --- Strategy 1: auto_next from workflow config ---------------
        if wf_cfg.auto_next:
            logger.info(
                  "[fallback] Using auto_next '%s' for '%s'",
                wf_cfg.auto_next, wf_name,
                 )
            return {
                  "transition": "FORWARD",
                  "next_workflow": wf_cfg.auto_next,
                 }

        # --- Strategy 2: on_blocker_return from workflow config --------
        if (
            wf_cfg.on_blocker_return
            and isinstance(wf_cfg.on_blocker_return, dict)
             ):
            for target in wf_cfg.on_blocker_return.values():
                logger.info(
                      "[fallback] Using on_blocker_return '%s' for '%s'",
                    target, wf_name,
                     )
                return {
                      "transition": "RETURN",
                      "return_to": target,
                      "blocker_category": "FALLBACK_BLOCKER",
                     }

        # --- Strategy 3: transition rules from forgeflow.json --------
        for rule in self.config.transitions:
            if isinstance(rule, TransitionRule) and rule.forward:
                logger.info(
                      "[fallback] Using transition rule '%s' -> forward to '%s'",
                    rule.rule_id, rule.forward,
                     )
                return {
                      "transition": "FORWARD",
                      "next_workflow": rule.forward,
                      "blocker_category": "FALLBACK_RULE",
                     }

        # --- No fallback found -----------------------------------------
        logger.error(
              "[fallback] No transition rules matched for '%s'. Pipeline blocked.",
            wf_name,
             )
        return None
