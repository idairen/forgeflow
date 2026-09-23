"""Structural verification contracts; tool output is never manufactured here.

This module validates recorded evidence, not the truth or adequacy of a model's
assessment. Independent Review still owns that decision.
"""
import re

STRATEGIES = (
    "TDD", "BEHAVIORAL_TEST", "CHARACTERIZATION_TEST", "MIGRATION_REHEARSAL",
    "STATIC_VALIDATION", "CONFIGURATION_VALIDATION", "SECURITY_SCAN", "BENCHMARK",
    "DOCUMENTATION_VALIDATION", "MANUAL_ACCEPTANCE",
)
HEADERS = {
    "Verification Selection": ("Strategy", "Rationale", "Governing Obligation"),
    "Verification Evidence": ("Strategy", "Obligation or Check", "Source",
                              "Command or Procedure", "Target and Environment",
                              "Result", "Evidence Reference"),
    "Verification Plan": ("Slice ID", "Obligation", "Strategies", "Rationale",
                          "Required Checks", "Passing Criteria", "Evidence Required"),
    "Verification Requirements": ("Obligation", "Applies To", "Required Verification",
                                  "Passing Criteria", "Evidence Required"),
}


def section(text, name):
    matches = list(re.finditer(r"(?m)^## " + re.escape(name) + r"\s*$", text))
    if len(matches) != 1:
        raise ValueError(f"expected exactly one ## {name}")
    body = text[matches[0].end():]
    return re.split(r"(?m)^## ", body, maxsplit=1)[0].strip()


def table(text, name, headers=None):
    """Read one canonical Markdown table without discarding malformed rows."""
    lines = section(text, name).splitlines()
    headers = headers or HEADERS[name]
    expected = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    if len(lines) < 2 or lines[:2] != [expected, separator]:
        raise ValueError(f"invalid {name} table header")
    result = []
    ended = False
    for line in lines[2:]:
        if not line.startswith("|"):
            ended = True
            continue
        if ended or not line.endswith("|"):
            raise ValueError(f"invalid {name} table row")
        cells = [c.strip().replace(r"\|", "|") for c in
                 re.split(r"(?<!\\)\|", line[1:-1])]
        if len(cells) != len(headers) or any(not c or "{{" in c for c in cells):
            raise ValueError(f"invalid {name} table row")
        result.append(dict(zip(headers, cells)))
    return result


def strategy_list(value):
    values = value.split("; ")
    if not values or len(values) != len(set(values)) or any(v not in STRATEGIES for v in values):
        raise ValueError("invalid Verification Strategies")
    return values


def parse_verification(text, metadata, kind):
    """Return parsed evidence or raise a format/gate violation."""
    if kind == "Slice Plan":
        if "## Verification Plan" not in text:
            return {"verification_plan": [], "verification_actionable": False}
        rows = table(text, "Verification Plan")
        ids = metadata["Slice IDs"].split("; ")
        for row in rows:
            if row["Slice ID"] not in ids:
                raise ValueError("Verification Plan references undeclared Slice")
            strategy_list(row["Strategies"])
        if set(ids) != {row["Slice ID"] for row in rows}:
            raise ValueError("Verification Plan must cover every Slice")
        return {"verification_plan": rows, "verification_actionable": True}
    if kind == "Solution Plan":
        rows = table(text, "Verification Requirements") if "## Verification Requirements" in text else []
        if "## Verification Requirements" in text and not rows:
            raise ValueError("Verification Requirements must not be empty")
        return {"verification_requirements": rows}
    if kind != "Implement Record":
        return {}
    if any(k in metadata for k in ("Decision", "Result", "Return Workflow", "Return Scope")):
        raise ValueError("Implement cannot declare an overall Review Decision or Result")
    for name in ("Implementation Summary", "Open Issues", "Self-check"):
        if not section(text, name):
            raise ValueError(f"empty {name}")
    selection = table(text, "Verification Selection")
    evidence = table(text, "Verification Evidence")
    value = metadata.get("Verification Strategies", "")
    if value == "NONE":
        if metadata["Status"] != "BLOCKED" or selection or evidence or metadata.get("Blocker Category") not in {"ENGINEERING_GAP", "SLICE_VIOLATION"}:
            raise ValueError("NONE requires unresolved-selection upstream BLOCKED record")
        return {"verification_selection": [], "verification_evidence": []}
    selected = strategy_list(value)
    if list(dict.fromkeys(row["Strategy"] for row in selection)) != selected:
        raise ValueError("Verification Selection does not match metadata")
    for row in evidence:
        if row["Strategy"] not in selected:
            raise ValueError("evidence strategy is not selected")
        if row["Source"] not in {"TOOL_EXECUTION", "HUMAN_ACCEPTANCE", "MODEL_ASSESSMENT"}:
            raise ValueError("invalid evidence source")
        if row["Result"] not in {"SUCCEEDED", "FAILED", "NOT_RUN", "INCONCLUSIVE", "NOT_APPLICABLE"}:
            raise ValueError("invalid evidence result")
        if row["Strategy"] == "MANUAL_ACCEPTANCE" and row["Result"] == "SUCCEEDED" and row["Source"] != "HUMAN_ACCEPTANCE":
            raise ValueError("manual acceptance requires actual human evidence")
        if row["Strategy"] not in {"MANUAL_ACCEPTANCE", "DOCUMENTATION_VALIDATION"} and row["Result"] == "SUCCEEDED" and row["Source"] != "TOOL_EXECUTION":
            raise ValueError("executable strategy requires tool evidence")
    if metadata["Status"] == "READY_FOR_REVIEW":
        for choice in selection:
            if not any(e["Strategy"] == choice["Strategy"] for e in evidence):
                raise ValueError("READY_FOR_REVIEW lacks selected strategy evidence")
        if "TDD" in selected:
            red = [i for i, e in enumerate(evidence) if e["Strategy"] == "TDD" and e["Result"] == "FAILED" and e["Source"] == "TOOL_EXECUTION"]
            green = [i for i, e in enumerate(evidence) if e["Strategy"] == "TDD" and e["Result"] == "SUCCEEDED" and e["Source"] == "TOOL_EXECUTION"]
            if not red or not green or min(red) >= max(green):
                raise ValueError("TDD requires recorded RED before GREEN execution evidence")
        # Whether a failed supplementary check is blocking is a Review judgment;
        # required check coverage is compared with the Slice plan by the graph layer.
    return {"verification_selection": selection, "verification_evidence": evidence}
