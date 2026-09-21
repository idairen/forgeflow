"""Canonical ForgeFlow artifact discovery and metadata validation."""
import pathlib
import re

from .verification import parse_verification, table
from .attempts import inspect_attempts

from ..logging_config import get_logger

logger = get_logger()


class ArtifactParser:
    """Build and validate the canonical active artifact set."""

    _FILE_RULES = (
        (re.compile(r"planning\.md"), "Planning", "Plan"),
        (re.compile(r"lane-feature-((?:0[1-9]|[1-9][0-9]+))\.md"), "Feature Lane Record", "Grill"),
        (re.compile(r"requirement-feature-((?:0[1-9]|[1-9][0-9]+))\.md"), "Requirement", "Grill"),
        (re.compile(r"solution-plan\.md"), "Solution Plan", "Solution"),
        (re.compile(r"slice-plan-feature-((?:0[1-9]|[1-9][0-9]+))\.md"), "Slice Plan", "Slice"),
        (
            re.compile(r"implement-feature-((?:0[1-9]|[1-9][0-9]+))-slice-((?:0[1-9]|[1-9][0-9]+))\.md"),
            "Implement Record",
            "Implement",
        ),
        (
            re.compile(
                r"review-feature-((?:0[1-9]|[1-9][0-9]+))-slice-((?:0[1-9]|[1-9][0-9]+))-attempt-((?:0[1-9]|[1-9][0-9]+))\.md"
            ),
            "Review Report",
            "Review",
        ),
    )
    _FORBIDDEN_ARTIFACT_FILES = {"solution-plan-summary.md"}
    _ALLOWED_STATUS = {
        "Feature Lane Record": {"ACTIVE", "COMPLETE"},
        "Planning": {"DRAFT", "BLOCKED", "READY"},
        "Requirement": {"DRAFT", "BLOCKED", "READY"},
        "Solution Plan": {"DRAFT", "BLOCKED", "READY"},
        "Slice Plan": {"DRAFT", "BLOCKED", "READY"},
        "Implement Record": {"IN_PROGRESS", "BLOCKED", "READY_FOR_REVIEW"},
        "Review Report": {"READY"},
    }
    _TYPE_FIELDS = {
        "Feature Lane Record": ("Feature ID", "Feature Contract Version", "Attempt", "Dependency Requirement Versions", "Claim Evidence"),
        "Planning": ("Feature IDs", "Feature Contract Versions", "Change Set"),
        "Requirement": ("Feature ID", "Planning Version"),
        "Solution Plan": (
            "Based On Requirements",
            "Feature Engineering Versions",
        ),
        "Slice Plan": ("Feature ID", "Based On Solution", "Slice IDs"),
        "Implement Record": (
            "Feature ID",
            "Slice ID",
            "Attempt",
            "Solution Version",
            "Slice Plan Version",
            "Verification Strategies",
        ),
        "Review Report": (
            "Feature ID",
            "Slice ID",
            "Attempt",
            "Decision",
            "Solution Version",
            "Slice Plan Version",
            "Blocking Findings",
            "Non-blocking Findings",
        ),
    }
    _VERSION = re.compile(r"\d+\.\d+")
    _FEATURE = re.compile(r"F-((?:0[1-9]|[1-9][0-9]+))")
    _SLICE = re.compile(r"S-((?:0[1-9]|[1-9][0-9]+))")
    _SHARED_COMPONENT = re.compile(r"SC-((?:0[1-9]|[1-9][0-9]+))")
    _ENGINEERING_DECISION = re.compile(r"ED-((?:0[1-9]|[1-9][0-9]+))")
    _IMPACT_VALUES = {"DIRECT", "INDIRECT", "UNAFFECTED"}
    _SOLUTION_IMPACT_FIELDS = (
        "Shared Component IDs",
        "Feature Dependencies",
        "Feature Shared Components",
        "Feature Decision References",
        "Cross-Feature Impact",
    )
    _EMPTY_FEATURES = "NONE"
    _EMPTY_FEATURE_APPROVAL = re.compile(r"APPROVED: \S.*")
    _SCOPE = re.compile(r"(?:Project|Feature: F-(?:0[1-9]|[1-9][0-9]+)|Slice: F-(?:0[1-9]|[1-9][0-9]+)/S-(?:0[1-9]|[1-9][0-9]+))")
    _BLOCKER_ROUTES = {
        "PLAN_GAP": ("Plan", "Project"),
        "BUSINESS_GAP": ("Grill", "Feature"),
        "ENGINEERING_GAP": ("Solution", "Project"),
        "SLICE_VIOLATION": ("Slice", "Feature"),
        "IMPLEMENTATION_GAP": ("Implement", "Slice"),
    }
    _REVIEW_WORKFLOW_SCOPES = {
        "Plan": "Project",
        "Grill": "Feature",
        "Solution": "Project",
        "Slice": "Feature",
        "Implement": "Slice",
    }
    _REVIEW_OWNER_ORDER = tuple(_REVIEW_WORKFLOW_SCOPES)
    _FINDINGS_HEADER = (
        "| # | Severity | Owner Workflow | Affected Scope | Finding | Evidence | "
        "Violated Contract |"
    )
    _FINDINGS_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- |"
    _PLANNING_SECTIONS = (
        "Project Intent",
        "Project Goals",
        "Success Measures",
        "Project Constraints",
        "Assumptions",
        "Exclusions",
        "Features",
        "Change Set",
        "Intent Evolution",
    )
    _PLANNING_TABLES = {
        "Features": (
            "| Feature ID | Title | Outcome | Dependencies |",
            "| --- | --- | --- | --- |",
        ),
        "Change Set": (
            "| Feature ID | Change | Previous Contract Version | "
            "Current Contract Version | Rationale |",
            "| --- | --- | --- | --- | --- |",
        ),
    }
    _STRUCTURE_TABLES = {
        "Implementation Structure": (
            "| Component or Role | Source Root | Module or Package Pattern | "
            "Responsibility | Allowed Dependencies | Applies To | Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ),
        "Test Structure": (
            "| Test Level | Test Root | Module or Package Pattern | "
            "Production Relationship | Applies To | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ),
        "Planned File Placement": (
            "| Slice ID | Responsibility | Production Path or Pattern | "
            "Test Path or Pattern | Governing Decision | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
        ),
        "File Placement Conformance": (
            "| Actual Path | Kind | Responsibility | Planned Path or Pattern | "
            "Governing Decision | Conformance |",
            "| --- | --- | --- | --- | --- | --- |",
        ),
    }

    @classmethod
    def detect_artifact_state(cls, root_dir):
        """Return the validated active artifact set and graph-level errors."""
        root = pathlib.Path(root_dir)
        if not root.exists() and not root.is_symlink():
            return {
                "status": "empty",
                "root": str(root),
                "artifacts": {},
                "errors": [],
                "diagnostics": [],
                "ignored": [],
            }
        if root.is_symlink() or not root.is_dir():
            return {
                "status": "invalid",
                "root": str(root),
                "artifacts": {},
                "errors": ["artifact_root_is_not_a_directory"],
                "diagnostics": [
                    {
                        "code": "artifact_root_is_not_a_directory",
                        "artifacts": [],
                    }
                ],
                "ignored": [],
            }

        artifacts = {}
        errors = []
        diagnostics = []
        canonical_evidence = []
        ignored = []
        root_entries = sorted(root.iterdir(), key=lambda path: path.name)
        for path in root_entries:
            if path.name == "history" and path.is_dir():
                ignored.append("history/")
                continue
            if path.is_symlink() or (cls._match_filename(path.name) and not path.is_file()):
                errors.append(f"invalid artifact path: {path.name}")
                diagnostics.append({"code": "artifact_invalid", "artifacts": [cls._artifact_evidence(path)]})
                continue
            if not path.is_file():
                ignored.append(path.name + ("/" if path.is_dir() else ""))
                continue

            rule = cls._match_filename(path.name)
            if rule is None:
                if re.fullmatch(r"tdd-feature-\d+-slice-\d+\.md", path.name):
                    errors.append(f"retired active TDD requires explicit migration: {path.name}")
                    diagnostics.append({"code": "artifact_invalid", "artifacts": [cls._artifact_evidence(path)]})
                    continue
                if path.name in cls._FORBIDDEN_ARTIFACT_FILES:
                    errors.append(f"forbidden artifact filename: {path.name}")
                    diagnostics.append(
                        {
                            "code": "forbidden_artifact_filename",
                            "artifacts": [cls._artifact_evidence(path)],
                        }
                    )
                    continue
                ignored.append(path.name)
                continue
            evidence = cls._artifact_evidence(path)
            canonical_evidence.append(evidence)
            filename_match, expected_type, expected_owner = rule
            parsed, artifact_errors = cls._parse_artifact(
                path,
                filename_match,
                expected_type,
                expected_owner,
            )
            if artifact_errors:
                errors.extend(f"{path.name}: {error}" for error in artifact_errors)
                diagnostics.append(
                    {
                        "code": cls._diagnostic_code(artifact_errors[0]),
                        "artifacts": [evidence],
                    }
                )
                continue
            artifacts[path.name] = parsed

        if root_entries and "planning.md" not in artifacts:
            errors.append("non_empty_artifact_root_without_valid_planning")
            diagnostics.append(
                {
                    "code": "non_empty_artifact_root_without_valid_planning",
                    "artifacts": canonical_evidence,
                }
            )

        graph_errors = cls._validate_solution_graph_metadata(artifacts)
        if graph_errors:
            errors.extend(graph_errors)
            diagnostics.append(
                {
                    "code": "invalid_solution_impact_model",
                    "artifacts": [
                        cls._artifact_evidence(root / filename)
                        for filename in ("planning.md", "solution-plan.md")
                        if (root / filename).is_file()
                    ],
                }
            )

        for artifact in artifacts.values():
            if artifact["artifact_type"] != "Implement Record":
                continue
            try:
                artifact.update(inspect_attempts(root, artifact, artifacts, cls._parse_metadata))
                cls._validate_required_verification(artifact, artifacts)
            except (ValueError, OSError, UnicodeError) as error:
                errors.append(f"{artifact['filename']}: {error}")
                diagnostics.append({"code": "artifact_invalid", "artifacts": [cls._artifact_evidence(root / artifact['filename'])]})

        status = "invalid" if errors else ("active" if artifacts else "empty")
        logger.debug(
            "Detected %d valid artifact(s), %d error(s), and %d ignored entry(s) in %s",
            len(artifacts),
            len(errors),
            len(ignored),
            root,
        )
        return {
            "status": status,
            "root": str(root),
            "artifacts": artifacts,
            "errors": errors,
            "diagnostics": diagnostics,
            "ignored": ignored,
        }

    @classmethod
    def _validate_required_verification(cls, record, artifacts):
        meta = record["metadata"]
        plan = artifacts.get(f"slice-plan-feature-{meta['Feature ID'][2:]}.md")
        if not plan or meta["Slice Plan Version"] != plan["version"] or record["status"] != "READY_FOR_REVIEW":
            return
        selected = {r["Strategy"] for r in record.get("verification_selection", [])}
        evidence = record.get("verification_evidence", [])
        for obligation in plan.get("verification_plan", []):
            if obligation["Slice ID"] != meta["Slice ID"]:
                continue
            required = set(obligation["Strategies"].split("; "))
            if not required <= selected:
                # Conditions remain normative prose evaluated by the participant;
                # the CLI never infers an unstated alternative from convenience.
                if "alternative" not in obligation["Rationale"].lower():
                    raise ValueError("READY_FOR_REVIEW omits mandatory Slice strategy")
                choices = [s for s in record.get("verification_selection", []) if s["Governing Obligation"] == obligation["Obligation"]]
                if not choices:
                    raise ValueError("missing permitted alternative rationale")
            for check in obligation["Required Checks"].split("; "):
                rows = [e for e in evidence if e["Obligation or Check"] == check]
                if not rows or rows[-1]["Result"] not in {"SUCCEEDED", "NOT_APPLICABLE"}:
                    raise ValueError(f"READY_FOR_REVIEW missing or pending required check: {check}")
                if rows[-1]["Result"] == "NOT_APPLICABLE" and "applicab" not in obligation["Rationale"].lower():
                    raise ValueError("NOT_APPLICABLE lacks an explicit plan condition")

    @classmethod
    def _artifact_evidence(cls, path):
        if path.is_symlink():
            return {"filename": path.name, "version": "INVALID_VERSION"}
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            version = "INVALID_VERSION"
        else:
            versions = [
                match.group(1).strip()
                for match in re.finditer(
                    r"(?m)^\| Version \| ([^|]+) \|$",
                    text,
                )
            ]
            version = (
                versions[0]
                if len(versions) == 1
                and cls._VERSION.fullmatch(versions[0]) is not None
                else "INVALID_VERSION"
            )
        return {"filename": path.name, "version": version}

    @staticmethod
    def _diagnostic_code(error):
        summary = error.split(":", 1)[0]
        return re.sub(r"[^a-z0-9]+", "_", summary.lower()).strip("_")

    @classmethod
    def check_artifact_exists(cls, artifacts_dir, artifact_name):
        """Check only a direct canonical path under the Artifact Root."""
        if cls._match_filename(artifact_name) is None:
            return False
        root = pathlib.Path(artifacts_dir)
        return root.is_dir() and (root / artifact_name).is_file()

    @classmethod
    def _match_filename(cls, filename):
        for pattern, artifact_type, owner in cls._FILE_RULES:
            match = pattern.fullmatch(filename)
            if match is not None:
                return match, artifact_type, owner
        return None

    @classmethod
    def _parse_artifact(cls, path, filename_match, expected_type, expected_owner):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            return None, [f"unreadable: {error}"]

        metadata, errors = cls._parse_metadata(text)
        if errors:
            return None, errors

        required = ("Artifact Type", "Version", "Status", "Owner Workflow")
        required += cls._TYPE_FIELDS[expected_type]
        missing = [field for field in required if field not in metadata]
        if missing:
            errors.append("missing metadata: " + ", ".join(missing))
        if metadata.get("Artifact Type") != expected_type:
            errors.append("Artifact Type does not match canonical filename")
        if metadata.get("Owner Workflow") != expected_owner:
            errors.append("Owner Workflow does not match Artifact Type")

        version = metadata.get("Version", "")
        if cls._VERSION.fullmatch(version) is None:
            errors.append("invalid Version")
        status = metadata.get("Status", "")
        if status not in cls._ALLOWED_STATUS[expected_type]:
            errors.append("invalid Status for Artifact Type")

        cls._validate_identifiers(metadata, filename_match, expected_type, errors)
        cls._validate_type_metadata(metadata, expected_type, errors)
        cls._validate_planning_sections(text, metadata, expected_type, errors)
        cls._validate_structure_sections(text, expected_type, errors)
        cls._validate_solution_summary(text, metadata, expected_type, errors)
        verification = {}
        try:
            verification = parse_verification(text, metadata, expected_type)
        except (ValueError, KeyError) as error:
            errors.append(str(error))
        if metadata.get("Workflow") == "TDD":
            errors.append("retired TDD workflow declaration")
        findings = []
        if expected_type == "Review Report":
            findings, finding_errors = cls._parse_review_findings(text)
            errors.extend(finding_errors)
            cls._validate_review_findings(metadata, findings, errors)
        if status == "BLOCKED":
            cls._validate_blocker(metadata, errors)

        if errors:
            return None, errors
        artifact = {
            "filename": path.name,
            "path": str(path),
            "artifact_type": expected_type,
            "owner_workflow": expected_owner,
            "version": version,
            "status": status,
            "metadata": metadata,
            "text": text,
            **verification,
        }
        if expected_type == "Planning":
            try:
                feature_rows = table(text, "Features", ("Feature ID", "Title", "Outcome", "Dependencies"))
                feature_ids = metadata["Feature IDs"].split("; ")
                if [r["Feature ID"] for r in feature_rows] != feature_ids:
                    raise ValueError("Features table does not match metadata order")
                dependencies = {r["Feature ID"]: [] if r["Dependencies"] == "NONE" else r["Dependencies"].split(", ") for r in feature_rows}
                if any(d not in feature_ids or d == f for f, ds in dependencies.items() for d in ds) or cls._dependency_cycle(dependencies):
                    raise ValueError("invalid Planning dependency graph")
                artifact["dependencies"] = dependencies
            except ValueError as error:
                if "## Features" in text or metadata.get("Artifact Protocol Version"):
                    return None, [str(error)]
                artifact["dependencies"] = {f: [] for f in metadata["Feature IDs"].split("; ") if f != "NONE"}
        if expected_type == "Review Report":
            artifact["findings"] = findings
        return artifact, []

    @staticmethod
    def _parse_metadata(text):
        lines = text.splitlines()
        if lines.count("## Metadata") != 1:
            return {}, ["artifact requires exactly one Metadata section"]
        if not lines or re.fullmatch(r"# \S.*", lines[0]) is None:
            return {}, ["artifact must begin with a level-one title"]

        index = 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines) or lines[index] != "## Metadata":
            return {}, ["title must be followed by ## Metadata"]
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        if (
            index + 1 >= len(lines)
            or lines[index] != "| Field | Value |"
            or lines[index + 1] != "| --- | --- |"
        ):
            return {}, ["invalid Metadata table header"]

        metadata = {}
        errors = []
        index += 2
        while index < len(lines) and lines[index].startswith("|"):
            match = re.fullmatch(r"\| ([^|]+) \| ([^|]+) \|", lines[index])
            if match is None:
                errors.append("invalid Metadata table row")
                break
            field, value = (part.strip() for part in match.groups())
            if field in metadata:
                errors.append(f"duplicate metadata field: {field}")
            elif not value or "{{" in value or "}}" in value:
                errors.append(f"invalid metadata value: {field}")
            else:
                metadata[field] = value
            index += 1
        return metadata, errors

    @classmethod
    def _parse_review_findings(cls, text):
        lines = text.splitlines()
        headings = [index for index, line in enumerate(lines) if line == "## Findings"]
        if len(headings) != 1:
            return [], ["Review Report must contain exactly one ## Findings section"]

        index = headings[0] + 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        if (
            index + 1 >= len(lines)
            or lines[index] != cls._FINDINGS_HEADER
            or lines[index + 1] != cls._FINDINGS_SEPARATOR
        ):
            return [], ["invalid Findings table header"]

        findings = []
        errors = []
        index += 2
        while index < len(lines) and lines[index].startswith("|"):
            match = re.fullmatch(
                r"\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| "
                r"([^|]+) \| ([^|]+) \| ([^|]+) \|",
                lines[index],
            )
            if match is None:
                errors.append("invalid Findings table row")
                index += 1
                continue

            (
                number,
                severity,
                owner_workflow,
                affected_scope,
                finding,
                evidence,
                violated_contract,
            ) = (part.strip() for part in match.groups())
            expected_number = len(findings) + 1
            if number != str(expected_number):
                errors.append("Findings row numbers must be sequential from 1")
            if severity not in {"BLOCKING", "NON_BLOCKING"}:
                errors.append("invalid Finding Severity")
            expected_scope = cls._REVIEW_WORKFLOW_SCOPES.get(owner_workflow)
            if expected_scope is None:
                errors.append("invalid Finding Owner Workflow")
            if cls._SCOPE.fullmatch(affected_scope) is None:
                errors.append("invalid Finding Affected Scope")
            elif (
                expected_scope is not None
                and affected_scope.split(":", 1)[0] != expected_scope
            ):
                errors.append("Finding Affected Scope does not match Owner Workflow")
            if any(
                not value
                or "{{" in value
                or "}}" in value
                or re.fullmatch(r"<[^>]+>", value) is not None
                for value in (finding, evidence, violated_contract)
            ):
                errors.append("invalid Finding content")
            findings.append(
                {
                    "number": number,
                    "severity": severity,
                    "owner_workflow": owner_workflow,
                    "affected_scope": affected_scope,
                    "finding": finding,
                    "evidence": evidence,
                    "violated_contract": violated_contract,
                }
            )
            index += 1
        return findings, errors

    @classmethod
    def _validate_structure_sections(cls, text, artifact_type, errors):
        section_names = {
            "Solution Plan": ("Implementation Structure", "Test Structure"),
            "Slice Plan": ("Planned File Placement",),
            "Implement Record": ("File Placement Conformance",),
        }.get(artifact_type, ())
        if not section_names:
            return

        lines = text.splitlines()
        positions = {
            name: [
                index for index, line in enumerate(lines) if line == f"## {name}"
            ]
            for name in section_names
        }
        if artifact_type == "Solution Plan":
            present = [name for name, indexes in positions.items() if indexes]
            if present and len(present) != len(section_names):
                errors.append(
                    "Solution structure sections must include both "
                    "Implementation Structure and Test Structure"
                )

        for name, indexes in positions.items():
            if not indexes:
                continue
            if len(indexes) != 1:
                errors.append(f"Artifact must contain exactly one ## {name} section")
                continue
            index = indexes[0] + 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            header, separator = cls._STRUCTURE_TABLES[name]
            if (
                index + 1 >= len(lines)
                or lines[index] != header
                or lines[index + 1] != separator
            ):
                errors.append(f"invalid {name} table header")

    @classmethod
    def _validate_planning_sections(cls, text, metadata, artifact_type, errors):
        if artifact_type != "Planning":
            return
        protocol_version = metadata.get("Artifact Protocol Version")
        if protocol_version is None:
            return
        if protocol_version != "2.11":
            errors.append("unsupported Planning Artifact Protocol Version")
            return

        lines = text.splitlines()
        positions = []
        for section in cls._PLANNING_SECTIONS:
            indexes = [
                index for index, line in enumerate(lines) if line == f"## {section}"
            ]
            if len(indexes) != 1:
                errors.append(
                    f"Planning must contain exactly one ## {section} section"
                )
                continue
            positions.append(indexes[0])

            content_index = indexes[0] + 1
            while content_index < len(lines) and not lines[content_index].strip():
                content_index += 1
            if (
                content_index >= len(lines)
                or lines[content_index].startswith("## ")
            ):
                errors.append(f"Planning section is empty: {section}")
                continue
            table = cls._PLANNING_TABLES.get(section)
            if table is not None:
                header, separator = table
                if (
                    content_index + 1 >= len(lines)
                    or lines[content_index] != header
                    or lines[content_index + 1] != separator
                ):
                    errors.append(f"invalid Planning {section} table header")

        if len(positions) == len(cls._PLANNING_SECTIONS) and positions != sorted(
            positions
        ):
            errors.append("Planning sections are out of canonical order")
    @staticmethod
    def _validate_solution_summary(text, metadata, artifact_type, errors):
        if artifact_type != "Solution Plan":
            return
        protocol_version = metadata.get("Artifact Protocol Version")
        if protocol_version is not None and protocol_version != "2.11":
            errors.append("unsupported Solution Artifact Protocol Version")
            return
        lines = text.splitlines()
        if protocol_version == "2.11":
            for required_section in (
                "Implementation Structure",
                "Test Structure",
            ):
                if f"## {required_section}" not in lines:
                    errors.append(
                        "Solution structure sections must include both "
                        "Implementation Structure and Test Structure"
                    )
                    break
        indexes = [
            index for index, line in enumerate(lines) if line == "## Solution Summary"
        ]
        if not indexes:
            if protocol_version == "2.11":
                errors.append(
                    "Solution Plan must contain exactly one ## Solution Summary section"
                )
            return
        if len(indexes) != 1:
            errors.append(
                "Solution Plan must contain exactly one ## Solution Summary section"
            )
            return
        content_index = indexes[0] + 1
        while content_index < len(lines) and not lines[content_index].strip():
            content_index += 1
        if (
            content_index >= len(lines)
            or lines[content_index].startswith("## ")
        ):
            errors.append("Solution Summary section is empty")

    @classmethod
    def _validate_review_findings(cls, metadata, findings, errors):
        blocking = [
            finding for finding in findings if finding["severity"] == "BLOCKING"
        ]
        non_blocking = [
            finding
            for finding in findings
            if finding["severity"] == "NON_BLOCKING"
        ]
        expected_counts = {
            "Blocking Findings": len(blocking),
            "Non-blocking Findings": len(non_blocking),
        }
        for field, expected in expected_counts.items():
            value = metadata.get(field, "")
            if value.isdigit() and int(value) != expected:
                errors.append(f"{field} does not match Findings table")

        if metadata.get("Decision") != "FAIL" or not blocking:
            return
        if any(
            finding["owner_workflow"] not in cls._REVIEW_OWNER_ORDER
            for finding in blocking
        ):
            return
        selected_owner = min(
            (finding["owner_workflow"] for finding in blocking),
            key=cls._REVIEW_OWNER_ORDER.index,
        )
        if metadata.get("Return Workflow") != selected_owner:
            errors.append("Return Workflow does not match blocking Finding precedence")
            return
        return_scope = metadata.get("Return Scope")
        if not any(
            finding["owner_workflow"] == selected_owner
            and finding["affected_scope"] == return_scope
            for finding in blocking
        ):
            errors.append("Return Scope does not match a selected blocking Finding")

    @classmethod
    def _validate_identifiers(cls, metadata, filename_match, artifact_type, errors):
        groups = filename_match.groups()
        if artifact_type in {"Feature Lane Record", "Requirement", "Slice Plan", "Implement Record", "Review Report"}:
            feature = cls._FEATURE.fullmatch(metadata.get("Feature ID", ""))
            if feature is None or feature.group(1) != groups[0]:
                errors.append("Feature ID does not match canonical filename")
        if artifact_type in {"Implement Record", "Review Report"}:
            slice_id = cls._SLICE.fullmatch(metadata.get("Slice ID", ""))
            if slice_id is None or slice_id.group(1) != groups[1]:
                errors.append("Slice ID does not match canonical filename")
        if artifact_type == "Review Report":
            attempt = metadata.get("Attempt", "")
            if not attempt.isdigit() or int(attempt) <= 0 or int(attempt) != int(groups[2]):
                errors.append("Attempt does not match canonical filename")
        elif artifact_type in {"Implement Record", "Feature Lane Record"}:
            attempt = metadata.get("Attempt", "")
            if not attempt.isdigit() or int(attempt) <= 0:
                errors.append("Attempt must be a positive integer")

    @classmethod
    def _validate_type_metadata(cls, metadata, artifact_type, errors):
        if artifact_type == "Planning":
            feature_ids = metadata.get("Feature IDs", "")
            feature_versions = metadata.get("Feature Contract Versions", "")
            empty_approval = metadata.get("Empty Feature Approval")
            if feature_ids == cls._EMPTY_FEATURES:
                if feature_versions != cls._EMPTY_FEATURES:
                    errors.append(
                        "NONE Feature IDs require NONE Feature Contract Versions"
                    )
                if empty_approval is None:
                    errors.append(
                        "NONE Feature IDs require Empty Feature Approval"
                    )
                elif (
                    cls._EMPTY_FEATURE_APPROVAL.fullmatch(empty_approval) is None
                    or re.fullmatch(
                        r"APPROVED: <[^>]+>", empty_approval
                    ) is not None
                ):
                    errors.append("invalid Empty Feature Approval")
            else:
                cls._validate_identifier_list(
                    feature_ids, cls._FEATURE, "Feature IDs", errors
                )
                cls._validate_version_map(
                    feature_versions,
                    "Feature Contract Versions",
                    errors,
                    expected_features=feature_ids.split("; "),
                )
                if empty_approval is not None:
                    errors.append(
                        "Empty Feature Approval is forbidden with declared Features"
                    )
        elif artifact_type == "Solution Plan":
            cls._validate_version_map(
                metadata.get("Based On Requirements", ""),
                "Based On Requirements",
                errors,
            )
            cls._validate_version_map(
                metadata.get("Feature Engineering Versions", ""),
                "Feature Engineering Versions",
                errors,
            )
            cls._validate_solution_impact_metadata(metadata, errors)
        elif artifact_type == "Slice Plan":
            cls._validate_identifier_list(
                metadata.get("Slice IDs", ""), cls._SLICE, "Slice IDs", errors
            )
        elif artifact_type == "Feature Lane Record":
            dependency_versions = metadata.get("Dependency Requirement Versions", "")
            if dependency_versions != "NONE":
                cls._validate_version_map(dependency_versions, "Dependency Requirement Versions", errors)

        version_fields = {
            "Feature Lane Record": ("Feature Contract Version",),
            "Requirement": ("Planning Version",),
            "Slice Plan": ("Based On Solution",),
            "Implement Record": ("Solution Version", "Slice Plan Version"),
            "Review Report": ("Solution Version", "Slice Plan Version"),
        }
        for field in version_fields.get(artifact_type, ()):
            if field in metadata and cls._VERSION.fullmatch(metadata[field]) is None:
                errors.append(f"invalid {field}")

        if artifact_type == "Review Report":
            decision = metadata.get("Decision")
            if decision not in {"PASS", "FAIL"}:
                errors.append("Decision must be PASS or FAIL")
            for field in ("Blocking Findings", "Non-blocking Findings"):
                value = metadata.get(field, "")
                if not value.isdigit():
                    errors.append(f"{field} must be a non-negative integer")
            blocking = metadata.get("Blocking Findings", "")
            if decision == "PASS":
                if blocking != "0":
                    errors.append("PASS requires zero Blocking Findings")
                if "Return Workflow" in metadata or "Return Scope" in metadata:
                    errors.append("PASS forbids return metadata")
            elif decision == "FAIL":
                if not blocking.isdigit() or int(blocking) <= 0:
                    errors.append("FAIL requires positive Blocking Findings")
                if "Return Workflow" not in metadata or "Return Scope" not in metadata:
                    errors.append("FAIL requires Return Workflow and Return Scope")
                else:
                    return_workflow = metadata["Return Workflow"]
                    return_scope = metadata["Return Scope"]
                    expected_scope = cls._REVIEW_WORKFLOW_SCOPES.get(return_workflow)
                    if expected_scope is None:
                        errors.append("invalid Return Workflow")
                    if cls._SCOPE.fullmatch(return_scope) is None:
                        errors.append("invalid Return Scope")
                    elif return_scope.split(":", 1)[0] != expected_scope:
                        errors.append("Return Scope does not match Return Workflow")

    @staticmethod
    def _validate_identifier_list(value, pattern, field, errors):
        entries = value.split("; ")
        if not entries or any(pattern.fullmatch(entry) is None for entry in entries):
            errors.append(f"invalid {field}")
        elif len(set(entries)) != len(entries):
            errors.append(f"duplicate identifier in {field}")

    @classmethod
    def _validate_version_map(
        cls,
        value,
        field,
        errors,
        expected_features=None,
    ):
        entries = value.split("; ")
        features = []
        for entry in entries:
            parts = entry.split(" = ")
            if (
                len(parts) != 2
                or cls._FEATURE.fullmatch(parts[0]) is None
                or cls._VERSION.fullmatch(parts[1]) is None
            ):
                errors.append(f"invalid {field}")
                return
            if parts[0] in features:
                errors.append(f"duplicate Feature ID in {field}")
                return
            features.append(parts[0])
        if expected_features is not None and features != expected_features:
            errors.append(f"{field} does not match Feature IDs")

    @classmethod
    def _validate_solution_impact_metadata(cls, metadata, errors):
        present = [field for field in cls._SOLUTION_IMPACT_FIELDS if field in metadata]
        if not present:
            return
        if len(present) != len(cls._SOLUTION_IMPACT_FIELDS):
            missing = [
                field for field in cls._SOLUTION_IMPACT_FIELDS if field not in metadata
            ]
            errors.append("partial Solution impact metadata: " + ", ".join(missing))
            return

        component_ids = metadata["Shared Component IDs"]
        if component_ids != "NONE":
            cls._validate_identifier_list(
                component_ids,
                cls._SHARED_COMPONENT,
                "Shared Component IDs",
                errors,
            )
        cls._validate_relation_map(
            metadata["Feature Dependencies"],
            "Feature Dependencies",
            cls._FEATURE,
            errors,
        )
        cls._validate_relation_map(
            metadata["Feature Shared Components"],
            "Feature Shared Components",
            cls._SHARED_COMPONENT,
            errors,
        )
        cls._validate_relation_map(
            metadata["Feature Decision References"],
            "Feature Decision References",
            cls._ENGINEERING_DECISION,
            errors,
        )
        cls._validate_relation_map(
            metadata["Cross-Feature Impact"],
            "Cross-Feature Impact",
            None,
            errors,
            allowed_values=cls._IMPACT_VALUES,
        )

    @classmethod
    def _validate_relation_map(
        cls,
        value,
        field,
        target_pattern,
        errors,
        allowed_values=None,
    ):
        sources = []
        for entry in value.split("; "):
            parts = entry.split(" = ", 1)
            if len(parts) != 2 or cls._FEATURE.fullmatch(parts[0]) is None:
                errors.append(f"invalid {field}")
                return
            source, targets_value = parts
            if source in sources:
                errors.append(f"duplicate Feature ID in {field}")
                return
            sources.append(source)
            targets = targets_value.split(", ")
            if targets_value == "NONE":
                continue
            if "NONE" in targets or len(set(targets)) != len(targets):
                errors.append(f"invalid {field}")
                return
            if allowed_values is not None:
                if len(targets) != 1 or targets[0] not in allowed_values:
                    errors.append(f"invalid {field}")
                    return
            elif any(target_pattern.fullmatch(target) is None for target in targets):
                errors.append(f"invalid {field}")
                return

    @classmethod
    def _validate_solution_graph_metadata(cls, artifacts):
        planning = artifacts.get("planning.md")
        solution = artifacts.get("solution-plan.md")
        if planning is None or solution is None:
            return []
        metadata = solution["metadata"]
        feature_ids_value = planning["metadata"].get("Feature IDs", "NONE")
        feature_ids = [] if feature_ids_value == "NONE" else feature_ids_value.split("; ")
        errors = []
        baseline = [entry.split(" = ", 1)[0] for entry in metadata["Based On Requirements"].split("; ")]
        engineering = [entry.split(" = ", 1)[0] for entry in metadata["Feature Engineering Versions"].split("; ")]
        if baseline != engineering:
            return ["solution-plan.md: Requirement and engineering maps disagree"]
        if baseline != feature_ids:
            if not cls._valid_prior_solution_baseline(planning, solution, baseline):
                return ["solution-plan.md: unexplained prior Planning baseline"]
            solution["valid_but_stale"] = True
            feature_ids = baseline
        if not all(field in metadata for field in cls._SOLUTION_IMPACT_FIELDS):
            return errors
        relation_maps = {
            field: cls._relation_map_values(metadata[field])
            for field in cls._SOLUTION_IMPACT_FIELDS[1:]
        }
        for field, mapping in relation_maps.items():
            if list(mapping) != feature_ids:
                errors.append(f"solution-plan.md: {field} does not match Feature IDs")

        dependencies = relation_maps["Feature Dependencies"]
        active_features = set(feature_ids)
        for source, targets in dependencies.items():
            if source in targets:
                errors.append("solution-plan.md: Feature Dependencies contains self dependency")
            if any(target not in active_features for target in targets):
                errors.append("solution-plan.md: Feature Dependencies references inactive Feature")
        if cls._dependency_cycle(dependencies):
            errors.append("solution-plan.md: Feature Dependencies contains a cycle")

        component_ids = metadata["Shared Component IDs"]
        components = set() if component_ids == "NONE" else set(component_ids.split("; "))
        component_map = relation_maps["Feature Shared Components"]
        if any(component not in components for values in component_map.values() for component in values):
            errors.append("solution-plan.md: Feature Shared Components references unknown component")
        return errors

    @classmethod
    def _valid_prior_solution_baseline(cls, planning, solution, features):
        """Read only Planning lineage and Requirement versions referenced by Solution."""
        root = pathlib.Path(planning["path"]).parent
        history = root / "history"
        if history.is_symlink():
            return False
        current_version = tuple(map(int, planning["version"].split(".")))
        candidates = []
        for path in history.glob("planning-v*.md"):
            match = re.fullmatch(r"planning-v(\d+\.\d+)\.md", path.name)
            if not match or tuple(map(int, match[1].split("."))) >= current_version:
                continue
            if path.is_symlink():
                return False
            parsed, errors = cls._parse_artifact(path, re.fullmatch("planning", "planning"), "Planning", "Plan")
            if errors or parsed["version"] != match[1]:
                return False
            candidates.append(parsed)
        candidates.sort(key=lambda a: tuple(map(int, a["version"].split("."))))
        candidates.append(planning)
        references = dict(e.split(" = ") for e in solution["metadata"]["Based On Requirements"].split("; "))
        for index, candidate in enumerate(candidates[:-1]):
            if candidate["status"] != "READY" or candidate["metadata"]["Feature IDs"].split("; ") != features:
                continue
            versions = dict(e.split(" = ") for e in candidate["metadata"]["Feature Contract Versions"].split("; "))
            valid = True
            for feature, version in references.items():
                name = f"requirement-feature-{feature[2:]}"
                paths = [root / (name + ".md"), history / f"{name}-v{version}.md",
                         history / f"retired-feature-{feature[2:]}" / (name + ".md")]
                matched = False
                for path in paths:
                    if not path.is_file() or path.is_symlink() or path.parent.is_symlink():
                        continue
                    rule = cls._match_filename(name + ".md")
                    req, errors = cls._parse_artifact(path, *rule)
                    if not errors and req["version"] == version and req["status"] == "READY" and req["metadata"]["Planning Version"] == versions[feature]:
                        matched = True
                        break
                valid &= matched
            if not valid:
                continue
            for old, new in zip(candidates[index:], candidates[index + 1:]):
                try:
                    changes = table(new["text"], "Change Set", ("Feature ID", "Change", "Previous Contract Version", "Current Contract Version", "Rationale"))
                    before = dict(e.split(" = ") for e in old["metadata"]["Feature Contract Versions"].split("; "))
                    after = dict(e.split(" = ") for e in new["metadata"]["Feature Contract Versions"].split("; "))
                    if {r["Feature ID"] for r in changes} != set(before) | set(after):
                        valid = False
                    for row in changes:
                        f = row["Feature ID"]
                        if row["Previous Contract Version"] != before.get(f, "NONE") or row["Current Contract Version"] != after.get(f, "NONE"):
                            valid = False
                        allowed = {"ADDED"} if f not in before else {"RETIRED"} if f not in after else {"MODIFIED"} if before[f] != after[f] else {"RETAINED", "REORDERED"}
                        if row["Change"] not in allowed:
                            valid = False
                except (KeyError, ValueError):
                    valid = False
            if valid:
                return True
        return False

    @staticmethod
    def _relation_map_values(value):
        mapping = {}
        for entry in value.split("; "):
            source, targets_value = entry.split(" = ", 1)
            mapping[source] = [] if targets_value == "NONE" else targets_value.split(", ")
        return mapping

    @staticmethod
    def _dependency_cycle(dependencies):
        visiting = set()
        visited = set()

        def visit(feature_id):
            if feature_id in visiting:
                return True
            if feature_id in visited:
                return False
            visiting.add(feature_id)
            if any(visit(target) for target in dependencies.get(feature_id, [])):
                return True
            visiting.remove(feature_id)
            visited.add(feature_id)
            return False

        return any(visit(feature_id) for feature_id in dependencies)

    @classmethod
    def _validate_blocker(cls, metadata, errors):
        fields = (
            "Blocker Category",
            "Blocker Owner",
            "Affected Scope",
            "Blocker Reason",
            "Blocker Evidence",
        )
        missing = [field for field in fields if field not in metadata]
        if missing:
            errors.append("missing blocker metadata: " + ", ".join(missing))
            return
        route = cls._BLOCKER_ROUTES.get(metadata["Blocker Category"])
        if route is None:
            errors.append("invalid Blocker Category")
            return
        expected_owner, expected_scope = route
        if metadata["Blocker Owner"] != expected_owner:
            errors.append("Blocker Owner does not match Blocker Category")
        affected_scope = metadata["Affected Scope"]
        if cls._SCOPE.fullmatch(affected_scope) is None:
            errors.append("invalid Affected Scope")
        elif affected_scope.split(":", 1)[0] != expected_scope:
            errors.append("Affected Scope does not match Blocker Category")
