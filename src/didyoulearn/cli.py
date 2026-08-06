"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .assignment import assign_tutor
from .demo import demo_runs, demo_task
from .errors import DidYouLearnError
from .evidence import make_receipt, verify_receipt
from .io import discover_json, read_json, read_records, write_json
from .privacy import pseudonymize, public_run
from .reporting import write_report
from .scoring import score_study
from .server import serve
from .validation import validate_run, validate_task


def _task_map(path: str | Path) -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for candidate in discover_json(path):
        value = read_json(candidate)
        if not isinstance(value, dict) or "task_id" not in value:
            continue
        findings = validate_task(value)
        errors = [finding for finding in findings if finding.severity == "error"]
        if errors:
            rendered = "; ".join(f"{finding.path}: {finding.message}" for finding in errors[:8])
            raise DidYouLearnError(f"{candidate}: {rendered}")
        task_id = str(value["task_id"])
        if task_id in tasks:
            raise DidYouLearnError(f"Duplicate task_id '{task_id}'")
        tasks[task_id] = value
    if not tasks:
        raise DidYouLearnError(f"No task packs found in {path}")
    return tasks


def _validate(paths: list[str], kind: str) -> int:
    checked = 0
    errors = 0
    for raw_path in paths:
        for path in discover_json(raw_path):
            value = read_json(path)
            selected = kind
            if selected == "auto":
                selected = (
                    "task" if isinstance(value, dict) and "learning_objectives" in value else "run"
                )
            findings = validate_task(value) if selected == "task" else validate_run(value)
            checked += 1
            if findings:
                print(path)
                for finding in findings:
                    print(
                        f"  {finding.severity.upper()} {finding.code} {finding.path}: {finding.message}"
                    )
                    if finding.severity == "error":
                        errors += 1
            else:
                print(f"OK {path}")
    print(f"Checked {checked} file(s); {errors} error(s).")
    return 1 if errors else 0


