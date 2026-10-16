// Shared pieces of the terminal lab (#labs...): the lab switcher, terminal transcripts, command
// output and the prediction comparison, text with `code` spans, drill tallies and the random source.
// Each lab-*.js adds its page to SD.labs.
SD.labs = (() => {
  const { h } = SD.dom;
  const LABS = [
    ["pipes", "Pipelines"],
    ["perms", "Permissions"],
    ["paths", "Paths"],
    ["chains", "Exit codes"],
    ["lab10", "Lab 10, solved"],
  ];
  let seed = Date.now() >>> 0;

  // A fresh random source for drills (seeded, so the pure generators stay testable).
  const random = () => SD.util.seededRandom((seed = (seed + 0x9e3779b9) >>> 0));

  // The switch between the labs and the page heading; crumbs only on a page below a lab
  // (a pipeline), where the switch does not say where you are.
  function head(current, title, crumbs = []) {
    return [
      crumbs.length ? SD.ui.crumbs([["Terminal lab", "#labs"], ...crumbs, [title]]) : null,
      h(
        "nav",
        { class: "lab-nav", "aria-label": "Labs" },
        LABS.map(([id, label]) =>
          h("a", {
            href: SD.route.href("labs", id),
            "aria-current": id === current ? "page" : null,
            text: label,
          }),
        ),
      ),
      h("h1", { text: title }),
    ];
  }

  // A terminal transcript in the code frame: [{cmd}, {out}, {err}] lines; cmd may hold nodes.
  function term(lines, { label = "terminal", live = false } = {}) {
    const code = h(
      "code",
      {},
      lines.map((line) => {
        if ("cmd" in line)
          return h("span", { class: "t-line" }, h("span", { class: "gp", text: "$ " }), line.cmd, "\n");
        if ("err" in line) return h("span", { class: "t-line t-err", text: `${line.err}\n` });
        return h("span", { class: "t-line", text: `${line.out}\n` });
      }),
    );
    return h(
      "div",
      { class: "code tty" },
      h("span", { class: "code-lang", "aria-hidden": "true", text: label }),
      h("pre", { tabindex: "0", "aria-live": live ? "polite" : null }, code),
    );
  }

  // The output of a command in the code frame (plain text, never parsed as HTML); no output at all
  // says so.
  function outputBlock(text) {
    if (text === "") return h("p", { class: "pipe-empty", text: "(no output)" });
    return h(
      "div",
      { class: "code" },
      h("span", { class: "code-lang", "aria-hidden": "true", text: "output" }),
      h("pre", { tabindex: "0" }, h("code", { text })),
    );
  }

  // A typed prediction against the real output: the verdict line and, when they differ, the line
  // diff (SD.pipes.compare), with its key.
  function comparison(prediction, output) {
    const c = SD.pipes.compare(prediction, output);
    const text = c.exact
      ? "Your prediction matches the output."
      : c.total
        ? `${c.matched} of ${SD.util.plural(c.total, "line")} as you predicted.`
        : "There is no output at all.";
    return h(
      "div",
      { class: "pipe-compare" },
      SD.ui.verdict(c.exact, text),
      c.exact
        ? null
        : h(
            "div",
            {},
            h(
              "div",
              { class: "code" },
              h("span", { class: "code-lang", "aria-hidden": "true", text: "prediction vs output" }),
              h(
                "pre",
                { tabindex: "0" },
                h(
                  "code",
                  {},
                  c.rows.map((row) => {
                    const [cls, sign] = {
                      same: ["d-ctx", " "],
                      missing: ["d-add", "+"],
                      extra: ["d-del", "-"],
                    }[row.kind];
                    return h("span", { class: `dline ${cls}`, text: `${sign} ${row.text}` });
                  }),
                ),
              ),
            ),
            h("p", {
              class: "fine",
              text:
                "- a line you predicted that is not in the output · + a line of the output you did not " +
                "predict. Spacing is ignored.",
            }),
          ),
    );
  }

  // "Run `uv run pytest` first" -> text and <code> nodes (the text is never parsed as HTML).
  function codeText(text) {
    return String(text)
      .split(/(`[^`]*`)/)
      .filter(Boolean)
      .map((part) =>
        part.startsWith("`") && part.endsWith("`") ? h("code", { text: part.slice(1, -1) }) : part,
      );
  }

  // Drill tallies, kept with the progress (they sync): drafts "labs.<name>" = {right, total}.
  function tally(name) {
    const t = SD.store.draft(`labs.${name}`);
    return t && Number.isInteger(t.right) && Number.isInteger(t.total) ? t : { right: 0, total: 0 };
  }

  function count(name, ok) {
    const t = tally(name);
    SD.store.setDraft(`labs.${name}`, { right: t.right + (ok ? 1 : 0), total: t.total + 1 });
  }

  function tallyText(name) {
    const t = tally(name);
    return t.total ? `${t.right} of ${t.total} right so far` : "No answers yet";
  }

  return { LABS, random, head, term, outputBlock, comparison, codeText, tally, count, tallyText };
})();
