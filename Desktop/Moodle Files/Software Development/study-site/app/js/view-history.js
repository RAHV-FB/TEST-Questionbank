// History (#history, #history.<hash>, #history.guess[.<hash>]): the expense-tracker's commits
// as a timeline grouped by tag, one page per commit with its --stat and diff, and the guessing
// game (view-history-guess.js).
(() => {
  const { h } = SD.dom;
  const U = SD.historyUi;
  let kindFilter = null; // a commit kind, or null for every kind

  function lessonLink(ref, text) {
    const section = SD.data.section(ref);
    if (!section) return null;
    return h("a", { href: "#" + SD.data.sectionRoute(ref) }, text, h("span", { html: section.heading_html }));
  }

  function item(commit, mark) {
    return h(
      "li",
      { class: "hist-item" },
      h(
        "a",
        { class: "hist-link", href: SD.route.href("history", commit.hash) },
        h(
          "span",
          { class: "hist-top" },
          h("span", { class: "hist-hash", text: commit.hash }),
          h("span", { class: "hist-date", text: SD.util.dayLabel(Date.parse(commit.git.date)) }),
          U.kindChip(commit.kind),
          commit.tag ? U.tagChip(commit.tag) : null,
          mark === "right"
            ? h("span", { class: "hist-guessed" }, SD.ui.statusMark("pass", "guessed right"))
            : null,
          mark === "wrong"
            ? h("span", { class: "hist-guessed" }, SD.ui.statusMark("fail", "guessed wrong"))
            : null,
        ),
        h("span", { class: "hist-msg", text: commit.message }),
      ),
      h("div", { class: "prose hist-sum", html: commit.summary_html }),
    );
  }

  function renderIndex(root, mod) {
    const commits = mod.commits;
    const record = U.record();
    const tally = SD.history.tally(commits, record);
    const kinds = [...new Set(commits.map((c) => c.kind))];
    const timeline = h("div", { class: "hist-timeline" });
    const count = h("p", { class: "fine", "aria-live": "polite" });
    const first = commits[0];
    const last = commits[commits.length - 1];

    const buttons = [null, ...kinds].map((kind) =>
      h("button", {
        type: "button",
        class: "seg-btn",
        "aria-pressed": String(kindFilter === kind),
        text: kind ? `${kind} ${commits.filter((c) => c.kind === kind).length}` : "All",
        onclick: () => {
          kindFilter = kind;
          buttons.forEach((b, i) => b.setAttribute("aria-pressed", String([null, ...kinds][i] === kind)));
          paint();
        },
      }),
    );

    function paint() {
      const groups = SD.history.groups(commits);
      let shown = 0;
      timeline.replaceChildren(
        ...groups.map((g) => {
          const list = g.commits.filter((c) => !kindFilter || c.kind === kindFilter);
          shown += list.length;
          const tagged = g.commits[g.commits.length - 1];
          return h(
            "section",
            {
              class: "hist-group",
              hidden: list.length === 0,
              "aria-labelledby": `tag-${g.tag || "untagged"}`,
            },
            h(
              "div",
              { class: "hist-group-head" },
              h(
                "h2",
                { id: `tag-${g.tag || "untagged"}` },
                g.tag
                  ? h("span", { class: "hist-tag", text: g.tag })
                  : h("span", { class: "hist-untagged", text: "After the last tag" }),
                g.note ? h("span", { class: "hist-note", text: g.note }) : null,
              ),
              g.tag
                ? h("p", { class: "fine hist-lesson link-line" }, lessonLink(tagged.section_ref, "Lesson: "))
                : null,
            ),
            h(
              "ol",
              { class: "hist-list" },
              list.map((c) => item(c, record[c.hash])),
            ),
          );
        }),
      );
      count.textContent = kindFilter
        ? `${SD.util.plural(shown, `${kindFilter} commit`)} of ${commits.length}.`
        : `${SD.util.plural(commits.length, "commit")}, oldest first.`;
    }

    root.append(
      h(
        "div",
        { class: "page page-wide hist" },
        h("h1", { text: "Expense-tracker history" }),
        h("p", {
          class: "lead",
          text:
            `The demo project, commit by commit, from ${SD.util.dayLabel(Date.parse(first.git.date))} to ` +
            `${SD.util.dayLabel(Date.parse(last.git.date))}. Tags mark where the sessions stop. Open a ` +
            `commit to read its ` +
            "--stat and diff, or guess its message from the diff alone.",
        }),
        h(
          "div",
          { class: "hist-cta" },
          SD.ui.linkButton(
            "Guess the message",
            SD.route.href(
              "history",
              "guess",
              SD.history.next(commits, record, SD.util.seededRandom(Date.now() >>> 0)),
            ),
            "primary",
          ),
          h("span", {
            class: "meta-line",
            text: tally.tried
              ? `${tally.tried} of ${commits.length} tried · ${tally.right} picked right`
              : "Not tried yet",
          }),
        ),
        h(
          "div",
          { class: "seg hist-kinds", role: "group", "aria-label": "Show commits of one kind" },
          buttons,
        ),
        count,
        timeline,
      ),
    );
    paint();
    return { title: "History", resume: "Expense-tracker history", live: true };
  }

  function pagerLink(commit, rel) {
    if (!commit) return h("span");
    return h(
      "a",
      { class: `pager-link pager-${rel}`, href: SD.route.href("history", commit.hash), rel },
      h("span", { class: "label", text: rel === "prev" ? "← Previous commit" : "Next commit →" }),
      h(
        "span",
        { class: "pager-title" },
        h("span", { class: "mono", text: commit.hash }),
        " ",
        commit.message,
      ),
    );
  }

  function renderCommit(root, mod, commit) {
    const commits = mod.commits;
    const at = commits.indexOf(commit);
    const prev = commits[at - 1] || null;
    const next = commits[at + 1] || null;
    root.append(
      h(
        "div",
        { class: "page page-wide hist" },
        SD.ui.crumbs([["History", "#history"], [commit.hash]]),
        h(
          "p",
          { class: "hist-meta" },
          h("span", { class: "hist-hash", text: commit.hash }),
          h("span", { class: "meta-line", text: `${U.dateText(commit)} · ${U.position(commits, commit)}` }),
          U.kindChip(commit.kind),
          commit.tag ? U.tagChip(commit.tag) : null,
        ),
        h("h1", { class: "hist-title", text: commit.message }),
        commit.tag && commit.git.tag_note
          ? h(
              "p",
              { class: "fine" },
              "Tagged ",
              h("span", { class: "mono", text: commit.tag }),
              `: ${commit.git.tag_note}`,
            )
          : null,
        h(
          "div",
          { class: "hist-read" },
          h("h2", { text: "What changed" }),
          h("div", { class: "prose", html: commit.summary_html }),
          h("h2", { text: "Which session idea" }),
          h("div", { class: "prose", html: commit.concepts_html }),
          SD.ui.note("Is it a good message?", commit.message_html, "exam"),
        ),
        h("h2", { text: "The --stat" }),
        U.stat(commit),
        U.hiddenNote(commit),
        h("h2", { text: "The diff" }),
        U.diff(commit),
        h(
          "div",
          { class: "actions" },
          SD.data.section(commit.section_ref)
            ? SD.ui.linkButton("Read the lesson", "#" + SD.data.sectionRoute(commit.section_ref))
            : null,
          SD.ui.linkButton("Guess another commit's message", "#history.guess", "quiet"),
        ),
        h(
          "nav",
          { class: "pager", "aria-label": "Commits" },
          pagerLink(prev, "prev"),
          pagerLink(next, "next"),
        ),
      ),
    );
    return {
      title: `${commit.hash} · History`,
      resume: `Commit ${commit.hash}`,
      onKey(event) {
        const target = event.key === "ArrowLeft" ? prev : event.key === "ArrowRight" ? next : null;
        if (!target || SD.dom.inScroller(event)) return false;
        SD.router.go(SD.route.build("history", target.hash));
        return true;
      },
    };
  }

  function missing(root, title, text, next, action) {
    root.append(h("div", { class: "page" }, h("h1", { text: title }), SD.ui.empty(text, next, action)));
    return { title };
  }

  SD.router.register("history", {
    render({ root, args }) {
      const mod = U.module();
      if (!mod) {
        return missing(
          root,
          "Expense-tracker history",
          "The history module is not in this build.",
          "Rebuild the page once content/history.json exists; meanwhile, practise questions.",
          SD.ui.linkButton("Go to Practice", "#practice", "primary"),
        );
      }
      if (args[0] === "guess") {
        const hash = args[1] || SD.historyGuess.pick(mod);
        if (!mod.commits.some((c) => c.hash === hash)) {
          return missing(
            root,
            "Guess the message",
            `There is no commit ${hash} in this history.`,
            "Guess one that is.",
            SD.ui.linkButton("Guess another", "#history.guess", "primary"),
          );
        }
        return SD.historyGuess.render(root, mod, hash);
      }
      if (!args[0]) return renderIndex(root, mod);
      const commit = mod.commits.find((c) => c.hash === args[0]);
      if (!commit) {
        return missing(
          root,
          "No such commit",
          `There is no commit ${args[0]} in this history.`,
          "Pick one from the timeline.",
          SD.ui.linkButton("All commits", "#history", "primary"),
        );
      }
      return renderCommit(root, mod, commit);
    },
  });
})();
