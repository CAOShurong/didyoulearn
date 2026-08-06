(function () {
  "use strict";

  const phases = ["setup", "pretest", "teach", "posttest", "transfer", "reflect", "export"];
  const state = {
    task: null,
    phase: "setup",
    answers: { pretest: {}, posttest: {}, transfer: {}, retention: {} },
    locked: new Set(),
    timerStartedAt: null,
    teachingSeconds: 0,
    timerHandle: null,
    run: null
  };

  const byId = (id) => document.getElementById(id);
  const message = byId("lab-message");

  function setMessage(text, isError) {
    message.textContent = text || "";
    message.style.color = isError ? "var(--rust)" : "var(--teal)";
  }

  function cleanId(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9._-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 70);
  }

  function validateTask(task) {
    const required = [
      "schema_version", "task_id", "version", "title", "domain", "level",
      "estimated_teaching_minutes", "learning_objectives", "teaching_brief", "forms"
    ];
    if (!task || typeof task !== "object") {
      throw new Error("The selected file is not a JSON task object.");
    }
    for (const key of required) {
      if (!(key in task)) {
        throw new Error(`Task field '${key}' is missing.`);
      }
    }
    for (const form of ["pretest", "posttest", "transfer"]) {
      if (!Array.isArray(task.forms[form]) || !task.forms[form].length) {
        throw new Error(`Task form '${form}' must contain assessment items.`);
      }
    }
    return task;
  }

  function selectTask(task) {
    state.task = validateTask(task);
    state.answers = { pretest: {}, posttest: {}, transfer: {}, retention: {} };
    state.locked.clear();
    const selected = byId("selected-task");
    selected.hidden = false;
    selected.innerHTML = "";
    const wrapper = document.createElement("div");
    const heading = document.createElement("h4");
    heading.textContent = state.task.title;
    const meta = document.createElement("p");
    meta.textContent = `${state.task.domain} · ${state.task.level} · ${state.task.estimated_teaching_minutes} minutes · ${state.task.review_status}`;
    wrapper.append(heading, meta);
    selected.append(wrapper);
    document.querySelector('[data-phase-panel="setup"] .next').disabled = false;
    for (const form of ["pretest", "posttest", "transfer"]) {
      renderAssessment(form);
    }
    byId("teaching-brief").textContent = buildBrief();
    setMessage("Task ready. Assessment answers remain hidden until export.", false);
  }

  function buildBrief() {
    if (!state.task) return "";
    const brief = state.task.teaching_brief;
    const objectives = state.task.learning_objectives.map((item) => `- ${item}`).join("\n");
    const instructions = brief.instructions.map((item) => `- ${item}`).join("\n");
    const prohibited = brief.prohibited_disclosures.map((item) => `- ${item}`).join("\n");
    return [
      "You are the tutor in a bounded learning study.",
      "",
      `Learning goal: ${brief.goal}`,
      `Learner profile: ${brief.learner_profile}`,
      "",
      "Learning objectives:",
      objectives,
      "",
      "Teaching instructions:",
      instructions,
      "",
      "Boundaries:",
      prohibited,
      "",
      `Work interactively for about ${state.task.estimated_teaching_minutes} minutes. Diagnose the learner before explaining, check their understanding, and do not claim certainty beyond the provided material.`
    ].join("\n");
  }

  function renderAssessment(formName) {
    const form = byId(`${formName}-form`);
    form.innerHTML = "";
    state.task.forms[formName].forEach((item, index) => {
      const fieldset = document.createElement("fieldset");
      fieldset.className = "question";
      const legend = document.createElement("legend");
      legend.textContent = `${index + 1}. ${item.prompt}`;
      fieldset.append(legend);

      if (item.type === "single_choice" || item.type === "multiple_choice") {
        const options = document.createElement("div");
        options.className = "options";
        item.choices.forEach((choice) => {
          const label = document.createElement("label");
          label.className = "option";
          const input = document.createElement("input");
          input.type = item.type === "multiple_choice" ? "checkbox" : "radio";
          input.name = `${formName}-${item.id}`;
          input.value = choice.id;
          input.addEventListener("change", () => collectForm(formName));
          const text = document.createElement("span");
          text.textContent = choice.text;
          label.append(input, text);
          options.append(label);
        });
        fieldset.append(options);
      } else if (item.type === "numeric") {
        const input = document.createElement("input");
        input.className = "numeric-answer";
        input.type = "number";
        input.step = "any";
        input.name = `${formName}-${item.id}`;
        input.addEventListener("input", () => collectForm(formName));
        fieldset.append(input);
      } else {
        const input = document.createElement("textarea");
        input.className = "numeric-answer";
        input.rows = 4;
        input.name = `${formName}-${item.id}`;
        input.addEventListener("input", () => collectForm(formName));
        fieldset.append(input);
      }
      form.append(fieldset);
    });
  }

  function collectForm(formName) {
    const form = byId(`${formName}-form`);
    const answers = {};
    state.task.forms[formName].forEach((item) => {
      const name = `${formName}-${item.id}`;
      if (item.type === "multiple_choice") {
        answers[item.id] = Array.from(form.querySelectorAll(`[name="${name}"]:checked`)).map(
          (input) => input.value
        );
      } else {
        const input = form.querySelector(`[name="${name}"]:checked`) ||
          form.querySelector(`[name="${name}"]`);
        if (input && input.value !== "") {
          answers[item.id] = item.type === "numeric" ? Number(input.value) : input.value;
        }
      }
    });
    state.answers[formName] = answers;
    return answers;
  }

  function formComplete(formName) {
    const answers = collectForm(formName);
    return state.task.forms[formName].every((item) => {
      const answer = answers[item.id];
      return item.type === "multiple_choice" ? Array.isArray(answer) && answer.length : answer !== undefined;
    });
  }

  function freezeForm(formName) {
    collectForm(formName);
    state.locked.add(formName);
    byId(`${formName}-form`).querySelectorAll("input, textarea").forEach((input) => {
      input.disabled = true;
    });
  }

  function showPhase(nextPhase) {
    state.phase = nextPhase;
    document.querySelectorAll("[data-phase-panel]").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.phasePanel === nextPhase);
    });
    const currentIndex = phases.indexOf(nextPhase);
    document.querySelectorAll("#progress li").forEach((item) => {
      const index = phases.indexOf(item.dataset.phase);
      item.classList.toggle("active", index === currentIndex);
      item.classList.toggle("complete", index < currentIndex);
    });
    document.querySelector(".lab-shell").scrollIntoView({ behavior: "smooth", block: "start" });
    setMessage("", false);
  }

  function canAdvance(nextPhase) {
    if (nextPhase === "pretest") {
      if (!state.task) throw new Error("Select a task first.");
      const participant = byId("participant-id").value.trim();
      if (!/^[a-z0-9][a-z0-9._-]{2,79}$/.test(participant)) {
        throw new Error("Use a lowercase pseudonym with letters, numbers, dots, underscores, or hyphens.");
      }
    }
    if (nextPhase === "teach") {
      if (!formComplete("pretest")) throw new Error("Answer every pretest item before continuing.");
      freezeForm("pretest");
    }
    if (nextPhase === "posttest") {
      if (!byId("tutor-product").value.trim() || !byId("tutor-model").value.trim()) {
        throw new Error("Record the product and displayed model label.");
      }
      if (!byId("transcript").value.trim()) {
        throw new Error("Add the transcript or an evidence note.");
      }
      if (!byId("close-tutor").checked) {
        throw new Error("Confirm that the tutor and transcript are out of reach.");
      }
      stopTimer();
      if (state.teachingSeconds < 1) state.teachingSeconds = 1;
    }
    if (nextPhase === "transfer") {
      if (!formComplete("posttest")) throw new Error("Answer every mastery item.");
      freezeForm("posttest");
    }
    if (nextPhase === "reflect") {
      if (!formComplete("transfer")) throw new Error("Answer every transfer item.");
      freezeForm("transfer");
    }
    if (nextPhase === "export") {
      state.run = buildRun();
      renderSummary();
    }
    return true;
  }

  function scoreForm(formName) {
    let earned = 0;
    let possible = 0;
    state.task.forms[formName].forEach((item) => {
      const answer = state.answers[formName][item.id];
      possible += Number(item.points);
      let correct = false;
      if (item.type === "single_choice") correct = answer === item.answer;
      if (item.type === "multiple_choice") {
        correct = JSON.stringify([...(answer || [])].sort()) === JSON.stringify([...item.answer].sort());
      }
      if (item.type === "numeric") {
        correct = Number.isFinite(answer) && Math.abs(answer - item.answer) <= (item.tolerance || 0);
      }
      if (correct) earned += Number(item.points);
    });
    return possible ? earned / possible : null;
  }

  function buildRun() {
    const now = new Date();
    const random = crypto.getRandomValues(new Uint32Array(2));
    const runId = `run-${now.toISOString().slice(0, 10).replaceAll("-", "")}-${random[0].toString(16)}${random[1].toString(16)}`;
    const product = byId("tutor-product").value.trim();
    const model = byId("tutor-model").value.trim();
    const mode = byId("tutor-mode").value.trim() || "not-recorded";
    return {
      schema_version: "1.0",
      run_id: cleanId(runId),
      study_id: "community-local-lab",
      participant_id: byId("participant-id").value.trim(),
      task_id: state.task.task_id,
      task_version: state.task.version,
      tutor: {
        id: cleanId(`${product}-${model}-${mode}`) || "claimed-tutor",
        label: `${product} · ${model}`,
        product,
        model,
        mode
      },
      started_at: now.toISOString(),
      teaching_seconds: Math.max(1, Math.round(state.teachingSeconds)),
      truth_status: "not-reviewed",
      critical_error_ids: [],
      evidence_tier: "community-submitted",
      assessments: {
        pretest: state.answers.pretest,
        posttest: state.answers.posttest,
        transfer: state.answers.transfer,
        retention: {}
      },
      self_report: {
        understanding_before: Number(byId("understanding-before").value),
        understanding_after: Number(byId("understanding-after").value),
        cognitive_effort: Number(byId("cognitive-effort").value)
      },
      transcript: byId("transcript").value.trim(),
      local_scores_preview: {
        pretest: scoreForm("pretest"),
        posttest: scoreForm("posttest"),
        transfer: scoreForm("transfer")
      },
      boundary: "Product identity is participant-claimed; correctness has not been reviewed."
    };
  }

  function renderSummary() {
    const scores = state.run.local_scores_preview;
    const gain = scores.posttest - scores.pretest;
    const gap = state.run.self_report.understanding_after / 100 - scores.posttest;
    const values = [
      [`${Math.round(scores.posttest * 100)}%`, "Immediate mastery"],
      [`${Math.round(scores.transfer * 100)}%`, "Transfer"],
      [`${gain >= 0 ? "+" : ""}${Math.round(gain * 100)}`, "Raw gain points"],
      [`${gap >= 0 ? "+" : ""}${Math.round(gap * 100)}`, "Illusion gap"]
    ];
    byId("local-summary").innerHTML = values
      .map(([value, label]) => `<div class="summary-metric"><strong>${value}</strong><span>${label}</span></div>`)
      .join("");
  }

  function startTimer() {
    if (state.timerStartedAt !== null) return;
    state.timerStartedAt = Date.now();
    byId("timer-toggle").textContent = "Stop timer";
    state.timerHandle = window.setInterval(updateTimer, 250);
    updateTimer();
  }

  function stopTimer() {
    if (state.timerStartedAt === null) return;
    state.teachingSeconds += (Date.now() - state.timerStartedAt) / 1000;
    state.timerStartedAt = null;
    window.clearInterval(state.timerHandle);
    state.timerHandle = null;
    byId("timer-toggle").textContent = "Resume timer";
    updateTimer();
  }

  function updateTimer() {
    const current = state.timerStartedAt === null
      ? state.teachingSeconds
      : state.teachingSeconds + (Date.now() - state.timerStartedAt) / 1000;
    const rounded = Math.floor(current);
    const minutes = String(Math.floor(rounded / 60)).padStart(2, "0");
    const seconds = String(rounded % 60).padStart(2, "0");
    byId("timer").textContent = `${minutes}:${seconds}`;
  }

  function downloadJson(filename, value) {
    const blob = new Blob([`${JSON.stringify(value, null, 2)}\n`], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  function reset() {
    stopTimer();
    state.task = null;
    state.phase = "setup";
    state.answers = { pretest: {}, posttest: {}, transfer: {}, retention: {} };
    state.locked.clear();
    state.teachingSeconds = 0;
    state.run = null;
    document.querySelectorAll(".assessment").forEach((form) => { form.innerHTML = ""; });
    document.querySelectorAll("input:not([type=file]), textarea").forEach((input) => {
      if (input.id === "participant-id") input.value = "p-local-001";
      else if (input.type === "range") return;
      else if (input.type === "checkbox") input.checked = false;
      else input.value = "";
      input.disabled = false;
    });
    byId("selected-task").hidden = true;
    document.querySelector('[data-phase-panel="setup"] .next').disabled = true;
    updateTimer();
    showPhase("setup");
  }

  byId("use-sample").addEventListener("click", () => {
    try { selectTask(window.DYL_SAMPLE_TASK); } catch (error) { setMessage(error.message, true); }
  });

  byId("task-file").addEventListener("change", async (event) => {
    const [file] = event.target.files;
    if (!file) return;
    try {
      const task = JSON.parse(await file.text());
      selectTask(task);
    } catch (error) {
      setMessage(error.message || "Unable to read that task file.", true);
    }
  });

  document.querySelectorAll(".next").forEach((button) => {
    button.addEventListener("click", () => {
      try {
        canAdvance(button.dataset.next);
        showPhase(button.dataset.next);
      } catch (error) {
        setMessage(error.message, true);
      }
    });
  });

  document.querySelectorAll(".back").forEach((button) => {
    button.addEventListener("click", () => showPhase(button.dataset.back));
  });

  byId("copy-brief").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(byId("teaching-brief").textContent);
      setMessage("Teaching brief copied.", false);
    } catch (_error) {
      setMessage("Clipboard access was unavailable. Select and copy the brief manually.", true);
    }
  });

  byId("timer-toggle").addEventListener("click", () => {
    if (state.timerStartedAt === null) startTimer();
    else stopTimer();
  });

  ["understanding-before", "understanding-after", "cognitive-effort"].forEach((id) => {
    const output = byId(id === "understanding-before" ? "before-output" :
      id === "understanding-after" ? "after-output" : "effort-output");
    byId(id).addEventListener("input", (event) => { output.value = event.target.value; });
  });

  byId("download-run").addEventListener("click", () => {
    if (!state.run) return;
    downloadJson(`${state.run.run_id}.json`, state.run);
    setMessage("Run record downloaded. Keep the private transcript out of public releases.", false);
  });

  byId("reset-lab").addEventListener("click", reset);
})();
