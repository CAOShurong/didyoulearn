"""Deterministic fictional data used to exercise the full report pipeline."""

from __future__ import annotations

from typing import Any


def demo_task() -> dict[str, Any]:
    def item(form: str, number: int, answer: str) -> dict[str, Any]:
        return {
            "id": f"{form}-{number}",
            "type": "single_choice",
            "prompt": f"Fictional assessment item {number} for the {form} form.",
            "points": 1,
            "choices": [
                {"id": "a", "text": "Option A"},
                {"id": "b", "text": "Option B"},
                {"id": "c", "text": "Option C"},
            ],
            "answer": answer,
        }

    return {
        "schema_version": "1.0",
        "task_id": "demo.calibration",
        "version": "1.0.0",
        "title": "Fictional concept-learning demonstration",
        "domain": "demonstration",
        "level": "introductory",
        "language": "en",
        "review_status": "synthetic-demo",
        "estimated_teaching_minutes": 8,
        "learning_objectives": ["Exercise the outcome-scoring pipeline."],
        "prerequisites": [],
        "sources": [
            {
                "title": "DidYouLearn demonstration documentation",
                "publisher": "DidYouLearn",
                "url": "https://github.com/CAOShurong/didyoulearn",
            }
        ],
        "misconceptions": [{"id": "demo-m1", "description": "This task is real research data."}],
        "critical_errors": [{"id": "demo-e1", "description": "Presenting fictional data as real."}],
        "teaching_brief": {
            "goal": "Exercise the software.",
            "learner_profile": "A fictional participant.",
            "instructions": ["Use only fictional content."],
            "prohibited_disclosures": ["Do not claim that a named commercial model produced data."],
        },
        "forms": {
            "pretest": [
                item("pre", 1, "a"),
                item("pre", 2, "b"),
                item("pre", 3, "c"),
                item("pre", 4, "a"),
            ],
            "posttest": [
                item("post", 1, "b"),
                item("post", 2, "c"),
                item("post", 3, "a"),
                item("post", 4, "b"),
            ],
            "transfer": [
                item("transfer", 1, "c"),
                item("transfer", 2, "a"),
                item("transfer", 3, "b"),
                item("transfer", 4, "c"),
            ],
            "retention": [
                item("retention", 1, "a"),
                item("retention", 2, "c"),
                item("retention", 3, "b"),
                item("retention", 4, "a"),
            ],
        },
    }


def _answers(items: list[dict[str, Any]], correct_count: int, shift: int) -> dict[str, str]:
    output: dict[str, str] = {}
    wrong = {"a": "b", "b": "c", "c": "a"}
    for index, item in enumerate(items):
        correct = (index + shift) % len(items) < correct_count
        output[item["id"]] = item["answer"] if correct else wrong[item["answer"]]
    return output


def demo_runs() -> list[dict[str, Any]]:
    task = demo_task()
    tutor_profiles = [
        ("atlas", "Tutor Atlas", 3, 4, 3, 3, 78),
        ("beacon", "Tutor Beacon", 2, 4, 4, 3, 85),
        ("cedar", "Tutor Cedar", 3, 3, 3, 2, 72),
    ]
    runs: list[dict[str, Any]] = []
    for tutor_index, profile in enumerate(tutor_profiles):
        tutor_id, label, pre, post, transfer, retention, understanding = profile
        for repeat in range(6):
            forms = task["forms"]
            runs.append(
                {
                    "schema_version": "1.0",
                    "run_id": f"demo-{tutor_id}-{repeat + 1:02d}",
                    "study_id": "fictional-teaching-study",
                    "participant_id": f"p-demo-{tutor_index}{repeat:02d}",
                    "task_id": task["task_id"],
                    "task_version": task["version"],
                    "tutor": {
                        "id": tutor_id,
                        "label": label,
                        "product": "fictional",
                        "model": "fictional",
                        "mode": "demonstration",
                    },
                    "started_at": f"2026-08-{repeat + 1:02d}T09:00:00Z",
                    "teaching_seconds": 420 + repeat * 12,
                    "truth_status": "pass",
                    "critical_error_ids": [],
                    "evidence_tier": "coordinator-verified",
                    "assessments": {
                        "pretest": _answers(forms["pretest"], max(1, pre - (repeat % 2)), repeat),
                        "posttest": _answers(
                            forms["posttest"], max(1, post - (repeat % 3 == 0)), repeat
                        ),
                        "transfer": _answers(
                            forms["transfer"], max(1, transfer - (repeat % 4 == 0)), repeat
                        ),
                        "retention": _answers(
                            forms["retention"], max(1, retention - (repeat % 5 == 0)), repeat
                        ),
                    },
                    "self_report": {
                        "understanding_before": 35 + repeat,
                        "understanding_after": understanding + (repeat % 3) * 2,
                        "cognitive_effort": 58 + tutor_index * 4,
                    },
                }
            )
    return runs
