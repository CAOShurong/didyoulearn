"""Check repository-relative links and HTTPS task sources."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    failures: list[str] = []
    for markdown in ROOT.rglob("*.md"):
        if any(
            part.startswith(".") or part in {"build", "dist", "_site"} for part in markdown.parts
        ):
            continue
        for target in MARKDOWN_LINK.findall(markdown.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            path_text = target.split("#", 1)[0]
            if path_text and not (markdown.parent / path_text).resolve().exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> {target}")

    for task_file in (ROOT / "examples" / "tasks").glob("*.json"):
        task = json.loads(task_file.read_text(encoding="utf-8"))
        for source in task["sources"]:
            request = urllib.request.Request(
                source["url"],
                headers={"User-Agent": "DidYouLearn-link-check/0.1"},
                method="HEAD",
            )
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    if response.status >= 400:
                        failures.append(
                            f"{task_file.name} source HTTP {response.status}: {source['url']}"
                        )
            except urllib.error.HTTPError as exc:
                if exc.code not in {403, 405, 429}:
                    failures.append(f"{task_file.name} source HTTP {exc.code}: {source['url']}")
            except urllib.error.URLError as exc:
                failures.append(
                    f"{task_file.name} source unavailable: {source['url']} ({exc.reason})"
                )

    if failures:
        print("\n".join(f"FAIL {failure}" for failure in failures))
        return 1
    print("Repository-relative links and task source endpoints passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
