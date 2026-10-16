// The answer paper (#exam.attempt.<id> while the sitting runs): every question on one scrolling
// sheet with its number in the margin; a sticky bar with the count-down (it can be hidden), the
// warnings at 10 and 5 minutes and the question navigator (closed until asked for); a flag on every
// question and, on open ones, "Written on paper"; every answer saved as it changes, so a reload
// resumes with the right time left; and the hand-in step at the end of the paper (or throwing the
// sitting away). While the paper is open the shell drops its navigation (see shell.js). At 0:00
// the paper is handed in as it stands.
SD.examPaper = (() => {
  const { h } = SD.dom;
  const STATE_TEXT = { full: "answered", partial: "partly answered", blank: "blank" };
  const TICK_MS = 250;

  // Hand a sitting in: mark it, record every question marked so far in progress (wrong ones
  // become weak spots) and save it. Open answers are recorded when the student marks them. A
  // sitting with nothing answered is thrown away instead: it says nothing about the student.
  // Handing in is idempotent: the paper's own tick and the shell's settle() can both reach 0:00 in
  // the same moment, and only the first may record the answers.
  function handIn(record, timedOut, now = Date.now()) {
    const stored = SD.store.get().exams.find((e) => e.id === record.id);
    if (stored && stored.status !== "running") return stored;
    const questions = SD.exam.questionsOf(record, SD.data.question);
    if (SD.exam.untouched(record, questions)) return discard(record, now);
    const done = SD.exam.withTotals(SD.exam.finish(record, now, timedOut), questions);
    const marked = SD.exam.mark(questions, done).results.filter((r) => r.status !== "mark");
    SD.store.update("q", (s) => {
      for (const r of marked) s.q[r.qid] = SD.progress.record(s.q[r.qid], r.status === "pass", null, now);
    });
    const saved = { ...done, recorded: marked.map((r) => r.qid) };
    SD.store.saveExam(saved);
    return saved;
  }

  // Throw a sitting away: nothing is recorded. A stub stays so that a copy synced from another
  // device cannot bring it back.
  function discard(record, now = Date.now()) {
    const gone = SD.exam.discard(record, now);
    SD.store.saveExam(gone);
    return gone;
  }

  // Hand in every sitting whose time ran out while no one was looking at the paper.
  function settle(now = Date.now()) {
    for (const rec of SD.store.get().exams.filter((e) => SD.exam.expired(e, now))) handIn(rec, true, now);
  }

  function legend() {
    const sample = (cls, text) =>
      h("span", { class: "legend-item" }, h("span", { class: `nav-cell nav-sample ${cls}` }), text);
    return h(
      "p",
      { class: "nav-legend", "aria-hidden": "true" },
      sample("is-full", "answered"),
      sample("is-partial", "partly"),
      sample("", "blank"),
      sample("is-flagged", "flagged"),
    );
  }

  function render(root, record) {
    let rec = record;
    let finished = false;
    let navOpen = false;
    let confirming = null; // "handin" | "discard": pressed once, waiting for the second press
    const questions = SD.exam.questionsOf(rec, SD.data.question);
    const total = questions.length;
    const qLabel = (i) => `Q${i + 1}`;
    const isFlagged = (q) => rec.flags.includes(q.id);
    const onPaper = (q) => rec.paper_answers.includes(q.id);
    const stateOf = (q) => SD.exam.answerState(q, rec.answers[q.id], onPaper(q));
    const save = () => SD.store.saveExam(rec);
    const html = document.documentElement;

    // ---- the bar: time left, warnings, navigator toggle, hand in
    const time = h("span", { class: "exam-time", role: "timer", "aria-labelledby": "exam-time-label" });
    const timeOff = h("span", { class: "exam-time-off", text: "hidden" });
    const hideButton = h("button", { type: "button", class: "link-btn exam-hide", onclick: toggleTime });
    const warn = h("p", { class: "exam-warn", hidden: true });
    const navCount = h("span", { class: "exam-nav-count" });
    const navToggle = h(
      "button",
      {
        type: "button",
        class: "btn btn-secondary exam-nav-toggle",
        "aria-controls": "exam-nav",
        onclick: () => setNav(!navOpen),
      },
      "Questions ",
      navCount,
    );
    const cells = questions.map((_, i) =>
      h("button", { type: "button", class: "nav-cell", onclick: () => jump(i) }, String(i + 1)),
    );
    const nav = h(
      "nav",
      { class: "exam-nav", id: "exam-nav", "aria-label": "Questions" },
      h("div", { class: "nav-cells" }, cells),
      legend(),
    );
    const bar = h(
      "div",
      { class: "exam-bar" },
      h(
        "div",
        { class: "exam-bar-row" },
        h(
          "p",
          { class: "exam-clock" },
          h("span", { class: "label", id: "exam-time-label", text: "Time left" }),
          time,
          timeOff,
          hideButton,
        ),
        warn,
        h(
          "div",
          { class: "exam-bar-end" },
          navToggle,
          SD.ui.button("Hand in", { kind: "primary", onClick: showHandIn }),
        ),
      ),
      nav,
    );

    // ---- the paper and the hand-in step
    const sheets = h("div", { class: "exam-sheets" });
    const summary = h("div", { class: "handin-summary" });
    const handInTitle = h("h2", { id: "handin-title", tabindex: "-1", text: "Hand in" });
    const handInButton = SD.ui.button("Hand in the paper", { kind: "primary", onClick: pressHandIn });
    const keepButton = SD.ui.button("Keep working", { kind: "secondary", onClick: () => setConfirming(null) });
    const discardButton = SD.ui.button("Discard this sitting", { kind: "quiet", onClick: pressDiscard });
    const handInBox = h(
      "section",
      { class: "handin", "aria-labelledby": "handin-title" },
      handInTitle,
      summary,
      h("div", { class: "actions" }, handInButton, keepButton, discardButton),
    );
    const savingNotice =
      SD.store.storageMode() === "local"
        ? null
        : h("p", {
            class: "notice",
            text:
              "This browser is not saving: do not reload or close this page, because the sitting cannot " +
              "resume. Your answers are kept only while the page stays open.",
          });
    root.append(
      h(
        "div",
        { class: "page exam-sitting" },
        h(
          "header",
          { class: "exam-head" },
          h("p", { class: "label", text: "Answer paper" }),
          h("h1", { text: rec.title }),
          h("p", {
            class: "meta-line",
            text:
              `${SD.util.plural(total, "question")} · ${SD.util.plural(rec.max, "mark")} · ` +
              `${rec.minutes} minutes · started ${SD.util.dateTimeLabel(rec.started)}`,
          }),
          h("p", {
            class: "fine",
            text:
              "Multiple choice has no penalty: answer every question. Each open question takes " +
              "5–8 lines of prose across its parts. On the day you write them on paper: tick " +
              "“Written on paper” and mark them yourself after you hand in. Nothing is marked until then.",
          }),
          savingNotice,
        ),
        bar,
        sheets,
        handInBox,
      ),
    );

    // Mounted once the sheets are in the page, so restored answers size their lined areas.
    const items = questions.map((q, i) => {
      const slot = h("div", { class: "exam-q" });
      sheets.append(slot);
      const controller = SD.q.mount(slot, q, {
        mode: "exam",
        number: qLabel(i),
        meta: false,
        answer: rec.answers[q.id],
        onChange: (answer) => {
          rec = { ...rec, answers: { ...rec.answers, [q.id]: answer } };
          save();
          paint(i);
        },
      });
      const flag = h(
        "button",
        { type: "button", class: "seg-btn exam-flag", "aria-pressed": "false", onclick: () => toggleFlag(i) },
        "Flag for review",
      );
      const paper =
        q.type === "open"
          ? h(
              "button",
              { type: "button", class: "seg-btn exam-paper-toggle", "aria-pressed": "false", onclick: () => togglePaper(i) },
              "Written on paper",
            )
          : null;
      controller.el.tabIndex = -1;
      controller.el.append(
        h(
          "div",
          { class: "exam-q-foot" },
          h("span", { class: "exam-q-tools" }, flag, paper),
          h("span", { class: "exam-q-marks", text: SD.util.plural(SD.exam.marksOf(q), "mark") }),
        ),
      );
      return { q, controller, flag, paper };
    });

    function paintCell(i) {
      const { q, flag, paper } = items[i];
      const state = stateOf(q);
      const flagged = isFlagged(q);
      cells[i].classList.toggle("is-full", state === "full");
      cells[i].classList.toggle("is-partial", state === "partial");
      cells[i].classList.toggle("is-flagged", flagged);
      cells[i].setAttribute("aria-label", `Question ${i + 1}: ${STATE_TEXT[state]}${flagged ? ", flagged" : ""}`);
      flag.setAttribute("aria-pressed", String(flagged));
      if (paper) paper.setAttribute("aria-pressed", String(onPaper(q)));
    }

    function jumpList(title, indexes) {
      if (indexes.length === 0) return null;
      return h(
        "p",
        { class: "handin-line" },
        h("span", { class: "handin-key", text: title }),
        indexes.map((i) =>
          h("button", { type: "button", class: "link-btn q-jump", onclick: () => jump(i), text: qLabel(i) }),
        ),
      );
    }

    const where = (test) => items.map((item, i) => (test(item.q) ? i : -1)).filter((i) => i >= 0);
    const unfinished = () => where((q) => stateOf(q) !== "full").length;

    function paintSummary() {
      const blank = where((q) => stateOf(q) === "blank");
      const partial = where((q) => stateOf(q) === "partial");
      const flagged = where(isFlagged);
      const answered = total - blank.length;
      navCount.textContent = `${answered}/${total}`;
      if (confirming === "handin" && unfinished() === 0) confirming = null;
      summary.replaceChildren();
      SD.dom.append(summary, [
        h("p", { class: "handin-count", text: `${answered} of ${total} questions answered.` }),
        jumpList("Blank", blank),
        jumpList("Partly answered", partial),
        jumpList("Flagged for review", flagged),
        h("p", {
          class: "fine",
          text: blank.length
            ? "A blank scores nothing. A guess at a multiple-choice question, or a few lines on an open one, might."
            : "Every question has an answer. Handing in ends the paper: answers cannot change after that.",
        }),
      ]);
      paintConfirm();
    }

    // The two-step buttons: a first press only asks, a second one acts.
    function paintConfirm() {
      const n = unfinished();
      handInButton.textContent =
        confirming === "handin"
          ? `Hand in with ${n} unfinished: press again to confirm`
          : "Hand in the paper";
      keepButton.hidden = confirming === null;
      discardButton.textContent =
        confirming === "discard" ? "Discard: press again. Nothing will be recorded" : "Discard this sitting";
    }

    function setConfirming(next) {
      confirming = next;
      paintConfirm();
      if (next === "handin") {
        SD.dom.announce(`${unfinished()} questions are not finished. Press Hand in again to confirm.`);
      } else if (next === "discard") {
        SD.dom.announce("Press Discard again to throw this sitting away. Nothing will be recorded.");
      }
    }

    function pressHandIn() {
      if (unfinished() > 0 && confirming !== "handin") setConfirming("handin");
      else finish(false);
    }

    function pressDiscard() {
      if (confirming !== "discard") {
        setConfirming("discard");
        return;
      }
      finished = true;
      window.clearInterval(timer);
      discard(rec);
      SD.dom.announce("The sitting was discarded. Nothing was recorded.");
      SD.router.go("exam");
    }

    function paint(i) {
      paintCell(i);
      paintSummary();
    }

    function toggleFlag(i) {
      const { q } = items[i];
      const flags = isFlagged(q) ? rec.flags.filter((id) => id !== q.id) : [...rec.flags, q.id];
      rec = { ...rec, flags };
      save();
      paint(i);
    }

    function togglePaper(i) {
      const { q, controller } = items[i];
      const list = onPaper(q) ? rec.paper_answers.filter((id) => id !== q.id) : [...rec.paper_answers, q.id];
      rec = { ...rec, paper_answers: list };
      save();
      controller.el.classList.toggle("is-on-paper", onPaper(q));
      paint(i);
    }

    // The sticky bar's height goes to the page's scroll padding, so a focused field or a jump
    // target is never left under it.
    function stickyHeight() {
      html.style.setProperty("--sticky-extra", `${bar.offsetHeight}px`);
    }

    function setNav(open) {
      navOpen = open;
      nav.hidden = !open;
      navToggle.setAttribute("aria-expanded", String(open));
      stickyHeight();
    }

    function bringIntoView(el, focusEl) {
      if (navOpen) setNav(false);
      el.scrollIntoView({ block: "start" });
      focusEl.focus({ preventScroll: true });
    }

    function jump(i) {
      const { el } = items[i].controller;
      bringIntoView(el, el);
    }

    function showHandIn() {
      bringIntoView(handInBox, handInTitle);
    }

    function paintTime() {
      const hidden = Boolean(SD.store.get().prefs.timerHidden);
      time.hidden = hidden;
      timeOff.hidden = !hidden;
      hideButton.textContent = hidden ? "Show" : "Hide";
      hideButton.setAttribute("aria-label", hidden ? "Show the time left" : "Hide the time left");
      stickyHeight();
    }

    function toggleTime() {
      SD.store.setPref("timerHidden", !SD.store.get().prefs.timerHidden);
      paintTime();
    }

    // The warning stays inline in the bar (shown even with the time hidden) and is read out once.
    let level = SD.exam.warning(SD.exam.timeLeft(rec, Date.now()));
    function paintWarning() {
      warn.hidden = level === 0;
      warn.textContent = level ? `Last ${level} minutes` : "";
      bar.classList.toggle("is-warn", level === 10);
      bar.classList.toggle("is-urgent", level === 5);
      stickyHeight();
    }

    function tick() {
      const left = SD.exam.timeLeft(rec, Date.now());
      if (left <= 0) {
        finish(true);
        return;
      }
      time.textContent = SD.util.clock(left);
      const next = SD.exam.warning(left);
      if (next !== level) {
        level = next;
        paintWarning();
        SD.dom.announce(`${level} minutes left.`);
      }
    }

    function finish(timedOut) {
      if (finished) return;
      finished = true;
      window.clearInterval(timer);
      const saved = handIn(rec, timedOut);
      const gone = saved.status === "discarded";
      SD.dom.announce(
        gone
          ? "Nothing was answered, so the paper was not recorded."
          : timedOut
            ? "Time is up. Your paper has been handed in."
            : "Your paper has been handed in.",
      );
      SD.router.refresh();
    }

    // Handed in on another device: the synced record says so; show the results.
    const stop = SD.store.subscribe((state, kind) => {
      if (kind !== "all" || finished) return;
      const there = state.exams.find((e) => e.id === rec.id);
      if (there && there.status !== "running") {
        finished = true;
        SD.router.refresh();
      }
    });

    items.forEach((item, i) => {
      item.controller.el.classList.toggle("is-on-paper", onPaper(item.q));
      paintCell(i);
    });
    paintSummary();
    paintTime();
    paintWarning();
    setNav(false);
    // The route hands in a sitting that is already out of time before it gets here.
    time.textContent = SD.util.clock(SD.exam.timeLeft(rec, Date.now()));
    const timer = window.setInterval(tick, TICK_MS);
    const watch = typeof ResizeObserver === "function" ? new ResizeObserver(stickyHeight) : null;
    if (watch) watch.observe(bar);

    return {
      title: rec.title,
      resume: `${rec.title} (in progress)`,
      onKey(event) {
        const item = items.find(({ controller }) => controller.el.contains(document.activeElement));
        return item ? item.controller.key(event) : false;
      },
      cleanup() {
        window.clearInterval(timer);
        stop();
        if (watch) watch.disconnect();
        html.style.removeProperty("--sticky-extra");
      },
    };
  }

  return { render, handIn, settle };
})();
