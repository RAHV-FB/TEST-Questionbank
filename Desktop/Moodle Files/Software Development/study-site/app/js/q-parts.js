// Pieces shared by the three question components (q-mcq.js, q-open.js, q-sort.js).
SD.q = (() => {
  const { h } = SD.dom;
  const TYPE = { mcq: "Multiple choice", open: "Open answer", sort: "Sort" };
  let counter = 0;

  const nextId = () => `q${(counter += 1)}`;

  // The sheet that frames one question. opts.number puts "Q7" in the margin; opts.meta: false
  // hides the type/level/module line (the exam paper does that); opts.omit says what the page
  // above already names: "module" leaves out the module, "section" the module and the section.
  function sheet(q, opts, stemId) {
    const mod = SD.data.module(q.mid);
    const section = SD.data.section(q.section_ref);
    const where = q.paper ? SD.data.paper(q.paper)?.title : mod?.title;
    const heading = section && !q.paper ? section.plain : null;
    const metaParts = [
      TYPE[q.type],
      q.level,
      mod?.predicted ? "predicted" : null,
      opts.omit ? null : where,
      opts.omit === "section" ? null : heading,
    ];
    return h(
      "article",
      {
        class: `qsheet q-${q.type}${opts.number ? " numbered" : ""}`,
        "aria-labelledby": stemId,
        dataset: { qid: q.id },
      },
      opts.number ? h("p", { class: "q-num", text: opts.number }) : null,
      opts.meta === false
        ? null
        : h("p", { class: "q-meta", text: metaParts.filter(Boolean).join(" · ") }),
      h("div", { class: "q-stem prose", id: stemId, html: q.stem_html }),
    );
  }

  // The explanation, the dissection of a teacher's question, and the "Revise" link. The verdict
  // line sits higher up, in the slot from verdictSlot().
  function feedback(q, opts) {
    return h(
      "div",
      { class: "q-feedback" },
      SD.ui.note("Why", q.explanation_html),
      q.dissection_html ? SD.ui.note("What this question really tests", q.dissection_html) : null,
      opts.revise === false ? null : SD.ui.reviseLink(q),
    );
  }

  // An empty line under the stem that gets the verdict once the answer is checked, so the result
  // is where the student is looking, above the options. Focusable, so focus can move to it.
  const verdictSlot = () => h("div", { class: "q-verdict", tabindex: "-1" });

  return { nextId, sheet, feedback, verdictSlot };
})();
