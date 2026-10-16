// Lab 10, solved (#labs.lab10): every question of labs/10-wrangling.md answered on the real
// expenses.csv. Each step shows the question and the one pipeline that answers it; the student may
// predict the output, then reveals the real output and the answer. What was predicted and what was
// shown is kept per step (drafts "labs.lab10.<step id>"), so a revision session picks up where the
// last one stopped.
(() => {
  const { h } = SD.dom;
  const L = SD.lab10;

  const walkthrough = () => SD.data.module("pipes-bash")?.lab_walkthrough || null;
  const stored = (id) => L.read(SD.store.draft(L.draftKey(id)));
  const keep = (id, state) => SD.store.setDraft(L.draftKey(id), L.write(state));

  // "$ command" for each line of the pipeline, highlighted at build time (plain text when a build
  // has no pipeline_html).
  function pipelineBlock(step) {
    const rows = step.pipeline_html
      ? step.pipeline_html.map((html) => h("span", { html }))
      : step.pipeline.split("\n");
    return SD.labs.term(rows.map((cmd) => ({ cmd })));
  }

  function renderStep(step, number, of, onChange) {
    const li = h("li", { class: "pipe-stage walk-step", id: `walk-${step.id}` });
    let typed = stored(step.id).prediction;

    function reveal(area) {
      typed = area ? area.value : typed;
      keep(step.id, { shown: true, prediction: typed });
      if (typed.trim() && !L.isTrimmed(step.output)) {
        const c = SD.pipes.compare(typed, step.output);
        SD.dom.announce(c.exact ? "Your prediction matches." : `${c.matched} of ${c.total} lines as predicted.`);
      }
      paint();
      SD.dom.reveal(li.querySelector(".walk-result"));
      onChange();
    }

    function hide() {
      keep(step.id, { shown: false, prediction: typed });
      paint();
      li.querySelector("textarea")?.focus({ preventScroll: true });
      onChange();
    }

    function question() {
      return [
        h("p", { class: "label", text: L.stepLabel(number, of) }),
        h("div", { class: "prose walk-q", html: step.prompt_html }),
        pipelineBlock(step),
      ];
    }

    function hiddenState() {
      const id = `predict-${step.id}`;
      const area = h("textarea", {
        id,
        class: "predict",
        rows: "3",
        autocomplete: "off",
        autocapitalize: "off",
        spellcheck: "false",
        "aria-describedby": `${id}-help`,
      });
      area.value = typed;
      area.addEventListener("input", () => {
        typed = area.value;
        keep(step.id, { shown: false, prediction: typed });
      });
      area.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          reveal(area);
        }
      });
      return [
        h(
          "div",
          { class: "field" },
          h("label", { for: id, text: "Predict the output first" }),
          area,
          h("p", {
            class: "field-hint",
            id: `${id}-help`,
            text: "Optional, one line per output line. Ctrl+Enter (⌘+Enter on a Mac) shows the output and the answer.",
          }),
        ),
        h(
          "div",
          { class: "actions" },
          SD.ui.button("Show output and answer", { kind: "primary", onClick: () => reveal(area) }),
        ),
      ];
    }

    function shownState() {
      const trimmed = L.isTrimmed(step.output);
      return h(
        "div",
        { class: "walk-result", role: "group", "aria-label": "Output and answer" },
        SD.labs.outputBlock(step.output),
        typed.trim() && !trimmed ? SD.labs.comparison(typed, step.output) : null,
        typed.trim() && trimmed
          ? h("p", {
              class: "fine",
              text: "The output is shortened here, so your prediction is not compared line by line.",
            })
          : null,
        SD.ui.note("Answer", step.answer_html, "plain"),
        h("div", { class: "actions" }, SD.ui.button("Hide the answer", { kind: "quiet", onClick: hide })),
      );
    }

    function paint() {
      li.replaceChildren(...question(), ...(stored(step.id).shown ? [shownState()] : hiddenState()));
    }

    paint();
    return li;
  }

  function renderPage(root, walk) {
    const blocks = L.groups(walk);
    const progress = h("p", { class: "meta-line" });
    const hideAll = SD.ui.button("Hide every answer", {
      kind: "quiet",
      onClick: () => {
        for (const { step } of L.steps(walk)) {
          const state = stored(step.id);
          if (state.shown) keep(step.id, { shown: false, prediction: state.prediction });
        }
        SD.router.refresh();
      },
    });

    function count() {
      const t = L.tally(walk, stored);
      progress.textContent = L.tallyText(t);
      hideAll.hidden = t.shown === 0;
    }

    const headings = new Map();
    const sections = blocks.map((block) => {
      const heading = h("h2", { id: `walk-${block.id}`, text: block.title });
      headings.set(block.id, heading);
      return h(
        "section",
        { class: "lab-block", "aria-labelledby": heading.id },
        heading,
        block.intro_html ? h("div", { class: "prose pipe-goal", html: block.intro_html }) : null,
        h(
          "ol",
          { class: "pipe-stages" },
          block.steps.map((step, i) => renderStep(step, i + 1, block.steps.length, count)),
        ),
      );
    });

    const jump = h(
      "nav",
      { class: "walk-jump", "aria-label": "Jump to a part of the lab" },
      blocks.map((block) =>
        SD.ui.button(block.short, {
          kind: "quiet",
          onClick: () => {
            const heading = headings.get(block.id);
            heading.tabIndex = -1;
            heading.focus({ preventScroll: true });
            heading.scrollIntoView({ block: "start" });
          },
        }),
      ),
    );

    root.append(
      h(
        "div",
        { class: "page page-wide lab" },
        SD.labs.head("lab10", walk.title),
        h("div", { class: "prose lead", html: walk.file_note_html }),
        h("div", { class: "walk-meta" }, progress, hideAll),
        jump,
        sections,
      ),
    );
    count();
    return { title: "Lab 10, solved · Terminal lab", resume: "Terminal lab: Lab 10, solved" };
  }

  SD.labs.lab10 = {
    title: "Lab 10, solved",
    render(root) {
      const walk = walkthrough();
      if (walk) return renderPage(root, walk);
      root.append(
        h(
          "div",
          { class: "page lab" },
          SD.labs.head("lab10", "Lab 10, solved"),
          SD.ui.empty(
            "Lab 10 is not in this build.",
            "Rebuild the page once content/pipes-bash.json has its lab_walkthrough.",
            null,
          ),
        ),
      );
      return { title: "Lab 10, solved · Terminal lab" };
    },
  };
})();
