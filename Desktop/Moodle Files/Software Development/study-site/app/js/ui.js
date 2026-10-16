// Shared UI pieces used by several views, plus SD.stats: progress figures read from the store.
SD.ui = (() => {
  const { h } = SD.dom;
  const STATUS_TEXT = { pass: "passing", fail: "failing", part: "in progress", none: "not tried" };
  // The two outline shapes of a mark, in a 16-unit box; "part" is the circle with its left half filled.
  const MARK_PATHS = {
    pass: ["M3.5 8.5 6.5 11.5 12.5 4.5"],
    fail: ["M4 4 12 12M12 4 4 12"],
  };
  const GROUPS = {
    M1: "M1 · Starting a project",
    M2: "M2 · Clean code and tests",
    M3: "M3 · Terminal and shell",
    X: "Across the course",
  };

  // Modules grouped by their course part, in course order: [["M1", [mod, ...]], ...].
  function moduleGroups() {
    const groups = new Map();
    for (const mod of SD.data.modules) {
      if (!groups.has(mod.module)) groups.set(mod.module, []);
      groups.get(mod.module).push(mod);
    }
    return [...groups];
  }

  const groupLabel = (code) => GROUPS[code] || code;

  // A status shape drawn as SVG (✓ ✗ ○ and the half circle), so it looks the same in every font
  // and on every system. Colour comes from the surrounding text colour.
  function mark(kind) {
    const el = SD.dom.svg("svg", {
      class: "mk",
      viewBox: "0 0 16 16",
      "aria-hidden": "true",
      focusable: "false",
    });
    if (MARK_PATHS[kind]) {
      for (const d of MARK_PATHS[kind]) el.append(SD.dom.svg("path", { d }));
    } else {
      el.append(SD.dom.svg("circle", { cx: 8, cy: 8, r: 5 }));
      if (kind === "part") el.append(SD.dom.svg("path", { d: "M8 3a5 5 0 0 0 0 10z", class: "fill" }));
    }
    return el;
  }

  // The CI-check mark: the shape plus words for screen readers (colour is never the only signal).
  function statusMark(status, label = STATUS_TEXT[status]) {
    return h("span", { class: `mark mark-${status}` }, mark(status), h("span", { class: "vh", text: label }));
  }

  // "✓ passing", "✗ failing", "○ not tried", or a plain chip such as "predicted" (kind "warn").
  function chip(text, kind = "none") {
    return h("span", { class: `chip chip-${kind}`, text });
  }

  function statusChip(status, text = STATUS_TEXT[status]) {
    return h("span", { class: `chip chip-${status === "part" ? "none" : status}` }, mark(status), text);
  }

  // The verdict line of a question or drill: the shape, then the words ("Correct.", "Not quite.").
  function verdict(ok, text) {
    return h("p", { class: `verdict verdict-${ok ? "pass" : "fail"}` }, mark(ok ? "pass" : "fail"), text);
  }

  // A module's course code for lists: "M1", "M2", "M3"; nothing for the course-wide ones.
  const moduleCode = (mod) => (/^M\d+$/.test(mod.module) ? mod.module : "");

  function dots(statuses) {
    return h(
      "span",
      { class: "dots", "aria-hidden": "true" },
      statuses.map((s) => h("span", { class: `dot dot-${s}` })),
    );
  }

  // pytest's summary line, e.g. "14 passed, 3 failed, 2 to mark in 52m10s".
  function pytestLine(summary) {
    const parts = [];
    summary.segments.forEach((seg, i) => {
      if (i > 0) parts.push(", ");
      parts.push(h("span", { class: `py-${seg.kind}`, text: seg.text }));
    });
    if (summary.tail) parts.push(" " + summary.tail);
    return h("p", { class: "pytest" }, parts);
  }

  function progress(done, total, label) {
    return h(
      "div",
      { class: "progress" },
      h("span", { class: "progress-text", text: `${done}/${total}` }),
      h(
        "div",
        {
          class: "bar",
          role: "progressbar",
          "aria-label": label,
          "aria-valuemin": "0",
          "aria-valuemax": String(total),
          "aria-valuenow": String(done),
        },
        h("span", { style: `width: ${SD.util.percent(done, total)}%` }),
      ),
    );
  }

  // [["Learn", "#learn"], ["Testing and TDD", "#learn.testing-tdd"], ["Section 3"]]
  function crumbs(items) {
    return h(
      "nav",
      { class: "crumbs", "aria-label": "Breadcrumb" },
      h(
        "ol",
        {},
        items.map(([text, href]) =>
          h("li", {}, href ? h("a", { href, text }) : h("span", { "aria-current": "page", text })),
        ),
      ),
    );
  }

  function button(label, { kind = "secondary", onClick = null, ...rest } = {}) {
    return h("button", { type: "button", class: `btn btn-${kind}`, onclick: onClick, ...rest }, label);
  }

  function linkButton(label, href, kind = "secondary") {
    return h("a", { class: `btn btn-${kind}`, href }, label);
  }

  // A labelled block of content HTML: "Exam note", "Model answer", "How it is examined".
  function note(label, html, kind = "plain") {
    return h(
      "div",
      { class: `note note-${kind}` },
      h("p", { class: "label", text: label }),
      h("div", { class: "prose", html }),
    );
  }

  // Like note(), but the student can fold it away: a <details> that starts open.
  function foldNote(label, html, kind = "plain") {
    return h(
      "details",
      { class: `note note-${kind} fold`, open: true },
      h("summary", { class: "label", text: label }),
      h("div", { class: "prose", html }),
    );
  }

  function reviseLink(q) {
    const section = SD.data.section(q.section_ref);
    if (!section) return null;
    return h(
      "p",
      { class: "revise" },
      h(
        "a",
        { href: "#" + SD.data.sectionRoute(section.id) },
        "Revise: ",
        h("span", { html: section.heading_html }),
      ),
    );
  }

  function predictedNote() {
    return h(
      "p",
      { class: "predicted-note" },
      chip("predicted", "warn"),
      " Written before the session 10 slides were published. Re-check it after class on Fri 16 Oct.",
    );
  }

  function empty(title, text, action) {
    return h(
      "div",
      { class: "empty" },
      h("p", { class: "empty-title", text: title }),
      h("p", { text }),
      action || null,
    );
  }

  // What the student has done toward a plan item, for the small hint under it.
  function planHint(item) {
    const state = SD.store.get();
    return SD.planner.hint(item.link, {
      sections(mid) {
        const mod = SD.data.module(mid);
        if (!mod) return null;
        return { read: mod.sections.filter((s) => state.sec[s.id]).length, total: mod.sections.length };
      },
      lastExam(paperId) {
        const done = SD.exam.lastDone(state.exams, paperId);
        return done ? { score: done.score, max: done.max } : null;
      },
    });
  }

  // Plan items as a checklist: the tick box is its own control, the item's words are the link.
  // Ticking saves at once. An item with a dayLabel shows it first (items carried over from
  // earlier days).
  function planItems(items) {
    const planState = SD.store.get().plan;
    return h(
      "ul",
      { class: "plan-items" },
      items.map((item) => {
        const id = `plan-${item.id}`;
        const done = Boolean(planState[item.id]?.done);
        const hint = planHint(item);
        return h(
          "li",
          { class: done ? "plan-item is-done" : "plan-item" },
          h(
            "label",
            { class: "plan-tick" },
            h("input", {
              type: "checkbox",
              checked: done,
              "aria-labelledby": `${id}-link`,
              onchange: (e) => {
                SD.store.setPlanItem(item.id, e.target.checked);
                e.target.closest("li").classList.toggle("is-done", e.target.checked);
              },
            }),
          ),
          h(
            "span",
            { class: "plan-text" },
            item.dayLabel ? h("span", { class: "plan-day-tag", text: item.dayLabel }) : null,
            h("a", { class: "plan-link", id: `${id}-link`, href: item.link, text: item.label }),
            hint ? h("span", { class: "plan-hint", text: hint }) : null,
          ),
        );
      }),
    );
  }

  return {
    moduleGroups,
    groupLabel,
    moduleCode,
    mark,
    statusMark,
    chip,
    statusChip,
    verdict,
    dots,
    pytestLine,
    progress,
    crumbs,
    button,
    linkButton,
    note,
    foldNote,
    reviseLink,
    predictedNote,
    empty,
    planItems,
  };
})();

