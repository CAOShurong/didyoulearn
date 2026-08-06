"""Small, deterministic JSON and record-loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import DidYouLearnError


def read_json(path: str | Path) -> Any:
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DidYouLearnError(f"File not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise DidYouLearnError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def write_json(path: str | Path, value: Any) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def read_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DidYouLearnError(
                    f"Invalid JSONL in {source} at line {number}: {exc.msg}"
                ) from exc
            if not isinstance(record, dict):
                raise DidYouLearnError(f"Record {number} in {source} is not an object")
            records.append(record)
        return records

    value = read_json(source)
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    if isinstance(value, dict) and isinstance(value.get("runs"), list):
        runs = value["runs"]
        if all(isinstance(item, dict) for item in runs):
            return runs
    raise DidYouLearnError(f"{source} must be a JSON array, a runs object, or JSONL records")


def discover_json(path: str | Path) -> list[Path]:
    source = Path(path)
    if source.is_file():
        return [source]
    if source.is_dir():
        return sorted(candidate for candidate in source.rglob("*.json") if candidate.is_file())
    raise DidYouLearnError(f"Path not found: {source}")
