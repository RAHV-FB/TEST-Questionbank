// Question components: multiple choice, open answers and sorting. CR.q.mount(container, q, opts)
// appends a question sheet and returns a controller {el, done(), shown(), key(event), answers()}.
// Modes: "practice" (answer, check, full feedback, the attempt is recorded), "exam" (answer only,
// no feedback, nothing recorded; onChange) and "review" (read-only answer with every why, the
// explanation and, for an open question, its marking).
//   opts.number         text for the margin, e.g. "Q7"
//   opts.meta           false hides the type · level line (exam papers)
//   opts.answer         restore an answer: mcq option index, open {label: text}, sort [categoryId|null]
//   opts.ticks          open review: restore the self-marking {label: [rubric indexes]}
//   opts.onChange(a)    exam: every change, same shape as `answer`
//   opts.onAnswer(r)    practice: after checking, {qid, type, ok, ...}; open: after "Record my mark"
//   opts.onReveal()     practice: the feedback has appeared (an open question: the model answer)
//   opts.onRecord(r)    open review: shows "Record my mark"; r = {score, max, ticks, full}
//   opts.recorded       open review: starts as "Recorded x/y"
//   opts.onMark(r)      open review: after each tick
//   opts.record         false leaves the attempt record alone
//   opts.shuffle        false keeps a–d order in practice (default: shuffled once a question was seen)
//   opts.markable       false (open review of a blank answer) shows the model answer but no ticking
//   opts.onPaper        open: the answer was written on paper
//   opts.verdict        false leaves the verdict line out (the explanation page, nothing was answered)
//   opts.tutor          false leaves out "Ask Claude about this"
CR.q = (() => {
  const { h } = CR.dom;
  const TYPE = { mcq: "Multiple choice", open: "Open answer", sort: "Sort" };
  const LETTERS = "abcdefgh";
  let counter = 0;

  const nextId = () => `q${(counter += 1)}`;

  function sheet(q, opts, stemId) {
    return h(
      "article",
      {
        class: `qsheet q-${q.type}${opts.number ? " numbered" : ""}`,
        "aria-labelledby": stemId,
        dataset: { qid: q.id },
      },
      opts.number ? h("p", { class: "q-num", text: opts.number }) : null,
      opts.meta === false ? null : h("p", { class: "q-meta", text: [TYPE[q.type], q.level].join(" · ") }),
      h("div", { class: "q-stem prose", id: stemId, html: q.stem_html }),
    );
  }

  // The explanation, what a teacher's sample question really tests, the way back to the basics and
  // the tutor. The verdict sits higher up, in the slot from verdictSlot().
  function feedback(q, opts, getAnswer) {
    return h(
      "div",
      { class: "q-feedback" },
      CR.ui.note("Why", q.explanation_html),
      q.dissection_html ? CR.ui.note("What this question really tests", q.dissection_html) : null,
      opts.tutor === false ? null : CR.ui.tutorBox(q, getAnswer),
      opts.revise === false ? null : CR.ui.basicsLink(q),
      q.source_ref ? h("p", { class: "source" }, "Source: ", CR.dom.codeText(q.source_ref)) : null,
    );
  }

  const verdictSlot = () => h("div", { class: "q-verdict", tabindex: "-1" });

  // ------------------------------------------------------------------ multiple choice

  function mcq(container, q, opts) {
    const mode = opts.mode || "practice";
    const id = nextId();
    const stemId = `${id}-stem`;
    const attempts = CR.store.get().q[q.id]?.a || 0;
    const shuffle = mode === "practice" && opts.shuffle !== false && attempts > 0;
    const order = shuffle
      ? CR.util.shuffled(
          q.options.map((_, i) => i),
          CR.util.hashString(`${q.id}#${attempts}`),
        )
      : q.options.map((_, i) => i);
    let choice = Number.isInteger(opts.answer) ? opts.answer : null;
    let checked = false;

    const el = sheet(q, opts, stemId);
    const slot = verdictSlot();
    const rows = order.map((orig, pos) => {
      const option = q.options[orig];
      const input = h("input", {
        type: "radio",
        class: "opt-input",
        name: id,
        value: String(orig),
        checked: choice === orig,
        disabled: mode === "review",
        onchange: () => select(orig),
      });
      const why = h("span", { class: "opt-why prose", html: option.why_html, hidden: true });
      const mark = h("span", { class: "opt-mark" });
      const row = h(
        "label",
        { class: "opt" },
        input,
        h("span", { class: "opt-letter", text: `${LETTERS[pos]})` }),
        h("span", { class: "opt-body" }, h("span", { class: "opt-text prose", html: option.text_html }), why),
        mark,
      );
      return { orig, pos, row, input, why, mark };
    });
    el.append(
      slot,
      h("fieldset", { class: "opts" }, h("legend", { class: "vh", text: "Choose one answer" }), rows.map((r) => r.row)),
    );
    const checkButton =
      mode === "practice" ? CR.ui.button("Check answer", { kind: "primary", disabled: true, onClick: check }) : null;
    if (checkButton) {
      el.append(
        h("div", { class: "q-actions" }, checkButton, h("span", { class: "fine", text: "Keys: a to d choose, Enter checks." })),
      );
    }

    function paint() {
      for (const r of rows) r.row.classList.toggle("is-selected", r.orig === choice);
      if (checkButton) checkButton.disabled = choice === null;
    }

    function select(orig) {
      if (checked || mode === "review") return;
      choice = orig;
      paint();
      if (opts.onChange) opts.onChange(orig);
    }

    function verdictText() {
      const right = rows.find((r) => q.options[r.orig].correct);
      const letter = `${LETTERS[right.pos]})`;
      if (choice === null) return [false, `Not answered. The answer is ${letter}`];
      if (!q.options[choice].correct) return [false, `Not quite. The answer is ${letter}`];
      return [true, "Correct."];
    }

    function reveal() {
      for (const r of rows) {
        const correct = q.options[r.orig].correct;
        const mine = r.orig === choice;
        r.input.disabled = true;
        r.why.hidden = false;
        r.row.classList.toggle("is-correct", correct);
        r.row.classList.toggle("is-wrong", !correct && mine);
        if (correct) r.mark.replaceChildren(CR.ui.mark("pass"), mine ? "your answer" : "correct answer");
        else if (mine) r.mark.replaceChildren(CR.ui.mark("fail"), "your answer");
      }
      el.querySelector(".q-actions")?.remove();
      const [ok, text] = verdictText();
      if (opts.verdict !== false) slot.replaceChildren(CR.ui.verdict(ok, text));
      el.append(feedback(q, opts, () => ({ choice })));
      return text;
    }

    function check() {
      if (choice === null || checked) return;
      checked = true;
      const ok = q.options[choice].correct;
      if (opts.record !== false) CR.store.recordAnswer(q.id, ok);
      CR.dom.announce(reveal());
      CR.dom.reveal(slot);
      if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "mcq", ok, choice });
      if (opts.onReveal) opts.onReveal();
    }

    if (mode === "review") {
      checked = true;
      reveal();
    }
    paint();
    container.append(el);

    return {
      el,
      done: () => checked,
      shown: () => checked,
      answers: () => choice,
      // a–d or 1–4 choose an option; Enter checks. Returns true when the key was used.
      key(event) {
        if (checked || mode === "review" || event.altKey || event.ctrlKey || event.metaKey) return false;
        if (event.key === "Enter" && mode === "practice" && choice !== null) {
          check();
          return true;
        }
        const k = event.key.toLowerCase();
        const pos = /^[a-h]$/.test(k) ? LETTERS.indexOf(k) : /^[1-8]$/.test(k) ? Number(k) - 1 : -1;
        if (pos < 0 || pos >= rows.length) return false;
        rows[pos].input.checked = true;
        rows[pos].input.focus();
        select(rows[pos].orig);
        return true;
      },
    };
  }

  // ------------------------------------------------------------------ open answers

  function open(container, q, opts) {
    const mode = opts.mode || "practice";
    const id = nextId();
    const target = CR.util.parseRange(q.lines);
    const draftKey = (label) => `open.${q.id}.${label}`;
    const answers = {};
    const ticks = {};
    const markable = opts.markable !== false;
    let revealed = false;
    let recorded = mode === "review" && Boolean(opts.recorded);

    const el = sheet(q, opts, `${id}-stem`);
    const total = h("p", { class: "lines-total" });

    const parts = q.parts.map((part, index) => {
      const pid = `${id}-p${index}`;
      answers[part.label] =
        mode === "practice" ? CR.store.draft(draftKey(part.label)) : opts.answer?.[part.label] || "";
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
          h("span", { class: "part-marks", text: CR.util.plural(part.marks, "mark") }),
        ),
        area,
        h("p", { class: "part-foot" }, estimate),
        marking,
      );
      area.addEventListener("input", () => {
        answers[part.label] = area.value;
        fit(area);
        paintLines();
        if (mode === "practice") CR.store.setDraft(draftKey(part.label), area.value);
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
        const n = CR.util.lineEstimate(p.area.value);
        sum += n;
        p.estimate.textContent = `≈ ${CR.util.plural(n, "line")}`;
      }
      let advice = "";
      if (target && sum > 0 && sum < target.lo) advice = " · shorter than the paper expects";
      if (target && sum > target.hi) advice = " · longer than the paper expects";
      total.textContent = `≈ ${CR.util.plural(sum, "handwritten line")} in total, target ${q.lines}${advice}`;
    }

    el.append(h("div", { class: "parts" }, parts.map((p) => p.row)), total);

    // ---- self-marking

    const scoreLine = h("p", { class: "score-line", "aria-live": "polite" });
    const recordButton = CR.ui.button("Record my mark", { kind: "primary", onClick: record });

    // The button stays focusable (aria-disabled, not disabled) so focus is not lost once recorded.
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
      return { ...CR.scoring.openScore(q, t), ticks: t };
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
          return h("div", { class: "rubric-item" }, box, h("label", { for: `${p.pid}-r${i}`, html }));
        }),
      );
    }

    function openMarking() {
      revealed = true;
      for (const p of parts) {
        p.marking.append(
          CR.ui.note("Model answer", p.part.model_answer_html, "model"),
          rubricList(p),
          h("p", { class: "part-score-line" }, "Part ", p.part.label, ": ", h("span", { class: "part-score" })),
          h("div", { class: "weak-answers", hidden: true }, CR.ui.note("Where answers lose marks", p.part.weak_answers_html, "warn")),
        );
        p.marking.hidden = false;
      }
      el.querySelector(".q-actions")?.remove();
      const canRecord = markable && (mode === "practice" || opts.onRecord);
      el.append(
        scoreLine,
        canRecord ? h("div", { class: "q-actions" }, recordButton) : null,
        feedback(q, opts, () => ({
          answers: { ...answers },
          score: current().score,
          max: current().max,
        })),
      );
      const now = paintScore();
      if (recorded) setRecorded(now);
    }

    // The first record counts an attempt; recording again after changing ticks corrects it.
    function record() {
      if (recordButton.getAttribute("aria-disabled") === "true") return;
      const now = current();
      if (mode === "practice") {
        if (opts.record !== false) {
          if (recorded) CR.store.amendAnswer(q.id, now.full);
          else CR.store.recordAnswer(q.id, now.full);
        }
        if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "open", ok: now.full, ...now });
      } else if (opts.onRecord) {
        opts.onRecord({ qid: q.id, ...now });
      }
      recorded = true;
      setRecorded(now);
      CR.dom.announce(`Recorded ${now.score} out of ${now.max}.`);
    }

    if (mode === "practice") {
      el.append(
        h(
          "div",
          { class: "q-actions" },
          CR.ui.button("Show model answer", {
            kind: "primary",
            onClick: () => {
              openMarking();
              CR.dom.announce("Model answer shown. Tick each point your answer makes.");
              CR.dom.reveal(parts[0].marking);
              if (opts.onReveal) opts.onReveal();
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
      shown: () => revealed,
      key: () => false,
      answers: () => ({ ...answers }),
    };
  }

  // ------------------------------------------------------------------ sorting

  function sort(container, q, opts) {
    const mode = opts.mode || "practice";
    const id = nextId();
    const answers = q.items.map((_, i) => opts.answer?.[i] ?? null);
    // Up to four categories sit in one row; five or more in two even rows (3 + 2, not 4 + 1).
    const columns = q.categories.length <= 4 ? q.categories.length : Math.ceil(q.categories.length / 2);
    let checked = false;

    const el = sheet(q, opts, `${id}-stem`);
    const slot = verdictSlot();
    const placed = h("span", { class: "fine", "aria-live": "polite" });

    const rows = q.items.map((item, i) => {
      const textId = `${id}-i${i}`;
      const buttons = q.categories.map((cat, c) =>
        h(
          "button",
          {
            type: "button",
            class: "seg-btn",
            "aria-pressed": "false",
            disabled: mode === "review",
            onclick: () => assign(i, cat.id),
          },
          h("span", { class: "key", "aria-hidden": "true", text: String(c + 1) }),
          h("span", { class: "seg-label" }, CR.dom.codeText(cat.label)),
        ),
      );
      const result = h("div", { class: "sort-result", hidden: true });
      const row = h(
        "li",
        {
          class: "sort-item",
          tabindex: mode === "review" ? null : "0",
          "aria-labelledby": textId,
          onkeydown: (e) => onItemKey(e, i),
        },
        h("div", { class: "sort-text prose", id: textId, html: item.text_html }),
        h("div", { class: "seg", style: `--cols: ${columns}`, role: "group", "aria-label": `Category for item ${i + 1}` }, buttons),
        result,
      );
      return { item, row, buttons, result };
    });

    el.append(
      slot,
      h("p", { class: "fine sort-help" }, "Choose a category for every item. Keyboard: focus an item, then press 1 to ", String(q.categories.length), "."),
      h("ol", { class: "sort-items" }, rows.map((r) => r.row)),
    );

    const checkButton =
      mode === "practice" ? CR.ui.button("Check answers", { kind: "primary", disabled: true, onClick: check }) : null;
    if (checkButton) el.append(h("div", { class: "q-actions" }, checkButton, placed));

    function paint() {
      rows.forEach((r, i) =>
        r.buttons.forEach((b, c) => b.setAttribute("aria-pressed", String(answers[i] === q.categories[c].id))),
      );
      const n = answers.filter((a) => a !== null).length;
      placed.textContent = `${n} of ${answers.length} placed`;
      if (checkButton) checkButton.disabled = n < answers.length;
    }

    function assign(i, catId) {
      if (checked || mode === "review") return;
      answers[i] = catId;
      paint();
      if (opts.onChange) opts.onChange(answers.slice());
    }

    function onItemKey(event, i) {
      if (checked || mode === "review") return;
      const n = Number(event.key);
      if (Number.isInteger(n) && n >= 1 && n <= q.categories.length) {
        assign(i, q.categories[n - 1].id);
        (rows[i + 1] || rows[i]).row.focus();
        event.preventDefault();
        event.stopPropagation();
      } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        const next = rows[i + (event.key === "ArrowDown" ? 1 : -1)];
        if (next) next.row.focus();
        event.preventDefault();
      }
    }

    function reveal() {
      const score = CR.scoring.sortScore(q, answers);
      rows.forEach((r, i) => {
        const ok = score.items[i];
        const right = q.categories.find((c) => c.id === r.item.category);
        r.buttons.forEach((b) => (b.disabled = true));
        r.row.removeAttribute("tabindex");
        r.row.classList.add(ok ? "is-correct" : "is-wrong");
        const chosen = q.categories.find((c) => c.id === answers[i]);
        const line = ok
          ? CR.dom.plain(right.label)
          : `Belongs in: ${CR.dom.plain(right.label)} (you chose ${chosen ? CR.dom.plain(chosen.label) : "nothing"})`;
        r.result.replaceChildren(
          h("p", { class: `sort-verdict verdict-${ok ? "pass" : "fail"}` }, CR.ui.mark(ok ? "pass" : "fail"), line),
          h("div", { class: "prose", html: r.item.why_html }),
        );
        r.result.hidden = false;
      });
      el.querySelector(".q-actions")?.remove();
      const text = score.full ? `All ${score.total} placed correctly.` : `${score.correct} of ${score.total} placed correctly.`;
      slot.replaceChildren(CR.ui.verdict(score.full, text));
      el.append(feedback(q, opts, () => ({ answers: answers.slice() })));
      return { text, score };
    }

    function check() {
      if (checked || answers.includes(null)) return;
      checked = true;
      const { text, score } = reveal();
      if (opts.record !== false) CR.store.recordAnswer(q.id, score.full);
      CR.dom.announce(text);
      CR.dom.reveal(slot);
      if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "sort", ok: score.full, answers: answers.slice() });
      if (opts.onReveal) opts.onReveal();
    }

    if (mode === "review") {
      checked = true;
      reveal();
    }
    paint();
    container.append(el);

    return {
      el,
      done: () => checked,
      shown: () => checked,
      answers: () => answers.slice(),
      // Enter checks once every item is placed.
      key(event) {
        if (event.key !== "Enter" || checked || mode !== "practice" || answers.includes(null)) return false;
        check();
        return true;
      },
    };
  }

  // The component for a question's type.
  function mount(container, q, opts = {}) {
    if (q.type === "mcq") return mcq(container, q, opts);
    if (q.type === "open") return open(container, q, opts);
    if (q.type === "sort") return sort(container, q, opts);
    throw new RangeError(`unknown question type ${q.type}`);
  }

  return { mount, nextId, LETTERS };
})();
