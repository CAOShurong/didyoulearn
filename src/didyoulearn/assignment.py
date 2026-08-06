"""Deterministic, balanced tutor-condition assignment."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any

from .errors import StudyDesignError


def assign_tutor(
    *,
    participant_id: str,
    task_id: str,
    stratum: str,
    tutors: list[str],
    existing: list[dict[str, Any]],
    salt: str,
) -> dict[str, str]:
    if not tutors or len(set(tutors)) != len(tutors):
        raise StudyDesignError("Tutor ids must be a non-empty unique list")
    if not salt:
        raise StudyDesignError("A study-specific assignment salt is required")
    duplicate = any(
        row.get("participant_id") == participant_id and row.get("task_id") == task_id
        for row in existing
    )
    if duplicate:
        raise StudyDesignError(
            "A participant cannot be assigned two tutor conditions for the same task"
        )

    relevant = [
        row for row in existing if row.get("task_id") == task_id and row.get("stratum") == stratum
    ]
    counts = Counter(str(row.get("tutor_id")) for row in relevant)
    minimum = min(counts.get(tutor, 0) for tutor in tutors)
    candidates = [tutor for tutor in tutors if counts.get(tutor, 0) == minimum]
    candidates.sort(
        key=lambda tutor: hashlib.sha256(
            f"{salt}\0{participant_id}\0{task_id}\0{stratum}\0{tutor}".encode()
        ).hexdigest()
    )
    return {
        "participant_id": participant_id,
        "task_id": task_id,
        "stratum": stratum,
        "tutor_id": candidates[0],
    }
