// Flashcards (#cards[.<module>]): Leitner boxes 1–5. Due cards come first, then new ones.
// Flip with F or Space; grade with 1 (again: back to box 1), 2 (good: up one box), 3 (easy: up two).
(() => {
  const { h } = SD.dom;
  const KIND = { concept: "Concept", distinction: "Distinction", reading: "Reading", recall: "Recall" };
  const GRADE_LABEL = { again: "Again", good: "Good", easy: "Easy" };
  let session = null; // {key, queue: [ids], done: [{id, grade}], flipped}

  // A review is scheduled so that every card is back before the exam eve.
  const examStart = () => Date.parse(SD.data.meta.exam.date);

  function waitText(entry, grade) {
    const days = SD.leitner.waitDays(entry, grade, Date.now(), examStart());
    if (days === 0) return "this session";
    return days === 1 ? "tomorrow" : `in ${days} days`;
  }

  function boxStrip(boxes) {
    return h(
      "div",
      { class: "boxes", role: "list", "aria-label": "Cards per box" },
      boxes.map((n, i) =>
        h(
          "div",
          { class: "box", role: "listitem" },
          h("span", { class: "box-n", text: String(n) }),
          h("span", { class: "box-label", text: `box ${i + 1}` }),
        ),
      ),
    );
  }

  function queueFor(ids, length) {
    const fc = SD.store.get().fc;
    return length === 0
      ? SD.leitner.queue(ids, fc, Date.now(), Infinity, false)
      : SD.leitner.queue(ids, fc, Date.now(), length);
  }

  function renderStart(root, mid) {
    const stats = SD.stats.cards(mid);
    const saved = SD.store.get().prefs.cardsLength;
    const length = Number.isInteger(saved) ? saved : 20;
    const moduleSelect = h(
      "select",
      { id: "cards-module" },
      h("option", { value: "", text: "All modules" }),
      SD.data.modules.map((mod) => h("option", { value: mod.id, text: mod.title })),
    );
    moduleSelect.value = mid || "";
    moduleSelect.addEventListener("change", () =>
      SD.router.go(moduleSelect.value ? SD.route.build("cards", moduleSelect.value) : "cards"),
    );
    const lengthSelect = h(
      "select",
      { id: "cards-length" },
      [10, 20, 50].map((n) => h("option", { value: String(n), text: `${n} cards` })),
      h("option", { value: "0", text: "All that are due" }),
    );
    lengthSelect.value = String(length);
    // 0 means every card that is due and none that is new.
    const queueSize = () => {
      const n = Number(lengthSelect.value);
      return n === 0 ? stats.due : Math.min(n, stats.due + stats.fresh);
    };
    const startButton = SD.ui.button("", {
      kind: "primary",
      onClick: () => {
        SD.store.setPref("cardsLength", Number(lengthSelect.value));
        session = {
          key: mid || "",
          queue: queueFor(stats.ids, Number(lengthSelect.value)),
          done: [],
          flipped: false,
        };
        SD.router.refresh();
      },
    });
    const paintButton = () => {
      const n = queueSize();
      startButton.textContent = n ? `Start: ${SD.util.plural(n, "card")}` : "Nothing due";
      startButton.disabled = n === 0;
    };
    lengthSelect.addEventListener("change", paintButton);
    paintButton();
    root.append(
      h(
        "div",
        { class: "page" },
        h("h1", { text: "Flashcards" }),
        h("p", {
          class: "lead",
          text:
            "A card you know moves up a box and comes back later: tomorrow from box 2, after a " +
            "week from box 5. A card you miss goes back to box 1 and returns in this session.",
        }),
        h(
          "div",
          { class: "card-figures" },
          h("p", {}, h("span", { class: "figure-value", text: String(stats.due) }), " due now"),
          h("p", {}, h("span", { class: "figure-value", text: String(stats.fresh) }), " not seen yet"),
        ),
        boxStrip(stats.boxes),
        h(
          "div",
          { class: "filters" },
          h("div", { class: "field" }, h("label", { for: "cards-module", text: "Module" }), moduleSelect),
          h("div", { class: "field" }, h("label", { for: "cards-length", text: "Session length" }), lengthSelect),
        ),
        h("div", { class: "actions" }, startButton),
      ),
    );
    return { title: "Flashcards" };
  }

  function renderSummary(root, s) {
    const tally = { again: 0, good: 0, easy: 0 };
    for (const d of s.done) tally[d.grade] += 1;
    root.append(
      h(
        "div",
        { class: "page" },
        h("p", { class: "label", text: "Flashcards" }),
        h("h1", { text: "Session complete" }),
        h("p", {
          class: "lead",
          text:
            `${SD.util.plural(s.done.length, "review")}: ` +
            `${tally.good} good, ${tally.easy} easy, ${tally.again} again.`,
        }),
        boxStrip(SD.stats.cards(s.key || null).boxes),
        h(
          "div",
          { class: "actions" },
          SD.ui.button("Back to flashcards", { kind: "primary", onClick: () => SD.router.refresh() }),
        ),
      ),
    );
    return { title: "Flashcards" };
  }

  function renderCard(root, s) {
    const id = s.queue[0];
    const card = SD.data.card(id);
    const entry = SD.store.get().fc[id];
    const mod = SD.data.module(card.mid);
    const reviewed = s.done.length;
    const back = h(
      "div",
      { class: "card-back", hidden: !s.flipped, tabindex: "-1", role: "group", "aria-label": "Answer" },
      h("div", { class: "prose", html: card.back_html }),
    );
    const flipButton = SD.ui.button("Show answer", { kind: "primary", onClick: flip });
    const grades = h(
      "div",
      { class: "grades", hidden: !s.flipped },
      SD.leitner.GRADES.map((grade, i) =>
        h(
          "button",
          {
            type: "button",
            class: `btn btn-${grade === "good" ? "primary" : "secondary"} grade`,
            onclick: () => rate(grade),
          },
          h("span", { class: "key", "aria-hidden": "true", text: String(i + 1) }),
          h("span", { class: "grade-name", text: GRADE_LABEL[grade] }),
          h("span", { class: "grade-wait", text: waitText(entry, grade) }),
        ),
      ),
    );

    // Focus goes to the answer, not to a grade button: a second Space or Enter must not grade
    // the card by accident. The answer is read out because focus lands on a group.
    function flip() {
      s.flipped = true;
      back.hidden = false;
      grades.hidden = false;
      flipButton.hidden = true;
      SD.dom.announce(`Answer: ${SD.util.truncate(back.textContent, 400)}`);
      SD.dom.reveal(back);
    }

    function rate(grade) {
      SD.store.reviewCard(id, grade, examStart());
      s.done.push({ id, grade });
      s.queue.shift();
      if (grade === "again") s.queue.push(id);
      s.flipped = false;
      SD.router.refresh();
    }

    root.append(
      h(
        "div",
        { class: "page" },
        h(
          "div",
          { class: "practice-bar" },
          h("p", { class: "label", text: `Flashcards${s.key ? " · " + mod.title : ""}` }),
          SD.ui.progress(reviewed, reviewed + s.queue.length, "Cards reviewed"),
          SD.ui.button("End session", {
            kind: "quiet",
            onClick: () => {
              s.queue = [];
              SD.router.refresh();
            },
          }),
        ),
        h(
          "article",
          { class: "flashcard", "aria-labelledby": "card-front" },
          h("h1", { class: "vh", text: "Flashcard" }),
          h("p", {
            class: "q-meta",
            text: [KIND[card.kind], mod.title, entry ? `box ${entry.box}` : "new"].join(" · "),
          }),
          h("div", { class: "card-front prose", id: "card-front", html: card.front_html }),
          back,
          h("div", { class: "q-actions" }, flipButton, grades),
        ),
      ),
    );
    return {
      title: "Flashcards",
      onKey(event) {
        const k = event.key.toLowerCase();
        if (!s.flipped && (k === "f" || k === " ")) {
          flip();
          return true;
        }
        if (s.flipped && (k === "f" || k === " ")) return true;
        const grade = { 1: "again", 2: "good", 3: "easy" }[k];
        if (s.flipped && grade) {
          rate(grade);
          return true;
        }
        return false;
      },
    };
  }

  SD.router.register("cards", {
    render({ root, args }) {
      const mid = args[0] && SD.data.module(args[0]) ? args[0] : null;
      if (session && session.key !== (mid || "")) session = null;
      if (!session) return renderStart(root, mid);
      if (session.queue.length === 0) {
        const finished = session;
        session = null; // the summary shows once; coming back starts afresh
        return renderSummary(root, finished);
      }
      return renderCard(root, session);
    },
  });
})();
