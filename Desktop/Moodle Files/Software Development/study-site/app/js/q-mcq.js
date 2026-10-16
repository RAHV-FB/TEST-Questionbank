// Multiple choice. Modes: "practice" (choose, optional confidence, check, full feedback, the
// attempt is recorded), "exam" (choose only; onChange), "review" (read-only with feedback).
SD.q.mcq = (container, q, opts = {}) => {
  const { h } = SD.dom;
  const mode = opts.mode || "practice";
  const id = SD.q.nextId();
  const stemId = `${id}-stem`;
  const attempt = SD.store.get().q[q.id]?.a || 0;
  const shuffle = mode === "practice" && opts.shuffle !== false;
  const order = shuffle
    ? SD.select.optionOrder(q.id, attempt, q.options.length)
    : q.options.map((_, i) => i);
  const LETTERS = "abcdefgh";
  const CONFIDENCE = [
    ["sure", "Sure"],
    ["unsure", "Unsure"],
    ["guess", "Guess"],
  ];
  let choice = Number.isInteger(opts.answer) ? opts.answer : null;
  let conf = null;
  let checked = false;

  const el = SD.q.sheet(q, opts, stemId);
  const slot = SD.q.verdictSlot();
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
    h(
      "fieldset",
      { class: "opts" },
      h("legend", { class: "vh", text: "Choose one answer" }),
      rows.map((r) => r.row),
    ),
  );

  const confButtons = CONFIDENCE.map(([value, label]) =>
    h("button", {
      type: "button",
      class: "seg-btn",
      "aria-pressed": "false",
      onclick: () => setConfidence(value),
      text: label,
    }),
  );
  const checkButton =
    mode === "practice"
      ? SD.ui.button("Check answer", { kind: "primary", disabled: true, onClick: check })
      : null;
  if (checkButton) {
    el.append(
      h(
        "div",
        { class: "q-actions" },
        h(
          "div",
          { class: "conf", role: "group", "aria-labelledby": `${id}-conf` },
          h("span", { class: "conf-label", id: `${id}-conf`, text: "How sure are you? (optional)" }),
          h("span", { class: "seg" }, confButtons),
        ),
        checkButton,
      ),
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

  function setConfidence(value) {
    conf = conf === value ? null : value;
    confButtons.forEach((b, i) => b.setAttribute("aria-pressed", String(CONFIDENCE[i][0] === conf)));
  }

  // [ok, words] for the verdict line; the shape (✓ or ✗) is drawn by SD.ui.verdict.
  function verdict() {
    const right = rows.find((r) => q.options[r.orig].correct);
    const letter = `${LETTERS[right.pos]})`;
    if (choice === null) return [false, `Not answered. The answer is ${letter}`];
    if (!q.options[choice].correct) return [false, `Not quite. The answer is ${letter}`];
    if (conf === "guess") {
      return [true, "Correct, but you guessed: it stays in your weak spots until you get it right again without guessing."];
    }
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
      if (correct) r.mark.replaceChildren(SD.ui.mark("pass"), mine ? "your answer" : "correct answer");
      else if (mine) r.mark.replaceChildren(SD.ui.mark("fail"), "your answer");
    }
    el.querySelector(".q-actions")?.remove();
    const [ok, text] = verdict();
    if (opts.verdict !== false) slot.replaceChildren(SD.ui.verdict(ok, text));
    el.append(SD.q.feedback(q, opts));
    return text;
  }

  function check() {
    if (choice === null || checked) return;
    checked = true;
    const ok = q.options[choice].correct;
    if (opts.record !== false) SD.store.recordAnswer(q.id, ok, conf);
    SD.dom.announce(reveal());
    SD.dom.reveal(slot);
    if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "mcq", ok, choice, conf });
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
};
