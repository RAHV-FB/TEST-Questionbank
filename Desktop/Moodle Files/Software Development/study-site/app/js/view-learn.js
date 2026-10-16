// Learn: #learn (all modules), #learn.<module> (module page), #learn.<module>.s<n> (a section
// with its quick check), #learn.<module>.end (traps and terms).
(() => {
  const { h } = SD.dom;

  function moduleMeta(mod) {
    const parts = [
      mod.module,
      `${mod.sessions.length === 1 ? "session" : "sessions"} ${mod.sessions.join(", ")}`,
      SD.util.plural(mod.sections.length, "section"),
      SD.util.plural(mod.questions.length, "question"),
      SD.util.plural(mod.flashcards.length, "flashcard"),
    ];
    return h("p", { class: "meta-line", text: parts.join(" · ") });
  }

  function statusLine(st) {
    if (st.status === "fail") return SD.ui.statusChip("fail", `${st.fail} of ${st.total} sections failing`);
    if (st.status === "pass") return SD.ui.statusChip("pass", "every section passing");
    if (st.pass > 0) return SD.ui.statusChip("part", `${st.pass} of ${st.total} sections passing`);
    if (st.status === "part") return SD.ui.statusChip("part", "in progress");
    return SD.ui.statusChip("none", "not tried yet");
  }

  function renderIndex(root) {
    root.append(
      h(
        "div",
        { class: "page page-wide" },
        h("h1", { text: "Learn" }),
        h("p", {
          class: "lead",
          text:
            "Every module in course order. Each section ends with a quick check, and a section " +
            "passes when you get 80% of its questions right (with 3 answered, or all of them in a " +
            "section with fewer).",
        }),
        SD.ui.moduleGroups().map(([code, mods]) =>
          h(
            "section",
            { class: "module-group" },
            h("h2", { class: "label", text: SD.ui.groupLabel(code) }),
            h(
              "ul",
              { class: "checks" },
              mods.map((mod) => {
                const st = SD.stats.module(mod.id);
                return h(
                  "li",
                  {},
                  h(
                    "a",
                    { class: "check-row", href: SD.route.href("learn", mod.id) },
                    SD.ui.statusMark(st.status),
                    h("span", { class: "check-code", text: SD.ui.moduleCode(mod) }),
                    h(
                      "span",
                      { class: "check-title" },
                      mod.title,
                      mod.predicted ? SD.ui.chip("predicted", "warn") : null,
                    ),
                    h("span", { class: "check-detail" }, SD.ui.dots(st.sections.map((s) => s.status))),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
    return { title: "Learn", live: true };
  }

  function firstUnread(mod) {
    const read = SD.store.get().sec;
    return mod.sections.find((s) => !read[s.id]) || null;
  }

  function renderModule(root, mod) {
    const st = SD.stats.module(mod.id);
    const read = SD.store.get().sec;
    const next = firstUnread(mod);
    const startSection = next || mod.sections[0];
    let startLabel = "Start with section 1";
    if (!next) startLabel = "Read it again from section 1";
    else if (next !== mod.sections[0]) startLabel = `Continue with section ${next.index + 1}`;
    root.append(
      h(
        "div",
        { class: "page" },
        SD.ui.crumbs([["Learn", "#learn"], [mod.title]]),
        h("h1", { text: mod.title }),
        moduleMeta(mod),
        h("p", { class: "status-line" }, statusLine(st)),
        h(
          "div",
          { class: "actions module-actions" },
          SD.ui.linkButton(startLabel, SD.route.href("learn", mod.id, startSection.token), "primary"),
          SD.ui.linkButton("Practise: Next 10", SD.route.href("practice", "next10", mod.id)),
          SD.ui.linkButton("Flashcards", SD.route.href("cards", mod.id), "quiet"),
        ),
        mod.predicted ? SD.ui.predictedNote() : null,
        h("div", { class: "prose", html: mod.summary_html }),
        SD.ui.foldNote("How it is examined", mod.exam_focus_html, "exam"),
        h("h2", { text: "Sections" }),
        h(
          "ol",
          { class: "section-list" },
          mod.sections.map((section, i) => {
            const s = st.sections[i];
            const answered = s.answered ? `${s.correct}/${s.answered} right` : "not tried";
            return h(
              "li",
              {},
              h(
                "a",
                { class: "section-row", href: SD.route.href("learn", mod.id, section.token) },
                SD.ui.statusMark(s.status),
                h("span", { class: "section-n", text: String(i + 1) }),
                h("span", { class: "section-title", html: section.heading_html }),
                h("span", { class: "section-detail", text: (read[section.id] ? "read · " : "") + answered }),
              ),
            );
          }),
          h(
            "li",
            {},
            h(
              "a",
              { class: "section-row section-end", href: SD.route.href("learn", mod.id, "end") },
              h("span", { class: "mark mark-none", "aria-hidden": "true" }),
              h("span", { class: "section-n" }),
              h("span", { class: "section-title", text: "Traps and terms" }),
              h("span", { class: "section-detail", text: `${mod.traps.length} traps · ${mod.terms.length} terms` }),
            ),
          ),
        ),
      ),
    );
    return { title: mod.title, resume: mod.title, live: true };
  }

  // Previous and next section; after the last section, "next" is the traps and terms page.
  function pagerLink(mod, section, rel) {
    if (rel === "prev" && !section) return h("span");
    const href = SD.route.href("learn", mod.id, section ? section.token : "end");
    return h(
      "a",
      { class: `pager-link pager-${rel}`, href, rel },
      h("span", { class: "label", text: rel === "prev" ? "← Previous" : "Next →" }),
      section
        ? h("span", { class: "pager-title", html: section.heading_html })
        : h("span", { class: "pager-title", text: "Traps and terms" }),
    );
  }

  function renderSection(root, mod, section) {
    SD.store.markSection(section.id);
    const prev = mod.sections[section.index - 1] || null;
    const next = mod.sections[section.index + 1] || null;
    const checks = h("div", { class: "quick-check-list" });
    const result = h("p", { class: "quick-result", "aria-live": "polite" });
    const WORDS = { pass: "passing", fail: "failing", part: "in progress", none: "not tried" };
    const paintResult = () => {
      const st = SD.stats.section(section.id);
      result.textContent = st.answered
        ? `Section so far: ${st.correct} of ${st.answered} answered right · ${WORDS[st.status]}`
        : "";
    };
    root.append(
      h(
        "div",
        { class: "page page-margin" },
        SD.ui.crumbs([
          ["Learn", "#learn"],
          [mod.title, SD.route.href("learn", mod.id)],
          [`Section ${section.index + 1} of ${mod.sections.length}`],
        ]),
        h(
          "div",
          { class: "with-margin" },
          h(
            "article",
            { class: "lesson" },
            h("h1", { html: section.heading_html }),
            h("p", { class: "source", text: `Source: ${section.source_ref}` }),
            mod.predicted ? SD.ui.predictedNote() : null,
            h("div", { class: "prose", html: section.body_html }),
            h(
              "div",
              { class: "key-points" },
              h("h2", { class: "label", text: "Key points" }),
              h("ul", {}, section.key_points.map((kp) => h("li", { html: kp }))),
            ),
          ),
          section.exam_note_html
            ? h(
                "aside",
                { class: "margin-note", "aria-label": "Exam note" },
                SD.ui.note("Exam note", section.exam_note_html, "exam"),
              )
            : null,
        ),
        h(
          "section",
          { class: "quick-check", "aria-labelledby": "quick-check-title" },
          h("h2", { id: "quick-check-title", text: "Quick check" }),
          h("p", {
            class: "fine",
            text: "Answer without scrolling back up. Your latest answer to each question counts towards the section's check.",
          }),
          result,
          checks,
        ),
        h(
          "nav",
          { class: "pager", "aria-label": "Sections" },
          pagerLink(mod, prev, "prev"),
          pagerLink(mod, next, "next"),
        ),
      ),
    );
    const controllers = section.check
      .map((qid) => SD.data.question(qid))
      .filter(Boolean)
      .map((q) => SD.q.mount(checks, q, { mode: "practice", revise: false, meta: false }));
    paintResult();
    const stop = SD.store.subscribe((_, kind) => {
      if (kind === "q") paintResult();
    });
    return {
      title: section.plain,
      resume: `${mod.title} · ${section.plain}`,
      cleanup: stop,
      onKey(event) {
        const inside = controllers.find((c) => c.el.contains(document.activeElement));
        if (inside) return inside.key(event);
        if (SD.dom.inScroller(event)) return false;
        if (event.key === "ArrowLeft" && prev) SD.router.go(SD.route.build("learn", mod.id, prev.token));
        else if (event.key === "ArrowRight") SD.router.go(SD.route.build("learn", mod.id, next ? next.token : "end"));
        else return false;
        return true;
      },
    };
  }

  function renderEnd(root, mod) {
    root.append(
      h(
        "div",
        { class: "page" },
        SD.ui.crumbs([["Learn", "#learn"], [mod.title, SD.route.href("learn", mod.id)], ["Traps and terms"]]),
        h("h1", { text: "Traps and terms" }),
        h("p", { class: "lead", text: `The wrong beliefs ${mod.title} corrects, and its vocabulary.` }),
        h("h2", { text: "Traps" }),
        h("ul", { class: "traps" }, mod.traps.map((trap) => h("li", { class: "prose", html: trap }))),
        h("h2", { text: "Terms" }),
        h(
          "dl",
          { class: "terms" },
          mod.terms.map((term) => {
            const section = SD.data.section(term.section_ref);
            return h(
              "div",
              { class: "term" },
              h("dt", { html: term.term_html }),
              h(
                "dd",
                {},
                h("span", { class: "prose", html: term.definition_html }),
                section
                  ? h(
                      "a",
                      { class: "term-link", href: "#" + SD.data.sectionRoute(section.id) },
                      `Section ${section.index + 1}`,
                    )
                  : null,
              ),
            );
          }),
        ),
        h(
          "div",
          { class: "actions" },
          SD.ui.linkButton("Practise this module: Next 10", SD.route.href("practice", "next10", mod.id), "primary"),
          SD.ui.linkButton("Flashcards for this module", SD.route.href("cards", mod.id)),
          SD.ui.linkButton("Back to the module", SD.route.href("learn", mod.id), "quiet"),
        ),
      ),
    );
    return { title: `${mod.title}: traps and terms`, resume: `${mod.title} · Traps and terms` };
  }

  function missing(root, what) {
    root.append(
      h(
        "div",
        { class: "page" },
        SD.ui.crumbs([["Learn", "#learn"], ["Not found"]]),
        h("h1", { text: "Not in this build" }),
        SD.ui.empty(
          `${what} is not in this build yet.`,
          "The content may still be being written. Pick a module from the list.",
          SD.ui.linkButton("All modules", "#learn", "primary"),
        ),
      ),
    );
    return { title: "Not found" };
  }

  SD.router.register("learn", {
    render({ root, args }) {
      const [mid, token] = args;
      if (!mid) return renderIndex(root);
      const mod = SD.data.module(mid);
      if (!mod) return missing(root, `The module "${mid}"`);
      if (!token) return renderModule(root, mod);
      if (token === "end") return renderEnd(root, mod);
      const section = mod.sections.find((s) => s.token === token);
      return section ? renderSection(root, mod, section) : missing(root, `Section "${token}" of ${mod.title}`);
    },
  });
})();
