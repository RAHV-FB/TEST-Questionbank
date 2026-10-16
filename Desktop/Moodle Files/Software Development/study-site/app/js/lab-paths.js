// Paths lab (#labs.paths): predict what pwd prints after a cd (the drill), or type cd, pwd and
// ls into a small terminal on the fixed tree (explore). The tree shows where pwd and OLDPWD are.
(() => {
  const { h } = SD.dom;
  const X = SD.paths;
  const START = { pwd: X.PROJECT, oldpwd: X.HOME };
  const page = {
    tab: "drill",
    drill: null, // {task, typed, checked, check}
    explore: { state: START, lines: [], history: [], note: "" },
  };

  const plainPath = (path) => path.replace(/^\/\/(?!\/)/, "/");

  // The tree with markers: marks = [[path, "pwd"], [path, "OLDPWD"]].
  function tree(marks) {
    const at = new Map();
    for (const [path, label] of marks) {
      if (!path) continue;
      const key = plainPath(path);
      at.set(key, at.has(key) ? `${at.get(key)}, ${label}` : label);
    }
    const lines = X.treeLines().map((line) => {
      const mark = at.get(line.path);
      return h(
        "span",
        { class: `tree-line${mark ? " is-marked" : ""}` },
        h("span", { class: "tree-branch", text: line.prefix }),
        h("span", { class: line.dir ? "tree-dir" : "tree-file", text: line.name }),
        mark ? h("span", { class: "tree-mark", text: `  ← ${mark}` }) : null,
        "\n",
      );
    });
    return h(
      "div",
      { class: "code tree" },
      h("span", { class: "code-lang", "aria-hidden": "true", text: "tree" }),
      h("pre", { tabindex: "0", role: "group", "aria-label": "The folder tree" }, h("code", {}, lines)),
    );
  }

  function newDrill() {
    return { task: X.task(SD.labs.random()), typed: "", checked: false, check: null };
  }

  function questionLines(t) {
    return [
      { cmd: "pwd" },
      { out: t.start.pwd },
      { cmd: "echo $OLDPWD" },
      { out: t.start.oldpwd },
      ...t.args.map((arg) => ({ cmd: X.commandText(arg) })),
      { cmd: "pwd" },
    ];
  }

  function answerLines(t, run) {
    const lines = [{ cmd: "pwd" }, { out: t.start.pwd }, { cmd: "echo $OLDPWD" }, { out: t.start.oldpwd }];
    t.args.forEach((arg, i) => {
      const r = run.results[i];
      lines.push({ cmd: X.commandText(arg) });
      if (r.out) lines.push({ out: r.out });
      if (r.err) lines.push({ err: r.err });
    });
    lines.push(
      { cmd: "pwd" },
      { out: run.state.pwd },
      { cmd: "echo $OLDPWD" },
      { out: run.state.oldpwd || "" },
    );
    return lines;
  }

  function renderDrill(main, aside) {
    if (!page.drill) page.drill = newDrill();
    const d = page.drill;
    const t = d.task;
    const run = X.run(t.start, t.args);
    const input = h("input", {
      type: "text",
      id: "pwd-guess",
      class: "mono-input wide-input",
      autocomplete: "off",
      autocapitalize: "off",
      spellcheck: "false",
      value: d.typed,
    });
    input.addEventListener("input", () => (d.typed = input.value));
    const button = SD.ui.button(d.checked ? "Next task" : "Check", { kind: "primary", type: "submit" });
    const out = h("div", { class: "drill-out", "aria-live": "polite" });
    const form = h(
      "form",
      {
        class: "drill-form",
        onsubmit: (event) => {
          event.preventDefault();
          if (d.checked) next();
          else check();
        },
      },
      h(
        "div",
        { class: "field" },
        h("label", { for: "pwd-guess", text: "What does the last pwd print?" }),
        input,
      ),
      h("div", { class: "actions" }, button),
    );

    function paintResult() {
      const c = d.check;
      const steps = t.args.map((arg, i) => {
        const before = i === 0 ? t.start : run.results[i - 1].state;
        return h(
          "li",
          {},
          h("p", { class: "mono step-cmd", text: `$ ${X.commandText(arg)}` }),
          X.explain(before, arg, run.results[i]).map((s) => h("p", {}, SD.labs.codeText(s))),
        );
      });
      let detail = c.ok ? "Right." : `Not quite: pwd prints ${run.state.pwd}.`;
      if (c.ok && !c.exact)
        detail += ` pwd prints it as ${run.state.pwd}: the full path, with no ~ and no slash at the end.`;
      SD.dom.fill(
        out,
        SD.ui.verdict(c.ok, detail),
        h("p", { class: "label", text: "What the terminal shows" }),
        SD.labs.term(answerLines(t, run)),
        h("p", { class: "label", text: "Why" }),
        h("ol", { class: "steps" }, steps),
      );
    }

    function check() {
      if (!input.value.trim()) {
        out.replaceChildren(
          h("p", { class: "notice", text: "Type the path you expect, for example /home/alice." }),
        );
        input.focus();
        return;
      }
      d.checked = true;
      d.check = X.checkPrediction(run.state.pwd, input.value);
      SD.labs.count("paths", d.check.ok);
      SD.dom.announce(d.check.ok ? "Right." : `Not quite. pwd prints ${run.state.pwd}.`);
      paint();
      main.querySelector(".drill-form .btn-primary")?.focus({ preventScroll: true });
    }

    function next() {
      page.drill = newDrill();
      paint();
      main.querySelector("#pwd-guess")?.focus({ preventScroll: true });
    }

    function paint() {
      renderDrill(main, aside);
    }

    input.disabled = d.checked;
    main.replaceChildren(
      h("p", { class: "fine", text: SD.labs.tallyText("paths") }),
      SD.labs.term(questionLines(t)),
      form,
      out,
    );
    if (d.checked) paintResult();
    const final = d.checked ? run.state : t.start;
    aside.replaceChildren(
      tree([
        [final.pwd, "pwd"],
        [final.oldpwd, "OLDPWD"],
      ]),
    );
    main.next = () => (d.checked ? next() : check());
  }

  function renderExplore(main, aside) {
    const e = page.explore;
    let back = e.history.length;
    const input = h("input", {
      type: "text",
      id: "term-input",
      class: "mono-input wide-input",
      autocomplete: "off",
      autocapitalize: "off",
      spellcheck: "false",
      "aria-describedby": "term-help",
    });
    input.addEventListener("keydown", (event) => {
      // ↑ and ↓ walk back through the commands typed so far, as in a real terminal.
      if (event.key !== "ArrowUp" && event.key !== "ArrowDown") return;
      event.preventDefault();
      back = Math.max(0, Math.min(e.history.length, back + (event.key === "ArrowUp" ? -1 : 1)));
      input.value = e.history[back] ?? "";
    });
    const shown = e.lines.length ? e.lines : [{ cmd: "pwd" }, { out: e.state.pwd }];
    const transcript = SD.labs.term(shown.slice(-80), { live: true });
    const form = h(
      "form",
      {
        class: "term-form",
        onsubmit: (event) => {
          event.preventDefault();
          const line = input.value;
          if (!line.trim()) return;
          const r = X.exec(e.state, line);
          e.history.push(line.trim());
          e.lines.push(
            { cmd: line.trim() },
            ...r.out.map((o) => ({ out: o })),
            ...r.err.map((x) => ({ err: x })),
          );
          e.note = r.note || "";
          e.state = r.state;
          // The transcript is redrawn with every command, so say what came out.
          SD.dom.announce([...r.out, ...r.err, e.note].filter(Boolean).join(". ") || "No output.");
          renderExplore(main, aside);
          const pre = main.querySelector(".tty pre");
          if (pre) pre.scrollTop = pre.scrollHeight;
          main.querySelector("#term-input")?.focus({ preventScroll: true });
        },
      },
      h(
        "label",
        { for: "term-input", class: "term-prompt" },
        h("span", { "aria-hidden": "true", text: "$" }),
        h("span", { class: "vh", text: "Command" }),
      ),
      input,
      SD.ui.button("Run", { kind: "primary", type: "submit" }),
    );
    main.replaceChildren(
      h(
        "p",
        { class: "fine", id: "term-help" },
        SD.labs.codeText(
          "Type `cd`, `pwd`, `ls` or `ls -a`, then Enter. ↑ brings back the last command, as in a real terminal.",
        ),
      ),
      transcript,
      form,
      h("p", { class: "notice term-note", "aria-live": "polite", text: e.note, hidden: !e.note }),
      h(
        "div",
        { class: "actions" },
        SD.ui.button("Start again", {
          kind: "quiet",
          onClick: () => {
            page.explore = { state: START, lines: [], history: [], note: "" };
            renderExplore(main, aside);
          },
        }),
      ),
    );
    aside.replaceChildren(
      tree([
        [e.state.pwd, "pwd"],
        [e.state.oldpwd, "OLDPWD"],
      ]),
    );
    main.next = null;
  }

  SD.labs.paths = {
    title: "Paths",
    render(root) {
      const main = h("div", { class: "path-main" });
      const aside = h("div", { class: "path-tree", role: "region", "aria-label": "Folder tree" });
      const tabs = [
        ["drill", "Predict pwd"],
        ["explore", "Explore"],
      ].map(([id, label]) =>
        h("button", {
          type: "button",
          class: "seg-btn",
          "aria-pressed": String(page.tab === id),
          text: label,
          onclick: () => {
            page.tab = id;
            tabs.forEach((b, i) => b.setAttribute("aria-pressed", String(["drill", "explore"][i] === id)));
            paint();
          },
        }),
      );
      const paint = () => (page.tab === "drill" ? renderDrill(main, aside) : renderExplore(main, aside));
      root.append(
        h(
          "div",
          { class: "page page-wide lab" },
          SD.labs.head("paths", "Paths"),
          h(
            "p",
            { class: "lead" },
            SD.labs.codeText(
              "One tree under `/`, a current directory and the one before it. Say where `cd` takes you, the " +
                "way bash does it, including when it refuses.",
            ),
          ),
          h("div", { class: "seg lab-tabs", role: "group", "aria-label": "Mode" }, tabs),
          h("div", { class: "path-layout" }, main, aside),
        ),
      );
      paint();
      return {
        title: "Paths · Terminal lab",
        resume: "Terminal lab: paths",
        onKey(event) {
          if (event.key !== "Enter" || typeof main.next !== "function") return false;
          main.next();
          return true;
        },
      };
    },
  };
})();
