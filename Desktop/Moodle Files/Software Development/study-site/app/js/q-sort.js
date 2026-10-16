// Sort (classification): each item gets a category by tapping its button, or by focusing the
// item and pressing 1–5. Modes: "practice" (check, why per item, recorded), "exam" (choose
// only; onChange(answers)), "review" (read-only with results). answers: category id per item.
SD.q.sort = (container, q, opts = {}) => {
  const { h } = SD.dom;
  const mode = opts.mode || "practice";
  const id = SD.q.nextId();
  const answers = q.items.map((_, i) => opts.answer?.[i] ?? null);
  // Up to four categories sit in one row; five or more in two even rows (3 + 2, not 4 + 1).
  const columns = q.categories.length <= 4 ? q.categories.length : Math.ceil(q.categories.length / 2);
  let checked = false;

  const el = SD.q.sheet(q, opts, `${id}-stem`);
  const slot = SD.q.verdictSlot();
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
        cat.label,
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
      h(
        "div",
        { class: "seg", style: `--cols: ${columns}`, role: "group", "aria-label": `Category for item ${i + 1}` },
        buttons,
      ),
      result,
    );
    return { item, row, buttons, result };
  });

  el.append(
    slot,
    h(
      "p",
      { class: "fine sort-help" },
      "Choose a category for every item. Keyboard: focus an item, then press 1–",
      String(q.categories.length),
      ".",
    ),
    h("ol", { class: "sort-items" }, rows.map((r) => r.row)),
  );

  const checkButton =
    mode === "practice"
      ? SD.ui.button("Check answers", { kind: "primary", disabled: true, onClick: check })
      : null;
  if (checkButton) el.append(h("div", { class: "q-actions" }, checkButton, placed));

  function paint() {
    rows.forEach((r, i) =>
      r.buttons.forEach((b, c) =>
        b.setAttribute("aria-pressed", String(answers[i] === q.categories[c].id)),
      ),
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
    const score = SD.scoring.sortScore(q, answers);
    rows.forEach((r, i) => {
      const ok = score.items[i];
      const right = q.categories.find((c) => c.id === r.item.category);
      r.buttons.forEach((b) => (b.disabled = true));
      r.row.removeAttribute("tabindex");
      r.row.classList.add(ok ? "is-correct" : "is-wrong");
      const chosen = q.categories.find((c) => c.id === answers[i]);
      const line = ok
        ? right.label
        : `Belongs in: ${right.label} (you chose ${chosen ? chosen.label : "nothing"})`;
      r.result.replaceChildren(
        h("p", { class: `sort-verdict verdict-${ok ? "pass" : "fail"}` }, SD.ui.mark(ok ? "pass" : "fail"), line),
        h("div", { class: "prose", html: r.item.why_html }),
      );
      r.result.hidden = false;
    });
    el.querySelector(".q-actions")?.remove();
    const text = score.full
      ? `All ${score.total} placed correctly.`
      : `${score.correct} of ${score.total} placed correctly.`;
    slot.replaceChildren(SD.ui.verdict(score.full, text));
    el.append(SD.q.feedback(q, opts));
    return { text, score };
  }

  function check() {
    if (checked || answers.includes(null)) return;
    checked = true;
    const { text, score } = reveal();
    if (opts.record !== false) SD.store.recordAnswer(q.id, score.full, null);
    SD.dom.announce(text);
    SD.dom.reveal(slot);
    if (opts.onAnswer) opts.onAnswer({ qid: q.id, type: "sort", ok: score.full, answers: answers.slice() });
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
    // Enter checks once every item is placed.
    key(event) {
      if (event.key !== "Enter" || checked || mode !== "practice" || answers.includes(null)) return false;
      check();
      return true;
    },
  };
};
