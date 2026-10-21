// Papers: the list, a paper's rules, a sitting (all questions on one page, a clock, no feedback
// until hand-in) and its results with the full review.
(() => {
  const { h } = CR.dom;
  const KIND_LABEL = { sample: "teacher's sample", realistic: "realistic", "worst-case": "worst case", beyond: "beyond" };

  function shape(paper) {
    const qs = CR.data.paperQuestions(paper);
    const mcq = qs.filter((q) => q.type === "mcq").length;
    const open = qs.filter((q) => q.type === "open").length;
    const marks = qs.reduce((sum, q) => sum + CR.scoring.marksOf(q), 0);
    return { qs, mcq, open, marks, text: `${mcq} multiple choice + ${open} open, ${marks} marks` };
  }

  function startPaper(paper) {
    const rec = CR.paper.start(paper, CR.data.paperQuestions(paper), Date.now());
    CR.store.savePaper(rec);
    CR.router.go(CR.route.build("sit", rec.id));
  }

  function lastLine(paperId) {
    const papers = CR.store.get().papers;
    const running = CR.paper.running(papers);
    if (running && running.paper === paperId) return "In progress";
    const last = CR.paper.lastDone(papers, paperId);
    if (!last) return "Not sat yet";
    return `Last: ${last.score}/${last.max} (${CR.util.percent(last.score, last.max)}%)${last.to_mark ? `, ${last.to_mark} to mark` : ""}`;
  }

  const notFound = (root, text) => {
    root.append(h("div", { class: "page" }, h("h1", { text: "Nothing at this address" }), h("p", { text }), h("p", {}, h("a", { href: "#paper", text: "All papers" }))));
    return { title: "Not found" };
  };

  // Hand a sitting in: every multiple-choice question and every blank open question is counted as an
  // attempt (so wrong ones reach the mistakes), the stop of this paper in the route is ticked, and
  // the finished record is saved and returned.
  function handIn(rec, timedOut) {
    const qs = rec.questions.map((id) => CR.data.question(id)).filter(Boolean);
    const now = Date.now();
    const done = CR.paper.handIn(rec, qs, now, timedOut);
    CR.store.update("q", (s) => done.outcomes.forEach((o) => CR.mistakes.record(s.q, o.qid, o.ok, now)));
    CR.store.savePaper(done.record);
    for (const stop of CR.data.stops) {
      if ((stop.kind === "paper" || stop.kind === "baseline") && stop.ref === rec.paper) CR.store.setDone(stop.id, true);
    }
    return done.record;
  }

  // A sitting whose time ran out while the page was closed is handed in when the page opens.
  // Returns true when one was handed in.
  function settle() {
    const now = Date.now();
    const late = CR.store.get().papers.filter((p) => p.status === "running" && CR.paper.expired(p, now));
    for (const rec of late) handIn(rec, true);
    return late.length > 0;
  }

  CR.papers = { settle };

  // ------------------------------------------------------------------ #paper

  function listView({ root }) {
    root.append(
      h(
        "div",
        { class: "page" },
        CR.ui.crumbs([["Route", "#home"], ["Papers"]]),
        h("h1", { text: "Papers" }),
        h("p", { class: "lead", text: "Sit a whole paper against the clock. Nothing is marked until you hand in; then every answer is explained and the open ones are marked against the rubric." }),
        h(
          "ul",
          { class: "paper-list" },
          CR.data.papers.map((p) => {
            const s = shape(p);
            return h(
              "li",
              {},
              h(
                "a",
                { class: "paper-row", href: CR.route.href("paper", p.id) },
                h("span", { class: "paper-kind label", text: KIND_LABEL[p.kind] || p.kind }),
                h("span", { class: "paper-title", text: p.title }),
                h("span", { class: "paper-last", text: lastLine(p.id) }),
                h("span", { class: "paper-meta", text: `${p.minutes} min · ${s.text}` }),
              ),
            );
          }),
        ),
      ),
    );
    return { title: "Papers" };
  }

  // ------------------------------------------------------------------ #paper.<id>

  function rulesView({ root, args }) {
    const paper = CR.data.paper(args[0]);
    if (!paper) return notFound(root, `There is no paper called "${args[0]}".`);
    const s = shape(paper);
    const papers = CR.store.get().papers;
    const running = CR.paper.running(papers);
    const mine = CR.paper.newestFirst(papers).filter((p) => p.paper === paper.id);
    const resume = running && running.paper === paper.id ? running : null;
    root.append(
      h(
        "div",
        { class: "page" },
        CR.ui.crumbs([["Route", "#home"], ["Papers", "#paper"], [paper.title]]),
        h("p", { class: "meta-line", text: KIND_LABEL[paper.kind] || paper.kind }),
        h("h1", { text: paper.title }),
        h("div", { class: "prose", html: paper.intro_html }),
        h(
          "dl",
          { class: "facts" },
          h("div", { class: "fact" }, h("dt", { class: "label", text: "Time" }), h("dd", { class: "figure-value", text: `${paper.minutes} min` })),
          h("div", { class: "fact" }, h("dt", { class: "label", text: "Questions" }), h("dd", { class: "figure-value", text: String(s.qs.length) }), h("dd", { class: "fine", text: `${s.mcq} multiple choice, ${s.open} open` })),
          h("div", { class: "fact" }, h("dt", { class: "label", text: "Marks" }), h("dd", { class: "figure-value", text: String(s.marks) })),
        ),
        h("h2", { text: "Rules" }),
        h(
          "ul",
          { class: "rules" },
          [
            "The clock starts when you press Start and keeps running if you leave the page. At 0:00 the paper is handed in for you.",
            "All questions are on one page. Nothing is marked until you hand in.",
            "Multiple choice has no penalty, so answer every one.",
            "Open answers: write them on paper, as on the day, and tick \"I wrote this on paper\"; or type them here. You mark them yourself against the rubric afterwards.",
            "No notes. No looking at the type pages.",
          ].map((t) => h("li", { text: t })),
        ),
        running && !resume
          ? h("p", { class: "notice" }, `${running.title} is still running. `, h("a", { href: CR.route.href("sit", running.id), text: "Go back to it" }))
          : null,
        h(
          "div",
          { class: "actions" },
          resume
            ? CR.ui.linkButton(`Resume (${CR.util.clock(CR.paper.timeLeft(resume, Date.now()))} left)`, CR.route.href("sit", resume.id), "primary")
            : CR.ui.button("Start the paper", { kind: "primary", onClick: () => startPaper(paper) }),
        ),
        mine.length
          ? [
              h("h2", { text: "Your sittings" }),
              h(
                "ul",
                { class: "attempts" },
                mine.map((p) =>
                  h(
                    "li",
                    {},
                    h(
                      "a",
                      { class: "attempt-row", href: CR.route.href("sit", p.id) },
                      h("span", { class: "attempt-date", text: CR.util.dateTimeLabel(p.started) }),
                      h("span", { class: "attempt-paper", text: p.status === "running" ? "In progress" : "Handed in" }),
                      h("span", { class: "attempt-score", text: p.status === "done" ? `${p.score}/${p.max}` : "" }),
                    ),
                  ),
                ),
              ),
            ]
          : null,
      ),
    );
    return { title: paper.title };
  }

  // ------------------------------------------------------------------ #sit.<id>: the paper itself

  function sitting(root, rec0) {
    let rec = rec0;
    const qs = rec.questions.map((id) => CR.data.question(id)).filter(Boolean);
    const persist = () => CR.store.savePaper(rec);
    const onPaperSet = () => new Set(rec.onpaper);
    const state = (q) => CR.paper.answerState(q, rec.answers[q.id], onPaperSet().has(q.id));

    function discardControl() {
      const holder = h("span", { class: "discard" });
      const idle = () => CR.dom.fill(holder, CR.ui.button("Throw this sitting away", { kind: "quiet", onClick: ask }));
      const ask = () =>
        CR.dom.fill(
          holder,
          h("span", { class: "fine", text: "Nothing will be recorded. " }),
          CR.ui.button("Throw it away", {
            kind: "secondary",
            onClick: () => {
              window.clearInterval(timer);
              CR.store.savePaper(CR.paper.discard(rec, Date.now()));
              CR.router.go(CR.route.build("paper", rec.paper));
            },
          }),
          CR.ui.button("Keep it", { kind: "quiet", onClick: idle }),
        );
      idle();
      return holder;
    }

    const clockEl = h("span", { class: "exam-time", role: "timer", "aria-live": "off" });
    const countEl = h("span", { class: "exam-count" });
    const confirm = h("div", { class: "exam-confirm", hidden: true });
    const bar = h("div", { class: "exam-bar" });
    const cells = qs.map((q, i) => {
      const cell = h("button", { type: "button", class: "nav-cell", onclick: () => jump(q.id), "aria-label": `Go to question ${i + 1}` }, String(i + 1));
      return { q, cell };
    });
    const sheets = new Map();

    function jump(qid) {
      const el = sheets.get(qid);
      if (!el) return;
      el.scrollIntoView({ block: "start" });
      el.focus({ preventScroll: true });
    }

    function paintNav() {
      let answered = 0;
      for (const { q, cell } of cells) {
        const st = state(q);
        if (st === "full") answered += 1;
        cell.classList.toggle("is-full", st === "full");
        cell.classList.toggle("is-partial", st === "partial");
      }
      countEl.textContent = `${answered} of ${qs.length} answered`;
    }

    function askHandIn() {
      const blank = qs.filter((q) => state(q) === "blank").length;
      CR.dom.fill(
        confirm,
        h("p", { class: "confirm-text", text: blank > 0 ? `Hand in now? ${CR.util.plural(blank, "question")} still blank. A blank multiple-choice answer scores nothing, and a guess costs nothing.` : "Hand in now? You cannot change your answers afterwards." }),
        h(
          "div",
          { class: "actions" },
          CR.ui.button("Hand in", { kind: "primary", onClick: () => finish(false) }),
          CR.ui.button("Keep going", { kind: "quiet", onClick: () => (confirm.hidden = true) }),
        ),
      );
      confirm.hidden = false;
      CR.dom.reveal(confirm);
    }

    const handButton = CR.ui.button("Hand in", { kind: "primary", onClick: askHandIn });
    CR.dom.fill(
      bar,
      h("div", { class: "exam-bar-row" }, h("p", { class: "exam-clock" }, h("span", { class: "label", text: "Time left" }), clockEl), countEl, h("div", { class: "exam-bar-end" }, handButton)),
      confirm,
    );
    const navCells = h("div", { class: "nav-cells exam-nav", role: "group", "aria-label": "Questions" }, cells.map((c) => c.cell));

    let timer = null;
    let lastWarn = 0;
    function tick() {
      const now = Date.now();
      if (CR.paper.expired(rec, now)) {
        finish(true);
        return;
      }
      const left = CR.paper.timeLeft(rec, now);
      clockEl.textContent = CR.util.clock(left);
      const w = CR.paper.warning(left);
      bar.classList.toggle("is-warn", w === 10);
      bar.classList.toggle("is-urgent", w === 5);
      if (w !== lastWarn && w > 0) CR.dom.announce(`${w} minutes left`);
      lastWarn = w;
    }

    function finish(timedOut) {
      window.clearInterval(timer);
      handIn(rec, timedOut);
      CR.router.refresh();
    }

    const list = h("div", { class: "exam-sheets" });
    qs.forEach((q, i) => {
      const holder = h("div", { class: "exam-item" });
      const c = CR.q.mount(holder, q, {
        mode: "exam",
        number: `Q${i + 1}`,
        meta: false,
        answer: rec.answers[q.id],
        onChange: (a) => {
          rec = { ...rec, answers: { ...rec.answers, [q.id]: a } };
          persist();
          paintNav();
        },
      });
      c.el.tabIndex = -1;
      sheets.set(q.id, c.el);
      if (q.type === "open") {
        holder.append(
          h(
            "label",
            { class: "onpaper" },
            h("input", {
              type: "checkbox",
              checked: rec.onpaper.includes(q.id),
              onchange: (e) => {
                const set = onPaperSet();
                if (e.target.checked) set.add(q.id);
                else set.delete(q.id);
                rec = { ...rec, onpaper: [...set] };
                holder.classList.toggle("is-on-paper", e.target.checked);
                persist();
                paintNav();
              },
            }),
            h("span", { text: "I wrote this on paper" }),
          ),
        );
        holder.classList.toggle("is-on-paper", rec.onpaper.includes(q.id));
      }
      list.append(holder);
    });

    root.append(
      h(
        "div",
        { class: "page-wide sitting" },
        h("div", { class: "exam-head" }, h("h1", { text: rec.title }), h("p", { class: "fine", text: "Answer here or on paper. Nothing is marked until you hand in." })),
        bar,
        navCells,
        list,
        h("div", { class: "exam-end" }, CR.ui.button("Hand in", { kind: "primary", onClick: askHandIn }), discardControl()),
      ),
    );
    paintNav();
    tick();
    timer = window.setInterval(tick, 1000);
    return {
      title: rec.title,
      cleanup() {
        window.clearInterval(timer);
      },
    };
  }

  // ------------------------------------------------------------------ results and review

  function results(root, rec0, crumbTrail) {
    let rec = rec0;
    const qs = rec.questions.map((id) => CR.data.question(id)).filter(Boolean);
    const headHolder = h("div", { class: "result-head" });
    const reviseHolder = h("div", { class: "revise-first" });
    const navHolder = h("div", { class: "nav-cells result-nav", role: "group", "aria-label": "Questions" });
    const sheets = new Map();

    function paintHeader() {
      const m = CR.paper.mark(qs, rec);
      const pct = CR.util.percent(m.score, m.max);
      CR.dom.fill(
        headHolder,
        h("p", { class: "figure-value score-big", text: `${m.score}/${m.max}` }),
        h("p", { class: "fine", text: `${pct}% of the marks${m.toMark ? `, with ${CR.util.plural(m.toMark, "open question")} still to mark` : ""}` }),
        CR.ui.pytestLine(CR.scoring.summary({ passed: m.passed, failed: m.failed, toMark: m.toMark, ms: rec.used_ms })),
        h("p", { class: "fine", text: rec.timed_out ? `Time ran out: handed in at ${rec.minutes}:00.` : `Handed in with ${CR.util.clock(rec.minutes * CR.util.MINUTE - rec.used_ms)} left.` }),
      );
      const lost = CR.paper.lostByType(m.results).filter((r) => CR.data.type(r.tid));
      CR.dom.fill(
        reviseHolder,
        lost.length
          ? [
              h("h2", { text: "Revise first" }),
              h("p", { class: "fine", text: "Where you lost the most marks, most first." }),
              h(
                "ul",
                { class: "revise-list" },
                lost.map((r) =>
                  h("li", {}, h("a", { href: CR.route.href("type", r.tid), text: CR.ui.typeLabel(r.tid) }), h("span", { class: "revise-where", text: `${r.lost} of ${r.max} ${r.max === 1 ? "mark" : "marks"} lost` })),
                ),
              ),
            ]
          : null,
      );
      CR.dom.fill(
        navHolder,
        m.results.map((r, i) =>
          h(
            "button",
            { type: "button", class: `nav-cell is-${r.status}`, onclick: () => jump(r.qid), "aria-label": `Question ${i + 1}: ${r.status === "pass" ? "right" : r.status === "fail" ? "wrong" : "to mark"}` },
            String(i + 1),
          ),
        ),
      );
    }

    function jump(qid) {
      const el = sheets.get(qid);
      if (!el) return;
      el.scrollIntoView({ block: "start" });
      el.focus({ preventScroll: true });
    }

    const list = h("div", { class: "exam-sheets" });
    qs.forEach((q, i) => {
      const holder = h("div", { class: "exam-item" });
      const onPaper = rec.onpaper.includes(q.id);
      const st = CR.paper.answerState(q, rec.answers[q.id], onPaper);
      const opts = { mode: "review", number: `Q${i + 1}`, meta: false, answer: rec.answers[q.id], record: false };
      if (q.type === "open") {
        Object.assign(opts, {
          ticks: rec.ticks[q.id],
          recorded: q.id in rec.marks,
          onPaper,
          markable: st !== "blank",
          onRecord: (r) => {
            const now = Date.now();
            const out = CR.paper.recordMark(rec, q, r.score, r.ticks, now);
            rec = CR.paper.withTotals(out.record, qs);
            CR.store.savePaper(rec);
            CR.store.update("q", (s) => {
              if (out.outcome.amend) CR.mistakes.amend(s.q, q.id, out.outcome.ok, now);
              else CR.mistakes.record(s.q, q.id, out.outcome.ok, now);
            });
            paintHeader();
          },
        });
      }
      const c = CR.q.mount(holder, q, opts);
      c.el.tabIndex = -1;
      sheets.set(q.id, c.el);
      list.append(holder);
    });

    const reviewStop = CR.data.stops.find((s) => s.kind === "review" && s.ref === rec.paper);
    const paper = CR.data.paper(rec.paper);
    root.append(
      h(
        "div",
        { class: "page-wide results" },
        CR.ui.crumbs(crumbTrail),
        h("h1", { text: `${rec.title}: result` }),
        headHolder,
        reviseHolder,
        h(
          "div",
          { class: "actions" },
          CR.ui.linkButton("Redo your mistakes", "#mistakes", "primary"),
          paper ? CR.ui.button("Sit this paper again", { kind: "secondary", onClick: () => startPaper(paper) }) : null,
          reviewStop
            ? CR.ui.button("Review done, go on", {
                kind: "secondary",
                onClick: () => {
                  CR.store.setDone(reviewStop.id, true);
                  const next = CR.clock.after(CR.data.stops, CR.store.get().done, reviewStop.id);
                  CR.router.go(next ? CR.route.stopRoute(next) : "home");
                },
              })
            : null,
        ),
        h("h2", { text: "Review" }),
        h("p", { class: "fine", text: "Every question with the reason for every option. Open answers: tick what your answer says, then record your mark. Recorded marks count in your score and in your mistakes." }),
        navHolder,
        list,
      ),
    );
    paintHeader();
    return { title: `${rec.title}: result` };
  }

  // ------------------------------------------------------------------ routes

  function sitView({ root, args }) {
    const rec = CR.store.get().papers.find((p) => p.id === args[0]);
    if (!rec || rec.status === "discarded") return notFound(root, "That sitting is not on this device.");
    const trail = [["Route", "#home"], ["Papers", "#paper"], [rec.title, CR.route.href("paper", rec.paper)], ["Result"]];
    if (rec.status === "running" && CR.paper.expired(rec, Date.now())) return results(root, handIn(rec, true), trail);
    if (rec.status === "running") return sitting(root, rec);
    return results(root, rec, trail);
  }

  function reviewView({ root, args }) {
    const paper = CR.data.paper(args[0]);
    if (!paper) return notFound(root, `There is no paper called "${args[0]}".`);
    const rec = CR.paper.lastDone(CR.store.get().papers, paper.id);
    if (!rec) {
      root.append(
        h(
          "div",
          { class: "page" },
          CR.ui.crumbs([["Route", "#home"], ["Papers", "#paper"], [`Review ${paper.title}`]]),
          h("h1", { text: `Review ${paper.title}` }),
          CR.ui.empty("Nothing to review yet", `You have not handed in ${paper.title}. Sit it first, then come back.`, CR.ui.linkButton(`Go to ${paper.title}`, CR.route.href("paper", paper.id), "primary")),
        ),
      );
      return { title: `Review ${paper.title}` };
    }
    return results(root, rec, [["Route", "#home"], ["Papers", "#paper"], [paper.title, CR.route.href("paper", paper.id)], ["Review"]]);
  }

  CR.router.register("paper", { nav: "papers", render: (ctx) => (ctx.args.length ? rulesView(ctx) : listView(ctx)) });
  CR.router.register("sit", { nav: "papers", render: sitView });
  CR.router.register("review", { nav: "papers", render: reviewView });
})();
