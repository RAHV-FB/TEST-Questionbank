// Pure parts of "Mark my answer with Claude": the request text, and a strict check of the reply.
// q here is plain text: {stem, lines, parts: [{label, prompt, marks, model, rubric: [text]}]}.
SD.marking = (() => {
  function request(q, answers) {
    const parts = q.parts.map((p) => {
      const rubric = p.rubric.map((r, i) => `  ${i}: ${r}`).join("\n");
      const answer = (answers[p.label] || "").trim() || "(no answer)";
      return [
        `PART ${p.label} (${p.marks} ${p.marks === 1 ? "mark" : "marks"})`,
        `Prompt: ${p.prompt}`,
        `Model answer: ${p.model}`,
        `Rubric points:\n${rubric}`,
        `Student's answer:\n"""\n${answer}\n"""`,
      ].join("\n");
    });
    return [
      "You are marking one answer from the mid-term of Software Development for Business, a",
      "university course. The exam is pen and paper: open answers are " + q.lines + " handwritten",
      "lines of prose in total, and students never write code.",
      "",
      "Mark strictly against the rubric. A rubric point is met only when the student's own words",
      "state it clearly. A keyword without the idea, a vague gesture, or a point that appears only",
      "in the model answer does not count. Do not reward length. The marks for a part are the",
      "number of rubric points met, capped at the part's marks.",
      "",
      `QUESTION\n${q.stem}`,
      "",
      parts.join("\n\n"),
      "",
      "Reply with only JSON in this shape, one entry per part, rubric points as indexes:",
      '{"parts":[{"label":"1","met":[0],"marks":1,"feedback":"what earned the mark and what is',
      'missing, in one or two sentences"}],"summary":"one sentence on the whole answer"}',
      'Write the feedback to the student as "you", in British English.',
    ].join("\n");
  }

  // Check Claude's reply against the question. Marks are recomputed from the rubric points
  // met (the same rule as self-marking), so a reply can never award more than the rubric allows.
  function parse(reply, q) {
    if (reply === null || typeof reply !== "object" || !Array.isArray(reply.parts)) {
      throw new Error("the reply has no parts list");
    }
    const parts = q.parts.map((p) => {
      const got = reply.parts.find((r) => r && String(r.label) === String(p.label));
      if (!got) throw new Error(`the reply has no part ${p.label}`);
      const met = [
        ...new Set(
          (Array.isArray(got.met) ? got.met : [])
            .filter((i) => typeof i === "number" || (typeof i === "string" && /^\d+$/.test(i)))
            .map(Number)
            .filter((i) => Number.isInteger(i) && i >= 0 && i < p.rubric.length),
        ),
      ].sort((a, b) => a - b);
      return {
        label: p.label,
        met,
        marks: Math.min(p.marks, met.length),
        max: p.marks,
        feedback: typeof got.feedback === "string" ? got.feedback.trim() : "",
      };
    });
    return {
      parts,
      score: parts.reduce((sum, p) => sum + p.marks, 0),
      max: parts.reduce((sum, p) => sum + p.max, 0),
      summary: typeof reply.summary === "string" ? reply.summary.trim() : "",
    };
  }

  return { request, parse };
})();
