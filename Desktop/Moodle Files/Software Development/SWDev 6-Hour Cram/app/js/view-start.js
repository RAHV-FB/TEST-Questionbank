// "How he marks": the box on the route page, and the page of the same name (the first stop). His
// marking guide word for word, the answer formula, the multiple-choice strategy, a 60-minute plan
// and the nine sample questions with the stop that teaches each.
CR.examBox = () => {
  const { h } = CR.dom;
  const intro = CR.data.intro;
  const typeLinks = (tids) =>
    tids.map((tid, i) => [
      i > 0 ? ", " : null,
      CR.data.type(tid) ? h("a", { href: CR.route.href("type", tid), text: CR.ui.typeLabel(tid) }) : h("span", { text: tid }),
    ]);
  return h(
    "div",
    { class: "exam-box" },
    h(
      "dl",
      { class: "facts" },
      intro.facts.map((f) => h("div", { class: "fact" }, h("dt", { class: "label", text: f.label }), h("dd", { class: "prose", html: f.value_html }))),
    ),
    h("div", { class: "note note-exam" }, h("p", { class: "label", text: "His limits" }), h("div", { class: "prose", html: intro.limits_html })),
    h("h3", { text: "How the open questions are marked" }),
    h("div", { class: "prose fine-prose", html: intro.marking.intro_html }),
    CR.ui.markingGuide(),
    h("h3", { text: "The answer formula" }),
    h("p", { class: "fine", text: "Every open part, in one or two sentences. The reason is the part that scores." }),
    h(
      "ol",
      { class: "formula" },
      intro.formula.map((f) => h("li", {}, h("span", { class: "formula-label", text: f.label }), h("span", { class: "prose", html: f.text_html }))),
    ),
    h("h3", { text: "Multiple choice" }),
    h("ul", { class: "prose technique" }, intro.mcq.map((t) => h("li", { html: t }))),
    h("h3", { text: "A 60-minute plan" }),
    h(
      "ol",
      { class: "plan" },
      intro.plan.map((p) =>
        h("li", {}, h("span", { class: "plan-min", text: `${p.minutes} min` }), h("span", { class: "plan-label", text: p.label }), h("span", { class: "prose", html: p.text_html })),
      ),
    ),
    h("h3", { text: "His nine sample questions" }),
    h("p", { class: "fine", text: "Six multiple choice, three open. The exam does not reuse them; it asks the same kinds of question. Each has a stop that starts from his question." }),
    h(
      "ol",
      { class: "shapes" },
      intro.shapes.map((s) =>
        h(
          "li",
          { class: "shape" },
          h("span", { class: "shape-n", text: `Q${s.n}` }),
          CR.ui.chip(s.type === "mcq" ? "multiple choice" : "open", s.type === "mcq" ? "none" : "warn"),
          h("span", { class: "shape-ask prose", html: s.ask_html }),
          h("span", { class: "shape-links fine" }, "Stop: ", typeLinks(s.tids)),
        ),
      ),
    ),
  );
};

CR.router.register("start", {
  nav: "home",
  render({ root }) {
    const { h } = CR.dom;
    const stop = CR.data.stop("intro-intro");
    const done = stop ? CR.clock.isDone(CR.store.get().done, stop.id) : false;
    const toggle = CR.ui.button(done ? "Marked done" : "Mark done and go on", {
      kind: "primary",
      onClick: () => {
        if (stop) CR.store.setDone(stop.id, true);
        CR.router.go("home");
      },
    });
    root.append(
      h(
        "div",
        { class: "page" },
        CR.ui.crumbs([["Route", "#home"], ["How he marks"]]),
        h("h1", { text: "How he marks" }),
        h("p", { class: "lead", text: "What he looks for, in one page. Read it once, then start the route." }),
        CR.examBox(),
        h("div", { class: "actions" }, toggle, CR.ui.linkButton("Back to the route", "#home", "quiet")),
      ),
    );
    return { title: "How he marks" };
  },
});