def _score(args: argparse.Namespace) -> int:
    tasks = _task_map(args.tasks)
    runs = read_records(args.runs)
    study = read_json(args.study) if args.study else {}
    result = score_study(
        tasks,
        runs,
        study=study,
        minimum_rank_n=args.minimum_rank_n,
        bootstrap_iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    write_json(args.output, result)
    print(f"Wrote {args.output}")
    return 0


def _report(args: argparse.Namespace) -> int:
    result = read_json(args.scores)
    if not isinstance(result, dict):
        raise DidYouLearnError("Scores file must contain an object")
    write_report(result, args.output)
    print(f"Wrote {args.output}")
    return 0


def _demo(args: argparse.Namespace) -> int:
    destination = Path(args.output)
    task = demo_task()
    runs = demo_runs()
    result = score_study(
        {task["task_id"]: task},
        runs,
        study={
            "study_id": "fictional-teaching-study",
            "title": "Fictional teaching-outcome demonstration",
            "question": "Can the pipeline separate mastery, transfer, retention, and confidence?",
            "synthetic": True,
        },
    )
    write_json(destination / "task.json", task)
    write_json(destination / "runs.json", runs)
    write_json(destination / "scores.json", result)
    write_report(result, destination / "report.html")
    print(f"Wrote fictional demonstration to {destination}")
    return 0


def _receipt(args: argparse.Namespace) -> int:
    run = read_json(args.run)
    task = read_json(args.task)
    transcript = Path(args.transcript).read_text(encoding="utf-8") if args.transcript else None
    write_json(args.output, make_receipt(run=run, task=task, transcript=transcript))
    print(f"Wrote {args.output}")
    return 0


def _verify_receipt(args: argparse.Namespace) -> int:
    receipt = read_json(args.receipt)
    run = read_json(args.run)
    task = read_json(args.task)
    transcript = Path(args.transcript).read_text(encoding="utf-8") if args.transcript else None
    failures = verify_receipt(receipt, run=run, task=task, transcript=transcript)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("OK receipt verified")
    return 0


def _assign(args: argparse.Namespace) -> int:
    existing = read_json(args.book) if Path(args.book).exists() else []
    if not isinstance(existing, list):
        raise DidYouLearnError("Assignment book must contain a JSON list")
    row = assign_tutor(
        participant_id=args.participant,
        task_id=args.task,
        stratum=args.stratum,
        tutors=args.tutors,
        existing=existing,
        salt=args.salt,
    )
    existing.append(row)
    write_json(args.book, existing)
    print(json.dumps(row, ensure_ascii=False))
    return 0


def _public_run(args: argparse.Namespace) -> int:
    run = read_json(args.run)
    if not isinstance(run, dict):
        raise DidYouLearnError("Run file must contain an object")
    write_json(args.output, public_run(run))
    print(f"Wrote {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="didyoulearn",
        description="Measure whether an AI tutor produced demonstrated learning.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate task packs or run records")
    validate_parser.add_argument("paths", nargs="+")
    validate_parser.add_argument("--kind", choices=("auto", "task", "run"), default="auto")
    validate_parser.set_defaults(handler=lambda args: _validate(args.paths, args.kind))

    score_parser = subparsers.add_parser("score", help="Score a study from task packs and runs")
    score_parser.add_argument("--tasks", required=True)
    score_parser.add_argument("--runs", required=True)
    score_parser.add_argument("--study")
    score_parser.add_argument("--output", required=True)
    score_parser.add_argument("--minimum-rank-n", type=int, default=5)
    score_parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    score_parser.add_argument("--seed", type=int, default=2026)
    score_parser.set_defaults(handler=_score)

    report_parser = subparsers.add_parser("report", help="Render a self-contained HTML report")
    report_parser.add_argument("--scores", required=True)
    report_parser.add_argument("--output", required=True)
    report_parser.set_defaults(handler=_report)

    demo_parser = subparsers.add_parser(
        "demo", help="Generate an explicitly fictional complete study"
    )
    demo_parser.add_argument("--output", default="didyoulearn-demo")
    demo_parser.set_defaults(handler=_demo)

    receipt_parser = subparsers.add_parser("receipt", help="Create an integrity receipt")
    receipt_parser.add_argument("--run", required=True)
    receipt_parser.add_argument("--task", required=True)
    receipt_parser.add_argument("--transcript")
    receipt_parser.add_argument("--output", required=True)
    receipt_parser.set_defaults(handler=_receipt)

    verify_parser = subparsers.add_parser("verify-receipt", help="Verify an integrity receipt")
    verify_parser.add_argument("--receipt", required=True)
    verify_parser.add_argument("--run", required=True)
    verify_parser.add_argument("--task", required=True)
    verify_parser.add_argument("--transcript")
    verify_parser.set_defaults(handler=_verify_receipt)

    assign_parser = subparsers.add_parser("assign", help="Assign one balanced tutor condition")
    assign_parser.add_argument("--participant", required=True)
    assign_parser.add_argument("--task", required=True)
    assign_parser.add_argument("--stratum", default="default")
    assign_parser.add_argument("--tutors", required=True, nargs="+")
    assign_parser.add_argument("--book", required=True)
    assign_parser.add_argument("--salt", required=True)
    assign_parser.set_defaults(handler=_assign)

    pseudonym_parser = subparsers.add_parser("pseudonym", help="Create a study-specific pseudonym")
    pseudonym_parser.add_argument("identifier")
    pseudonym_parser.add_argument("--secret", required=True)
    pseudonym_parser.set_defaults(
        handler=lambda args: print(pseudonymize(args.identifier, args.secret)) or 0
    )

    release_parser = subparsers.add_parser("public-run", help="Remove default private run fields")
    release_parser.add_argument("--run", required=True)
    release_parser.add_argument("--output", required=True)
    release_parser.set_defaults(handler=_public_run)

    serve_parser = subparsers.add_parser("serve", help="Open the local browser study lab")
    serve_parser.add_argument("--directory")
    serve_parser.add_argument("--port", type=int, default=8765)
    serve_parser.add_argument("--no-browser", action="store_true")
    serve_parser.set_defaults(
        handler=lambda args: (
            serve(args.directory, port=args.port, open_browser=not args.no_browser) or 0
        )
    )

    doctor_parser = subparsers.add_parser("doctor", help="Show runtime and privacy boundary")
    doctor_parser.set_defaults(
        handler=lambda _args: (
            print(
                json.dumps(
                    {
                        "didyoulearn": __version__,
                        "python": platform.python_version(),
                        "platform": platform.platform(),
                        "runtime_dependencies": 0,
                        "default_bind": "127.0.0.1",
                        "network_model_calls": False,
                    },
                    indent=2,
                )
            )
            or 0
        )
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (DidYouLearnError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    sys.exit(main())
