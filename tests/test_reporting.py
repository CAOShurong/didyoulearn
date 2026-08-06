from didyoulearn.demo import demo_runs, demo_task
from didyoulearn.reporting import build_report, write_report
from didyoulearn.scoring import score_study


def result():
    task = demo_task()
    return score_study(
        {task["task_id"]: task},
        demo_runs(),
        study={"title": "Fictional report", "synthetic": True},
        bootstrap_iterations=50,
    )


def test_report_is_self_contained_and_labels_fiction():
    html = build_report(result())
    assert "<!doctype html>" in html
    assert "Fictional demonstration" in html
    assert "Tutor Atlas" in html
    assert "https://" not in html
    assert "<script" not in html


def test_report_writes_utf8(tmp_path):
    output = write_report(result(), tmp_path / "report.html")
    assert output.exists()
    assert "DidYouLearn" in output.read_text(encoding="utf-8")


def test_report_escapes_study_title():
    value = result()
    value["study"]["title"] = "<script>alert(1)</script>"
    html = build_report(value)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>alert(1)</script>" not in html
