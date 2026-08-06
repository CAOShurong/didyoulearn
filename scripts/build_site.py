"""Build the static GitHub Pages artifact."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
sys.path.insert(0, str(SOURCE))

from didyoulearn.demo import demo_runs, demo_task  # noqa: E402
from didyoulearn.io import write_json  # noqa: E402
from didyoulearn.reporting import write_report  # noqa: E402
from didyoulearn.scoring import score_study  # noqa: E402


def main() -> int:
    destination = ROOT / "_site"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(ROOT / "src" / "didyoulearn" / "web", destination)
    (destination / "assets").mkdir(parents=True, exist_ok=True)
    for asset in (ROOT / "docs" / "assets").glob("*.svg"):
        shutil.copy2(asset, destination / "assets" / asset.name)
    shutil.copytree(ROOT / "schemas", destination / "schemas")

    task = demo_task()
    result = score_study(
        {task["task_id"]: task},
        demo_runs(),
        study={
            "study_id": "fictional-teaching-study",
            "title": "Fictional teaching-outcome demonstration",
            "question": "Can the pipeline separate mastery, transfer, retention, and confidence?",
            "synthetic": True,
        },
    )
    demo = destination / "demo"
    write_json(demo / "scores.json", result)
    write_report(result, demo / "report.html")
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
