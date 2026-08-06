<div align="center">
  <img src="https://raw.githubusercontent.com/CAOShurong/didyoulearn/main/docs/assets/hero.svg" alt="DidYouLearn measures prior knowledge, runs one bounded AI lesson, then verifies mastery, transfer, retention, and confidence calibration without the AI" width="100%">

  # DidYouLearn

  **Which AI actually helps you understand?**

  [Run the local lab](https://caoshurong.github.io/didyoulearn/#lab) ·
  [Open the fictional report](https://caoshurong.github.io/didyoulearn/demo/report.html) ·
  [Read the study protocol](docs/protocol.md)

  [![CI](https://github.com/CAOShurong/didyoulearn/actions/workflows/ci.yml/badge.svg)](https://github.com/CAOShurong/didyoulearn/actions/workflows/ci.yml)
  [![Pages](https://github.com/CAOShurong/didyoulearn/actions/workflows/pages.yml/badge.svg)](https://caoshurong.github.io/didyoulearn/)
  [![PyPI](https://img.shields.io/pypi/v/didyoulearn?color=1e6867)](https://pypi.org/project/didyoulearn/)
  [![Python](https://img.shields.io/badge/Python-3.11%2B-173b4c)](https://www.python.org/)
  [![Runtime dependencies](https://img.shields.io/badge/runtime_dependencies-0-4e6b55)](#privacy-and-trust-boundary)
  [![License: MIT](https://img.shields.io/badge/license-MIT-a44a3f)](LICENSE)
</div>

Frontier models are usually ranked by whether they solve a problem or whether a reviewer prefers
their answer. Those are useful questions, but they are not the question a learner asks:

> After the explanation ends and the AI is gone, can I explain the idea, apply it somewhere new,
> and still remember it later?

DidYouLearn is an open, provider-neutral laboratory for that question. It combines versioned
learning tasks, randomized tutor assignment, correctness review, unaided equivalent-form tests,
transfer and retention measures, confidence calibration, evidence receipts, and reproducible
reports.

The repository contains **no real commercial-model ranking yet**. Every committed model result is
explicitly fictional. Real rankings require real learners, reviewed tasks, declared protocols, and
enough evidence to support the comparison.

## The outcome, not the answer

DidYouLearn separates six dimensions that a single preference vote collapses:

| Dimension | Evidence | Interpretation |
|---|---|---|
| **Truth** | Declared critical-error review | A fluent falsehood cannot qualify for a rank |
| **Mastery** | Unaided equivalent-form post-test | What the learner can demonstrate immediately |
| **Transfer** | New setting or problem structure | Whether the learner acquired a reusable idea |
| **Retention** | Delayed unaided assessment | What remains after the first impression fades |
| **Calibration** | Perceived understanding minus mastery | Whether the explanation created an illusion of understanding |
| **Efficiency** | Learning gain per ten teaching minutes | How much learning the interaction produced for the time |

Correctness is a gate, not one compensable style score. A tutor condition is rank-eligible only
after the study's sample and truth thresholds are met.

## Start in sixty seconds

The browser lab runs locally and never calls a model:

```bash
python -m pip install didyoulearn
didyoulearn serve
```

Or open the [hosted static lab](https://caoshurong.github.io/didyoulearn/#lab). The hosted page
contains the same static HTML, CSS, and JavaScript. Study data remains in the page until you
explicitly download a run record.

The lab guides one complete no-API trial:

1. Select a reviewed task pack.
2. Complete the pretest without assistance.
3. Carry the generated teaching brief to ChatGPT, Claude, Gemini, Kimi, GLM, Qwen, or another
   product.
4. Record the displayed product, model, mode, teaching time, and transcript.
5. Close the tutor and complete new mastery and transfer questions.
6. Record perceived understanding and cognitive effort.
7. Export a portable run JSON file.

A no-API run is useful personal evidence, but its product identity is participant-claimed. The
software never pretends that a pasted transcript cryptographically proves its provider.

## One study, seven auditable stages

<p align="center">
  <img src="https://raw.githubusercontent.com/CAOShurong/didyoulearn/main/docs/assets/protocol.svg" alt="Seven study stages: consent, pretest, balanced assignment, bounded teaching, mastery and transfer verification, reflection, and delayed retention test" width="100%">
</p>

Learning creates carry-over by definition. A learner must not receive two tutor conditions for the
same concept. Repeated-measures studies use distinct matched topics and model participant and task
dependencies.

For randomized pre/post studies, the built-in pilot report uses a common-slope covariance
adjustment: it compares post-test performance at the pooled pretest mean. Raw gain remains visible,
but it is not treated as the only inferential statistic. Confirmatory work should pre-register its
analysis and use a suitable mixed-effects or hierarchical model.

## A scorecard, not one magic number

<p align="center">
  <img src="https://raw.githubusercontent.com/CAOShurong/didyoulearn/main/docs/assets/scorecard.svg" alt="Explicitly fictional tutor scorecards compare adjusted mastery, transfer, retention, truth pass, illusion gap, and evidence eligibility" width="100%">
</p>

The example above is deliberately fictional. It illustrates three important report behaviors:

- strong-looking results remain unranked below the evidence floor;
- transfer and retention remain visible beside immediate mastery;
- confidence that exceeds demonstrated mastery is reported as an illusion gap.

Generate the complete fictional study yourself:

```bash
didyoulearn demo --output demo
start demo/report.html        # Windows
open demo/report.html         # macOS
xdg-open demo/report.html     # Linux
```

The generated report is a single offline HTML file with its machine-readable result embedded.

## Complete CLI workflow

Validate a task registry:

```bash
didyoulearn validate examples/tasks --kind task
```

Score collected runs:

```bash
didyoulearn score \
  --tasks examples/tasks \
  --runs study/runs.jsonl \
  --study study/study.json \
  --output reports/scores.json
```

Render a self-contained report:

```bash
didyoulearn report \
  --scores reports/scores.json \
  --output reports/report.html
```

Create and verify an integrity receipt:

```bash
didyoulearn receipt \
  --task examples/tasks/statistics.p-value.json \
  --run study/run-001.json \
  --transcript study/run-001.txt \
  --output study/run-001.receipt.json

didyoulearn verify-receipt \
  --receipt study/run-001.receipt.json \
  --task examples/tasks/statistics.p-value.json \
  --run study/run-001.json \
  --transcript study/run-001.txt
```

Create a study-specific participant pseudonym:

```bash
didyoulearn pseudonym "private-local-identifier" --secret "study-specific-secret"
```

Assign one balanced tutor condition within a declared stratum:

```bash
didyoulearn assign \
  --participant p-4e7a \
  --task statistics.p-value \
  --stratum prior-medium \
  --tutors tutor-a tutor-b tutor-c \
  --book study/assignments.json \
  --salt "pre-registered-randomization-salt"
```

## Two evidence lanes

DidYouLearn does not pretend that convenience and experimental control are the same thing.

| Lane | Who runs the model? | Model identity | Intended use |
|---|---|---|---|
| **Community lab** | The learner in a subscription web product | Participant-claimed | Personal comparison, task testing, community signals |
| **Verified arena** | A study coordinator or declared provider integration | Coordinator- or provider-verified | Blind comparative studies and publishable evidence |

The core package does not require API keys. A future coordinator can implement an optional provider
runner without changing task, run, evidence, or report formats.

## Task packs

Version `0.1.0` includes six cross-domain **community-draft** task packs:

- p-value interpretation;
- base rates and conditional probability;
- natural selection;
- opportunity cost;
- association versus causation;
- overfitting and honest generalization estimates.

Each task declares:

```text
learning objectives + prerequisites + authoritative sources
  ├── misconception map
  ├── critical-error rules
  ├── bounded teaching brief
  ├── pretest form
  ├── equivalent post-test form
  ├── novel transfer form
  └── delayed retention form
```

`community-draft` is intentional: these tasks exercise the complete protocol but have not been
validated as psychometric instruments or reviewed by named domain experts. The project records that
boundary instead of laundering generated material into an “expert benchmark.”

See [task authoring](docs/task-authoring.md), the machine-readable
[task schema](schemas/task.schema.json), and [contribution rules](CONTRIBUTING.md).

## Architecture

```text
task registry
    │
    ├── dependency-free validator
    ├── balanced assignment engine
    ├── local browser study flow
    └── versioned run records
             │
             ├── correctness gate
             ├── assessment scorer
             ├── covariance adjustment
             ├── bootstrap uncertainty
             ├── privacy release filter
             └── integrity receipts
                       │
                       └── offline HTML + JSON report
```

The Python package has zero runtime dependencies and supports Python 3.11 or newer. The browser app
uses no framework, remote asset, analytics service, storage backend, or model SDK.

## Privacy and trust boundary

### What the default project does

- binds its local server only to `127.0.0.1`;
- sends a content security policy that blocks network connections from the app;
- uses no remote scripts, fonts, analytics, or model clients;
- keeps task responses in page memory until explicit download;
- can strip transcripts, notes, account fields, and direct identifiers before release;
- hashes task, run, and transcript content into a portable integrity receipt.

### What it cannot prove

- a participant-selected label identifies a provider's actual internal model route;
- a transcript was not edited before capture;
- a community task is a valid measurement instrument;
- an immediate gain will persist without a delayed test;
- a small, self-selected sample supports a general model ranking;
- a hash proves scientific validity rather than file integrity.

See [ethics and privacy](docs/ethics-and-privacy.md), [statistics](docs/statistics.md), and the
[no-API lab boundary](docs/no-api-lab.md).

## Why this is not another tutor-response benchmark

Existing work has established that solving and teaching are different capabilities. ELI-Why studies
whether explanations fit learner needs; MRBench and MathTutorBench evaluate pedagogical qualities
of tutoring responses; TeachBench measures post-instruction performance with an LLM proxy learner;
LearnLM combines pedagogy-focused model development with expert evaluation and controlled trials.

DidYouLearn's intended contribution is narrower and operational:

- public, provider-neutral task and evidence formats;
- real learner outcomes as the target quantity;
- consumer product surfaces as first-class conditions;
- transfer, retention, and confidence calibration beside immediate mastery;
- a no-API community lane that is explicitly separated from verified blind evidence.

The full [research landscape](docs/research-landscape.md) cites the relevant work and states the
project's no-go claims.

## Research and governance

DidYouLearn is infrastructure, not institutional ethics approval. Studies involving people must use
appropriate consent, data minimization, withdrawal, retention, and review procedures. If the intent
is generalizable research, consult the relevant institutional process before recruitment.

Public model claims must disclose:

- task and schema versions;
- product, displayed model, mode, and date;
- assignment method;
- exclusion and missing-data rules;
- truth-review procedure;
- sample size and uncertainty;
- evidence tier;
- whether the protocol was registered before outcome inspection.

## Development

```bash
git clone https://github.com/CAOShurong/didyoulearn.git
cd didyoulearn
python -m pip install -e .
python -m pip install pytest ruff build

python -m pytest
ruff check .
ruff format --check .
didyoulearn validate examples/tasks --kind task
python scripts/build_site.py
```

CI tests Python 3.11, 3.12, and 3.13, validates the task registry, checks JavaScript syntax, builds
the static site, builds the wheel and source distribution, installs the wheel into a clean
environment, and runs a complete fictional demonstration.

## Status

DidYouLearn is alpha research software. The engine and local study workflow are usable; the starter
task registry still needs independent educator, domain, accessibility, and psychometric review.
See the [roadmap](ROADMAP.md).

## Citation

Citation metadata is available in [CITATION.cff](CITATION.cff).

## License

[MIT](LICENSE) © 2026 Shurong Cao.