// Progress figures for views: CI-style statuses, weak spots, due cards, the last exam.
SD.stats = (() => {
  const q = () => SD.store.get().q;

  function section(id) {
    return SD.progress.sectionStatus(SD.data.sectionQuestions(id), q());
  }

  function module(mid) {
    const mod = SD.data.module(mid);
    const sections = mod.sections.map((s) => section(s.id));
    return { ...SD.progress.moduleStatus(sections.map((s) => s.status)), sections };
  }

  function weakIds() {
    return SD.progress.weakSpots(
      SD.data.allQuestions.map((x) => x.id),
      q(),
    );
  }

  function cards(mid = null) {
    const ids = SD.data.cards.filter((c) => !mid || c.mid === mid).map((c) => c.id);
    return { ids, ...SD.leitner.counts(ids, SD.store.get().fc, Date.now()) };
  }

  // The most recent finished exam record (see the record shape in app/API.md), or null.
  function lastExam() {
    const done = SD.store.get().exams.filter((e) => e.status === "done");
    return done.length ? done.reduce((a, b) => ((b.ended || 0) > (a.ended || 0) ? b : a)) : null;
  }

  // Where we stand against the real exam: before it (with a countdown), during, or after.
  function exam(now = Date.now()) {
    const start = Date.parse(SD.data.meta.exam.date);
    const end = start + SD.data.meta.exam.minutes * SD.util.MINUTE;
    if (now < start) return { state: "before", text: SD.util.countdown(start - now) };
    if (now < end) return { state: "during", text: "The mid-term is in progress" };
    return { state: "after", text: "The mid-term is over" };
  }

  return { section, module, weakIds, cards, lastExam, exam };
})();
