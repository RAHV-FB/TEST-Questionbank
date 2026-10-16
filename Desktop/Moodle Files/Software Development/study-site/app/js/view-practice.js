// Practice: #practice (choose mode, scope, type, level), #practice.<mode>[.<scope>[.<type>]]
// (a session: one question at a time with full feedback), and #q.<id> (a single question).
// mode: next10 | weak | new | sample; scope: all | <module id> | <section id>; type: any | mcq |
// open | sort. Levels and session length come from the form, remembered in prefs.practice.
(() => {
  const { h } = SD.dom;
  const LEVELS = ["core", "exam", "hard", "beyond"];
  const TYPES = [
    ["any", "Any type"],
    ["mcq", "Multiple choice"],
    ["open", "Open answer"],
    ["sort", "Sort"],
  ];
  const MODES = {
    next10: ["Next 10", "Up to 3 weak spots, then questions you have not tried, in course order."],
    weak: ["Weak spots", "Answered wrong, or right but guessed. The one seen longest ago comes first."],
    new: ["Not tried yet", "Questions you have never answered, in course order."],
    sample: ["Teacher's sample + variants", "The teacher's sample questions, each followed by its variants."],
  };
  let session = null;

  function prefs() {
    const saved = SD.store.get().prefs.practice || {};
    return {
      mode: MODES[saved.mode] ? saved.mode : "next10",
      scope: saved.scope || "all",
      type: saved.type || "any",
      levels: Array.isArray(saved.levels) && saved.levels.length ? saved.levels : LEVELS.slice(),
      length: Number.isInteger(saved.length) ? saved.length : 10,
    };
  }

  function scopeOf(token) {
    if (!token || token === "all") return { kind: "all", label: "All modules" };
    const mod = SD.data.module(token);
    if (mod) return { kind: "module", id: mod.id, label: mod.title };
    const section = SD.data.section(token);
    if (section) return { kind: "section", id: section.id, label: section.plain };
    return null;
  }

  // The questions a session draws from. Weak spots include questions met in exam papers.
  function pool(mode, scope, type, levels) {
    const source = mode === "weak" ? SD.data.allQuestions : SD.data.bank;
    return SD.select.filter(source, {
      scope: mode === "sample" ? { kind: "all" } : scope,
      type,
      levels,
    });
  }

  function size(mode, length) {
    if (mode === "next10") return 10;
    return length > 0 ? length : Infinity;
  }

  // ---- setup form

  function renderSetup(root, message) {
    const p = prefs();
    const state = SD.store.get();
    const startButton = SD.ui.button("Start", { kind: "primary", onClick: start });
    const modeInputs = {};
    const counts = {};
    const scopeSelect = h(
      "select",
      { id: "practice-scope" },
      h("option", { value: "all", text: "All modules" }),
      SD.data.modules.map((mod) =>
        h(
          "optgroup",
          { label: mod.title },
          h("option", { value: mod.id, text: `${mod.title}: whole module` }),
          mod.sections.map((s) =>
            h("option", { value: s.id, text: `${s.index + 1}. ${s.plain}` }),
          ),
        ),
      ),
    );
    scopeSelect.value = scopeOf(p.scope) ? p.scope : "all";
    const typeSelect = h(
      "select",
      { id: "practice-type" },
      TYPES.map(([value, label]) => h("option", { value, text: label })),
    );
    typeSelect.value = p.type;
    const lengthSelect = h(
      "select",
      { id: "practice-length" },
      h("option", { value: "10", text: "10 questions" }),
      h("option", { value: "20", text: "20 questions" }),
      h("option", { value: "0", text: "All that match" }),
    );
    lengthSelect.value = String(p.length);
    const levelBoxes = LEVELS.map((level) =>
      h("input", { type: "checkbox", id: `level-${level}`, value: level, checked: p.levels.includes(level) }),
    );

    function read() {
      const mode = Object.keys(modeInputs).find((m) => modeInputs[m].checked) || "next10";
      return {
        mode,
        scope: scopeSelect.value,
        type: typeSelect.value,
        levels: levelBoxes.filter((b) => b.checked).map((b) => b.value),
        length: Number(lengthSelect.value),
      };
    }

    function refresh() {
      const f = read();
      SD.store.setPref("practice", f);
      const scope = scopeOf(f.scope);
      for (const mode of Object.keys(MODES)) {
        const n = SD.select.pick(mode, pool(mode, scope, f.type, f.levels), state.q, Infinity).length;
        counts[mode].textContent = `${n} available`;
      }
      const n = Math.min(
        SD.select.pick(f.mode, pool(f.mode, scope, f.type, f.levels), state.q, Infinity).length,
        size(f.mode, f.length),
      );
      startButton.disabled = n === 0;
      startButton.textContent = n === 0 ? "No questions match" : `Start: ${SD.util.plural(n, "question")}`;
      scopeSelect.disabled = f.mode === "sample";
      lengthSelect.disabled = f.mode === "next10";
    }

    function start() {
      const f = read();
      const token = f.mode === "sample" ? "all" : f.scope;
      SD.router.go(SD.route.build("practice", f.mode, token, f.type));
    }

    const modeList = h(
      "fieldset",
      { class: "choice-list" },
      h("legend", { text: "Mode" }),
      Object.entries(MODES).map(([mode, [title, text]]) => {
        modeInputs[mode] = h("input", {
          type: "radio",
          name: "practice-mode",
          id: `mode-${mode}`,
          value: mode,
          checked: p.mode === mode,
        });
        counts[mode] = h("span", { class: "choice-count" });
        return h(
          "label",
          { class: "choice", for: `mode-${mode}` },
          modeInputs[mode],
          h(
            "span",
            { class: "choice-body" },
            h("span", { class: "choice-title", text: title }),
            h("span", { class: "choice-text", text }),
          ),
          counts[mode],
        );
      }),
    );

    const form = h(
      "form",
      { class: "practice-form", onchange: refresh, onsubmit: (e) => { e.preventDefault(); start(); } },
      modeList,
      h(
        "div",
        { class: "filters" },
        h("div", { class: "field" }, h("label", { for: "practice-scope", text: "Scope" }), scopeSelect),
        h("div", { class: "field" }, h("label", { for: "practice-type", text: "Type" }), typeSelect),
        h("div", { class: "field" }, h("label", { for: "practice-length", text: "Length" }), lengthSelect),
        h(
          "fieldset",
          { class: "field levels" },
          h("legend", { text: "Level" }),
          h(
            "div",
            { class: "level-boxes" },
            levelBoxes.map((box) => h("label", { class: "level", for: box.id }, box, box.value)),
          ),
        ),
      ),
      h("div", { class: "actions" }, startButton),
    );

    root.append(
      h(
        "div",
        { class: "page" },
        h("h1", { text: "Practice" }),
        h("p", {
          class: "lead",
          text:
            "One question at a time, with the full reasoning after every answer. Levels run " +
            "from core (the idea itself) to beyond (a step past the slides).",
        }),
        message ? h("p", { class: "notice", text: message }) : null,
        form,
      ),
    );
    refresh();
    return { title: "Practice" };
  }

  // ---- a session

  function newSession(key, mode, scope, type) {
    const p = prefs();
    const ids = SD.select.pick(mode, pool(mode, scope, type, p.levels), SD.store.get().q, size(mode, p.length));
    return { key, mode, scope, type, ids, index: 0, results: {}, started: Date.now(), ended: null };
  }

  // "Practice · Next 10 · Scrum · Open answer". Above a question the type is left out: the
  // question's own line names it.
  function sessionLabel(s, withType = true) {
    const scope = s.mode === "sample" ? null : s.scope.label;
    const type = s.type === "any" || !withType ? null : TYPES.find(([v]) => v === s.type)[1];
    return ["Practice", MODES[s.mode][0], scope, type].filter(Boolean).join(" · ");
  }

  // What a row of the summary says about a question: the start of its stem, or, when the stem is
  // only code, where it belongs.
  function rowText(q, number) {
    const text = SD.dom.excerpt(q.stem_html);
    if (text) return text;
    const section = SD.data.section(q.section_ref);
    return `${section ? section.plain : "Question"} (question ${number})`;
  }

  function renderSummary(root, s) {
    const values = s.ids.map((id) => s.results[id]);
    const passed = values.filter((v) => v === true).length;
    const failed = values.filter((v) => v === false).length;
    const toMark = values.filter((v) => v === "unmarked").length;
    const skipped = s.ids.length - passed - failed - toMark;
    const missed = s.ids.filter((id) => s.results[id] === false || s.results[id] === null || !(id in s.results));
    const sections = [...new Set(missed.map((id) => SD.data.question(id).section_ref))]
      .map((id) => SD.data.section(id))
      .filter(Boolean);
    const again = () => {
      session = newSession(s.key, s.mode, s.scope, s.type);
      SD.router.refresh();
    };
    const retry = () => {
      session = { ...s, ids: missed.slice(), index: 0, results: {}, started: Date.now(), ended: null };
      SD.router.refresh();
    };
    root.append(
      h(
        "div",
        { class: "page" },
        h("p", { class: "label", text: sessionLabel(s) }),
        h("h1", { text: "Session complete" }),
        SD.ui.pytestLine(
          SD.scoring.pytestSummary({ passed, failed, toMark, ms: (s.ended || Date.now()) - s.started }),
        ),
        skipped
          ? h("p", { class: "fine", text: `${SD.util.plural(skipped, "question")} skipped or not reached.` })
          : null,
        sections.length
          ? h(
              "section",
              { class: "revise-first", "aria-labelledby": "revise-title" },
              h("h2", { id: "revise-title", text: "Revise" }),
              h(
                "ul",
                { class: "revise-list" },
                sections.map((section) =>
                  h(
                    "li",
                    {},
                    h("a", { href: "#" + SD.data.sectionRoute(section.id), html: section.heading_html }),
                    h("span", {
                      class: "revise-where",
                      text: SD.data.module(section.mid)?.title || "",
                    }),
                  ),
                ),
              ),
            )
          : null,
        h("h2", { text: "The questions" }),
        h("p", { class: "fine", text: "Open one to read the full explanation again." }),
        h(
          "ol",
          { class: "result-list" },
          s.ids.map((id, i) => {
            const q = SD.data.question(id);
            const v = s.results[id];
            const status = v === true ? "pass" : v === false ? "fail" : "none";
            const label = v === true ? "right" : v === false ? "wrong" : v === "unmarked" ? "not marked" : "skipped";
            const section = v === true ? null : SD.data.section(q.section_ref);
            return h(
              "li",
              { class: "result-item" },
              h(
                "a",
                { class: "result-row", href: SD.route.href("q", id, "review") },
                SD.ui.statusMark(status, label),
                h("span", { class: "result-text", text: rowText(q, i + 1) }),
              ),
              section
                ? h(
                    "p",
                    { class: "result-revise" },
                    "Revise: ",
                    h("a", { href: "#" + SD.data.sectionRoute(section.id), html: section.heading_html }),
                  )
                : null,
            );
          }),
        ),
        h(
          "div",
          { class: "actions" },
          missed.length
            ? SD.ui.button(`Practise the ${missed.length} missed again`, { kind: "primary", onClick: retry })
            : null,
          SD.ui.button(s.mode === "next10" ? "Next 10" : "Another round", {
            kind: missed.length ? "secondary" : "primary",
            onClick: again,
          }),
          SD.ui.linkButton("Change the settings", "#practice", "quiet"),
        ),
      ),
    );
    return { title: "Practice results" };
  }

  function renderQuestion(root, s) {
    const id = s.ids[s.index];
    const q = SD.data.question(id);
    const slot = h("div", { class: "q-slot" });
    const last = s.index === s.ids.length - 1;
    const advance = () => {
      if (!(id in s.results)) s.results[id] = null;
      s.index += 1;
      if (s.index >= s.ids.length) s.ended = Date.now();
      SD.router.refresh();
    };
    const nextButton = SD.ui.button(last ? "See the results" : "Next question", {
      kind: "primary",
      onClick: advance,
    });
    const skipButton = SD.ui.button(q.type === "open" ? "Next question" : "Skip", {
      kind: "quiet",
      onClick: advance,
    });
    const after = h("div", { class: "q-next" }, skipButton);
    const finish = () => {
      s.ended = Date.now();
      s.index = s.ids.length;
      SD.router.refresh();
    };
    root.append(
      h(
        "div",
        { class: "page" },
        h("h1", { class: "vh", text: `Practice: question ${s.index + 1} of ${s.ids.length}` }),
        h(
          "div",
          { class: "practice-bar" },
          h("p", { class: "label", text: sessionLabel(s, false) }),
          SD.ui.progress(s.index + 1, s.ids.length, "Question in this session"),
          SD.ui.button("End session", { kind: "quiet", onClick: finish }),
        ),
        slot,
        after,
      ),
    );
    if (q.type === "open") s.results[id] = s.results[id] ?? "unmarked";
    const controller = SD.q.mount(slot, q, {
      mode: "practice",
      number: String(s.index + 1),
      omit: s.scope.kind === "all" ? null : s.scope.kind,
      onAnswer: (result) => {
        s.results[id] = result.ok;
        after.replaceChildren(nextButton);
      },
    });
    return {
      title: "Practice",
      resume: sessionLabel(s),
      onKey(event) {
        if (controller.key(event)) return true;
        if (event.key === "Enter" && controller.done()) {
          advance();
          return true;
        }
        return false;
      },
    };
  }

  SD.router.register("practice", {
    render({ root, args, route }) {
      const [mode, scopeToken, type = "any"] = args;
      if (!mode) return renderSetup(root, null);
      const scope = scopeOf(scopeToken);
      if (!MODES[mode] || !scope || !TYPES.some(([v]) => v === type)) {
        return renderSetup(root, "That practice link is not valid any more. Choose again below.");
      }
      if (!session || session.key !== route) session = newSession(route, mode, scope, type);
      if (session.ids.length === 0) {
        root.append(
          h(
            "div",
            { class: "page" },
            h("p", { class: "label", text: sessionLabel(session) }),
            h("h1", { text: "Nothing to practise here" }),
            SD.ui.empty(
              mode === "weak" ? "No weak spots in this scope." : "No questions match.",
              mode === "weak"
                ? "Questions you answer wrong, or get right by guessing, collect here."
                : "Widen the scope, the type or the levels.",
              SD.ui.linkButton("Choose another practice", "#practice", "primary"),
            ),
          ),
        );
        session = null;
        return { title: "Practice" };
      }
      if (session.index >= session.ids.length) {
        const finished = session;
        session = null; // the summary shows once; opening this link again starts a new round
        return renderSummary(root, finished);
      }
      return renderQuestion(root, session);
    },
  });

  // The answers typed into an open question before, for reading its explanation again.
  function savedAnswers(q) {
    if (q.type !== "open") return undefined;
    return Object.fromEntries(q.parts.map((p) => [p.label, SD.store.draft(`open.${q.id}.${p.label}`) || ""]));
  }

  // #q.<id>: one question to answer; #q.<id>.review: its explanation, read-only.
  SD.router.register("q", {
    nav: "practice",
    render({ root, args }) {
      const q = SD.data.question(args[0]);
      if (!q) return renderSetup(root, "That question is not in this build.");
      const review = args[1] === "review";
      const mod = SD.data.module(q.mid);
      const section = SD.data.section(q.section_ref);
      const page = h(
        "div",
        { class: "page" },
        SD.ui.crumbs([
          ["Practice", "#practice"],
          [mod ? mod.title : q.mid, mod ? SD.route.href("learn", mod.id) : null],
          [review ? "Explanation" : "Question"],
        ]),
        h("h1", { class: "vh", text: review ? "Explanation" : "Question" }),
      );
      root.append(page);
      const controller = SD.q.mount(
        page,
        q,
        review ? { mode: "review", verdict: false, answer: savedAnswers(q) } : { mode: "practice" },
      );
      const answered = Boolean(SD.store.get().q[q.id]);
      page.append(
        h(
          "div",
          { class: "actions" },
          review ? SD.ui.linkButton("Try it again", SD.route.href("q", q.id), "primary") : null,
          !review && answered ? SD.ui.linkButton("Read the explanation", SD.route.href("q", q.id, "review")) : null,
          section
            ? SD.ui.linkButton(
                "Practise this section: Next 10",
                SD.route.href("practice", "next10", section.id),
                review ? "secondary" : "quiet",
              )
            : null,
        ),
      );
      return { title: review ? "Explanation" : "Question", onKey: (event) => controller.key(event) };
    },
  });
})();
