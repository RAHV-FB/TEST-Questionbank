// Pipelines lab (#labs.pipes, #labs.pipes.<id>): the pipes-bash module's pipelines run stage by
// stage on its sample file. Before each output is shown the student may write a prediction,
// which is then compared line by line with the real output.
(() => {
  const { h } = SD.dom;
  const steps = new Map(); // pipeline id -> {revealed, predictions: []}

  const module = () => SD.data.module("pipes-bash");
  const doneMap = () => SD.store.draft("labs.pipes") || {};

  function markDone(id) {
    SD.store.setDraft("labs.pipes", { ...doneMap(), [id]: Date.now() });
  }

  // The command so far, the newest stage marked.
  function commandLine(stages, i) {
    const before = i > 0 ? SD.pipes.upTo(stages, i - 1) + " " : "";
    return SD.labs.term([{ cmd: [before, h("mark", { class: "pipe-new", text: stages[i].cmd.trim() })] }]);
  }

  function renderList(root) {
    const mod = module();
    const done = doneMap();
    root.append(
      h(
        "div",
        { class: "page page-wide lab" },
        SD.labs.head("pipes", "Pipelines"),
        mod
          ? [
              mod.predicted ? SD.ui.predictedNote() : null,
              h("p", {
                class: "lead",
                text:
                  "Each pipeline answers one question about expenses.csv. Run it one stage at a time: " +
                  "say what the next stage prints, then see it.",
              }),
              h(
                "ol",
                { class: "link-list pipe-list" },
                mod.pipelines.map((p, i) =>
                  h(
                    "li",
                    {},
                    h(
                      "a",
                      { href: SD.route.href("labs", "pipes", p.id) },
                      h(
                        "span",
                        { class: "link-title" },
                        h("span", { class: "pipe-n", text: `${i + 1}` }),
                        p.title,
                        done[p.id]
                          ? h("span", { class: "pipe-done" }, SD.ui.statusMark("pass", "stepped through"))
                          : null,
                      ),
                      h("span", { class: "fine", text: SD.dom.excerpt(p.goal_html, 140) }),
                      h("span", { class: "meta-line", text: SD.util.plural(p.stages.length, "stage") }),
                    ),
                  ),
                ),
              ),
            ]
          : SD.ui.empty(
              "The pipes module is not in this build.",
              "Rebuild the page once content/pipes-bash.json exists.",
              null,
            ),
      ),
    );
    return { title: "Pipelines · Terminal lab", resume: "Terminal lab: pipelines", live: true };
  }

  function renderStepper(root, mod, p) {
    if (!steps.has(p.id)) steps.set(p.id, { revealed: 0, predictions: [] });
    const s = steps.get(p.id);
    const list = mod.pipelines;
    const at = list.indexOf(p);
    const nextP = list[at + 1] || null;
    const stagesEl = h("ol", { class: "pipe-stages" });
    const endEl = h("div");
    const showAll = SD.ui.button("Show every stage", {
      kind: "quiet",
      onClick: () => {
        s.revealed = p.stages.length;
        paint();
      },
    });

    function reveal(i, textarea) {
      s.predictions[i] = textarea ? textarea.value : "";
      s.revealed = i + 1;
      if (s.predictions[i].trim()) {
        const c = SD.pipes.compare(s.predictions[i], p.stages[i].output);
        SD.dom.announce(
          c.exact ? "Your prediction matches." : `${c.matched} of ${c.total} lines as predicted.`,
        );
      }
      paint();
      stagesEl.querySelectorAll(".pipe-stage")[i]?.querySelector("pre")?.focus({ preventScroll: true });
    }

    function stageItem(stage, i) {
      const label = h("p", { class: "label", text: `Stage ${i + 1} of ${p.stages.length}` });
      if (i < s.revealed) {
        const prediction = s.predictions[i] || "";
        return h(
          "li",
          { class: "pipe-stage" },
          label,
          commandLine(p.stages, i),
          SD.labs.outputBlock(stage.output),
          prediction.trim() ? SD.labs.comparison(prediction, stage.output) : null,
          h("div", { class: "prose pipe-explain", html: stage.explain_html }),
        );
      }
      const id = `predict-${i}`;
      const area = h("textarea", {
        id,
        class: "predict",
        rows: "3",
        autocomplete: "off",
        autocapitalize: "off",
        spellcheck: "false",
        "aria-describedby": `${id}-help`,
      });
      area.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          reveal(i, area);
        }
      });
      return h(
        "li",
        { class: "pipe-stage is-current" },
        label,
        commandLine(p.stages, i),
        h(
          "div",
          { class: "field" },
          h("label", {
            for: id,
            text: i === 0 ? "What will this print? Predict first." : "What will the pipeline print now?",
          }),
          area,
          h("p", {
            class: "field-hint",
            id: `${id}-help`,
            text: "Optional, one line per output line. Ctrl+Enter (⌘+Enter on a Mac) shows the output.",
          }),
        ),
        h(
          "div",
          { class: "actions" },
          SD.ui.button("Show the output", { kind: "primary", onClick: () => reveal(i, area) }),
        ),
      );
    }

    function paint() {
      const shown = p.stages.slice(0, Math.min(s.revealed + 1, p.stages.length));
      stagesEl.replaceChildren(...shown.map(stageItem));
      showAll.hidden = s.revealed >= p.stages.length;
      if (s.revealed < p.stages.length) {
        endEl.replaceChildren();
        return;
      }
      if (!doneMap()[p.id]) markDone(p.id);
      SD.dom.fill(
        endEl,
        SD.ui.note("Takeaway", p.takeaway_html, "exam"),
        h(
          "div",
          { class: "actions" },
          nextP
            ? SD.ui.linkButton(`Next: ${nextP.title}`, SD.route.href("labs", "pipes", nextP.id), "primary")
            : SD.ui.linkButton("All pipelines", "#labs.pipes", "primary"),
          SD.ui.button("Start again", {
            kind: "quiet",
            onClick: () => {
              steps.set(p.id, { revealed: 0, predictions: [] });
              SD.router.refresh();
            },
          }),
        ),
      );
    }

    root.append(
      h(
        "div",
        { class: "page lab" },
        SD.labs.head("pipes", p.title, [["Pipelines", "#labs.pipes"]]),
        mod.predicted ? SD.ui.predictedNote() : null,
        h("div", { class: "prose pipe-goal", html: p.goal_html }),
        Object.entries(mod.sample_files).map(([name, text]) =>
          h(
            "details",
            { class: "pipe-file", open: true },
            h(
              "summary",
              {},
              h("span", { class: "mono", text: name }),
              " ",
              h("span", { class: "fine", text: SD.util.plural(SD.pipes.lines(text).length, "line") }),
            ),
            h(
              "div",
              { class: "code" },
              h("span", { class: "code-lang", "aria-hidden": "true", text: name }),
              h("pre", { tabindex: "0" }, h("code", { text: text.replace(/\n$/, "") })),
            ),
          ),
        ),
        h(
          "div",
          { class: "pipe-bar" },
          h("h2", { class: "pipe-run", text: "Run it stage by stage" }),
          showAll,
        ),
        stagesEl,
        endEl,
      ),
    );
    paint();
    return {
      title: `${p.title} · Pipelines`,
      resume: `Pipeline: ${p.title}`,
      onKey(event) {
        if (event.key !== "Enter" || s.revealed >= p.stages.length) return false;
        reveal(s.revealed, stagesEl.querySelector("textarea"));
        return true;
      },
    };
  }

  SD.labs.pipes = {
    title: "Pipelines",
    render(root, args) {
      const mod = module();
      const p = mod && args[0] ? mod.pipelines.find((x) => x.id === args[0]) : null;
      if (mod && args[0] && !p) {
        root.append(
          h(
            "div",
            { class: "page" },
            h("h1", { text: "No such pipeline" }),
            SD.ui.empty(
              `There is no pipeline called "${args[0]}".`,
              "Pick one from the list.",
              SD.ui.linkButton("All pipelines", "#labs.pipes", "primary"),
            ),
          ),
        );
        return { title: "Pipelines" };
      }
      return p ? renderStepper(root, mod, p) : renderList(root);
    },
  };
})();
