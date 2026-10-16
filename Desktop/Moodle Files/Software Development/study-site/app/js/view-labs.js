// Terminal lab (#labs, #labs.pipes[.<id>], #labs.perms, #labs.paths, #labs.chains, #labs.lab10): the
// index of the five labs, and the route that hands each one its page (lab-*.js).
(() => {
  const { h } = SD.dom;
  const ABOUT = {
    pipes: "Run each pipeline on expenses.csv one stage at a time, predicting every output first.",
    perms: "Switches, numbers and `ls -l` letters, the four modes from the slides, and a drill.",
    paths: "A fixed tree and a `cd` command: say what `pwd` prints, or explore with `cd`, `pwd` and `ls`.",
    chains: "`&&`, `||` and `;` with given exit statuses, and scripts with and without `set -e`.",
    lab10: "Every question of the wrangling lab answered on the real `expenses.csv`: the pipeline, the output, the reason.",
  };

  function progressText(id) {
    if (id === "lab10") {
      const walk = SD.data.module("pipes-bash")?.lab_walkthrough;
      if (!walk) return "Not in this build";
      const read = (stepId) => SD.lab10.read(SD.store.draft(SD.lab10.draftKey(stepId)));
      return SD.lab10.tallyText(SD.lab10.tally(walk, read));
    }
    if (id !== "pipes") return SD.labs.tallyText(id);
    const mod = SD.data.module("pipes-bash");
    if (!mod) return "Not in this build";
    const done = SD.store.draft("labs.pipes") || {};
    const n = mod.pipelines.filter((p) => done[p.id]).length;
    return `${n} of ${SD.util.plural(mod.pipelines.length, "pipeline")} stepped through`;
  }

  function renderIndex(root) {
    const mod = SD.data.module("pipes-bash");
    root.append(
      h(
        "div",
        { class: "page" },
        h("h1", { text: "Terminal lab" }),
        h("p", {
          class: "lead",
          text:
            "Sessions 9 and 10, practised the way the exam asks: read a command and " +
            "say what it does, before the terminal tells you.",
        }),
        h(
          "ul",
          { class: "link-list lab-list" },
          SD.labs.LABS.map(([id, label]) =>
            h(
              "li",
              {},
              h(
                "a",
                { href: SD.route.href("labs", id) },
                h(
                  "span",
                  { class: "link-title" },
                  label,
                  id === "pipes" && mod?.predicted ? SD.ui.chip("predicted", "warn") : null,
                ),
                h("span", { class: "fine" }, SD.labs.codeText(ABOUT[id])),
                h("span", { class: "meta-line", text: progressText(id) }),
              ),
            ),
          ),
        ),
      ),
    );
    return { title: "Terminal lab", live: true };
  }

  SD.router.register("labs", {
    render({ root, args }) {
      const lab = args[0] ? SD.labs[args[0]] : null;
      if (args[0] && (!lab || !SD.labs.LABS.some(([id]) => id === args[0]))) {
        root.append(
          h(
            "div",
            { class: "page" },
            h("h1", { text: "No such lab" }),
            SD.ui.empty(
              `There is no lab called "${args[0]}".`,
              "The terminal lab has five parts.",
              SD.ui.linkButton("Terminal lab", "#labs", "primary"),
            ),
          ),
        );
        return { title: "Terminal lab" };
      }
      return lab ? lab.render(root, args.slice(1)) : renderIndex(root);
    },
  });
})();
