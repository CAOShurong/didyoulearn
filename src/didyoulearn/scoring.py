"""Outcome scoring and transparent pilot-level aggregation."""

from __future__ import annotations

import math
import random
import statistics
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .errors import ValidationFailure
from .validation import validate_run, validate_task


@dataclass(frozen=True)
class FormScore:
    earned: float
    possible: float
    proportion: float | None
    scored_items: int
    total_items: int


@dataclass(frozen=True)
class RunScore:
    run_id: str
    study_id: str
    participant_id: str
    task_id: str
    tutor_id: str
    tutor_label: str
    evidence_tier: str
    truth_status: str
    truth_pass: bool
    pretest: float | None
    posttest: float | None
    transfer: float | None
    retention: float | None
    raw_gain: float | None
    illusion_gap: float | None
    efficiency_per_10_min: float | None
    teaching_seconds: int
    complete: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _unwrap_response(value: Any) -> tuple[Any, float | None]:
    if isinstance(value, dict) and "answer" in value:
        manual = value.get("score")
        return value["answer"], float(manual) if isinstance(manual, (int, float)) else None
    return value, None


def score_item(item: dict[str, Any], response: Any) -> float | None:
    answer, manual_score = _unwrap_response(response)
    points = float(item["points"])
    item_type = item["type"]

    if item_type == "short_text":
        if manual_score is None:
            return None
        return min(points, max(0.0, manual_score))
    if answer is None:
        return 0.0
    if item_type == "single_choice":
        return points if answer == item["answer"] else 0.0
    if item_type == "multiple_choice":
        if not isinstance(answer, list):
            return 0.0
        return points if set(answer) == set(item["answer"]) else 0.0
    if item_type == "numeric":
        if not isinstance(answer, (int, float)) or isinstance(answer, bool):
            return 0.0
        tolerance = float(item.get("tolerance", 0))
        return (
            points if math.isclose(float(answer), float(item["answer"]), abs_tol=tolerance) else 0.0
        )
    return None


def score_form(items: list[dict[str, Any]], responses: dict[str, Any]) -> FormScore:
    earned = 0.0
    possible = 0.0
    scored = 0
    for item in items:
        item_score = score_item(item, responses.get(item["id"]))
        if item_score is None:
            continue
        earned += item_score
        possible += float(item["points"])
        scored += 1
    proportion = earned / possible if possible else None
    return FormScore(
        earned=round(earned, 8),
        possible=round(possible, 8),
        proportion=round(proportion, 8) if proportion is not None else None,
        scored_items=scored,
        total_items=len(items),
    )


def _difference(after: float | None, before: float | None) -> float | None:
    if after is None or before is None:
        return None
    return round(after - before, 8)


def score_run(task: dict[str, Any], run: dict[str, Any]) -> RunScore:
    task_findings = validate_task(task)
    run_findings = validate_run(run, task)
    errors = [finding for finding in [*task_findings, *run_findings] if finding.severity == "error"]
    if errors:
        rendered = "; ".join(f"{finding.path}: {finding.message}" for finding in errors[:8])
        raise ValidationFailure(rendered)

    forms = task["forms"]
    assessments = run["assessments"]
    values: dict[str, float | None] = {}
    for form_name in ("pretest", "posttest", "transfer", "retention"):
        items = forms.get(form_name, [])
        responses = assessments.get(form_name, {})
        if items and isinstance(responses, dict):
            form_score = score_form(items, responses)
            values[form_name] = (
                form_score.proportion if form_score.scored_items == form_score.total_items else None
            )
        else:
            values[form_name] = None

    raw_gain = _difference(values["posttest"], values["pretest"])
    understanding_after = float(run["self_report"]["understanding_after"]) / 100
    illusion_gap = (
        round(understanding_after - values["posttest"], 8)
        if values["posttest"] is not None
        else None
    )
    minutes = int(run["teaching_seconds"]) / 60
    efficiency = round(raw_gain * 10 / minutes, 8) if raw_gain is not None and minutes > 0 else None
    truth_pass = run["truth_status"] == "pass" and not run["critical_error_ids"]
    complete = all(values[name] is not None for name in ("pretest", "posttest", "transfer"))
    tutor = run["tutor"]

    return RunScore(
        run_id=run["run_id"],
        study_id=run["study_id"],
        participant_id=run["participant_id"],
        task_id=run["task_id"],
        tutor_id=tutor["id"],
        tutor_label=tutor["label"],
        evidence_tier=run["evidence_tier"],
        truth_status=run["truth_status"],
        truth_pass=truth_pass,
        pretest=values["pretest"],
        posttest=values["posttest"],
        transfer=values["transfer"],
        retention=values["retention"],
        raw_gain=raw_gain,
        illusion_gap=illusion_gap,
        efficiency_per_10_min=efficiency,
        teaching_seconds=int(run["teaching_seconds"]),
        complete=complete,
    )


