// The mistakes, the breaks and the last page (the answer formula, final check).
(() => {
  const { h } = CR.dom;

  const notFound = (root, text) => {
    root.append(h("div", { class: "page" }, h("h1", { text: "Nothing at this address" }), h("p", { text }), h("p", {}, h("a", { href: "#home", text: "Back to the route" }))));
    return { title: "Not found" };
  };

  // A button that ticks a stop done and goes to the next one.
  function doneButton(stopId, label = "Done, go on", kind = "primary") {
    return CR.ui.button(label, {
      kind,
      onClick: () => {
        CR.store.setDone(stopId, true);
        const next = CR.clock.after(CR.data.stops, CR.store.get().done, stopId);
        CR.router.go(next ? CR.route.stopRoute(next) : "home");
      },
    });
  }

  // ------------------------------------------------------------------ mistakes

  function startRedo(ids) {
    CR.store.startSession("mistakes", CR.mistakes.newSession(ids, Date.now()));
    CR.router.go("mistakes.redo");
  }

  function queueIds() {
    return CR.mistakes.queue(CR.store.get().q, CR.data.knownIds);
  }

  function mistakesList({ root }) {
    const q = CR.store.get().q;
    const ids = queueIds();
    const cleared = Object.keys(q).filter((id) => CR.data.knownIds.has(id) && q[id].ok).length;
    // Groups in the order of the route (S1 to S9, then P1 to P4).
    const order = (tid) => {
      const at = CR.data.stops.findIndex((s) => s.kind === "type" && s.ref === tid);
      return at === -1 ? 999 : at;
    };
    const groups = CR.mistakes.groupBy(ids, (id) => CR.data.question(id).tid).sort((a, b) => order(a[0]) - order(b[0]) || (a[0] < b[0] ? -1 : 1));
    root.append(
      h(
        "div",
        { class: "page" },
        CR.ui.crumbs([["Route", "#home"], ["Mistakes"]]),
        h("h1", { text: "Mistakes" }),
        h("p", { class: "lead", text: "Every question your latest attempt got wrong, from practice and from papers. Redo them until the list is empty: a right answer takes a question off it." }),
        ids.length === 0
          ? CR.ui.empty("Nothing to redo yet", cleared > 0 ? `${CR.util.plural(cleared, "question")} answered right. Mistakes from practice and papers will collect here.` : "Mistakes from practice and papers will collect here.", CR.ui.linkButton("Back to the route", "#home", "primary"))
          : [
              h("p", { class: "pytest" }, h("span", { class: "py-fail", text: `${ids.length} to redo` }), h("span", { text: `, ${cleared} cleared` })),
              h("div", { class: "actions" }, CR.ui.button(`Redo all ${ids.length}`, { kind: "primary", onClick: () => startRedo(ids) })),
              groups.map(([tid, list]) =>
                h(
                  "section",
                  { class: "mistake-group" },
                  h(
                    "div",
                    { class: "block-head" },
                    h("h2", { text: CR.ui.typeLabel(tid) }),
                    groups.length > 1 ? CR.ui.button(`Redo these ${list.length}`, { kind: "secondary", onClick: () => startRedo(list) }) : null,
                  ),
                  h(
                    "ul",
                    { class: "result-list" },
                    list.map((id) =>
                      h(
                        "li",
                        { class: "result-item" },
                        h(
                          "a",
                          { class: "result-row", href: CR.route.href("q", id, "review") },
                          CR.ui.statusMark("fail", "wrong"),
                          h("span", { class: "result-text", text: CR.dom.excerpt(CR.data.question(id).stem_html, 120) }),
                        ),
                        h("p", { class: "result-revise", text: q[id].w > 1 ? `Wrong ${q[id].w} times` : "Wrong once" }),
                      ),
                    ),
                  ),
                ),
              ),
            ],
      ),
    );
    return { title: "Mistakes" };
  }

  function mistakesRedo({ root }) {
    const stop = CR.data.stop("mistakes-redo");
    return CR.practice.run(root, {
      key: "mistakes",
      ids: queueIds,
      heading: "Redo your mistakes",
      crumbs: [["Route", "#home"], ["Mistakes", "#mistakes"], ["Redo"]],
      emptyText: "You have no mistakes to redo. Practise a type or sit a paper first.",
      finish: (clean) => (stop ? doneButton(stop.id, "Mark done and go on", clean ? "primary" : "secondary") : CR.ui.linkButton("Back to the route", "#home", "secondary")),
    });
  }

  CR.router.register("mistakes", {
    nav: "mistakes",
    render: (ctx) => (ctx.args[0] === "redo" ? mistakesRedo(ctx) : mistakesList(ctx)),
  });

  // ------------------------------------------------------------------ break

  CR.router.register("break", {
    nav: "home",
    render({ root, args }) {
      const stop = CR.data.stops.find((s) => s.kind === "break" && s.ref === args[0]);
      if (!stop) return notFound(root, `There is no break called "${args[0]}".`);
      const readout = h("p", { class: "figure-value break-clock", role: "timer", "aria-live": "off", text: `${stop.minutes}:00` });
      const status = h("p", { class: "fine", "aria-live": "polite" });
      let timer = null;
      const startButton = CR.ui.button(`Start a ${stop.minutes}-minute timer`, {
        kind: "secondary",
        onClick: () => {
          const end = Date.now() + stop.minutes * CR.util.MINUTE;
          startButton.disabled = true;
          const tick = () => {
            const left = end - Date.now();
            readout.textContent = CR.util.clock(left);
            if (left <= 0) {
              window.clearInterval(timer);
              status.textContent = "Break over. Back to the route.";
              CR.dom.announce("Break over.");
              startButton.disabled = false;
            }
          };
          status.textContent = "";
          tick();
          timer = window.setInterval(tick, 1000);
        },
      });
      root.append(
        h(
          "div",
          { class: "page" },
          CR.ui.crumbs([["Route", "#home"], ["Break"]]),
          h("h1", { text: "Break" }),
          h("p", { class: "lead", text: stop.note }),
          readout,
          status,
          h("ul", { class: "prose break-list" }, ["Stand up and walk. Drink water.", "Eat something that is not sugar.", "Do not read notes. The next block starts clean."].map((t) => h("li", { text: t }))),
          h("div", { class: "actions" }, startButton, doneButton(stop.id, "Break over, go on")),
        ),
      );
      return {
        title: "Break",
        cleanup() {
          window.clearInterval(timer);
        },
      };
    },
  });

  // ------------------------------------------------------------------ final

  CR.router.register("final", {
    nav: "home",
    render({ root }) {
      const stop = CR.data.stop("final-say");
      const types = CR.data.stops.filter((s) => s.kind === "type" && CR.data.type(s.ref)).map((s) => CR.data.type(s.ref));
      const intro = CR.data.intro;
      root.append(
        h(
          "div",
          { class: "page" },
          CR.ui.crumbs([["Route", "#home"], ["The answer formula"]]),
          h("h1", { text: "The answer formula, final check" }),
          h("p", { class: "lead", text: "Every open answer he marks is the same three moves. Read this once, then the phrases for each stop. Use the course's own terms: they are the ones he marks." }),
          h("ol", { class: "formula" }, intro.formula.map((f) => h("li", {}, h("span", { class: "formula-label", text: f.label }), h("span", { class: "prose", html: f.text_html })))),
          CR.ui.markingGuide(),
          h("h2", { text: "Before you walk in" }),
          h("ul", { class: "prose technique", html: intro.mcq.map((t) => `<li>${t}</li>`).join("") }),
          h("h2", { text: "Phrases to write, stop by stop" }),
          types.length === 0 ? CR.ui.empty("No stops in this build", "The lists come from the stop pages.") : null,
          types.map((t) =>
            h(
              "section",
              { class: "say" },
              h("h3", {}, h("a", { href: CR.route.href("type", t.tid), text: CR.ui.typeLabel(t.tid) })),
              h("div", { class: "prose", html: t.say_html }),
            ),
          ),
          h("div", { class: "actions" }, stop ? doneButton(stop.id, "Done. Good luck.") : CR.ui.linkButton("Back to the route", "#home", "primary")),
        ),
      );
      return { title: "The answer formula" };
    },
  });
})();
