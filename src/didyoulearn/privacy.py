"""Pseudonym and release-minimization helpers."""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

PRIVATE_RUN_FIELDS = {
    "transcript",
    "notes",
    "email",
    "name",
    "provider_account",
    "screenshots",
}


def pseudonymize(raw_identifier: str, secret: str, *, prefix: str = "p") -> str:
    if not raw_identifier or not secret:
        raise ValueError("Both raw_identifier and secret are required")
    digest = hmac.new(secret.encode(), raw_identifier.encode(), hashlib.sha256).hexdigest()
    return f"{prefix}-{digest[:16]}"


def public_run(run: dict[str, Any]) -> dict[str, Any]:
    released = {key: value for key, value in run.items() if key not in PRIVATE_RUN_FIELDS}
    released["release_note"] = (
        "Direct identifiers and free-text evidence were removed by DidYouLearn's default release filter."
    )
    return released
