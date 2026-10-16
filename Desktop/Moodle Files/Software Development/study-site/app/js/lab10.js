// The solved Lab 10 page's logic (#labs.lab10): the walkthrough's steps in page order, what the
// store remembers for a step (a prediction, and whether the answer was shown), and how many
// answers have been shown. No DOM here, so tests can run it.
SD.lab10 = (() => {
  const PREDICTION_MAX = 4000;
  // The line that stands for lines left out of a long output: "(… 412 more lines)".
  const MORE_LINES = /^\(… (\d+) more lines?\)$/;

  // The page's blocks in order: the lab's "What done looks like" list, then each exercise.
  // Each block: {id, title, short (for the jump buttons), intro_html, steps}.
  function groups(walk) {
    const summary = {
      id: "summary",
      title: "What done looks like",
      short: "Checklist",
      intro_html: walk.summary_intro_html || "",
      steps: walk.summary_steps || [],
    };
    const exercises = (walk.exercises || []).map((ex) => ({
      id: ex.id,
      title: ex.title,
      short: ex.title.split(" — ")[0],
      intro_html: ex.intro_html || "",
      steps: ex.steps || [],
    }));
    return [summary, ...exercises];
  }

  // Every step in page order: [{step, group, number, of}] (number is 1-based within its block).
  function steps(walk) {
    return groups(walk).flatMap((group) =>
      group.steps.map((step, i) => ({ step, group, number: i + 1, of: group.steps.length })),
    );
  }

  // One draft per step, so two devices only ever clash over the same step.
  const draftKey = (stepId) => `labs.lab10.${stepId}`;

  // What the store holds for a step: {s: answer shown, p: the prediction text}. Anything else
  // (nothing yet, a damaged value) reads as "not shown, no prediction".
  function read(value) {
    const ok = value !== null && typeof value === "object" && !Array.isArray(value);
    return {
      shown: ok && value.s === true,
      prediction: ok && typeof value.p === "string" ? value.p.slice(0, PREDICTION_MAX) : "",
    };
  }

  function write({ shown, prediction }) {
    return { s: Boolean(shown), p: String(prediction || "").slice(0, PREDICTION_MAX) };
  }

  // Counts the steps whose answer is shown. readStep(id) gives the step's state ({shown, ...}).
  function tally(walk, readStep) {
    const all = steps(walk);
    return { shown: all.filter(({ step }) => readStep(step.id).shown).length, total: all.length };
  }

  function tallyText({ shown, total }) {
    return shown ? `${shown} of ${SD.util.plural(total, "answer")} shown` : "No answers shown yet";
  }

  // A long output keeps its first and last lines and says how many it left out; such an output
  // cannot be compared line by line with a prediction.
  const isTrimmed = (output) => String(output).split("\n").some((line) => MORE_LINES.test(line));

  // The label above a step: "Question 3 of 8" (the block's heading says which exercise).
  const stepLabel = (number, of) => `Question ${number} of ${of}`;

  return { groups, steps, draftKey, read, write, tally, tallyText, isTrimmed, stepLabel };
})();
