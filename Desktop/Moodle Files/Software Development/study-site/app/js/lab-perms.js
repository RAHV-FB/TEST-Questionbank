// Permissions lab (#labs.perms): switches <-> number <-> ls -l letters, the slide's four modes,
// and a drill that shows a mode in one form and asks for it in another.
(() => {
  const { h } = SD.dom;
  const P = SD.perms;
  const CLASS_LABEL = { owner: "owner (you)", group: "group", others: "others" };
  const FORM_ASK = {
    number: "Write it as a number",
    letters: "Write it as ls -l letters",
    switches: "Set the switches",
  };
  const FORM_SHOWN = { number: "This number", letters: "These ls -l letters", switches: "These switches" };
  const explorer = { mode: 0o644, type: "-" };
  let drill = null; // {task, checked, result, answer}

  // Nine toggle buttons in three groups, reading like the ls -l string, with the working under
  // each group, after an optional type box. onChange(mode) after a toggle; without it the row is
  // read-only. paint(mode, type) redraws it.
  function switchRow(mode, { onChange = null, type = null, label }) {
    const row = h("div", { class: "perm-switches", role: "group", "aria-label": label });
    const bit = (m, who, what) => {
      const on = P.has(m, who, what);
      if (!onChange)
        return h("span", {
          class: `perm-bit${on ? " is-on" : ""}`,
          "aria-hidden": "true",
          text: on ? what : "-",
        });
      return h("button", {
        type: "button",
        class: "perm-bit",
        "aria-pressed": String(on),
        "aria-label": `${who} ${P.WORD[what]}`,
        text: on ? what : "-",
        onclick: () => onChange(P.toggle(m, who, what)),
      });
    };
    const paint = (m, t = type) => {
      SD.dom.fill(
        row,
        t
          ? h(
              "div",
              { class: "perm-group perm-type" },
              h("span", { class: "perm-bit is-static", text: t }),
              h("span", { class: "perm-cap", text: "type" }),
            )
          : null,
        P.WHO.map((who) =>
          h(
            "div",
            { class: "perm-group" },
            h(
              "span",
              { class: "perm-bits" },
              P.WHAT.map((what) => bit(m, who, what)),
            ),
            h(
              "span",
              { class: "perm-cap" },
              h("span", { class: "perm-who", text: CLASS_LABEL[who] }),
              h("span", { class: "perm-sum", text: P.sum(m, who) }),
            ),
          ),
        ),
        onChange ? null : h("span", { class: "vh", text: `${P.toLs(m, t || "-")}: ${reading(m)}` }),
      );
    };
    paint(mode);
    return { el: row, paint };
  }

  function lsLine(mode, type) {
    return type === "d"
      ? [
          { cmd: `chmod ${P.toOctal(mode)} src` },
          { cmd: "ls -ld src" },
          { out: `${P.toLs(mode, "d")} 3 alice alice 60 Oct 11 17:07 src` },
        ]
      : [
          { cmd: `chmod ${P.toOctal(mode)} hello.sh` },
          { cmd: "ls -l hello.sh" },
          { out: `${P.toLs(mode)} 1 alice alice 31 Oct 11 17:07 hello.sh` },
        ];
  }

  function reading(mode) {
    return P.WHO.map((who) => `${who}: ${P.rights(mode, who)}`).join(" · ");
  }

  function renderExplorer() {
    const box = h("section", { class: "lab-block", "aria-labelledby": "perm-explore" });
    const octal = h("input", {
      type: "text",
      id: "perm-octal",
      inputmode: "numeric",
      autocomplete: "off",
      spellcheck: "false",
      maxlength: "4",
      class: "mono-input",
    });
    const letters = h("input", {
      type: "text",
      id: "perm-letters",
      autocomplete: "off",
      autocapitalize: "off",
      spellcheck: "false",
      maxlength: "10",
      class: "mono-input",
    });
    const octalHint = h("p", { class: "field-hint", id: "perm-octal-hint", "aria-live": "polite" });
    const lettersHint = h("p", { class: "field-hint", id: "perm-letters-hint", "aria-live": "polite" });
    octal.setAttribute("aria-describedby", octalHint.id);
    letters.setAttribute("aria-describedby", lettersHint.id);
    const read = h("p", { class: "perm-reading" });
    const termBox = h("div");
    const typical = h("p", { class: "perm-typical" });
    const typeButtons = [
      ["-", "File"],
      ["d", "Directory"],
    ].map(([t, label]) =>
      h("button", {
        type: "button",
        class: "seg-btn",
        "aria-pressed": String(explorer.type === t),
        onclick: () => {
          explorer.type = t;
          paint();
        },
        text: `${label} (${t})`,
      }),
    );
    const row = switchRow(explorer.mode, {
      label: "Permission switches",
      type: explorer.type,
      onChange: (m) => {
        explorer.mode = m;
        paint();
      },
    });

    function paint(except = null) {
      const { mode, type } = explorer;
      typeButtons.forEach((b, i) => b.setAttribute("aria-pressed", String(["-", "d"][i] === type)));
      row.paint(mode, type);
      if (except !== octal) octal.value = P.toOctal(mode);
      if (except !== letters) letters.value = P.toLs(mode, type);
      if (except !== octal) octalHint.textContent = "";
      if (except !== letters) lettersHint.textContent = "";
      read.replaceChildren(
        h("span", { class: "label", text: "Who may do what" }),
        h("span", { text: reading(mode) }),
      );
      termBox.replaceChildren(SD.labs.term(lsLine(mode, type)));
      const c = P.common(mode);
      SD.dom.fill(
        typical,
        c
          ? h(
              "span",
              {},
              h("strong", { text: `${P.toOctal(mode)}: ${c.use}.` }),
              " The slide's typical use for this number.",
            )
          : "",
      );
      typical.hidden = !c;
    }

    octal.addEventListener("input", () => {
      const m = P.parseOctal(octal.value);
      if (m === null) {
        octalHint.textContent = "Three digits from 0 to 7, one per class: owner, group, others.";
        return;
      }
      explorer.mode = m;
      paint(octal);
    });
    letters.addEventListener("input", () => {
      const parsed = P.parseLetters(letters.value);
      if (!parsed) {
        lettersHint.textContent =
          "A type (- or d), then r, w, x or - for owner, group and others: ten characters.";
        return;
      }
      explorer.mode = parsed.mode;
      if (parsed.type) explorer.type = parsed.type;
      paint(letters);
    });
    for (const input of [octal, letters]) input.addEventListener("blur", () => paint());

    box.append(
      h("h2", { id: "perm-explore", text: "Switches, number and letters" }),
      h("p", {
        class: "fine",
        text:
          "Each class gets r (read, 4), w (write, 2) and x (execute, 1); a class's digit is the sum of " +
          "what it has. For a folder, x means you may enter it.",
      }),
      h("div", { class: "seg perm-type-seg", role: "group", "aria-label": "Kind of entry" }, typeButtons),
      row.el,
      h(
        "div",
        { class: "perm-fields" },
        h(
          "div",
          { class: "field" },
          h("label", { for: "perm-octal", text: "Number (for chmod)" }),
          octal,
          octalHint,
        ),
        h(
          "div",
          { class: "field" },
          h("label", { for: "perm-letters", text: "ls -l letters" }),
          letters,
          lettersHint,
        ),
      ),
      read,
      typical,
      termBox,
    );
    paint();
    return box;
  }

  function renderCommon() {
    return h(
      "section",
      { class: "lab-block", "aria-labelledby": "perm-common" },
      h("h2", { id: "perm-common", text: "The four modes the slides use" }),
      h(
        "div",
        { class: "table-wrap" },
        h(
          "table",
          { class: "perm-table" },
          h(
            "thead",
            {},
            h(
              "tr",
              {},
              h("th", { text: "Number" }),
              h("th", { text: "Letters" }),
              h("th", { text: "Typical use" }),
              h("th", {}, h("span", { class: "vh", text: "Show" })),
            ),
          ),
          h(
            "tbody",
            {},
            P.COMMON.map((c) =>
              h(
                "tr",
                {},
                h("td", { class: "mono", text: P.toOctal(c.mode) }),
                h("td", { class: "mono", text: P.toLetters(c.mode) }),
                h("td", { text: c.use }),
                h(
                  "td",
                  {},
                  SD.ui.button("Show", {
                    kind: "quiet",
                    "aria-label": `Show ${P.toOctal(c.mode)} in the switches`,
                    onClick: () => {
                      explorer.mode = c.mode;
                      explorer.type = "-";
                      const fresh = renderExplorer();
                      document.querySelector("[aria-labelledby='perm-explore']").replaceWith(fresh);
                      SD.dom.announce(`Showing ${P.toOctal(c.mode)} in the switches.`);
                      SD.dom.reveal(fresh.querySelector("#perm-explore"));
                    },
                  }),
                ),
              ),
            ),
          ),
        ),
      ),
      SD.ui.note(
        "Session 9 slides",
        "<p><code>chmod 777</code> makes the error go away and the problem worse. A new file never gets " +
          "execution permissions: <code>chmod +x</code> is a statement that a file is a program.</p>",
        "exam",
      ),
    );
  }

  function shownTarget(t) {
    if (t.from === "number") return h("p", { class: "perm-target mono", text: P.toOctal(t.mode) });
    if (t.from === "letters") return h("p", { class: "perm-target mono", text: P.toLs(t.mode) });
    return switchRow(t.mode, { label: "Target switches", type: "-" }).el;
  }

  function renderDrill() {
    const box = h("section", { class: "lab-block", "aria-labelledby": "perm-drill" });
    if (!drill) drill = { task: P.task(SD.labs.random()), checked: false, result: null, answer: 0 };
    const d = drill;
    const t = d.task;
    const out = h("div", { class: "drill-out", "aria-live": "polite" });
    let answerEl;
    let read;
    if (t.to === "switches") {
      const row = switchRow(d.answer, {
        label: "Your switches",
        type: "-",
        onChange: (m) => {
          d.answer = m;
          row.paint(m);
        },
      });
      answerEl = row.el;
      read = () => d.answer;
    } else {
      const input = h("input", {
        type: "text",
        id: "perm-answer",
        class: "mono-input",
        autocomplete: "off",
        autocapitalize: "off",
        spellcheck: "false",
        inputmode: t.to === "number" ? "numeric" : null,
        maxlength: t.to === "number" ? "4" : "10",
      });
      answerEl = h(
        "div",
        { class: "field" },
        h("label", {
          for: "perm-answer",
          text: t.to === "number" ? "Number" : "ls -l letters, as the first column of ls -l shows them",
        }),
        input,
      );
      read = () => input.value;
    }
    const checkButton = SD.ui.button("Check", { kind: "primary", type: "submit" });
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
      answerEl,
      h("div", { class: "actions" }, checkButton),
    );

    function check() {
      const result = P.check(t, read());
      if (!result.readable && t.to !== "switches") {
        out.replaceChildren(
          h("p", {
            class: "notice",
            text:
              t.to === "number"
                ? "Write three digits from 0 to 7, like 750."
                : "Write the letters as ls -l shows them: - for a file, then r, w, x or - in each of the " +
                  "nine places.",
          }),
        );
        return;
      }
      d.checked = true;
      d.result = result;
      SD.labs.count("perms", result.ok);
      lock();
      paintResult();
      SD.dom.announce(result.ok ? "Right." : "Not quite.");
      checkButton.focus({ preventScroll: true });
    }

    function lock() {
      form.querySelectorAll("input, button.perm-bit").forEach((el) => (el.disabled = true));
      checkButton.textContent = "Next";
    }

    function paintResult() {
      const r = d.result;
      let detail = r.ok ? "Right." : "Not quite.";
      if (r.directory)
        detail += " A leading d means a directory; this is a file, so the letters start with -.";
      SD.dom.fill(
        out,
        SD.ui.verdict(r.ok, detail),
        h(
          "dl",
          { class: "perm-answer" },
          h("div", {}, h("dt", { text: "Number" }), h("dd", { class: "mono", text: P.toOctal(t.mode) })),
          h("div", {}, h("dt", { text: "ls -l" }), h("dd", { class: "mono", text: P.toLs(t.mode) })),
          h(
            "div",
            {},
            h("dt", { text: "Working" }),
            h("dd", { class: "mono", text: P.WHO.map((who) => `${who} ${P.sum(t.mode, who)}`).join(" · ") }),
          ),
          h("div", {}, h("dt", { text: "Who may do what" }), h("dd", { text: reading(t.mode) })),
        ),
        !r.ok && r.given !== null && r.given !== t.mode
          ? h(
              "p",
              { class: "fine" },
              SD.labs.codeText(`You gave \`${P.toOctal(r.given)}\`, which is \`${P.toLs(r.given)}\`.`),
            )
          : null,
      );
    }

    function next() {
      drill = { task: P.task(SD.labs.random(), t.mode), checked: false, result: null, answer: 0 };
      const fresh = renderDrill();
      box.replaceWith(fresh);
      fresh.querySelector("input, button.perm-bit")?.focus({ preventScroll: true });
    }

    box.append(
      h("h2", { id: "perm-drill", text: "Drill" }),
      h("p", { class: "fine", text: SD.labs.tallyText("perms") }),
      h("p", { class: "drill-ask" }, h("span", { class: "label", text: FORM_SHOWN[t.from] })),
      shownTarget(t),
      h("p", { class: "drill-ask", text: `${FORM_ASK[t.to]}.` }),
      form,
      out,
    );
    if (d.checked) {
      lock();
      paintResult();
    }
    box.next = () => (d.checked ? next() : check());
    return box;
  }

  SD.labs.perms = {
    title: "Permissions",
    render(root) {
      const drillBox = renderDrill();
      root.append(
        h(
          "div",
          { class: "page page-wide lab" },
          SD.labs.head("perms", "Permissions"),
          h(
            "p",
            { class: "lead" },
            SD.labs.codeText(
              "Session 9 reads `-rwxr-xr-x` as a type and three classes. Flip the switches, type a number or " +
                "the letters, and see the other two follow.",
            ),
          ),
          renderExplorer(),
          renderCommon(),
          drillBox,
        ),
      );
      return {
        title: "Permissions · Terminal lab",
        resume: "Terminal lab: permissions",
        onKey(event) {
          if (event.key !== "Enter") return false;
          const live = root.querySelector("#perm-drill")?.closest("section");
          if (live && typeof live.next === "function") live.next();
          return Boolean(live);
        },
      };
    },
  };
})();
