"""Dependency-free validation for task packs and study runs."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

TASK_SCHEMA_VERSION = "1.0"
RUN_SCHEMA_VERSION = "1.0"
FORM_NAMES = ("pretest", "posttest", "transfer", "retention")
ITEM_TYPES = {"single_choice", "multiple_choice", "numeric", "short_text"}
TRUTH_STATUSES = {"pass", "fail", "not-reviewed"}
EVIDENCE_TIERS = {
    "community-submitted",
    "evidence-complete",
    "coordinator-verified",
    "provider-verified",
}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,79}$")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    path: str
    severity: str = "error"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _required(
    obj: dict[str, Any],
    keys: tuple[str, ...],
    findings: list[Finding],
    path: str = "$",
) -> None:
    for key in keys:
        if key not in obj:
            findings.append(
                Finding("missing-field", f"Required field '{key}' is missing", f"{path}.{key}")
            )


def _valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def _validate_item(item: Any, path: str, findings: list[Finding]) -> None:
    if not isinstance(item, dict):
        findings.append(Finding("invalid-type", "Assessment item must be an object", path))
        return
    _required(item, ("id", "type", "prompt", "points"), findings, path)
    item_id = item.get("id")
    if not isinstance(item_id, str) or not ID_PATTERN.match(item_id):
        findings.append(
            Finding("invalid-id", "Item id must be a stable lowercase identifier", f"{path}.id")
        )
    item_type = item.get("type")
    if item_type not in ITEM_TYPES:
        findings.append(
            Finding(
                "invalid-item-type",
                f"Item type must be one of {sorted(ITEM_TYPES)}",
                f"{path}.type",
            )
        )
        return
    points = item.get("points")
    if not isinstance(points, (int, float)) or isinstance(points, bool) or points <= 0:
        findings.append(
            Finding("invalid-points", "Points must be a positive number", f"{path}.points")
        )

    if item_type in {"single_choice", "multiple_choice"}:
        choices = item.get("choices")
        answer = item.get("answer")
        if (
            not isinstance(choices, list)
            or len(choices) < 2
            or not all(
                isinstance(choice, dict)
                and isinstance(choice.get("id"), str)
                and isinstance(choice.get("text"), str)
                for choice in choices
            )
        ):
            findings.append(
                Finding(
                    "invalid-choices",
                    "Choice items need at least two id/text choices",
                    f"{path}.choices",
                )
            )
        choice_ids = {
            choice["id"]
            for choice in choices or []
            if isinstance(choice, dict) and isinstance(choice.get("id"), str)
        }
        if item_type == "single_choice" and answer not in choice_ids:
            findings.append(
                Finding(
                    "invalid-answer",
                    "Single-choice answer must name one choice id",
                    f"{path}.answer",
                )
            )
        if item_type == "multiple_choice" and (
            not isinstance(answer, list)
            or not answer
            or not all(isinstance(value, str) for value in answer)
            or not set(answer).issubset(choice_ids)
        ):
            findings.append(
                Finding(
                    "invalid-answer",
                    "Multiple-choice answer must be a non-empty list of choice ids",
                    f"{path}.answer",
                )
            )
    elif item_type == "numeric":
        if not isinstance(item.get("answer"), (int, float)) or isinstance(item.get("answer"), bool):
            findings.append(
                Finding("invalid-answer", "Numeric answer must be a number", f"{path}.answer")
            )
        tolerance = item.get("tolerance", 0)
        if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or tolerance < 0:
            findings.append(
                Finding(
                    "invalid-tolerance",
                    "Numeric tolerance must be non-negative",
                    f"{path}.tolerance",
                )
            )
    elif item_type == "short_text":
        rubric = item.get("rubric")
        if (
            not isinstance(rubric, list)
            or not rubric
            or not all(isinstance(entry, str) and entry.strip() for entry in rubric)
        ):
            findings.append(
                Finding(
                    "missing-rubric",
                    "Short-text items need a non-empty human-scoring rubric",
                    f"{path}.rubric",
                )
            )


def validate_task(task: Any) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(task, dict):
        return [Finding("invalid-type", "Task pack must be a JSON object", "$")]

    _required(
        task,
        (
            "schema_version",
            "task_id",
            "version",
            "title",
            "domain",
            "level",
            "language",
            "review_status",
            "estimated_teaching_minutes",
            "learning_objectives",
            "sources",
            "misconceptions",
            "critical_errors",
            "teaching_brief",
            "forms",
        ),
        findings,
    )
    if task.get("schema_version") != TASK_SCHEMA_VERSION:
        findings.append(
            Finding(
                "unsupported-schema",
                f"Task schema_version must be '{TASK_SCHEMA_VERSION}'",
                "$.schema_version",
            )
        )
    task_id = task.get("task_id")
    if not isinstance(task_id, str) or not ID_PATTERN.match(task_id):
        findings.append(
            Finding("invalid-id", "task_id must be a stable lowercase identifier", "$.task_id")
        )
    minutes = task.get("estimated_teaching_minutes")
    if not isinstance(minutes, int) or isinstance(minutes, bool) or not 2 <= minutes <= 60:
        findings.append(
            Finding(
                "invalid-duration",
                "estimated_teaching_minutes must be an integer from 2 to 60",
                "$.estimated_teaching_minutes",
            )
        )

    objectives = task.get("learning_objectives")
    if (
        not isinstance(objectives, list)
        or not objectives
        or not all(isinstance(value, str) and value.strip() for value in objectives)
    ):
        findings.append(
            Finding(
                "missing-objectives",
                "learning_objectives must be a non-empty string list",
                "$.learning_objectives",
            )
        )

    sources = task.get("sources")
    if not isinstance(sources, list) or not sources:
        findings.append(
            Finding("missing-sources", "At least one authoritative source is required", "$.sources")
        )
    else:
        for index, source in enumerate(sources):
            path = f"$.sources[{index}]"
            if not isinstance(source, dict):
                findings.append(Finding("invalid-source", "Source must be an object", path))
                continue
            _required(source, ("title", "publisher", "url"), findings, path)
            if not _valid_url(source.get("url")):
                findings.append(
                    Finding("invalid-source-url", "Source URL must use HTTPS", f"{path}.url")
                )

    for field in ("misconceptions", "critical_errors"):
        values = task.get(field)
        if not isinstance(values, list) or not values:
            findings.append(
                Finding(f"missing-{field}", f"{field} must be a non-empty list", f"$.{field}")
            )
        elif not all(
            isinstance(value, dict)
            and isinstance(value.get("id"), str)
            and isinstance(value.get("description"), str)
            for value in values
        ):
            findings.append(
                Finding(
                    f"invalid-{field}",
                    f"Every {field} entry needs id and description",
                    f"$.{field}",
                )
            )

    brief = task.get("teaching_brief")
    if not isinstance(brief, dict):
        findings.append(
            Finding("invalid-brief", "teaching_brief must be an object", "$.teaching_brief")
        )
    else:
        _required(
            brief,
            ("goal", "learner_profile", "instructions", "prohibited_disclosures"),
            findings,
            "$.teaching_brief",
        )

    forms = task.get("forms")
    if not isinstance(forms, dict):
        findings.append(Finding("invalid-forms", "forms must be an object", "$.forms"))
        return findings

    for required_form in ("pretest", "posttest", "transfer"):
        if not isinstance(forms.get(required_form), list) or not forms.get(required_form):
            findings.append(
                Finding(
                    "missing-form",
                    f"{required_form} must contain at least one item",
                    f"$.forms.{required_form}",
                )
            )

    all_ids: set[str] = set()
    for form_name in FORM_NAMES:
        items = forms.get(form_name, [])
        if items is None:
            continue
        if not isinstance(items, list):
            findings.append(
                Finding("invalid-form", f"{form_name} must be a list", f"$.forms.{form_name}")
            )
            continue
        for index, item in enumerate(items):
            path = f"$.forms.{form_name}[{index}]"
            _validate_item(item, path, findings)
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                if item["id"] in all_ids:
                    findings.append(
                        Finding(
                            "duplicate-item-id", f"Duplicate item id '{item['id']}'", f"{path}.id"
                        )
                    )
                all_ids.add(item["id"])

    return findings


def validate_run(run: Any, task: dict[str, Any] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(run, dict):
        return [Finding("invalid-type", "Run must be a JSON object", "$")]
    _required(
        run,
        (
            "schema_version",
            "run_id",
            "study_id",
            "participant_id",
            "task_id",
            "task_version",
            "tutor",
            "started_at",
            "teaching_seconds",
            "truth_status",
            "critical_error_ids",
            "evidence_tier",
            "assessments",
            "self_report",
        ),
        findings,
    )
    if run.get("schema_version") != RUN_SCHEMA_VERSION:
        findings.append(
            Finding(
                "unsupported-schema",
                f"Run schema_version must be '{RUN_SCHEMA_VERSION}'",
                "$.schema_version",
            )
        )
    for field in ("run_id", "study_id", "participant_id", "task_id"):
        value = run.get(field)
        if not isinstance(value, str) or not ID_PATTERN.match(value):
            findings.append(
                Finding(
                    "invalid-id", f"{field} must be a stable lowercase identifier", f"$.{field}"
                )
            )
    tutor = run.get("tutor")
    if not isinstance(tutor, dict):
        findings.append(Finding("invalid-tutor", "tutor must be an object", "$.tutor"))
    else:
        _required(tutor, ("id", "label", "product", "model", "mode"), findings, "$.tutor")
    seconds = run.get("teaching_seconds")
    if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds <= 0:
        findings.append(
            Finding(
                "invalid-duration",
                "teaching_seconds must be a positive integer",
                "$.teaching_seconds",
            )
        )
    if run.get("truth_status") not in TRUTH_STATUSES:
        findings.append(
            Finding(
                "invalid-truth-status",
                f"truth_status must be one of {sorted(TRUTH_STATUSES)}",
                "$.truth_status",
            )
        )
    if run.get("evidence_tier") not in EVIDENCE_TIERS:
        findings.append(
            Finding(
                "invalid-evidence-tier",
                f"evidence_tier must be one of {sorted(EVIDENCE_TIERS)}",
                "$.evidence_tier",
            )
        )
    error_ids = run.get("critical_error_ids")
    if not isinstance(error_ids, list) or not all(isinstance(value, str) for value in error_ids):
        findings.append(
            Finding(
                "invalid-critical-errors",
                "critical_error_ids must be a list of strings",
                "$.critical_error_ids",
            )
        )
    if run.get("truth_status") == "pass" and error_ids:
        findings.append(
            Finding(
                "truth-conflict",
                "A passing truth status cannot include critical errors",
                "$.truth_status",
            )
        )
    assessments = run.get("assessments")
    if not isinstance(assessments, dict):
        findings.append(
            Finding("invalid-assessments", "assessments must be an object", "$.assessments")
        )
    else:
        for form_name in ("pretest", "posttest", "transfer"):
            if not isinstance(assessments.get(form_name), dict):
                findings.append(
                    Finding(
                        "missing-assessment",
                        f"{form_name} responses must be an object",
                        f"$.assessments.{form_name}",
                    )
                )
    self_report = run.get("self_report")
    if not isinstance(self_report, dict):
        findings.append(
            Finding("invalid-self-report", "self_report must be an object", "$.self_report")
        )
    else:
        for field in ("understanding_before", "understanding_after", "cognitive_effort"):
            value = self_report.get(field)
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not 0 <= value <= 100
            ):
                findings.append(
                    Finding(
                        "invalid-self-report",
                        f"{field} must be a number from 0 to 100",
                        f"$.self_report.{field}",
                    )
                )

    if task is not None:
        if run.get("task_id") != task.get("task_id"):
            findings.append(
                Finding("task-mismatch", "Run task_id does not match task pack", "$.task_id")
            )
        if run.get("task_version") != task.get("version"):
            findings.append(
                Finding(
                    "version-mismatch",
                    "Run task_version does not match task pack",
                    "$.task_version",
                )
            )
        valid_error_ids = {
            item.get("id") for item in task.get("critical_errors", []) if isinstance(item, dict)
        }
        for error_id in error_ids or []:
            if error_id not in valid_error_ids:
                findings.append(
                    Finding(
                        "unknown-critical-error",
                        f"Critical error '{error_id}' is not declared by the task",
                        "$.critical_error_ids",
                    )
                )

    return findings
