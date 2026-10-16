// Home (#home): the countdown, the exam in two lines, where to continue, today's plan block,
// weak spots, due cards, the last paper, and the module check list.
(() => {
  const { h } = SD.dom;

  // Where "Continue" leads: back into a paper that is running, else the last place visited.
  function continueLink() {
    const state = SD.store.get();
    const live = SD.exam.running(state.exams);
    if (live) {
      const left = SD.util.countdown(SD.exam.timeLeft(live, Date.now()));
      return SD.ui.linkButton(
        `Return to ${live.title}: ${left} left`,
        SD.route.href("exam", "attempt", live.id),
        "primary",
      );
    }
    return state.last ? SD.ui.linkButton(`Continue: ${state.last.label}`, "#" + state.last.route, "primary") : null;
  }

  function head() {
    const meta = SD.data.meta.exam;
    const exam = SD.stats.exam();
    const resume = continueLink();
    return h(
      "header",
      { class: "home-head" },
      h("p", { class: "label", text: "The mid-term" }),
      exam.state === "before"
        ? h("h1", { class: "home-title" }, h("span", { class: "count", text: exam.text }), " to go")
        : h("h1", { class: "home-title", text: exam.text }),
      h("p", {
        class: "exam-line",
        text:
          `${SD.util.dateTimeLabel(Date.parse(meta.date), SD.util.EXAM_TZ)} · room ${meta.room} · ` +
          `${meta.minutes} minutes · ${meta.weight} of the course mark`,
      }),
      h("p", {
        class: "exam-line exam-line-2",
        text:
          `Pen and paper, closed book · multiple choice with no penalty · open answers ` +
          `of 5–8 lines · sessions ${meta.sessions} · no code writing`,
      }),
      resume ? h("p", { class: "home-continue" }, resume) : null,
    );
  }

  // The plan after the exam has been sat: nothing left to do but look back.
  function afterExam() {
    return h(
      "section",
      { class: "home-block", "aria-labelledby": "after-title" },
      h("h2", { id: "after-title", text: "After the exam" }),
      h("p", {
        text: "The mid-term has taken place. Your papers, answers and weak spots stay here to read back.",
      }),
      h(
        "div",
        { class: "actions" },
        SD.ui.linkButton("Your papers", "#exam"),
        SD.ui.linkButton("Weak spots", "#practice.weak", "quiet"),
      ),
    );
  }

  // Today's block of the plan, with what is left from earlier days underneath.
  function today() {
    if (SD.stats.exam().state === "after") return { paint() {}, el: afterExam() };
    const days = SD.data.plan;
    const index = SD.planner.todayIndex(days, SD.util.dateKey(Date.now(), SD.util.EXAM_TZ));
    if (index < 0) return null;
    const day = days[index];
    const next = days[index + 1] || null;
    const behind = SD.planner
      .missed(days, SD.store.get().plan, index)
      .map(({ day: d, item }) => ({ ...item, dayLabel: d.label }));
    const count = h("span", { class: "fine" });
    const finished = h("p", { class: "day-done", hidden: true });
    const carried = h("summary", { class: "missed-head" });
    const paint = () => {
      const p = SD.planner.dayProgress(day, SD.store.get().plan);
      count.textContent = `${p.done} of ${p.total} done`;
      finished.hidden = p.done < p.total;
      finished.replaceChildren(
        "Done for today.",
        next ? ` Next: ${next.label}, ${next.title}. ` : " ",
        next ? h("a", { href: "#plan", text: "See the plan" }) : null,
      );
      const left = behind.filter((item) => !SD.store.get().plan[item.id]?.done).length;
      carried.textContent = left ? `From earlier days: ${left} not done` : "From earlier days: all done";
    };
    paint();
    return {
      paint,
      el: h(
        "section",
        { class: "home-block", "aria-labelledby": "today-title" },
        h(
          "div",
          { class: "block-head" },
          h("h2", { id: "today-title" }, `Today · ${day.label}`, day.when ? `, ${day.when.toLowerCase()}` : ""),
          count,
        ),
        h("p", { class: "day-title", text: day.title }),
        day.note_html ? h("div", { class: "prose fine-prose", html: day.note_html }) : null,
        SD.ui.planItems(day.items),
        finished,
        behind.length
          ? h("details", { class: "missed", open: true }, carried, SD.ui.planItems(behind))
          : null,
        h("p", { class: "link-line" }, h("a", { href: "#plan", text: "The whole eight-day plan" })),
      ),
    };
  }

  function figures() {
    const weak = SD.stats.weakIds().length;
    const cards = SD.stats.cards();
    const exam = SD.stats.lastExam();
    if (weak === 0 && cards.due === 0 && !exam) {
      // Day one: three zeros say nothing, so one line says where to start.
      return h(
        "div",
        { class: "figures-none" },
        h("p", {
          class: "fine",
          text: `Nothing recorded yet: no weak spots, ${SD.util.plural(cards.fresh, "flashcard")} not seen, no paper sat.`,
        }),
        h(
          "p",
          { class: "link-line" },
          h("a", { href: "#exam.sample", text: "Sit the sample paper, cold" }),
          h("a", { href: "#cards", text: "Start the flashcards" }),
        ),
      );
    }
    const figure = (label, value, text, link) =>
      h(
        "div",
        { class: "figure" },
        h("p", { class: "label", text: label }),
        value,
        h("p", { class: "fine", text }),
        link,
      );
    return h(
      "section",
      { class: "figures", "aria-label": "Progress" },
      figure(
        "Weak spots",
        h("p", { class: "figure-value", text: String(weak) }),
        "Answered wrong, or right but guessed.",
        weak ? h("a", { href: "#practice.weak", text: "Practise weak spots" }) : null,
      ),
      figure(
        "Flashcards",
        h("p", { class: "figure-value", text: String(cards.due) }),
        `due now, and ${cards.fresh} not seen yet.`,
        h("a", { href: "#cards", text: "Review flashcards" }),
      ),
      figure(
        "Last paper",
        exam
          ? SD.ui.pytestLine(
              SD.scoring.pytestSummary({
                passed: exam.passed,
                failed: exam.failed,
                toMark: exam.to_mark,
                ms: exam.used_ms ?? null,
              }),
            )
          : h("p", { class: "figure-value figure-none", text: "None yet" }),
        exam
          ? `${exam.title}, ${SD.util.dateTimeLabel(exam.ended)}.`
          : "Start with the teacher's sample paper, cold.",
        h("a", { href: exam ? "#exam" : "#exam.sample", text: exam ? "All papers" : "Sit the sample paper" }),
      ),
    );
  }

  function checks() {
    return h(
      "section",
      { class: "home-block", "aria-labelledby": "checks-title" },
      h(
        "div",
        { class: "block-head" },
        h("h2", { id: "checks-title", text: "Module checks" }),
        h("span", {
          class: "fine",
          text: "A section passes at 80% right with 3 answered (all of them, in a smaller section) and fails below 60%.",
        }),
      ),
      h(
        "ul",
        { class: "checks" },
        SD.data.modules.map((mod) => {
          const st = SD.stats.module(mod.id);
          let detail = "not tried";
          if (st.status === "fail") detail = `${st.fail} of ${st.total} sections failing`;
          else if (st.pass > 0) detail = `${st.pass} of ${st.total} sections passing`;
          else if (st.status === "part") detail = "in progress";
          return h(
            "li",
            {},
            h(
              "a",
              { class: "check-row", href: SD.route.href("learn", mod.id) },
              SD.ui.statusMark(st.status),
              h("span", { class: "check-code", text: SD.ui.moduleCode(mod) }),
              h("span", { class: "check-title" }, mod.title, mod.predicted ? SD.ui.chip("predicted", "warn") : null),
              h("span", { class: "check-detail", text: detail }),
            ),
          );
        }),
      ),
    );
  }

  SD.router.register("home", {
    render({ root }) {
      const block = today();
      root.append(h("div", { class: "page page-wide home" }, head(), block?.el, figures(), checks()));
      const stop = SD.store.subscribe((_, kind) => {
        if (kind === "plan" && block) block.paint();
      });
      return { title: "Home", cleanup: stop, live: true };
    },
  });
})();
