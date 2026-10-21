// The sample block at the top of S1 to S9: his question as the teacher set it, "Try it first" (pick
// a) to d), or write each part), then "Show his answer", which reveals his official answer word for
// word and, below it, what he is looking for. What was tried and whether the answer is shown are
// kept per stop (CR.store.sample), and the typed parts are kept as drafts, so the block comes back as
// it was left. Nothing here is sent anywhere.
CR.sample = (() => {
  const { h } = CR.dom;
  const LETTERS = "abcd";
  const TARGET_LINES = "5–8";

  const draftKey = (tid, label) => `sample.${tid}.${label}`;

  function fit(area) {
    if (!area.isConnected) return;
    area.style.height = "auto";
    area.style.height = `${area.scrollHeight + 2}px`;
  }

  // ---- multiple choice: four options, picked before his answer is shown

  function optionRows(name, s, onPick) {
    return s.options.map((html, i) => {
      const input = h("input", { type: "radio", class: "opt-input", name, value: String(i), onchange: () => onPick(i) });
      const mark = h("span", { class: "opt-mark" });
      const row = h(
        "label",
        { class: "opt" },
        input,
        h("span", { class: "opt-letter", text: `${LETTERS[i]})` }),
        h("span", { class: "opt-body" }, h("span", { class: "opt-text prose", html })),
        mark,
      );
      return { row, input, mark };
    });
  }

  function paintOptions(rows, s, pick, shown) {
    rows.forEach((r, i) => {
      r.input.checked = i === pick;
      r.input.disabled = shown;
      r.row.classList.toggle("is-selected", !shown && i === pick);
      r.row.classList.toggle("is-correct", shown && i === s.answer);
      r.row.classList.toggle("is-wrong", shown && i === pick && i !== s.answer);
      if (shown && i === s.answer) r.mark.replaceChildren(CR.ui.mark("pass"), i === pick ? "your answer, and his" : "his answer");
      else if (shown && i === pick) r.mark.replaceChildren(CR.ui.mark("fail"), "your answer");
      else r.mark.replaceChildren();
    });
  }

  function mcqVerdict(s, pick) {
    const his = `${LETTERS[s.answer]})`;
    if (pick === null) return CR.ui.verdict(false, `You did not pick one. His answer is ${his}`);
    if (pick === s.answer) return CR.ui.verdict(true, `You picked ${his}, his answer.`);
    return CR.ui.verdict(false, `You picked ${LETTERS[pick]}). His answer is ${his}`);
  }

  // ---- open: a lined box for each part

  function openParts(tid, s) {
    const total = h("p", { class: "lines-total" });
    const areas = s.parts.map((html, i) => {
      const label = String(i + 1);
      const id = CR.q.nextId();
      const area = h("textarea", {
        class: "lined",
        id: `${id}-answer`,
        rows: "3",
        spellcheck: "true",
        "aria-labelledby": `${id}-label ${id}-prompt`,
      });
      area.value = CR.store.draft(draftKey(tid, label));
      const row = h(
        "div",
        { class: "part" },
        h(
          "div",
          { class: "part-head part-head-open" },
          h("span", { class: "part-label", id: `${id}-label`, text: `${label}.` }),
          h("div", { class: "part-prompt prose", id: `${id}-prompt`, html }),
        ),
        area,
      );
      area.addEventListener("input", () => {
        CR.store.setDraft(draftKey(tid, label), area.value);
        fit(area);
        paintLines();
      });
      return { area, row };
    });

    function paintLines() {
      const sum = areas.reduce((n, a) => n + CR.util.lineEstimate(a.area.value), 0);
      total.textContent = `≈ ${CR.util.plural(sum, "handwritten line")} so far, the paper allows ${TARGET_LINES} for all three parts`;
    }
    paintLines();
    return { rows: areas.map((a) => a.row), total, fit: () => areas.forEach((a) => fit(a.area)) };
  }

  // ---- the block

  function mount(t) {
    const s = t.sample;
    const tid = t.tid;
    const id = CR.q.nextId();
    const saved = CR.store.sample(tid);
    let pick = Number.isInteger(saved.pick) && saved.pick < (s.options || []).length ? saved.pick : null;
    let shown = Boolean(saved.shown);
    const isMcq = s.kind === "mcq";

    const rows = isMcq ? optionRows(id, s, choose) : [];
    const open = isMcq ? null : openParts(tid, s);
    const hide = CR.ui.button("Hide his answer and try again", { kind: "quiet", onClick: tryAgain });
    const show = CR.ui.button("Show his answer", { kind: "primary", onClick: reveal });
    const answerBox = h("div", { class: "sample-answer", tabindex: "-1", hidden: true });

    const el = h(
      "section",
      { class: "sample", id: "sec-sample", "aria-labelledby": `${id}-title`, tabindex: "-1" },
      h(
        "div",
        { class: "sample-head" },
        h("p", { class: "label", id: `${id}-title`, text: `His question ${s.qnum}, from the teacher's sample` }),
        CR.ui.chip(isMcq ? "multiple choice" : "open", isMcq ? "none" : "warn"),
      ),
      h("div", { class: "sample-q prose", html: s.question_html }),
      h("p", { class: "label sample-step", text: isMcq ? "Try it first: pick one" : "Try it first: write each part" }),
      isMcq ? h("fieldset", { class: "opts" }, h("legend", { class: "vh", text: "Choose one answer" }), rows.map((r) => r.row)) : h("div", { class: "parts" }, open.rows, open.total),
      h(
        "div",
        { class: "q-actions" },
        show,
        hide,
        h("span", { class: "fine", text: isMcq ? "Keys: a to d choose. Answer first, then open his answer. Judge your reasons, not the letter." : "Answer on paper or here first, then open his answer. Judge your reasons, not the letter." }),
      ),
      answerBox,
    );

    function fillAnswer() {
      const his = CR.ui.note("Teacher's official answer", s.his_answer_html, "teacher");
      CR.dom.fill(
        answerBox,
        isMcq ? h("div", { class: "q-verdict" }, mcqVerdict(s, pick)) : null,
        isMcq ? his : h("div", { class: "answer-grid" }, his, CR.ui.markingGuide()),
        CR.ui.note("What he is looking for", s.decoded_html, "exam"),
      );
    }

    function paint() {
      if (isMcq) paintOptions(rows, s, pick, shown);
      show.hidden = shown;
      hide.hidden = !shown;
      answerBox.hidden = !shown;
      if (shown) fillAnswer();
    }

    function choose(i) {
      if (shown) return;
      pick = i;
      CR.store.setSample(tid, { pick: i });
      paint();
    }

    function reveal() {
      shown = true;
      CR.store.setSample(tid, { shown: true, pick });
      paint();
      CR.dom.announce("His answer is shown below your attempt.");
      CR.dom.reveal(answerBox);
    }

    function tryAgain() {
      shown = false;
      if (isMcq) pick = null;
      CR.store.setSample(tid, { shown: false, pick });
      paint();
      CR.dom.announce("His answer is hidden. Try again.");
      el.scrollIntoView({ block: "start" });
    }

    // a to d or 1 to 4 choose an option while focus is inside the block (not in a text box).
    el.addEventListener("keydown", (event) => {
      if (!isMcq || shown || event.altKey || event.ctrlKey || event.metaKey || CR.dom.isTyping(event)) return;
      const k = event.key.toLowerCase();
      const pos = /^[a-d]$/.test(k) ? LETTERS.indexOf(k) : /^[1-4]$/.test(k) ? Number(k) - 1 : -1;
      if (pos < 0 || pos >= rows.length) return;
      event.preventDefault();
      rows[pos].input.focus();
      choose(pos);
    });

    paint();
    if (open) window.setTimeout(open.fit, 0);
    return el;
  }

  return { mount };
})();
