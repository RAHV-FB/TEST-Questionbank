// The practice runner: one question at a time from a list of ids, a session that survives a reload,
// and a summary with "redo the ones you missed". Used by a type's practice and by the mistakes.
CR.practice = (() => {
  const { h } = CR.dom;

  const known = (ids) => ids.filter((id) => CR.data.question(id));

  function resultRow(id, res) {
    const q = CR.data.question(id);
    const status = res === true ? "pass" : res === false ? "fail" : "none";
    const word = res === true ? "right" : res === false ? "wrong" : "skipped";
    return h(
      "li",
      { class: "result-item" },
      h(
        "a",
        { class: "result-row", href: CR.route.href("q", id, "review") },
        CR.ui.statusMark(status, word),
        h("span", { class: "result-text", text: CR.dom.excerpt(q.stem_html, 120) }),
      ),
    );
  }

  // opts: {key, ids() -> ids to start from, heading, crumbs, finish(): extra buttons for the summary,
  // emptyText}.
  function run(root, opts) {
    let sess = CR.store.session(opts.key);
    if (!sess || !sess.ids.every((id) => CR.data.question(id))) {
      sess = CR.mistakes.newSession(known(opts.ids()), Date.now());
      CR.store.startSession(opts.key, sess);
    }
    const holder = h("div", { class: "practice" });
    let ctrl = null;
    let ready = () => false;

    const save = (next, fresh = false) => {
      sess = next;
      if (fresh) CR.store.startSession(opts.key, sess);
      else CR.store.setSession(opts.key, sess);
    };
    const next = () => {
      if (!CR.mistakes.sessionAnswered(sess)) save(CR.mistakes.sessionAnswer(sess, null, Date.now()));
      save(CR.mistakes.sessionNext(sess, Date.now()));
      show();
      window.scrollTo(0, 0);
    };

    function question() {
      const id = CR.mistakes.sessionCurrent(sess);
      const q = CR.data.question(id);
      const total = sess.ids.length;
      const slot = h("div", { class: "practice-q" });
      const nextButton = CR.ui.button(sess.i + 1 === total ? "See the results" : "Next question", {
        kind: "primary",
        hidden: true,
        onClick: next,
      });
      const skip = CR.ui.button("Skip", { kind: "quiet", onClick: next });
      ready = () => (q.type === "open" ? ctrl.done() : ctrl.shown());
      const reveal = () => {
        nextButton.hidden = false;
        skip.hidden = true;
      };
      CR.dom.fill(
        holder,
        h("div", { class: "practice-bar" }, h("p", { class: "label", text: `Question ${sess.i + 1} of ${total}` }), CR.ui.progress(sess.i, total, "Practice progress")),
        slot,
        h("div", { class: "practice-foot" }, h("span", { class: "fine foot-hint", text: "Keys: a to d, Enter" }), skip, nextButton),
      );
      ctrl = CR.q.mount(slot, q, {
        mode: "practice",
        onAnswer: (r) => {
          if (!CR.mistakes.sessionAnswered(sess)) save(CR.mistakes.sessionAnswer(sess, r.ok, Date.now()));
          reveal();
        },
        onReveal: reveal,
      });
    }

    function summary() {
      ctrl = null;
      ready = () => false;
      const sum = CR.mistakes.sessionSummary(sess);
      const missed = sum.wrong.length + sum.skipped.length;
      const segments = [{ text: `${sum.right} right`, kind: "pass" }];
      if (sum.wrong.length) segments.push({ text: `${sum.wrong.length} wrong`, kind: "fail" });
      if (sum.skipped.length) segments.push({ text: `${sum.skipped.length} skipped`, kind: "warn" });
      CR.dom.fill(
        holder,
        h("p", { class: "figure-value", text: `${sum.right} of ${sum.total} right` }),
        CR.ui.pytestLine({ segments, tail: "" }),
        missed === 0 ? h("p", { class: "lead", text: "Every one right. Go on to the next stop." }) : h("p", { class: "lead", text: "Open any question to read why. Then redo the ones you missed." }),
        h("ul", { class: "result-list" }, sess.ids.map((id) => resultRow(id, sess.res[id] ?? null))),
        h(
          "div",
          { class: "actions" },
          missed > 0
            ? CR.ui.button(`Redo the ${missed} you missed`, {
                kind: "primary",
                onClick: () => {
                  save(CR.mistakes.sessionRedo(sess, Date.now()), true);
                  show();
                  window.scrollTo(0, 0);
                },
              })
            : null,
          opts.finish ? opts.finish(missed === 0) : null,
          CR.ui.button("Start again", {
            kind: "quiet",
            onClick: () => {
              save(CR.mistakes.newSession(known(opts.ids()), Date.now()), true);
              show();
              window.scrollTo(0, 0);
            },
          }),
        ),
      );
    }

    function show() {
      if (CR.mistakes.sessionFinished(sess)) return summary();
      // A reload after checking: the answer is kept, so go on to the next question.
      if (CR.mistakes.sessionAnswered(sess)) {
        save(CR.mistakes.sessionNext(sess, Date.now()));
        return show();
      }
      return question();
    }

    root.append(
      h(
        "div",
        { class: "page practice-page" },
        CR.ui.crumbs(opts.crumbs),
        h("h1", { text: opts.heading }),
        sess.ids.length === 0 ? CR.ui.empty("Nothing here yet", opts.emptyText || "There are no questions to practise.") : holder,
      ),
    );
    if (sess.ids.length > 0) show();
    return {
      title: opts.heading,
      onKey(event) {
        if (ctrl && ctrl.key(event)) return true;
        if (event.key === "Enter" && ctrl && ready()) {
          next();
          return true;
        }
        return false;
      },
    };
  }

  function runType(root, t) {
    const stopId = `type-${t.tid}`;
    return run(root, {
      key: t.tid,
      ids: () => t.practice,
      heading: `Practice: ${t.name}`,
      crumbs: [["Route", "#home"], [CR.ui.typeLabel(t.tid), CR.route.href("type", t.tid)], ["Practice"]],
      finish: (clean) =>
        CR.ui.button("Mark this stop done and go on", {
          kind: clean ? "primary" : "secondary",
          onClick: () => {
            CR.store.setDone(stopId, true);
            const next = CR.clock.after(CR.data.stops, CR.store.get().done, stopId);
            CR.router.go(next ? CR.route.stopRoute(next) : "home");
          },
        }),
    });
  }

  // The explanation of one question, read-only: #q.<id>.review
  function review(root, id) {
    const q = CR.data.question(id);
    if (!q) {
      root.append(h("div", { class: "page" }, h("h1", { text: "Nothing at this address" }), h("p", {}, h("a", { href: "#home", text: "Back to the route" }))));
      return { title: "Not found" };
    }
    const holder = h("div", { class: "practice-q" });
    root.append(
      h(
        "div",
        { class: "page" },
        CR.ui.crumbs([["Route", "#home"], ["Question"]]),
        h("h1", { text: "Question and explanation" }),
        holder,
        h("div", { class: "actions" }, CR.ui.button("Back", { kind: "secondary", onClick: () => window.history.back() })),
      ),
    );
    CR.q.mount(holder, q, { mode: "review", verdict: false, record: false });
    return { title: "Question" };
  }

  return { run, runType, review };
})();

CR.router.register("q", {
  nav: "home",
  render({ root, args }) {
    return CR.practice.review(root, args[0]);
  },
});
