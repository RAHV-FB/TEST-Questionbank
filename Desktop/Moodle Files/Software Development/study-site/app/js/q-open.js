// Open question: parts with lined answer areas and a handwriting line estimate. Modes:
// "practice" (drafts save as you type; "Show model answer" opens self-marking; "Record my mark"),
// "exam" (write only; onChange(answers)), "review" (answers read-only, marking open; onMark; with
// onAnswer it also offers "Record my mark", and recorded: true starts it as recorded).
// Self-marking: tick each rubric point the answer makes; a part scores min(marks, ticked).
// "Mark my answer with Claude" appears only when the sample capability is available.
SD.q.open = (container, q, opts = {}) => {
  const { h } = SD.dom;
  const mode = opts.mode || "practice";
  const id = SD.q.nextId();
  const target = SD.util.parseRange(q.lines);
  const draftKey = (label) => `open.${q.id}.${label}`;
  const answers = {};
  const ticks = {};
  // opts.markable: false (review of an answer left blank) shows the model answer and the rubric
  // but leaves ticking and recording out: there is nothing to mark.
  const markable = opts.markable !== false;
  let revealed = false;
  let recorded = mode === "review" && Boolean(opts.recorded);

  const el = SD.q.sheet(q, opts, `${id}-stem`);
  const total = h("p", { class: "lines-total" });

  const parts = q.parts.map((part, index) => {
    const pid = `${id}-p${index}`;
    answers[part.label] =
      mode === "practice" ? SD.store.draft(draftKey(part.label)) || "" : opts.answer?.[part.label] || "";
    ticks[part.label] = new Set(opts.ticks?.[part.label] || []);
    const area = h("textarea", {
      class: "lined",
      id: `${pid}-answer`,
      rows: "3",
      spellcheck: "true",
      readonly: mode === "review",
      placeholder: opts.onPaper ? "Written on paper." : null,
      "aria-labelledby": `${pid}-label ${pid}-prompt`,
    });
    area.value = answers[part.label];
    const estimate = h("span", { class: "lines-est" });
    const marking = h("div", { class: "part-marking", hidden: true });
    const row = h(
      "div",
      { class: "part" },
      h(
        "div",
        { class: "part-head" },
        h("span", { class: "part-label", id: `${pid}-label`, text: `${part.label}.` }),
        h("div", { class: "part-prompt prose", id: `${pid}-prompt`, html: part.prompt_html }),
        h("span", { class: "part-marks", text: SD.util.plural(part.marks, "mark") }),
      ),
      area,
      h("p", { class: "part-foot" }, estimate),
      marking,
    );
    area.addEventListener("input", () => {
      answers[part.label] = area.value;
      fit(area);
      paintLines();
      // Saved on every keystroke: the store batches the disk writes, and nothing is left pending
      // that a reload or a quick move to the next part could lose.
      if (mode === "practice") SD.store.setDraft(draftKey(part.label), area.value);
      if (mode === "exam" && opts.onChange) opts.onChange({ ...answers });
    });
    return { part, pid, area, estimate, marking, row };
  });

  function fit(area) {
    if (!area.isConnected) return;
    area.style.height = "auto";
    area.style.height = `${area.scrollHeight + 2}px`;
  }

  function paintLines() {
    let sum = 0;
    for (const p of parts) {
      const n = SD.util.lineEstimate(p.area.value);
      sum += n;
      p.estimate.textContent = `≈ ${SD.util.plural(n, "line")}`;
    }
    let advice = "";
    if (target && sum > 0 && sum < target.lo) advice = " · shorter than the paper expects";
    if (target && sum > target.hi) advice = " · longer than the paper expects";
    total.textContent = `≈ ${SD.util.plural(sum, "handwritten line")} in total, target ${q.lines}${advice}`;
  }

  el.append(
    h("div", { class: "parts" }, parts.map((p) => p.row)),
    total,
  );

  // ---- self-marking

  const scoreLine = h("p", { class: "score-line", "aria-live": "polite" });
  const claudeArea = h("div", { class: "claude-area" });
  const recordButton = SD.ui.button("Record my mark", { kind: "primary", onClick: record });

  // The button stays focusable (aria-disabled, not disabled) so keyboard focus is not lost when
  // the mark has been recorded.
  function setRecorded(now) {
    recordButton.setAttribute("aria-disabled", "true");
    recordButton.textContent = `Recorded ${now.score}/${now.max}`;
  }

  function setRecordable() {
    recordButton.removeAttribute("aria-disabled");
    recordButton.textContent = "Record my mark";
  }

  function current() {
    const t = Object.fromEntries(Object.entries(ticks).map(([label, set]) => [label, [...set]]));
    return { ...SD.scoring.openScore(q, t), ticks: t };
  }

  function paintScore() {
    const now = current();
    scoreLine.hidden = !markable;
    now.parts.forEach((ps, i) => {
      const p = parts[i];
      p.marking.querySelector(".part-score").textContent = `${ps.score}/${ps.max}`;
      p.marking.querySelector(".weak-answers").hidden = ps.score >= ps.max;
    });
    scoreLine.textContent = `Your mark: ${now.score}/${now.max}`;
    return now;
  }

  function rubricList(p) {
    return h(
      "fieldset",
      { class: "rubric" },
      h("legend", { text: markable ? "Tick each point your answer makes" : "What a full answer makes" }),
      p.part.rubric.map((html, i) => {
        const box = h("input", {
          type: "checkbox",
          id: `${p.pid}-r${i}`,
          checked: ticks[p.part.label].has(i),
          disabled: !markable,
          onchange: (e) => {
            if (e.target.checked) ticks[p.part.label].add(i);
            else ticks[p.part.label].delete(i);
            const now = paintScore();
            setRecordable();
            if (mode === "review" && opts.onMark) opts.onMark(now);
          },
        });
        return h(
          "div",
          { class: "rubric-item", dataset: { index: String(i) } },
          box,
          h("label", { for: `${p.pid}-r${i}`, html }),
        );
      }),
    );
  }

  function openMarking() {
    revealed = true;
    for (const p of parts) {
      p.marking.append(
        SD.ui.note("Model answer", p.part.model_answer_html, "model"),
        rubricList(p),
        h("p", { class: "part-score-line" }, "Part ", p.part.label, ": ", h("span", { class: "part-score" })),
        h(
          "div",
          { class: "weak-answers", hidden: true },
          SD.ui.note("Where answers lose marks", p.part.weak_answers_html, "warn"),
        ),
      );
      p.marking.hidden = false;
    }
    el.querySelector(".q-actions")?.remove();
    const actions = h(
      "div",
      { class: "q-actions" },
      markable && (mode === "practice" || opts.onAnswer) ? recordButton : null,
      markable ? claudeArea : null,
    );
    el.append(scoreLine, actions, SD.q.feedback(q, opts));
    const now = paintScore();
    if (recorded) setRecorded(now);
    if (markable) offerClaude();
  }

  // The first record counts an attempt; recording again after changing ticks corrects it.
  function record() {
    if (recordButton.getAttribute("aria-disabled") === "true") return;
    const now = current();
    if (opts.record !== false) {
      if (recorded) SD.store.amendAnswer(q.id, now.full);
      else SD.store.recordAnswer(q.id, now.full, null);
    }
    recorded = true;
    setRecorded(now);
    SD.dom.announce(`Recorded ${now.score} out of ${now.max}.`);
    if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "open", ok: now.full, ...now });
  }

  // ---- Claude marking (only on a click, never on load)

  function offerClaude() {
    SD.claude.canMark().then((ok) => {
      if (!ok || !el.isConnected) return;
      const status = h("p", { class: "claude-status", "aria-live": "polite" });
      const ask = SD.ui.button("Mark my answer with Claude", {
        kind: "secondary",
        onClick: async () => {
          ask.disabled = true;
          status.textContent = "Asking Claude to mark against the rubric. This can take a minute.";
          const reply = await SD.claude.mark(q, { ...answers });
          if (reply.result) {
            status.textContent = "";
            showClaude(reply.result);
          } else {
            status.textContent = reply.error;
          }
          if (reply.hide) ask.remove();
          else ask.disabled = false;
        },
      });
      claudeArea.replaceChildren(ask, status);
    });
  }

  function showClaude(result) {
    el.querySelectorAll(".claude-part, .claude-total").forEach((n) => n.remove());
    el.querySelectorAll(".rubric-item.by-claude").forEach((n) => n.classList.remove("by-claude"));
    result.parts.forEach((rp, i) => {
      const p = parts[i];
      for (const index of rp.met) {
        p.marking.querySelector(`.rubric-item[data-index="${index}"]`)?.classList.add("by-claude");
      }
      p.marking.querySelector(".rubric").after(
        h(
          "div",
          { class: "claude-part" },
          h("p", { class: "label", text: `Claude: ${rp.marks}/${rp.max}` }),
          h("p", { text: rp.feedback }),
        ),
      );
    });
    claudeArea.append(
      h(
        "div",
        { class: "claude-total" },
        h("p", { class: "label", text: `Claude's mark: ${result.score}/${result.max}` }),
        result.summary ? h("p", { text: result.summary }) : null,
        h("p", {
          class: "fine",
          text: "Points Claude counted are marked in each rubric. Your own ticks decide the recorded mark.",
        }),
      ),
    );
  }

  if (mode === "practice") {
    el.append(
      h(
        "div",
        { class: "q-actions" },
        SD.ui.button("Show model answer", {
          kind: "primary",
          onClick: () => {
            openMarking();
            SD.dom.announce("Model answer shown. Tick each point your answer makes.");
            SD.dom.reveal(parts[0].marking);
          },
        }),
        h("span", { class: "fine", text: "Write first: the model answer opens the marking." }),
      ),
    );
  }
  if (mode === "review") openMarking();
  container.append(el);
  for (const p of parts) fit(p.area);
  paintLines();

  return {
    el,
    // In practice the question is done once the mark is recorded; in review once it is open.
    done: () => (mode === "practice" ? recorded : revealed),
    key: () => false,
    answers: () => ({ ...answers }),
  };
};
