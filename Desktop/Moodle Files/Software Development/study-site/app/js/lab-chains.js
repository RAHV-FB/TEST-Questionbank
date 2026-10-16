// Exit codes lab (#labs.chains): commands with given exit statuses joined by &&, || and ; (one
// line) or run as a script with or without set -e. Tick the commands that run, say what echo $?
// prints, then see each command's reason. Course examples first, then generated practice.
(() => {
  const { h } = SD.dom;
  const C = SD.chains;
  const MODES = [
    ["line", "One line"],
    ["script", "Scripts"],
  ];
  const SOURCES = [
    ["examples", "Course examples"],
    ["practice", "Random drill"],
  ];
  const page = {
    mode: "line",
    source: "examples",
    index: { line: 0, script: 0 },
    task: null,
    runs: [],
    status: "",
    checked: false,
  };

  const examples = (mode) => C.EXAMPLES.filter((ex) => ex.mode === mode);

  function loadTask() {
    if (page.source === "examples") {
      const list = examples(page.mode);
      const ex = list[page.index[page.mode] % list.length];
      page.task = {
        ...ex,
        parsed: C.parse(ex.text),
        number: (page.index[page.mode] % list.length) + 1,
        of: list.length,
      };
    } else {
      page.task = C.drill(page.mode, SD.labs.random());
    }
    page.runs = page.task.parsed.commands.map(() => false);
    page.status = "";
    page.checked = false;
  }

  function artefact(t) {
    if (t.mode === "line") return SD.labs.term([{ cmd: t.text }, { cmd: "echo $?" }]);
    return h(
      "div",
      {},
      h(
        "div",
        { class: "code" },
        h("span", { class: "code-lang", "aria-hidden": "true", text: "scripts/check.sh" }),
        h("pre", { tabindex: "0" }, h("code", { text: t.text })),
      ),
      SD.labs.term([{ cmd: "./scripts/check.sh" }, { cmd: "echo $?" }]),
    );
  }

  const exitChip = (status) => SD.ui.chip(`exit ${status}`, status === 0 ? "pass" : "fail");

  function render(root) {
    if (!page.task) loadTask();
    const t = page.task;
    const result = C.evaluate(t.parsed, t.statuses);
    const box = h("div", { class: "chain-task" });
    const statusInput = h("input", {
      type: "text",
      id: "chain-status",
      class: "mono-input",
      inputmode: "numeric",
      autocomplete: "off",
      maxlength: "3",
      value: page.status,
      disabled: page.checked,
    });
    statusInput.addEventListener("input", () => (page.status = statusInput.value));
    const out = h("div", { class: "drill-out", "aria-live": "polite" });
    const verdictBox = h("div", { "aria-live": "polite" });
    const check = page.checked ? C.check(result, { runs: page.runs, status: page.status }) : null;

    const rows = t.parsed.commands.map((cmd, i) => {
      const step = result.steps[i];
      const id = `chain-run-${i}`;
      const tick = h("input", {
        type: "checkbox",
        id,
        checked: page.runs[i],
        disabled: page.checked,
        onchange: (e) => (page.runs[i] = e.target.checked),
      });
      const after = page.checked
        ? h(
            "div",
            { class: "chain-why" },
            h(
              "p",
              { class: "chain-fact" },
              step.ran
                ? h("span", {}, "ran ", exitChip(step.status))
                : h("span", { class: "chain-skipped", text: "did not run" }),
              h(
                "span",
                { class: `tick-verdict ${check.runs[i] ? "py-pass" : "py-fail"}` },
                SD.ui.mark(check.runs[i] ? "pass" : "fail"),
                check.runs[i] ? "your tick is right" : "your tick is wrong",
              ),
            ),
            h("p", {}, SD.labs.codeText(C.explain(t.parsed, step))),
            C.errexitNote(t.parsed, step)
              ? h("p", { class: "chain-errexit" }, SD.labs.codeText(C.errexitNote(t.parsed, step)))
              : null,
          )
        : null;
      return h(
        "li",
        { class: `chain-row${page.checked && !step.ran ? " is-skipped" : ""}` },
        tick,
        h("label", { for: id, class: "chain-cmd" }, h("code", { text: cmd })),
        h(
          "span",
          { class: "chain-given" },
          h("span", { class: "vh", text: "would exit with " }),
          exitChip(t.statuses[i]),
        ),
        after,
      );
    });

    const button = SD.ui.button(
      page.checked ? (page.source === "examples" ? "Next example" : "Next task") : "Check",
      { kind: "primary", type: "submit" },
    );
    const form = h(
      "form",
      {
        class: "drill-form",
        onsubmit: (event) => {
          event.preventDefault();
          if (page.checked) next();
          else submit();
        },
      },
      h("p", {
        class: "drill-ask",
        text: "Suppose each command, if it runs, exits with the status shown. Tick the ones that run.",
      }),
      h("ul", { class: "chain-rows" }, rows),
      h(
        "div",
        { class: "field chain-status" },
        h("label", { for: "chain-status" }, h("code", { text: "echo $?" }), " prints"),
        statusInput,
      ),
      verdictBox,
      out,
      h("div", { class: "actions" }, button),
    );

    function submit() {
      if (!/^\s*\d+\s*$/.test(statusInput.value)) {
        verdictBox.replaceChildren(
          h("p", { class: "notice", text: "Write the number echo $? prints, for example 0 or 1." }),
        );
        statusInput.focus();
        return;
      }
      page.checked = true;
      const c = C.check(result, { runs: page.runs, status: page.status });
      SD.labs.count("chains", c.ok);
      SD.dom.announce(c.ok ? "Right." : "Not quite.");
      repaint();
      root.querySelector(".chain-task .drill-form .btn-primary")?.focus({ preventScroll: true });
    }

    function next() {
      if (page.source === "examples") page.index[page.mode] += 1;
      loadTask();
      repaint();
      root.querySelector(".chain-task input")?.focus({ preventScroll: true });
    }

    function repaint() {
      box.replaceWith(render(root));
    }

    if (check) {
      const wrongTicks = check.runs.filter((ok) => !ok).length;
      const parts = [
        wrongTicks ? `${SD.util.plural(wrongTicks, "tick")} wrong` : "every tick right",
        check.statusOk ? `$? right` : `$? is ${result.status}`,
      ];
      verdictBox.replaceChildren(
        SD.ui.verdict(check.ok, `${check.ok ? "Right" : "Not quite"}: ${parts.join(", ")}.`),
      );
      const groups = t.parsed.lists.map((list) => C.grouped(t.parsed, list)).filter(Boolean);
      SD.dom.fill(
        out,
        groups.length
          ? h(
              "p",
              { class: "chain-group" },
              h("span", { class: "label", text: "bash reads it as" }),
              groups.map((g) => h("code", { class: "chain-grouped", text: g })),
            )
          : null,
        h("p", {}, SD.labs.codeText(C.finalNote(t.parsed, result))),
        t.lesson
          ? h(
              "div",
              { class: "note note-exam" },
              h("p", { class: "label", text: "What this shows" }),
              h("p", { text: t.lesson }),
            )
          : null,
      );
    }

    box.append(
      h("p", { class: "fine", text: SD.labs.tallyText("chains") }),
      t.title
        ? h("p", { class: "label", text: `Example ${t.number} of ${t.of}` })
        : h("p", { class: "label", text: "Random drill" }),
      t.title ? h("h2", { class: "chain-title", text: t.title }) : null,
      artefact(t),
      form,
    );
    box.next = () => (page.checked ? next() : submit());
    return box;
  }

  // A labelled choice between a few options. Picking one repaints only the task below, so the
  // student keeps their place and the focus stays on the button just pressed.
  function segs(list, key, label, onPick) {
    const id = `chains-${key}`;
    const buttons = list.map(([value, text]) =>
      h("button", {
        type: "button",
        class: "seg-btn",
        "aria-pressed": String(page[key] === value),
        text,
        onclick: () => {
          if (page[key] === value) return;
          onPick(value);
          buttons.forEach((b, i) => b.setAttribute("aria-pressed", String(page[key] === list[i][0])));
          SD.dom.announce(`${label}: ${text}`);
        },
      }),
    );
    return h(
      "div",
      { class: "chain-control" },
      h("p", { class: "label", id }, label),
      h("div", { class: "seg", role: "group", "aria-labelledby": id }, buttons),
    );
  }

  SD.labs.chains = {
    title: "Exit codes",
    render(root) {
      const pick = (key) => (id) => {
        page[key] = id;
        page.task = null;
        root.querySelector(".chain-task")?.replaceWith(render(root));
      };
      root.append(
        h(
          "div",
          { class: "page page-wide lab" },
          SD.labs.head("chains", "Exit codes"),
          h(
            "p",
            { class: "lead" },
            SD.labs.codeText(
              "Every command leaves a number: 0 is success, anything else is failure. `&&` runs the next " +
                "command only after a 0, `||` only after a failure, `;` always. With `set -e` a script stops " +
                "at the first failure that is not a test.",
            ),
          ),
          h(
            "div",
            { class: "chain-controls" },
            segs(MODES, "mode", "Kind", pick("mode")),
            segs(SOURCES, "source", "Source", pick("source")),
          ),
          render(root),
        ),
      );
      return {
        title: "Exit codes · Terminal lab",
        resume: "Terminal lab: exit codes",
        onKey(event) {
          const task = root.querySelector(".chain-task");
          if (event.key !== "Enter" || !task) return false;
          task.next();
          return true;
        },
      };
    },
  };
})();
