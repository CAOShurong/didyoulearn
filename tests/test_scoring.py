from copy import deepcopy

import pytest

from didyoulearn.demo import demo_runs, demo_task
from didyoulearn.scoring import score_form, score_item, score_run, score_study


def test_score_item_types():
    assert score_item({"type": "single_choice", "answer": "a", "points": 2}, "a") == 2
    assert score_item({"type": "single_choice", "answer": "a", "points": 2}, "b") == 0
    assert (
        score_item(
            {"type": "multiple_choice", "answer": ["a", "c"], "points": 2},
            ["c", "a"],
        )
        == 2
    )
    assert (
        score_item({"type": "numeric", "answer": 3.14, "tolerance": 0.01, "points": 1}, 3.145) == 1
    )
    assert (
        score_item(
            {"type": "short_text", "rubric": ["idea"], "points": 3}, {"answer": "x", "score": 2}
        )
        == 2
    )


def test_unscored_short_text_is_not_in_denominator():
    items = [{"id": "q", "type": "short_text", "rubric": ["idea"], "points": 2}]
    result = score_form(items, {"q": "answer"})
    assert result.proportion is None
    assert result.possible == 0


def test_demo_run_scores_complete_outcomes():
    result = score_run(demo_task(), demo_runs()[0])
    assert result.complete
    assert result.truth_pass
    assert result.pretest is not None
    assert result.posttest is not None
    assert result.transfer is not None
    assert result.retention is not None


def test_unscored_manual_item_makes_run_incomplete():
    task = demo_task()
    run = deepcopy(demo_runs()[0])
    task["forms"]["posttest"].append(
        {
            "id": "post-manual",
            "type": "short_text",
            "prompt": "Explain the idea.",
            "rubric": ["States the relevant principle."],
            "points": 1,
        }
    )
    run["assessments"]["posttest"]["post-manual"] = {"answer": "An explanation."}

    result = score_run(task, run)

    assert result.posttest is None
    assert not result.complete


def test_truth_failure_blocks_safe_group():
    task = demo_task()
    runs = demo_runs()
    failed = deepcopy(runs[0])
    failed["truth_status"] = "fail"
    failed["critical_error_ids"] = ["demo-e1"]
    failed["run_id"] = "demo-atlas-failed"
    result = score_study(
        {task["task_id"]: task},
        [*runs, failed],
        minimum_rank_n=5,
        bootstrap_iterations=100,
    )
    atlas = next(row for row in result["tutors"] if row["tutor_id"] == "atlas")
    assert atlas["truth_pass_rate"] == pytest.approx(6 / 7)
    assert not atlas["rank_eligible"]
    assert atlas["rank"] is None


def test_rank_is_withheld_below_sample_floor():
    task = demo_task()
    result = score_study(
        {task["task_id"]: task},
        demo_runs()[:3],
        minimum_rank_n=5,
        bootstrap_iterations=50,
    )
    assert result["tutors"][0]["rank"] is None
    assert not result["tutors"][0]["rank_eligible"]


def test_demo_study_ranks_three_tutors_deterministically():
    task = demo_task()
    result = score_study(
        {task["task_id"]: task},
        demo_runs(),
        bootstrap_iterations=100,
        seed=17,
    )
    assert result["counts"] == {"runs": 18, "tasks": 1, "participants": 18, "tutors": 3}
    ranks = [row["rank"] for row in result["tutors"]]
    assert ranks == [1, 2, 3]
    assert all(row["adjusted_posttest_interval"] is not None for row in result["tutors"])


def test_missing_task_is_rejected():
    with pytest.raises(Exception, match="No task pack"):
        score_study({}, demo_runs()[:1])


@pytest.mark.parametrize(
    ("keyword", "value"),
    [("minimum_rank_n", 0), ("bootstrap_iterations", 0)],
)
def test_invalid_study_settings_are_rejected(keyword, value):
    kwargs = {keyword: value}
    with pytest.raises(ValueError, match=keyword):
        score_study({demo_task()["task_id"]: demo_task()}, demo_runs()[:1], **kwargs)
