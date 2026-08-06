from copy import deepcopy

from didyoulearn.demo import demo_runs, demo_task
from didyoulearn.validation import validate_run, validate_task


def codes(findings):
    return {finding.code for finding in findings}


def test_demo_task_is_valid():
    assert validate_task(demo_task()) == []


def test_demo_runs_are_valid_against_task():
    task = demo_task()
    assert all(validate_run(run, task) == [] for run in demo_runs())


def test_task_requires_transfer_form():
    task = demo_task()
    task["forms"]["transfer"] = []
    assert "missing-form" in codes(validate_task(task))


def test_task_rejects_duplicate_item_ids():
    task = demo_task()
    task["forms"]["posttest"][0]["id"] = task["forms"]["pretest"][0]["id"]
    assert "duplicate-item-id" in codes(validate_task(task))


def test_task_rejects_non_https_source():
    task = demo_task()
    task["sources"][0]["url"] = "http://example.test/task"
    assert "invalid-source-url" in codes(validate_task(task))


def test_run_rejects_truth_conflict():
    task = demo_task()
    run = deepcopy(demo_runs()[0])
    run["critical_error_ids"] = ["demo-e1"]
    assert "truth-conflict" in codes(validate_run(run, task))


def test_run_rejects_unknown_critical_error():
    task = demo_task()
    run = deepcopy(demo_runs()[0])
    run["truth_status"] = "fail"
    run["critical_error_ids"] = ["not-declared"]
    assert "unknown-critical-error" in codes(validate_run(run, task))


def test_run_accepts_missing_retention_responses():
    task = demo_task()
    run = deepcopy(demo_runs()[0])
    run["assessments"].pop("retention")
    assert validate_run(run, task) == []
