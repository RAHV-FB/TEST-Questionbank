// "Guess the message" (#history.guess[.<hash>]): the diff of one commit with its message hidden.
// Write the subject you would give it, or pick one of four real messages from the history, then
// see the real one, its review and what the commit did.
SD.historyGuess = (() => {
  const { h } = SD.dom;
  const U = SD.historyUi;
  const LETTERS = "abcd";
  const HABITS = [
    'Imperative: it completes "If applied, this commit will ...".',
    "It says what the change does, not how the code does it.",
    "It is specific: it names the behaviour or the thing that changed.",
  ];
  let state = null; // {hash, seed, typed, pick, revealed}

  function save(hash, mark) {
    SD.store.setDraft("history.guess", { ...U.record(), [hash]: mark });
  }

  function render(root, mod, hash) {
    const commits = mod.commits;
    const commit = commits.find((c) => c.hash === hash);
    if (!state || state.hash !== hash) {
      state = {
        hash,
        seed: (Date.now() >>> 0) ^ SD.util.hashString(hash),
        typed: "",
        pick: null,
        revealed: false,
        jump: false,
      };
    }
    const s = state;
    const options = SD.history.candidates(commits, hash, s.seed);
    const tally = SD.history.tally(commits, U.record());
    // Focus moves here after the reveal (see the end of render), so keyboard and screen-reader
    // users land on the answer rather than back at the top of a long diff.
    const out = h("div", { class: "guess-out", tabindex: "-1", role: "region", "aria-label": "The real message" });

    const input = h("input", {
      type: "text",
      id: "guess-message",
      class: "wide-input",
      maxlength: "100",
      autocomplete: "off",
      value: s.typed,
      disabled: s.revealed,
    });
    const preview = h("p", { class: "fine guess-preview" });
    const paintPreview = () => (preview.textContent = s.typed.trim() ? SD.history.ifApplied(s.typed) : "");
    input.addEventListener("input", () => {
      s.typed = input.value;
      paintPreview();
    });
    paintPreview();

    const rows = options.map((opt, i) => {
      const radio = h("input", {
        type: "radio",
        class: "opt-input",
        name: "guess-pick",
        value: String(i),
        checked: s.pick === i,
        disabled: s.revealed,
        onchange: () => choose(i),
      });
      const mark = h("span", { class: "opt-mark" });
      const why = h("span", { class: "opt-why", hidden: true });
      const row = h(
        "label",
        { class: `opt${s.pick === i ? " is-selected" : ""}` },
        radio,
        h("span", { class: "opt-letter", text: `${LETTERS[i]})` }),
        h("span", { class: "opt-body" }, h("span", { class: "opt-text", text: opt.message }), why),
        mark,
      );
      return { opt, row, radio, mark, why };
    });

    function choose(i) {
      if (s.revealed) return;
      s.pick = i;
      rows.forEach((r, k) => r.row.classList.toggle("is-selected", k === i));
    }

    const revealButton = SD.ui.button(s.revealed ? "Next commit" : "Reveal the real message", {
      kind: "primary",
      type: "submit",
    });
    const form = h(
      "form",
      {
        class: "qsheet guess-sheet",
        "aria-labelledby": "guess-title",
        onsubmit: (event) => {
          event.preventDefault();
          if (s.revealed) next();
          else reveal();
        },
      },
      h("h2", { id: "guess-title", class: "guess-h", text: "Your message" }),
      h(
        "div",
        { class: "field" },
        h("label", { for: "guess-message", text: "Write the subject line you would give this commit" }),
        input,
        preview,
      ),
      h(
        "fieldset",
        { class: "opts guess-opts" },
        h("legend", {
          class: "guess-legend",
          text: `Or pick the real one: ${options.length === 4 ? "four" : options.length} messages from this history`,
        }),
        rows.map((r) => r.row),
      ),
      h(
        "div",
        { class: "actions" },
        revealButton,
        s.revealed ? SD.ui.linkButton("Open this commit", SD.route.href("history", hash)) : null,
      ),
    );

    function paintReveal() {
      rows.forEach((r, i) => {
        r.radio.disabled = true;
        r.row.classList.toggle("is-correct", r.opt.real);
        r.row.classList.toggle("is-wrong", !r.opt.real && s.pick === i);
        if (r.opt.real) r.mark.textContent = s.pick === i ? "✓ your pick" : "✓ real message";
        else r.mark.textContent = s.pick === i ? "✗ your pick" : "";
        if (!r.opt.real) {
          r.why.hidden = false;
          r.why.replaceChildren(
            "The message of ",
            h("a", { href: SD.route.href("history", r.opt.hash), class: "mono", text: r.opt.hash }),
            ".",
          );
        }
      });
      const picked = s.pick === null ? null : options[s.pick];
      const verdict =
        picked === null
          ? null
          : SD.ui.verdict(
              picked.real,
              picked.real
                ? "You picked the real message."
                : `Not this one: you picked the message of ${picked.hash}.`,
            );
      const typed = s.typed.trim();
      SD.dom.fill(
        out,
        verdict,
        h(
          "div",
          { class: "guess-compare" },
          typed
            ? h(
                "div",
                { class: "guess-line" },
                h("p", { class: "label", text: "You wrote" }),
                h("p", { class: "guess-msg", text: typed }),
                h("p", { class: "fine", text: SD.history.ifApplied(typed) }),
              )
            : null,
          h(
            "div",
            { class: "guess-line" },
            h("p", { class: "label", text: "The real message" }),
            h(
              "p",
              { class: "guess-msg" },
              h("span", { class: "mono hist-hash", text: commit.hash }),
              " ",
              commit.message,
            ),
            h("p", { class: "fine", text: SD.history.ifApplied(commit.message) }),
          ),
        ),
        typed
          ? h(
              "fieldset",
              { class: "guess-habits" },
              h("legend", { text: "Check your own message against the three habits of the demo history" }),
              HABITS.map((text, i) =>
                h(
                  "div",
                  { class: "rubric-item" },
                  h("input", { type: "checkbox", id: `habit-${i}` }),
                  h("label", { for: `habit-${i}`, text }),
                ),
              ),
            )
          : null,
        SD.ui.note("Is the real message a good one?", commit.message_html, "exam"),
        h(
          "div",
          { class: "kind-line" },
          h("span", { class: "label", text: "Kind" }),
          U.kindChip(commit.kind),
          commit.tag ? U.tagChip(commit.tag) : null,
        ),
        h("h3", { text: "What changed" }),
        h("div", { class: "prose", html: commit.summary_html }),
        h("h3", { text: "Which session idea" }),
        h("div", { class: "prose", html: commit.concepts_html }),
      );
    }

    function reveal() {
      s.revealed = true;
      const picked = s.pick === null ? null : options[s.pick];
      if (picked) save(hash, picked.real ? "right" : "wrong");
      else if (s.typed.trim()) save(hash, "written");
      s.jump = true;
      // Render at the commit's own address (from #history.guess too), so a reload keeps it.
      SD.router.go(SD.route.build("history", "guess", hash));
      const verdict = picked ? (picked.real ? "You picked the real message. " : "Not the real message. ") : "";
      SD.dom.announce(`${verdict}The real message: ${commit.message}`);
    }

    function next() {
      const random = SD.util.seededRandom((Date.now() >>> 0) ^ 0x5bd1e995);
      SD.router.go(SD.route.build("history", "guess", SD.history.next(commits, U.record(), random, hash)));
    }

    root.append(
      h(
        "div",
        { class: "page page-wide hist" },
        SD.ui.crumbs([["History", "#history"], ["Guess the message"]]),
        h("h1", { text: "Guess the message" }),
        h("p", {
          class: "meta-line",
          text:
            `${U.position(commits, commit)} · ${U.dateText(commit)} · ${tally.tried} of ` +
            `${commits.length} tried, ${tally.right} picked right`,
        }),
        h("p", {
          class: "lead",
          text:
            "Read the --stat first, then the diff. Write the subject line you would give this commit, or " +
            "pick the real one from four messages of this history.",
        }),
        U.stat(commit),
        U.hiddenNote(commit),
        U.diff(commit),
        form,
        out,
      ),
    );
    if (s.revealed) paintReveal();
    if (s.jump) {
      s.jump = false;
      // After the router's own scroll to the top: bring the answer into view and focus it.
      window.requestAnimationFrame(() => {
        out.scrollIntoView({ block: "start" });
        out.focus({ preventScroll: true });
      });
    }
    return {
      title: "Guess the message · History",
      resume: "History: guess the message",
      onKey(event) {
        if (event.key === "Enter") {
          // Without a pick or a typed message Enter does nothing: only the button gives up.
          if (!s.revealed && s.pick === null && !s.typed.trim()) return false;
          if (s.revealed) next();
          else reveal();
          return true;
        }
        const pos = LETTERS.indexOf(event.key.toLowerCase());
        if (s.revealed || pos < 0 || pos >= rows.length || event.altKey || event.ctrlKey || event.metaKey)
          return false;
        rows[pos].radio.checked = true;
        rows[pos].radio.focus({ preventScroll: true });
        choose(pos);
        return true;
      },
    };
  }

  // The commit for #history.guess without a hash: the one on screen while it is still a
  // question, else the next one to guess.
  function pick(mod) {
    if (state && !state.revealed && mod.commits.some((c) => c.hash === state.hash)) return state.hash;
    return SD.history.next(mod.commits, U.record(), SD.util.seededRandom(Date.now() >>> 0));
  }

  return { render, pick };
})();
