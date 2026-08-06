# Contributing

DidYouLearn accepts code, task packs, documentation, translations, and methodological review.

## Before opening a pull request

1. Open an issue for changes that alter the study protocol or scoring interpretation.
2. Do not submit proprietary course material, private transcripts, or real participant records.
3. Cite authoritative sources for every factual teaching task.
4. Mark task-review status accurately. `community-draft` is the default; only maintainers may mark a
   task `reviewed`, and `expert-reviewed` requires a named, documented domain review.
5. Run:

   ```bash
   python -m pytest
   ruff check .
   ruff format --check .
   didyoulearn validate examples/tasks
   ```

## Task review

A task pull request must include learning objectives, prerequisites, common misconceptions,
equivalent pre/post forms, at least one transfer item, critical-error rules, and stable sources.
Task volume is not a substitute for review quality.