def _mean(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return round(statistics.fmean(present), 8) if present else None


def _pooled_slope(scores: list[RunScore]) -> tuple[float, float]:
    rows = [score for score in scores if score.truth_pass and score.complete]
    if len(rows) < 2:
        return 0.0, _mean([score.pretest for score in rows]) or 0.0
    pre = [float(score.pretest) for score in rows if score.pretest is not None]
    post = [float(score.posttest) for score in rows if score.posttest is not None]
    mean_pre = statistics.fmean(pre)
    mean_post = statistics.fmean(post)
    variance = sum((value - mean_pre) ** 2 for value in pre)
    if variance == 0:
        return 0.0, mean_pre
    covariance = sum((x - mean_pre) * (y - mean_post) for x, y in zip(pre, post, strict=True))
    return covariance / variance, mean_pre


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _bootstrap_interval(
    values: list[float],
    *,
    iterations: int,
    seed: int,
    confidence: float = 0.95,
) -> list[float] | None:
    if len(values) < 2:
        return None
    generator = random.Random(seed)
    estimates = [
        statistics.fmean(generator.choice(values) for _ in range(len(values)))
        for _ in range(iterations)
    ]
    tail = (1 - confidence) / 2
    return [
        round(_percentile(estimates, tail), 8),
        round(_percentile(estimates, 1 - tail), 8),
    ]


def score_study(
    tasks: dict[str, dict[str, Any]],
    runs: list[dict[str, Any]],
    *,
    study: dict[str, Any] | None = None,
    minimum_rank_n: int = 5,
    bootstrap_iterations: int = 2000,
    seed: int = 2026,
) -> dict[str, Any]:
    if minimum_rank_n < 1:
        raise ValueError("minimum_rank_n must be at least 1")
    if bootstrap_iterations < 1:
        raise ValueError("bootstrap_iterations must be at least 1")

    scores: list[RunScore] = []
    for run in runs:
        task = tasks.get(str(run.get("task_id")))
        if task is None:
            raise ValidationFailure(f"No task pack found for run task_id '{run.get('task_id')}'")
        scores.append(score_run(task, run))

    slope, grand_pre = _pooled_slope(scores)
    grouped: dict[str, list[RunScore]] = defaultdict(list)
    for score in scores:
        grouped[score.tutor_id].append(score)

    tutor_rows: list[dict[str, Any]] = []
    for tutor_index, (tutor_id, group) in enumerate(sorted(grouped.items())):
        valid = [score for score in group if score.truth_pass and score.complete]
        adjusted = [
            float(score.posttest) - slope * (float(score.pretest) - grand_pre)
            for score in valid
            if score.posttest is not None and score.pretest is not None
        ]
        truth_reviewed = [score for score in group if score.truth_status != "not-reviewed"]
        truth_pass_rate = (
            sum(score.truth_pass for score in truth_reviewed) / len(truth_reviewed)
            if truth_reviewed
            else None
        )
        retention_values = [score.retention for score in valid if score.retention is not None]
        row = {
            "tutor_id": tutor_id,
            "tutor_label": group[0].tutor_label,
            "n_total": len(group),
            "n_complete_truth_pass": len(valid),
            "n_retention": len(retention_values),
            "truth_pass_rate": round(truth_pass_rate, 8) if truth_pass_rate is not None else None,
            "pretest": _mean([score.pretest for score in valid]),
            "posttest": _mean([score.posttest for score in valid]),
            "adjusted_posttest": round(statistics.fmean(adjusted), 8) if adjusted else None,
            "adjusted_posttest_interval": _bootstrap_interval(
                adjusted,
                iterations=bootstrap_iterations,
                seed=seed + tutor_index,
            ),
            "raw_gain": _mean([score.raw_gain for score in valid]),
            "transfer": _mean([score.transfer for score in valid]),
            "retention": _mean(retention_values),
            "illusion_gap": _mean([score.illusion_gap for score in valid]),
            "efficiency_per_10_min": _mean([score.efficiency_per_10_min for score in valid]),
            "rank_eligible": len(valid) >= minimum_rank_n
            and truth_pass_rate is not None
            and truth_pass_rate >= 0.95,
            "rank": None,
        }
        tutor_rows.append(row)

    eligible = sorted(
        (row for row in tutor_rows if row["rank_eligible"]),
        key=lambda row: (-float(row["adjusted_posttest"]), row["tutor_id"]),
    )
    for rank, row in enumerate(eligible, start=1):
        row["rank"] = rank

    tutor_rows.sort(key=lambda row: (row["rank"] is None, row["rank"] or 10**9, row["tutor_id"]))
    study_meta = {
        "study_id": scores[0].study_id if scores else "empty-study",
        "title": "DidYouLearn study",
        "synthetic": False,
        **(study or {}),
    }
    return {
        "schema_version": "1.0",
        "study": study_meta,
        "method": {
            "primary": "common-slope covariance-adjusted post-test mean",
            "pooled_pretest_slope": round(slope, 8),
            "grand_pretest_mean": round(grand_pre, 8),
            "bootstrap_iterations": bootstrap_iterations,
            "bootstrap_seed": seed,
            "minimum_rank_n": minimum_rank_n,
            "truth_pass_threshold": 0.95,
        },
        "counts": {
            "runs": len(scores),
            "tasks": len({score.task_id for score in scores}),
            "participants": len({score.participant_id for score in scores}),
            "tutors": len(grouped),
        },
        "tutors": tutor_rows,
        "runs": [score.to_dict() for score in scores],
        "interpretation": [
            "Correctness is a rank gate, not a compensable style score.",
            "A withheld rank means the evidence floor was not met; it does not mean the tutor is poor.",
            "The built-in adjustment is suitable for pilot diagnostics, not a substitute for a pre-registered hierarchical analysis.",
            "Community-submitted model identities are claims unless coordinator or provider verification is documented.",
        ],
    }
