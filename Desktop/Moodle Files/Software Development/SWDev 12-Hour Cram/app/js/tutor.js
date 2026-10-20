// The text sent to Claude by "Ask Claude about this": built from plain text of a question, the
// student's answer and an optional question of their own. Pure, so it can be tested.
// plain: {type, stem, explanation, options?: [{text, correct, why}], parts?: [{label, prompt, marks,
// model, rubric: [text]}], items?: [{text, category}], categories?: [{id, label}]}.
CR.tutor = (() => {
  const LETTERS = "abcdefgh";
  const MAX_ASK = 300;

  const clean = (text) => String(text ?? "").replace(/\s+/g, " ").trim().slice(0, MAX_ASK);

  function questionBlock(plain, answer) {
    const lines = [`QUESTION\n${plain.stem}`, ""];
    if (plain.type === "mcq") {
      lines.push("OPTIONS");
      plain.options.forEach((o, i) => lines.push(`${LETTERS[i]}) ${o.text}${o.correct ? "  [the right answer]" : ""}`));
      const choice = Number.isInteger(answer?.choice) ? answer.choice : null;
      lines.push("", choice === null ? "The student did not choose an option." : `The student chose ${LETTERS[choice]}).`);
      lines.push("", `COURSE EXPLANATION\n${plain.explanation}`);
    } else if (plain.type === "open") {
      plain.parts.forEach((p) => {
        const mine = String(answer?.answers?.[p.label] ?? "").trim() || "(nothing written)";
        lines.push(`PART ${p.label} (${p.marks} ${p.marks === 1 ? "mark" : "marks"}): ${p.prompt}`);
        lines.push(`Model answer: ${p.model}`);
        lines.push(`Rubric: ${p.rubric.map((r, i) => `${i + 1}. ${r}`).join(" ")}`);
        lines.push(`Student's answer: ${mine}`, "");
      });
      if (answer && Number.isFinite(answer.score)) lines.push(`The student marked themselves ${answer.score} out of ${answer.max}.`, "");
      lines.push(`COURSE EXPLANATION\n${plain.explanation}`);
    } else {
      const label = (id) => plain.categories.find((c) => c.id === id)?.label ?? "(not placed)";
      lines.push(`CATEGORIES: ${plain.categories.map((c) => c.label).join(", ")}`, "ITEMS");
      plain.items.forEach((it, i) => {
        const mine = label(answer?.answers?.[i]);
        lines.push(`- ${it.text} | right: ${label(it.category)} | student: ${mine}`);
      });
      lines.push("", `COURSE EXPLANATION\n${plain.explanation}`);
    }
    return lines.join("\n");
  }

  // The whole prompt. `ask` is what the student typed, if anything (cut to 300 characters).
  function request(plain, answer, ask = "") {
    const extra = clean(ask);
    return [
      "You are a patient tutor for the mid-term of Software Development for Business, a university",
      "course. The exam is pen and paper: students never write code and are not tested on memorised",
      "flags. A student has just answered one practice question and wants to understand it better.",
      "",
      "Rules: use only the question, the options and the course explanation below, and do not invent",
      "facts about the course. Write in British English, in plain sentences, with no headings, no code",
      "blocks and no more than 120 words.",
      "",
      extra
        ? `The student asks: "${extra}". Answer that first, then give the one idea to remember.`
        : "Say what the student's answer shows they probably believed or did right, give the one idea " +
          "that fixes it in the course's terms, and end with one short sentence they could write on the " +
          "paper. If they were right, say which trap to watch for next time.",
      "",
      questionBlock(plain, answer),
    ].join("\n");
  }

  return { MAX_ASK, request };
})();
