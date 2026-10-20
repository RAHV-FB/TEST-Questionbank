// Shared UI pieces used by several views.
CR.ui = (() => {
  const { h } = CR.dom;
  // The two outline shapes of a mark, in a 16-unit box; "part" is the circle with its left half filled.
  const MARK_PATHS = {
    pass: ["M3.5 8.5 6.5 11.5 12.5 4.5"],
    fail: ["M4 4 12 12M12 4 4 12"],
  };
  const STATUS_TEXT = { pass: "passing", fail: "failing", part: "in progress", none: "not tried" };

  // A status shape drawn as SVG (a tick, a cross, a circle, a half circle), so it looks the same in
  // every font and on every system. Colour comes from the surrounding text colour.
  function mark(kind) {
    const el = CR.dom.svg("svg", { class: "mk", viewBox: "0 0 16 16", "aria-hidden": "true", focusable: "false" });
    if (MARK_PATHS[kind]) {
      for (const d of MARK_PATHS[kind]) el.append(CR.dom.svg("path", { d }));
    } else {
      el.append(CR.dom.svg("circle", { cx: 8, cy: 8, r: 5 }));
      if (kind === "part") el.append(CR.dom.svg("path", { d: "M8 3a5 5 0 0 0 0 10z", class: "fill" }));
    }
    return el;
  }

  // The shape plus words for screen readers (colour is never the only signal).
  function statusMark(status, label = STATUS_TEXT[status]) {
    return h("span", { class: `mark mark-${status}` }, mark(status), h("span", { class: "vh", text: label }));
  }

  function chip(text, kind = "none") {
    return h("span", { class: `chip chip-${kind}`, text });
  }

  // The verdict line of a question: the shape, then the words ("Correct.", "Not quite.").
  function verdict(ok, text) {
    return h("p", { class: `verdict verdict-${ok ? "pass" : "fail"}` }, mark(ok ? "pass" : "fail"), text);
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
        h("span", { style: `width: ${CR.util.percent(done, total)}%` }),
      ),
    );
  }

  // [["Route", "#home"], ["Failing tests"]] -> a breadcrumb trail.
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

  // A labelled block of content HTML: "Why", "Model answer", "Spot it".
  function note(label, html, kind = "plain") {
    return h("div", { class: `note note-${kind}` }, h("p", { class: "label", text: label }), h("div", { class: "prose", html }));
  }

  function empty(title, text, action) {
    return h("div", { class: "empty" }, h("p", { class: "empty-title", text: title }), h("p", { text }), action || null);
  }

  // "Back to the basics" link for a question: its cram type's page.
  function basicsLink(q) {
    const name = CR.data.names[q.tid];
    if (!name || !CR.data.types[q.tid]) return null;
    return h("p", { class: "revise" }, h("a", { href: CR.route.href("type", q.tid), text: `Back to the basics: ${q.tid} ${name}` }));
  }

  // "Ask Claude about this": appears only when the sample capability resolves, and nothing is sent
  // until the click. getAnswer() returns the student's answer in the shape CR.tutor.request reads.
  function tutorBox(q, getAnswer) {
    const box = h("div", { class: "tutor", hidden: true });
    CR.claude.canAsk().then((ok) => {
      if (!ok || !box.isConnected) return;
      const typed = h("input", {
        type: "text",
        class: "tutor-input",
        maxlength: String(CR.tutor.MAX_ASK),
        placeholder: "Optional: ask something specific, such as why not b?",
        "aria-label": "Your question for Claude (optional)",
      });
      const out = h("div", { class: "tutor-out prose", "aria-live": "polite", hidden: true });
      const status = h("p", { class: "fine tutor-status", "aria-live": "polite" });
      let control = null;
      const stop = button("Stop", { kind: "quiet", hidden: true, onClick: () => control && control.abort() });
      const ask = button("Ask Claude about this", {
        kind: "secondary",
        onClick: async () => {
          control = new AbortController();
          ask.disabled = true;
          stop.hidden = false;
          out.hidden = true;
          status.textContent = "Thinking. This can take a few seconds.";
          const reply = await CR.claude.ask(q, getAnswer(), typed.value, {
            signal: control.signal,
            onText: (text) => {
              status.textContent = "";
              out.hidden = false;
              out.textContent = text;
            },
          });
          stop.hidden = true;
          if (reply.text !== undefined) {
            status.textContent = "";
            out.hidden = false;
            out.textContent = reply.text;
          } else {
            status.textContent = reply.error;
            if (reply.partial) {
              out.hidden = false;
              out.textContent = reply.partial;
            }
          }
          if (reply.hide) box.hidden = true;
          else ask.disabled = false;
        },
      });
      box.append(h("p", { class: "label", text: "Tutor" }), h("div", { class: "tutor-row" }, typed, ask, stop), status, out);
      box.hidden = false;
    });
    return box;
  }

  return { mark, statusMark, chip, verdict, pytestLine, progress, crumbs, button, linkButton, note, empty, basicsLink, tutorBox };
})();
