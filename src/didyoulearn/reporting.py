"""Self-contained HTML reporting with no network assets."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


def _percent(value: float | None, *, signed: bool = False) -> str:
    if value is None:
        return "—"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value * 100:.1f}"


def _interval(value: list[float] | None) -> str:
    if not value:
        return "interval pending"
    return f"{value[0] * 100:.1f}–{value[1] * 100:.1f}"


def _bar(label: str, value: float | None, color: str) -> str:
    observed = max(0.0, min(1.0, value or 0.0))
    width = observed * 100
    display = _percent(value)
    return (
        '<div class="metric-row">'
        f'<span class="metric-label">{escape(label)}</span>'
        '<span class="metric-track">'
        f'<span class="metric-fill" style="width:{width:.2f}%;background:{color}"></span>'
        "</span>"
        f'<strong class="metric-value">{display}</strong>'
        "</div>"
    )


def build_report(result: dict[str, Any]) -> str:
    study = result.get("study", {})
    tutors = result.get("tutors", [])
    counts = result.get("counts", {})
    synthetic = bool(study.get("synthetic"))
    warning = (
        '<div class="warning"><strong>Fictional demonstration.</strong> '
        "Tutor names and results on this page are synthetic. They validate the software, "
        "not any commercial model.</div>"
        if synthetic
        else ""
    )
    colors = ["#1f5364", "#a44a3f", "#9a722a", "#4e6b55", "#715b78"]
    cards: list[str] = []
    for index, tutor in enumerate(tutors):
        rank = f"#{tutor['rank']}" if tutor.get("rank") is not None else "rank withheld"
        eligibility = (
            "evidence gate passed" if tutor.get("rank_eligible") else "more evidence required"
        )
        cards.append(
            f"""
            <article class="tutor-card">
              <div class="card-head">
                <div>
                  <p class="eyebrow">{escape(rank.upper())}</p>
                  <h3>{escape(str(tutor.get("tutor_label", tutor.get("tutor_id", "Tutor"))))}</h3>
                </div>
                <span class="evidence">{escape(eligibility)}</span>
              </div>
              <p class="sample">n={tutor.get("n_complete_truth_pass", 0)} complete, truth-passing
                trials · {_interval(tutor.get("adjusted_posttest_interval"))}</p>
              {_bar("Adjusted mastery", tutor.get("adjusted_posttest"), colors[index % len(colors)])}
              {_bar("Transfer", tutor.get("transfer"), "#55728a")}
              {_bar("Retention", tutor.get("retention"), "#77715c")}
              <dl>
                <div><dt>Raw gain</dt><dd>{_percent(tutor.get("raw_gain"), signed=True)}</dd></div>
                <div><dt>Illusion gap</dt><dd>{_percent(tutor.get("illusion_gap"), signed=True)}</dd></div>
                <div><dt>Truth pass</dt><dd>{_percent(tutor.get("truth_pass_rate"))}</dd></div>
                <div><dt>Gain / 10 min</dt><dd>{_percent(tutor.get("efficiency_per_10_min"), signed=True)}</dd></div>
              </dl>
            </article>
            """
        )

    method = result.get("method", {})
    interpretation = "".join(
        f"<li>{escape(str(item))}</li>" for item in result.get("interpretation", [])
    )
    embedded = escape(json.dumps(result, ensure_ascii=False, sort_keys=True))
    title = escape(str(study.get("title", "DidYouLearn study")))
    subtitle = escape(
        str(
            study.get(
                "question",
                "Which AI tutor produced demonstrated learning—not merely a fluent explanation?",
            )
        )
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{title} · DidYouLearn</title>
  <style>
    :root {{
      --paper:#f4f0e8; --ink:#17242b; --muted:#58666c; --line:#cbc3b5;
      --navy:#173a4b; --rust:#a44a3f; --teal:#1f6a6a; --white:#fffdf8;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0; color:var(--ink); background:var(--paper);
      font-family:Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
      line-height:1.55;
    }}
    main {{ width:min(1180px, calc(100% - 40px)); margin:0 auto; padding:52px 0 72px; }}
    header {{ border-top:12px solid var(--navy); border-bottom:1px solid var(--line); padding:52px 0 40px; }}
    .eyebrow {{
      margin:0 0 10px; color:var(--rust); font-family:ui-monospace, SFMono-Regular, monospace;
      font-weight:750; font-size:.76rem; letter-spacing:.16em; text-transform:uppercase;
    }}
    h1 {{ max-width:920px; margin:0; font:700 clamp(2.3rem,6vw,5.4rem)/.98 Georgia,serif; letter-spacing:-.04em; }}
    .subtitle {{ max-width:760px; color:var(--muted); font-size:1.18rem; margin:24px 0 0; }}
    .statline {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:30px; }}
    .statline span {{ border:1px solid var(--line); background:rgba(255,255,255,.32); padding:8px 12px; border-radius:999px; }}
    .warning {{ margin:28px 0 0; padding:14px 18px; border-left:4px solid var(--rust); background:#f2ddd5; }}
    section {{ margin-top:44px; }}
    .section-head {{ display:flex; justify-content:space-between; gap:24px; align-items:end; border-bottom:1px solid var(--line); margin-bottom:22px; }}
    h2 {{ margin:0 0 12px; font:700 1.8rem/1.15 Georgia,serif; }}
    .section-note {{ color:var(--muted); margin:0 0 12px; max-width:570px; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:18px; }}
    .tutor-card {{ min-width:0; border:1px solid var(--line); background:var(--white); padding:24px; border-radius:8px; box-shadow:0 8px 24px rgba(28,39,42,.04); }}
    .card-head {{ display:flex; justify-content:space-between; align-items:start; gap:16px; }}
    h3 {{ margin:0; font:700 1.5rem/1.1 Georgia,serif; overflow-wrap:anywhere; }}
    .evidence {{ max-width:132px; text-align:center; color:var(--muted); background:#ece7dc; padding:5px 8px; border-radius:3px; font-size:.76rem; }}
    .sample {{ margin:16px 0; color:var(--muted); font-size:.88rem; }}
    .metric-row {{ display:grid; grid-template-columns:112px minmax(50px,1fr) 42px; gap:10px; align-items:center; margin:12px 0; font-size:.82rem; }}
    .metric-track {{ height:8px; background:#e5e0d5; border-radius:10px; overflow:hidden; }}
    .metric-fill {{ display:block; height:100%; }}
    .metric-value {{ text-align:right; }}
    dl {{ display:grid; grid-template-columns:1fr 1fr; gap:1px; background:var(--line); border:1px solid var(--line); margin:22px 0 0; }}
    dl div {{ background:var(--white); padding:10px; }}
    dt {{ color:var(--muted); font-size:.73rem; }}
    dd {{ margin:2px 0 0; font-weight:750; }}
    .method {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }}
    .method > div {{ border-top:3px solid var(--navy); padding-top:16px; }}
    code {{ background:#e7e1d5; padding:.1em .3em; }}
    footer {{ color:var(--muted); border-top:1px solid var(--line); margin-top:50px; padding-top:20px; font-size:.86rem; }}
    details {{ margin-top:28px; }}
    pre {{ white-space:pre-wrap; overflow-wrap:anywhere; background:#182b34; color:#edf0e9; padding:18px; border-radius:5px; max-height:420px; overflow:auto; }}
    @media (max-width:700px) {{
      main {{ width:min(100% - 24px,1180px); padding-top:24px; }}
      header {{ padding-top:36px; }}
      .section-head,.method {{ display:block; }}
      .metric-row {{ grid-template-columns:96px minmax(40px,1fr) 38px; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <p class="eyebrow">Outcome-based AI tutor evaluation</p>
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <div class="statline">
      <span>{counts.get("participants", 0)} participants</span>
      <span>{counts.get("tasks", 0)} tasks</span>
      <span>{counts.get("tutors", 0)} tutor conditions</span>
      <span>{counts.get("runs", 0)} trials</span>
    </div>
    {warning}
  </header>

  <section>
    <div class="section-head">
      <div><p class="eyebrow">Scorecards</p><h2>Did the learner actually learn?</h2></div>
      <p class="section-note">Ranks require the declared sample and truth gates. Outcome dimensions
      remain separate so fluent style cannot conceal weak transfer or retention.</p>
    </div>
    <div class="cards">{"".join(cards) or "<p>No tutor results are available.</p>"}</div>
  </section>

  <section>
    <div class="section-head">
      <div><p class="eyebrow">Method</p><h2>What this report can support</h2></div>
    </div>
    <div class="method">
      <div>
        <h3>Primary pilot estimate</h3>
        <p>{escape(str(method.get("primary", "Not specified")))}</p>
        <p>Pooled pretest slope: <code>{method.get("pooled_pretest_slope", "—")}</code><br>
        Bootstrap iterations: <code>{method.get("bootstrap_iterations", "—")}</code></p>
      </div>
      <div>
        <h3>Interpretation boundaries</h3>
        <ul>{interpretation}</ul>
      </div>
    </div>
    <details>
      <summary>Embedded machine-readable result</summary>
      <pre>{embedded}</pre>
    </details>
  </section>

  <footer>Generated by DidYouLearn. No external scripts, fonts, analytics, or model services.</footer>
</main>
</body>
</html>
"""


def write_report(result: dict[str, Any], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_report(result), encoding="utf-8")
    return destination
