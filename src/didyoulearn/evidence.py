"""Canonical hashes and portable study receipts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def make_receipt(
    *,
    run: dict[str, Any],
    task: dict[str, Any],
    transcript: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    receipt = {
        "receipt_version": "1.0",
        "run_id": run.get("run_id"),
        "task_id": task.get("task_id"),
        "task_version": task.get("version"),
        "run_sha256": sha256_digest(run),
        "task_sha256": sha256_digest(task),
        "transcript_sha256": hashlib.sha256(transcript.encode("utf-8")).hexdigest()
        if transcript is not None
        else None,
        "created_at": created_at or datetime.now(UTC).replace(microsecond=0).isoformat(),
        "claim": (
            "This receipt proves byte-level integrity for the recorded materials. "
            "It does not prove commercial model identity or experimental validity."
        ),
    }
    receipt["receipt_sha256"] = sha256_digest(receipt)
    return receipt


def verify_receipt(
    receipt: dict[str, Any],
    *,
    run: dict[str, Any],
    task: dict[str, Any],
    transcript: str | None = None,
) -> list[str]:
    failures: list[str] = []
    if receipt.get("run_sha256") != sha256_digest(run):
        failures.append("run hash mismatch")
    if receipt.get("task_sha256") != sha256_digest(task):
        failures.append("task hash mismatch")
    expected_transcript = (
        hashlib.sha256(transcript.encode("utf-8")).hexdigest() if transcript is not None else None
    )
    if receipt.get("transcript_sha256") != expected_transcript:
        failures.append("transcript hash mismatch")
    without_receipt_hash = dict(receipt)
    observed = without_receipt_hash.pop("receipt_sha256", None)
    if observed != sha256_digest(without_receipt_hash):
        failures.append("receipt hash mismatch")
    return failures
