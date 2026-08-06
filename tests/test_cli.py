import json

from didyoulearn.cli import main
from didyoulearn.demo import demo_runs, demo_task


def test_doctor(capsys):
    assert main(["doctor"]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["runtime_dependencies"] == 0
    assert output["network_model_calls"] is False


def test_demo_command(tmp_path):
    destination = tmp_path / "demo"
    assert main(["demo", "--output", str(destination)]) == 0
    assert (destination / "task.json").exists()
    assert (destination / "runs.json").exists()
    assert (destination / "scores.json").exists()
    assert (destination / "report.html").exists()


def test_validate_command(tmp_path):
    task_file = tmp_path / "task.json"
    task_file.write_text(json.dumps(demo_task()), encoding="utf-8")
    assert main(["validate", str(task_file), "--kind", "task"]) == 0


def test_score_and_report_commands(tmp_path):
    task_dir = tmp_path / "tasks"
    task_dir.mkdir()
    (task_dir / "task.json").write_text(json.dumps(demo_task()), encoding="utf-8")
    runs = tmp_path / "runs.json"
    runs.write_text(json.dumps(demo_runs()), encoding="utf-8")
    scores = tmp_path / "scores.json"
    report = tmp_path / "report.html"

    assert (
        main(
            [
                "score",
                "--tasks",
                str(task_dir),
                "--runs",
                str(runs),
                "--output",
                str(scores),
                "--bootstrap-iterations",
                "50",
            ]
        )
        == 0
    )
    assert main(["report", "--scores", str(scores), "--output", str(report)]) == 0
    assert report.exists()
