// A type page: the one idea, how to spot it, the basics with quick checks, the method, worked
// examples, twists, traps, what to write, and the way into the practice.
(() => {
  const { h } = CR.dom;
  const SECTIONS = [
    ["sec-basics", "Basics"],
    ["sec-method", "Method"],
    ["sec-worked", "Worked"],
    ["sec-twists", "Twists"],
    ["sec-traps", "Traps"],
    ["sec-say", "Write this"],
    ["sec-practice", "Practice"],
  ];

  // One quick check: pick an option and it answers at once. The pick is kept, so the page comes back
  // as you left it; "Try again" clears it.
  function checkItem(c, n, total) {
    const id = CR.q.nextId();
    const saved = CR.store.get().checks[c.id];
    let pick = saved ? saved.pick : null;
    const slot = h("div", { class: "q-verdict", tabindex: "-1" });
    const why = h("div", { class: "prose check-why", html: c.why_html, hidden: true });
    const again = CR.ui.button("Try again", {
      kind: "quiet",
      hidden: true,
      onClick: () => {
        CR.store.clearCheck(c.id);
        pick = null;
        paint(false);
      },
    });
    const rows = c.options.map((html, i) => {
      const input = h("input", {
        type: "radio",
        class: "opt-input",
        name: id,
        value: String(i),
        onchange: () => choose(i),
      });
      const mark = h("span", { class: "opt-mark" });
      const row = h(
        "label",
        { class: "opt" },
        input,
        h("span", { class: "opt-letter", text: `${CR.q.LETTERS[i]})` }),
        h("span", { class: "opt-body" }, h("span", { class: "opt-text prose", html })),
        mark,
      );
      return { row, input, mark };
    });
    const el = h(
      "fieldset",
      { class: "qcheck", dataset: { check: c.id } },
      h("legend", { class: "label", text: `Check ${n} of ${total}` }),
      h("div", { class: "q-stem prose", html: c.q_html }),
      slot,
      h("div", { class: "opts" }, rows.map((r) => r.row)),
      why,
      again,
    );

    function paint(announce) {
      const shown = pick !== null;
      rows.forEach((r, i) => {
        r.input.checked = i === pick;
        r.input.disabled = shown;
        r.row.classList.toggle("is-selected", !shown && i === pick);
        r.row.classList.toggle("is-correct", shown && i === c.answer);
        r.row.classList.toggle("is-wrong", shown && i === pick && i !== c.answer);
        if (shown && i === c.answer) r.mark.replaceChildren(CR.ui.mark("pass"), i === pick ? "your answer" : "correct answer");
        else if (shown && i === pick) r.mark.replaceChildren(CR.ui.mark("fail"), "your answer");
        else r.mark.replaceChildren();
      });
      why.hidden = !shown;
      again.hidden = !shown;
      if (!shown) {
        slot.replaceChildren();
        return;
      }
      const ok = pick === c.answer;
      const text = ok ? "Correct." : `Not quite. The answer is ${CR.q.LETTERS[c.answer]})`;
      slot.replaceChildren(CR.ui.verdict(ok, text));
      if (announce) {
        CR.dom.announce(text);
        CR.dom.reveal(slot);
      }
    }

    function choose(i) {
      if (pick !== null) return;
      pick = i;
      CR.store.setCheck(c.id, i, i === c.answer);
      paint(true);
    }

    // a–d or 1–4 pick an option while focus is inside the check.
    el.addEventListener("keydown", (event) => {
      if (pick !== null || event.altKey || event.ctrlKey || event.metaKey) return;
      const k = event.key.toLowerCase();
      const pos = /^[a-h]$/.test(k) ? CR.q.LETTERS.indexOf(k) : /^[1-8]$/.test(k) ? Number(k) - 1 : -1;
      if (pos < 0 || pos >= rows.length) return;
      event.preventDefault();
      choose(pos);
    });
    paint(false);
    return el;
  }

  function practiceBox(t) {
    const sess = CR.store.session(t.tid);
    const href = CR.route.href("type", t.tid, "practice");
    const total = t.practice.length;
    const box = h("div", { class: "practice-box" });
    if (!sess) {
      box.append(
        h("p", { text: `${total} real exam-style questions, from core to hard. One at a time; after each one you see why every option is right or wrong.` }),
        h("div", { class: "actions" }, CR.ui.linkButton("Start the practice", href, "primary")),
      );
      return box;
    }
    const sum = CR.mistakes.sessionSummary(sess);
    if (sum.finished) {
      box.append(
        h("p", { class: "figure-value", text: `${sum.right} of ${sum.total} right` }),
        h(
          "div",
          { class: "actions" },
          sum.wrong.length + sum.skipped.length > 0
            ? CR.ui.button(`Redo the ${sum.wrong.length + sum.skipped.length} you missed`, {
                kind: "primary",
                onClick: () => {
                  CR.store.startSession(t.tid, CR.mistakes.sessionRedo(sess, Date.now()));
                  CR.router.go(CR.route.build("type", t.tid, "practice"));
                },
              })
            : null,
          CR.ui.linkButton("See the results", href, sum.wrong.length ? "secondary" : "primary"),
          CR.ui.button("Start again", {
            kind: "quiet",
            onClick: () => {
              CR.store.startSession(t.tid, CR.mistakes.newSession(t.practice, Date.now()));
              CR.router.go(CR.route.build("type", t.tid, "practice"));
            },
          }),
        ),
      );
      return box;
    }
    box.append(
      CR.ui.progress(sess.i, sum.total, "Practice progress"),
      h("div", { class: "actions" }, CR.ui.linkButton("Continue the practice", href, "primary")),
    );
    return box;
  }

  function missingPage(root, tid) {
    root.append(
      h(
        "div",
        { class: "page" },
        h("h1", { text: CR.data.names[tid] ? `${tid} is not in this build` : "Nothing at this address" }),
        h("p", { text: CR.data.names[tid] ? `${CR.data.names[tid]} has no content in this build yet.` : `There is no type called "${tid}".` }),
        h("p", {}, h("a", { href: "#home", text: "Back to the route" })),
      ),
    );
    return { title: "Not found" };
  }

  function render({ root, args }) {
    const [tid, sub] = args;
    const t = CR.data.type(tid);
    if (!t) return missingPage(root, tid);
    if (sub === "practice") return CR.practice.runType(root, t);
    const stopId = `type-${tid}`;
    const done = CR.clock.isDone(CR.store.get().done, stopId);

    const doneBox = h("input", {
      type: "checkbox",
      id: "type-done",
      checked: done,
      onchange: (e) => {
        CR.store.setDone(stopId, e.target.checked);
        paintNext();
      },
    });
    const nextHolder = h("div", { class: "type-next" });
    function paintNext() {
      const next = CR.clock.after(CR.data.stops, CR.store.get().done, stopId);
      CR.dom.fill(
        nextHolder,
        next
          ? CR.ui.linkButton(`Next: ${next.tid ? `${next.tid} ` : ""}${next.title}`, next.href, "primary")
          : CR.ui.linkButton("Back to the route", "#home", "primary"),
      );
    }

    const checkTotal = t.basics.reduce((n, b) => n + b.checks.length, 0);
    let checkNo = 0;
    const basics = t.basics.map((b) =>
      h(
        "div",
        { class: "basic" },
        h("h3", { html: b.heading_html }),
        h("div", { class: "prose", html: b.body_html }),
        b.checks.map((c) => checkItem(c, (checkNo += 1), checkTotal)),
      ),
    );

    root.append(
      h(
        "div",
        { class: "page type-page" },
        CR.ui.crumbs([["Route", "#home"], [`${tid} ${t.name}`]]),
        h("p", { class: "meta-line", text: `${tid} · ${CR.util.minutesLabel(t.minutes)} suggested · ${t.practice.length} practice questions` }),
        h("h1", { text: t.name }),
        h("div", { class: "one" }, h("p", { class: "label", text: "The one idea" }), h("div", { class: "prose lead-prose", html: t.one_html })),
        h(
          "nav",
          { class: "secnav", "aria-label": "Sections of this page" },
          SECTIONS.map(([id, label]) => h("button", { type: "button", class: "seg-btn", onclick: () => CR.dom.scrollToId(id), text: label })),
        ),
        h("h2", { text: "How it appears on the paper" }),
        h("div", { class: "prose", html: t.shape_html }),
        CR.ui.note("Spot it", t.spot_html, "exam"),
        h("h2", { id: "sec-basics", tabindex: "-1", text: "Basics" }),
        basics,
        h("h2", { id: "sec-method", tabindex: "-1", text: "Method" }),
        h("p", { class: "fine", text: "Follow these steps, in this order, on the paper." }),
        h("ol", { class: "method" }, t.method.map((m) => h("li", {}, h("div", { class: "prose", html: m })))),
        h("h2", { id: "sec-worked", tabindex: "-1", text: t.worked.length > 1 ? "Worked examples" : "Worked example" }),
        t.worked.map((w, i) =>
          h(
            "details",
            { class: "worked", open: i === 0 },
            h("summary", { class: "worked-summary", text: w.title }),
            h("div", { class: "prose", html: w.question_html }),
            h("p", { class: "label", text: "Steps" }),
            h("ol", { class: "steps" }, w.steps.map((s) => h("li", { class: "prose", html: s }))),
            CR.ui.note("Answer", w.answer_html, "model"),
          ),
        ),
        h("h2", { id: "sec-twists", tabindex: "-1", text: "Twists the teacher could set" }),
        h(
          "ul",
          { class: "twists" },
          t.twists.map((x) => h("li", {}, h("div", { class: "prose twist", html: x.twist_html }), h("div", { class: "prose how", html: x.how_html }))),
        ),
        h("h2", { id: "sec-traps", tabindex: "-1", text: "Traps" }),
        h("ul", { class: "traps" }, t.traps.map((x) => h("li", { class: "prose", html: x }))),
        h("h2", { id: "sec-say", tabindex: "-1", text: "Write this on the paper" }),
        CR.ui.note("Words that score", t.say_html, "model"),
        h("h2", { id: "sec-practice", tabindex: "-1", text: "Practice" }),
        practiceBox(t),
        h(
          "div",
          { class: "type-foot" },
          h("label", { class: "done-label" }, doneBox, h("span", { text: "I have finished this type" })),
          nextHolder,
        ),
      ),
    );
    paintNext();
    return { title: `${tid} ${t.name}` };
  }

  CR.router.register("type", { nav: "home", render });
})();
