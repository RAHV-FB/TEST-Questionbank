// Exam: #exam (the papers on offer and every attempt), #exam.<paper> (sample, bank, paper-a …:
// the rules screen, as on the day, and Start), #exam.attempt.<id> (the sitting while it runs, see
// exam-paper.js; its results once handed in, see exam-results.js). One sitting runs at a time; a
// sitting whose time ran out while the page was closed is handed in when this view opens.
(() => {
  const { h } = SD.dom;
  const KIND = {
    sample: "Teacher's sample",
    realistic: "Mock paper · realistic",
    "worst-case": "Mock paper · worst case",
    beyond: "Mock paper · a step beyond",
    bank: "Drawn from the bank",
  };
  const START = {
    sample: "Start the sample paper",
    bank: "Draw and start a paper",
  };
  const shape = SD.exam.BANK_SHAPE;
  const ABOUT = {
    sample:
      "The questions of the teacher's sample document, in its order. The real exam does not " +
      "reuse them: sit it cold to see where you stand.",
    bank:
      `${shape.mcq} multiple choice and ${shape.open} open questions spread across the modules, ` +
      "drawn when you start. Your weak spots and the questions you have not tried come first, " +
      "and no question appears twice.",
  };

  const present = (ids) => ids.map(SD.data.question).filter(Boolean);

  // The teacher's paper sat a second time uses variants, so a better score is not just memory.
  const isResit = (paper) => paper.id === SD.exam.SAMPLE && SD.exam.lastDone(SD.store.get().exams, paper.id) !== null;

  // The questions of the sitting that starts now.
  function draw(paper, now) {
    if (!paper.questions) return SD.exam.buildBank(SD.data.bank, SD.store.get().q, SD.util.hashString(String(now)));
    if (!isResit(paper)) return paper.questions;
    const sample = SD.data.module("sample-paper");
    const originals = present(paper.questions);
    const variants = sample.questions.filter((q) => q.origin === "teacher-variant");
    return SD.exam.resit(originals, variants, SD.store.get().q, SD.util.hashString(String(now)));
  }

  const totalMarks = (qs) => qs.reduce((sum, q) => sum + SD.exam.marksOf(q), 0);
  const scoreText = (e) =>
    `${e.score}/${e.max} · ${SD.util.percent(e.score, e.max)}%` + (e.to_mark ? `, ${e.to_mark} to mark` : "");

  function runningNote(rec, paperId) {
    const left = SD.util.countdown(SD.exam.timeLeft(rec, Date.now()));
    const other = paperId !== null && paperId !== rec.paper;
    return h(
      "div",
      { class: "note exam-running" },
      h("p", { class: "label", text: "In progress" }),
      h("p", {
        text: other
          ? `${rec.title} is in progress, with ${left} left. Hand it in before you start another paper.`
          : `${rec.title} is in progress, with ${left} left. The clock runs whether or not the paper is open.`,
      }),
      SD.ui.linkButton("Return to the paper", SD.route.href("exam", "attempt", rec.id), "primary"),
    );
  }

  // ---- #exam

  function paperRow(paper, exams) {
    const qs = paper.questions ? present(paper.questions) : present(SD.exam.buildBank(SD.data.bank, {}, 0));
    const size = paper.questions
      ? `${SD.util.plural(qs.length, "question")} · ${SD.util.plural(totalMarks(qs), "mark")}`
      : SD.util.plural(qs.length, "question");
    const last = SD.exam.lastDone(exams, paper.id);
    const first = SD.exam.firstDone(exams, paper.id);
    return h(
      "li",
      {},
      h(
        "a",
        { class: "paper-row", href: SD.route.href("exam", paper.id) },
        h("span", { class: "label paper-kind", text: KIND[paper.kind] || paper.kind }),
        h("span", { class: "paper-title", text: paper.title }),
        h("span", {
          class: "paper-about",
          text: paper.intro_html ? SD.dom.excerpt(paper.intro_html, 170, true) : ABOUT[paper.kind],
        }),
        h("span", { class: "paper-meta", text: `${size} · ${paper.minutes} min` }),
        h("span", {
          class: "paper-last",
          text: !last
            ? "Not sat yet"
            : first !== last
              ? `First ${first.score}/${first.max} · last ${scoreText(last)}`
              : `Last: ${scoreText(last)}`,
        }),
      ),
    );
  }

  function attemptsList(exams) {
    if (exams.length === 0) {
      return SD.ui.empty(
        "No papers sat yet.",
        "Start with the teacher's sample paper, cold: it shows where you stand before you revise.",
        SD.ui.linkButton("Open the sample paper", SD.route.href("exam", SD.exam.SAMPLE), "primary"),
      );
    }
    return h(
      "ul",
      { class: "attempts" },
      SD.exam.newestFirst(exams).map((e) =>
        h(
          "li",
          {},
          h(
            "a",
            { class: "attempt-row", href: SD.route.href("exam", "attempt", e.id) },
            h("span", { class: "attempt-date", text: SD.util.dateTimeLabel(e.started) }),
            h("span", { class: "attempt-paper", text: e.title }),
            h("span", {
              class: "attempt-score",
              text: e.status === "running" ? "in progress" : scoreText(e),
            }),
            e.status === "done"
              ? h(
                  "span",
                  { class: "attempt-line" },
                  SD.ui.pytestLine(
                    SD.scoring.pytestSummary({
                      passed: e.passed,
                      failed: e.failed,
                      toMark: e.to_mark,
                      ms: e.used_ms,
                    }),
                  ),
                  e.timed_out ? h("span", { class: "fine", text: "Time ran out." }) : null,
                )
              : null,
          ),
        ),
      ),
    );
  }

  function chooser(root, message) {
    const exams = SD.store.get().exams;
    const live = SD.exam.running(exams);
    const day = SD.util.dateTimeLabel(Date.parse(SD.data.meta.exam.date));
    root.append(
      h(
        "div",
        { class: "page exam-home" },
        h("h1", { text: "Exam" }),
        h("p", {
          class: "lead",
          text:
            `Sit a paper the way you will on ${day}: one hour, closed book, no feedback until you ` +
            "hand in. Then mark it and read the reasoning behind every answer.",
        }),
        message ? h("p", { class: "notice", text: message }) : null,
        live ? runningNote(live, null) : null,
        h("h2", { text: "Papers" }),
        h("ul", { class: "paper-list" }, SD.exam.catalogue(SD.data).map((p) => paperRow(p, exams))),
        h("h2", { text: "Your attempts" }),
        attemptsList(exams),
      ),
    );
    return { title: "Exam", resume: "Exam papers", live: true };
  }

  // ---- #exam.<paper>: the rules, as on the day

  function rulesFor(paper, count) {
    const pace = paper.kind === "sample" ? `a fair pace for ${SD.util.plural(count, "question")}` : "as on the day";
    return [
      [
        "Time.",
        `${paper.minutes} minutes, ${pace}. The clock starts when you press Start and keeps running ` +
          "if you leave this page or reload it. At 0:00 the paper is handed in as it stands. A paper " +
          "with nothing answered is not recorded.",
      ],
      [
        "Closed book.",
        "On the day you write with pen on paper, with no notes and no devices. Close the slides and " +
          "other tabs before you start; the page drops its menus while the paper is open. Write the open " +
          "answers on paper if you can: tick “Written on paper” on each one and mark them yourself " +
          "after you hand in. Type them only if you cannot.",
      ],
      [
        "Multiple choice has no penalty.",
        "A wrong answer costs nothing, so answer every question, even when you are unsure.",
      ],
      [
        "Each open question takes 5–8 lines.",
        "Write prose across its numbered parts. The estimate under each answer counts handwritten " +
          "lines of about 60 characters.",
      ],
      [
        "You will not write code.",
        "You read code, tool output or a diff and say what it does, what is wrong, or how you would " +
          "change it, in words. Judgement, not memorised flags.",
      ],
      [
        "No feedback until you hand in.",
        "Flag a question to come back to it. The bar shows which questions are answered, flagged or blank.",
      ],
      [
        "Marking.",
        "Multiple choice is marked when you hand in, one mark each. You then mark each open answer " +
          "against its rubric and read the reasoning for every question. Wrong answers join your weak spots.",
      ],
    ];
  }

  function facts(paper, qs) {
    const counts = SD.exam.typeCounts(qs);
    const split = [
      counts.mcq ? `${counts.mcq} multiple choice` : null,
      counts.open ? `${counts.open} open` : null,
    ].filter(Boolean);
    const fact = (term, value, note) =>
      h(
        "div",
        { class: "fact" },
        h("dt", { class: "label", text: term }),
        h("dd", {}, h("span", { class: "fact-value", text: value }), h("span", { class: "fine", text: note })),
      );
    return h(
      "dl",
      { class: "paper-facts" },
      fact("Questions", String(qs.length), split.join(" + ")),
      paper.questions ? fact("Marks", String(totalMarks(qs)), "1 per multiple choice") : null,
      fact("Time", `${paper.minutes} min`, "count-down, can be hidden"),
    );
  }

  function rules(root, paper) {
    const live = SD.exam.running(SD.store.get().exams);
    const qs = present(paper.questions || SD.exam.buildBank(SD.data.bank, {}, 0));
    const start = () => {
      // Another tab or a double click may have started a sitting since this page was drawn.
      if (SD.exam.running(SD.store.get().exams)) {
        SD.router.refresh();
        return;
      }
      const now = Date.now();
      const rec = SD.exam.start(paper, present(draw(paper, now)), now);
      SD.store.saveExam(rec);
      SD.router.go(SD.route.build("exam", "attempt", rec.id));
    };
    let action = null;
    if (live) action = runningNote(live, paper.id);
    else if (qs.length === 0) {
      action = SD.ui.empty(
        "There are no questions to draw yet.",
        "The bank fills as the modules are written. Practise what exists meanwhile.",
        SD.ui.linkButton("Go to Practice", "#practice", "primary"),
      );
    } else {
      action = h(
        "div",
        { class: "actions" },
        SD.ui.button(`${START[paper.kind] || `Start ${paper.title}`} (${paper.minutes} min)`, {
          kind: "primary",
          onClick: start,
        }),
        SD.ui.linkButton("All papers", "#exam", "quiet"),
      );
    }
    root.append(
      h(
        "div",
        { class: "page exam-rules" },
        SD.ui.crumbs([["Exam", "#exam"], [paper.title]]),
        h("p", { class: "label", text: KIND[paper.kind] || paper.kind }),
        h("h1", { text: paper.title }),
        paper.intro_html
          ? h("div", { class: "prose lead", html: paper.intro_html })
          : h("p", { class: "lead", text: ABOUT[paper.kind] }),
        isResit(paper)
          ? h("p", {
              class: "note note-exam",
              text:
                "You have sat these nine questions already, so this sitting swaps each for a variant of " +
                "the same shape. A better score now shows what you understand, not what you remember.",
            })
          : null,
        facts(paper, qs),
        SD.store.storageMode() === "local"
          ? null
          : h("p", {
              class: "notice",
              text:
                "This browser is not saving progress, so a sitting cannot resume after a reload. " +
                "Keep the page open for the whole paper.",
            }),
        h("h2", { text: "The rules, as on the day" }),
        h(
          "ul",
          { class: "rules" },
          rulesFor(paper, qs.length).map(([lead, text]) => h("li", {}, h("strong", { text: lead }), " ", text)),
        ),
        action,
      ),
    );
    return { title: paper.title };
  }

  SD.router.register("exam", {
    render({ root, args }) {
      SD.examPaper.settle();
      const [first, second] = args;
      if (!first) return chooser(root, null);
      if (first === "attempt") {
        const rec = SD.store.get().exams.find((e) => e.id === second);
        if (rec?.status === "discarded") {
          return chooser(root, "That paper was discarded, so nothing from it was recorded.");
        }
        if (!rec) return chooser(root, "That attempt is not saved on this device. Your attempts are listed below.");
        return rec.status === "running" ? SD.examPaper.render(root, rec) : SD.examResults.render(root, rec);
      }
      const paper = SD.exam.catalogue(SD.data).find((p) => p.id === first);
      if (!paper) return chooser(root, `There is no paper called "${first}" in this build yet. Choose one below.`);
      return rules(root, paper);
    },
  });
})();
