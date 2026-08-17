"""Canonical ForgeFlow artifact discovery and metadata validation."""
import pathlib
import re

from ..logging_config import get_logger

logger = get_logger()


class ArtifactParser:
    """Build the active artifact set defined by Artifact Protocol 2.4."""

    _FILE_RULES = (
        (re.compile(r"planning\.md"), "Planning", "Plan"),
        (re.compile(r"requirement-feature-(\d{2})\.md"), "Requirement", "Grill"),
        (re.compile(r"solution-plan\.md"), "Solution Plan", "Solution"),
        (re.compile(r"slice-plan-feature-(\d{2})\.md"), "Slice Plan", "Slice"),
        (
            re.compile(r"tdd-feature-(\d{2})-slice-(\d{2})\.md"),
            "TDD Record",
            "TDD",
        ),
        (
            re.compile(
                r"review-feature-(\d{2})-slice-(\d{2})-attempt-(\d{2})\.md"
            ),
            "Review Report",
            "Review",
        ),
    )
    _ALLOWED_STATUS = {
        "Planning": {"DRAFT", "BLOCKED", "READY"},
        "Requirement": {"DRAFT", "BLOCKED", "READY"},
        "Solution Plan": {"DRAFT", "BLOCKED", "READY"},
        "Slice Plan": {"DRAFT", "BLOCKED", "READY"},
        "TDD Record": {"IN_PROGRESS", "BLOCKED", "READY_FOR_REVIEW"},
        "Review Report": {"READY"},
    }
    _TYPE_FIELDS = {
        "Planning": ("Feature IDs",),
        "Requirement": ("Feature ID", "Planning Version"),
        "Solution Plan": ("Based On Requirements",),
        "Slice Plan": ("Feature ID", "Based On Solution", "Slice IDs"),
        "TDD Record": (
            "Feature ID",
            "Slice ID",
            "Attempt",
            "Solution Version",
            "Slice Plan Version",
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
    _FEATURE = re.compile(r"F-(\d{2})")
    _SLICE = re.compile(r"S-(\d{2})")
    _EMPTY_FEATURES = "NONE"
    _EMPTY_FEATURE_APPROVAL = re.compile(r"APPROVED: \S.*")
    _SCOPE = re.compile(r"(?:Project|Feature: F-\d{2}|Slice: F-\d{2}/S-\d{2})")
    _BLOCKER_ROUTES = {
        "PLAN_GAP": ("Plan", "Project"),
        "BUSINESS_GAP": ("Grill", "Feature"),
        "ENGINEERING_GAP": ("Solution", "Project"),
        "SLICE_VIOLATION": ("Slice", "Feature"),
        "IMPLEMENTATION_GAP": ("TDD", "Slice"),
    }
    _REVIEW_WORKFLOW_SCOPES = {
        "Plan": "Project",
        "Grill": "Feature",
        "Solution": "Project",
        "Slice": "Feature",
        "TDD": "Slice",
    }
    _REVIEW_OWNER_ORDER = tuple(_REVIEW_WORKFLOW_SCOPES)
    _FINDINGS_HEADER = (
        "| # | Severity | Owner Workflow | Affected Scope | Finding | Evidence | "
        "Violated Contract |"
    )
    _FINDINGS_SEPARATOR = "| --- | --- | --- | --- | --- | --- | --- |"

    @classmethod
    def detect_artifact_state(cls, root_dir):
        """Return the validated active artifact set and graph-level errors."""
        root = pathlib.Path(root_dir)
        if not root.exists():
            return {
                "status": "empty",
                "root": str(root),
                "artifacts": {},
                "errors": [],
                "diagnostics": [],
                "ignored": [],
            }
        if not root.is_dir():
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
            if not path.is_file():
                ignored.append(path.name + ("/" if path.is_dir() else ""))
                continue

            rule = cls._match_filename(path.name)
            if rule is None:
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
    def _artifact_evidence(cls, path):
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
        }
        if expected_type == "Review Report":
            artifact["findings"] = findings
        return artifact, []

    @staticmethod
    def _parse_metadata(text):
        lines = text.splitlines()
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
        if artifact_type in {"Requirement", "Slice Plan", "TDD Record", "Review Report"}:
            feature = cls._FEATURE.fullmatch(metadata.get("Feature ID", ""))
            if feature is None or feature.group(1) != groups[0]:
                errors.append("Feature ID does not match canonical filename")
        if artifact_type in {"TDD Record", "Review Report"}:
            slice_id = cls._SLICE.fullmatch(metadata.get("Slice ID", ""))
            if slice_id is None or slice_id.group(1) != groups[1]:
                errors.append("Slice ID does not match canonical filename")
        if artifact_type == "Review Report":
            attempt = metadata.get("Attempt", "")
            if not attempt.isdigit() or int(attempt) <= 0 or int(attempt) != int(groups[2]):
                errors.append("Attempt does not match canonical filename")
        elif artifact_type == "TDD Record":
            attempt = metadata.get("Attempt", "")
            if not attempt.isdigit() or int(attempt) <= 0:
                errors.append("Attempt must be a positive integer")

    @classmethod
    def _validate_type_metadata(cls, metadata, artifact_type, errors):
        if artifact_type == "Planning":
            feature_ids = metadata.get("Feature IDs", "")
            empty_approval = metadata.get("Empty Feature Approval")
            if feature_ids == cls._EMPTY_FEATURES:
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
                if empty_approval is not None:
                    errors.append(
                        "Empty Feature Approval is forbidden with declared Features"
                    )
        elif artifact_type == "Solution Plan":
            cls._validate_version_map(
                metadata.get("Based On Requirements", ""), errors
            )
        elif artifact_type == "Slice Plan":
            cls._validate_identifier_list(
                metadata.get("Slice IDs", ""), cls._SLICE, "Slice IDs", errors
            )

        version_fields = {
            "Requirement": ("Planning Version",),
            "Slice Plan": ("Based On Solution",),
            "TDD Record": ("Solution Version", "Slice Plan Version"),
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
    def _validate_version_map(cls, value, errors):
        entries = value.split("; ")
        features = set()
        for entry in entries:
            parts = entry.split(" = ")
            if (
                len(parts) != 2
                or cls._FEATURE.fullmatch(parts[0]) is None
                or cls._VERSION.fullmatch(parts[1]) is None
            ):
                errors.append("invalid Based On Requirements")
                return
            if parts[0] in features:
                errors.append("duplicate Feature ID in Based On Requirements")
                return
            features.add(parts[0])

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
