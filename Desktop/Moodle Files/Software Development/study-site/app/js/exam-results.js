// Results of a sitting (#exam.attempt.<id> once handed in): the pytest-style summary, the score
// in marks and per cent, the time used, the per-module breakdown, and every question in review:
// your answer, the correct one, every option's why, the explanation and the Revise link. Open
// answers are marked here against each part's rubric (or by Claude) and then recorded; until
// then they count 0 and show as "to mark".
SD.examResults = (() => {
  const { h } = SD.dom;
  const FILTERS = [
    ["all", "All"],
    ["fail", "Wrong"],
    ["mark", "To mark"],
    ["flag", "Flagged"],
  ];
  const REVISE_ROWS = 5;
  const SHAPE = { pass: "pass", fail: "fail", mark: "none" };

  // [status for the mark, word, score text] for the line above each question.
  function verdict(r) {
    if (r.status === "mark") return ["none", "To mark", SD.util.plural(r.max, "mark")];
    const score = `${r.score}/${r.max}`;
    if (r.state === "blank") return ["fail", "Not answered", score];
    if (r.type === "open") return [r.status, r.status === "pass" ? "Full marks" : "Below full marks", score];
    return [r.status, r.status === "pass" ? "Right" : "Wrong", score];
  }

  function figure(label, value, note) {
    return h(
      "div",
      { class: "figure" },
      h("p", { class: "label", text: label }),
      h("p", { class: "figure-value", text: value }),
      h("p", { class: "fine", text: note }),
    );
  }

  const moduleOrder = (row) => SD.data.module(row.mid)?.order ?? 99;
  const sectionOrder = (row) => SD.data.section(row.sid)?.index ?? 99;

  // The row heading: a module (code and title) or, for a paper on one module, a section.
  function rowLink(row) {
    if (row.sid !== undefined) {
      const section = SD.data.section(row.sid);
      if (!section) return row.sid;
      return h(
        "a",
        { href: "#" + SD.data.sectionRoute(section.id) },
        h("span", { class: "module-code", text: section.token }),
        h("span", { html: section.heading_html }),
      );
    }
    const mod = SD.data.module(row.mid);
    if (!mod) return row.mid;
    return [
      h(
        "a",
        { href: SD.route.href("learn", mod.id) },
        h("span", { class: "module-code", text: SD.ui.moduleCode(mod) }),
        mod.title,
      ),
      mod.predicted ? SD.ui.chip("predicted", "warn") : null,
    ];
  }

  // rows: m.modules or m.sections; label: the first column's heading.
  function breakdownTable(rows, label) {
    const num = (text) => h("td", { class: "num", text });
    const order = label === "Section" ? sectionOrder : moduleOrder;
    return h(
      "table",
      { class: "module-table" },
      h(
        "thead",
        {},
        h(
          "tr",
          {},
          h("th", { scope: "col", text: label }),
          h("th", { scope: "col", class: "num", text: "Right" }),
          h("th", { scope: "col", class: "num", text: "Marks" }),
          h("th", { scope: "col", class: "num", text: "%" }),
        ),
      ),
      h(
        "tbody",
        {},
        rows
          .slice()
          .sort((a, b) => order(a) - order(b))
          .map((row) =>
            h(
              "tr",
              {},
              h("th", { scope: "row" }, rowLink(row)),
              num(`${row.passed}/${row.count}`),
              h(
                "td",
                { class: "num" },
                `${row.score}/${row.max}`,
                row.toMark ? h("span", { class: "to-mark-note", text: `${row.toMark} to mark` }) : null,
              ),
              num(`${SD.util.percent(row.score, row.max)}%`),
            ),
          ),
      ),
    );
  }

  function render(root, record) {
    let rec = record;
    let filter = "all";
    const questions = SD.exam.questionsOf(rec, SD.data.question);
    const summary = h("div", { class: "exam-summary" });
    const revise = h("section", { class: "revise-first", "aria-labelledby": "revise-first-title" });
    const breakdown = h("div", { class: "table-wrap" });
    // A paper on one module (the teacher's sample) is broken down by section instead.
    const bySection = new Set(questions.map((q) => q.mid)).size === 1;
    const filterButtons = FILTERS.map(([key, text]) =>
      h(
        "button",
        { type: "button", class: "seg-btn", "aria-pressed": String(key === filter), onclick: () => setFilter(key) },
        text,
        h("span", { class: "seg-count" }),
      ),
    );
    const cells = questions.map((_, i) =>
      h("button", { type: "button", class: "review-cell", onclick: () => jump(i) }),
    );
    const list = h("div", { class: "review-list" });
    const againText = {
      [SD.exam.BANK]: "Draw another paper",
      [SD.exam.SAMPLE]: "Sit the sample paper again",
    };
    const again = SD.ui.linkButton(
      againText[rec.paper] || `Sit ${rec.title} again`,
      SD.route.href("exam", rec.paper),
      "primary",
    );

    root.append(
      h(
        "div",
        { class: "page exam-results" },
        SD.ui.crumbs([["Exam", "#exam"], [rec.title, SD.route.href("exam", rec.paper)], ["Results"]]),
        h("p", { class: "label", text: `Started ${SD.util.dateTimeLabel(rec.started)}` }),
        h("h1", { text: `${rec.title}: results` }),
        summary,
        revise,
        h("h2", { text: bySection ? "By section" : "By module" }),
        breakdown,
        h("h2", { text: "Every question" }),
        h("p", {
          class: "fine",
          text: "Your answer, the correct one, why each option is right or wrong, and the section to revise.",
        }),
        h("div", { class: "seg review-filter", role: "group", "aria-label": "Show questions" }, filterButtons),
        h("p", { class: "label review-grid-label", id: "review-grid-label", text: "Jump to" }),
        h("nav", { class: "review-grid", "aria-labelledby": "review-grid-label" }, cells),
        list,
        h("div", { class: "actions" }, again, SD.ui.linkButton("All papers", "#exam")),
      ),
    );

    const onPaper = (q) => rec.paper_answers.includes(q.id);

    // Mounted once the list is in the page, so the read-only answers size their lined areas.
    const items = questions.map((q, i) => {
      const head = h("p", { class: "review-head" });
      const holder = h("div", { class: "review-body" });
      const box = h("div", { class: "review-q" }, head, holder);
      list.append(box);
      const item = { q, box, head, holder };
      mountQuestion(item, i);
      return item;
    });

    function mountQuestion(item, i) {
      const { q, holder } = item;
      holder.replaceChildren();
      const opts = { mode: "review", number: `Q${i + 1}`, meta: false, answer: rec.answers[q.id] };
      let blank = false;
      if (q.type === "open") {
        const ticks = rec.ticks[q.id] || {};
        opts.ticks = ticks;
        opts.onPaper = onPaper(q);
        blank = SD.exam.answerState(q, rec.answers[q.id], onPaper(q)) === "blank";
        if (blank) {
          opts.markable = false;
        } else {
          opts.record = false;
          opts.recorded = q.id in rec.marks && SD.scoring.openScore(q, ticks).score === rec.marks[q.id];
          opts.onMark = (now) => {
            rec = { ...rec, ticks: { ...rec.ticks, [q.id]: now.ticks } };
            SD.store.saveExam(rec);
          };
          opts.onAnswer = (result) => recordMark(q, result);
        }
      }
      if (blank) {
        holder.append(
          h(
            "div",
            { class: "paper-prompt" },
            h("p", {
              class: "fine",
              text: "Left blank in the box, so it scores 0. If you wrote this answer on paper, say so to mark it yourself.",
            }),
            SD.ui.button("I wrote this on paper", { kind: "secondary", onClick: () => markPaper(item, i) }),
          ),
        );
      }
      const controller = SD.q.mount(holder, q, opts);
      controller.el.tabIndex = -1;
    }

    // An open answer written on paper: it becomes markable like a typed one. If hand-in already
    // counted it as wrong, recording its mark corrects that attempt.
    function markPaper(item, i) {
      rec = SD.exam.withTotals({ ...rec, paper_answers: [...rec.paper_answers, item.q.id] }, questions);
      SD.store.saveExam(rec);
      mountQuestion(item, i);
      paint();
      SD.dom.announce("Marked as written on paper. Tick the rubric points your answer makes.");
      item.box.querySelector(".qsheet").focus({ preventScroll: true });
    }

    // The first mark counts an attempt in progress; marking again corrects it.
    function recordMark(q, result) {
      const first = !rec.recorded.includes(q.id);
      rec = SD.exam.withTotals(
        {
          ...rec,
          ticks: { ...rec.ticks, [q.id]: result.ticks },
          marks: { ...rec.marks, [q.id]: result.score },
          recorded: first ? [...rec.recorded, q.id] : rec.recorded,
        },
        questions,
      );
      SD.store.saveExam(rec);
      if (first) SD.store.recordAnswer(q.id, result.full);
      else SD.store.amendAnswer(q.id, result.full);
      paint();
    }

    // How this sitting compares with the first one of the same paper.
    function baselineLine(m) {
      const first = SD.exam.firstDone(SD.store.get().exams, rec.paper);
      if (!first || first.id === rec.id || m.toMark) return null;
      return h("p", {
        class: "fine",
        text:
          `First sitting of this paper: ${first.score}/${first.max} (${SD.util.percent(first.score, first.max)}%). ` +
          `Now: ${m.score}/${m.max} (${SD.util.percent(m.score, m.max)}%).`,
      });
    }

    function paintSummary(m) {
      const firstToMark = m.results.findIndex((r) => r.status === "mark");
      summary.replaceChildren();
      SD.dom.append(summary, [
        SD.ui.pytestLine(
          SD.scoring.pytestSummary({ passed: m.passed, failed: m.failed, toMark: m.toMark, ms: rec.used_ms }),
        ),
        rec.timed_out
          ? h("p", { class: "notice", text: "Time ran out: the paper was handed in automatically at 0:00." })
          : null,
        baselineLine(m),
        h(
          "div",
          { class: "figures exam-figures" },
          figure(
            "Score",
            `${m.score}/${m.max}`,
            m.toMark ? `${SD.util.plural(m.toMark, "open answer")} still to mark` : "marks",
          ),
          figure("Per cent", `${SD.util.percent(m.score, m.max)}%`, m.toMark ? "so far" : "of the marks"),
          figure("Time used", SD.util.duration(rec.used_ms), `of ${rec.minutes} minutes`),
        ),
        firstToMark >= 0
          ? h(
              "p",
              { class: "to-mark" },
              "Mark your open answers: tick each rubric point your answer makes, then Record my mark. ",
              h("button", {
                type: "button",
                class: "link-btn",
                text: `Go to Q${firstToMark + 1}`,
                onclick: () => jump(firstToMark),
              }),
            )
          : null,
      ]);
    }

    const shows = (key, r, flagged) =>
      key === "all" || (key === "flag" ? flagged : r.status === key);

    function paintReview(m) {
      const flagged = new Set(rec.flags);
      filterButtons.forEach((button, k) => {
        const key = FILTERS[k][0];
        const n = m.results.filter((r) => shows(key, r, flagged.has(r.qid))).length;
        button.querySelector(".seg-count").textContent = String(n);
        button.setAttribute("aria-pressed", String(key === filter));
        button.disabled = n === 0 && key !== "all";
      });
      m.results.forEach((r, i) => {
        const [kind, word, score] = verdict(r);
        const isFlagged = flagged.has(r.qid);
        items[i].head.replaceChildren();
        SD.dom.append(items[i].head, [
          SD.ui.statusMark(kind, ""),
          h("span", { class: "review-word", text: word }),
          h("span", { class: "review-score", text: score }),
          isFlagged ? SD.ui.chip("flagged", "none") : null,
        ]);
        items[i].box.hidden = !shows(filter, r, isFlagged);
        cells[i].className = `review-cell is-${r.status}`;
        cells[i].replaceChildren(SD.ui.mark(SHAPE[r.status]), String(i + 1));
        cells[i].setAttribute("aria-label", `Question ${i + 1}: ${word.toLowerCase()}`);
      });
    }

    // The sections that cost the most marks, with a way straight to practising the weak spots.
    function paintRevise(m) {
      const lost = SD.exam.lostBySection(m.results).slice(0, REVISE_ROWS);
      revise.hidden = lost.length === 0;
      revise.replaceChildren();
      if (lost.length === 0) return;
      SD.dom.append(revise, [
        h("h2", { id: "revise-first-title", text: "Revise first" }),
        h(
          "ul",
          { class: "revise-list" },
          lost.map(({ sid, lost: marks }) => {
            const section = SD.data.section(sid);
            if (!section) return null;
            const mod = SD.data.module(section.mid);
            return h(
              "li",
              {},
              h("a", { href: "#" + SD.data.sectionRoute(sid), html: section.heading_html }),
              h("span", { class: "revise-where", text: `${mod ? mod.title + " · " : ""}${SD.util.plural(marks, "mark")} lost` }),
            );
          }),
        ),
        h("div", { class: "actions" }, SD.ui.linkButton("Practise weak spots", "#practice.weak", "secondary")),
      ]);
    }

    function paint() {
      const m = SD.exam.mark(questions, rec);
      paintSummary(m);
      paintRevise(m);
      breakdown.replaceChildren(
        bySection ? breakdownTable(m.sections, "Section") : breakdownTable(m.modules, "Module"),
      );
      paintReview(m);
    }

    function setFilter(key) {
      filter = key;
      paintReview(SD.exam.mark(questions, rec));
    }

    function jump(i) {
      if (items[i].box.hidden) setFilter("all");
      items[i].box.scrollIntoView({ block: "start" });
      items[i].box.querySelector(".qsheet").focus({ preventScroll: true });
    }

    paint();
    return { title: `${rec.title} results`, resume: `${rec.title} results` };
  }

  return { render };
})();
