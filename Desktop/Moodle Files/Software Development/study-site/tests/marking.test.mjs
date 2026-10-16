// SD.marking: the text sent to Claude to mark an open answer, and the strict check of its reply.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { marking } = load("marking.js");
const q = {
  stem: "A teammate wrote this test.",
  lines: "5–8",
  parts: [
    { label: "1", prompt: "What does it check?", marks: 1, model: "Nothing.", rubric: ["Says there is no assert"] },
    {
      label: "2",
      prompt: "Why does CI fail?",
      marks: 2,
      model: "The file.",
      rubric: ["Names the file", "Clean clone", "Mentions CI"],
    },
  ],
};

test("request carries the question, every part, the rubric indexes and the answers", () => {
  const text = marking.request(q, { 1: "  It asserts nothing.  " });
  assert.match(text, /A teammate wrote this test\./);
  assert.match(text, /PART 1 \(1 mark\)/);
  assert.match(text, /PART 2 \(2 marks\)/);
  assert.match(text, /  0: Names the file\n  1: Clean clone\n  2: Mentions CI/);
  assert.match(text, /"""\nIt asserts nothing\.\n"""/, "the answer is trimmed");
  assert.match(text, /"""\n\(no answer\)\n"""/, "a blank part says so");
  assert.match(text, /5–8 handwritten/);
  assert.match(text, /Reply with only JSON/);
});

test("parse recomputes marks from the rubric points met", () => {
  const r = marking.parse(
    {
      parts: [
        { label: 1, met: [0], marks: 5, feedback: " Good. " },
        { label: "2", met: [2, 2, "0", 9, -1, 1.5], marks: 2, feedback: "Half." },
      ],
      summary: "Fine.",
    },
    q,
  );
  assert.deepEqual(r.parts, [
    { label: "1", met: [0], marks: 1, max: 1, feedback: "Good." },
    { label: "2", met: [0, 2], marks: 2, max: 2, feedback: "Half." },
  ]);
  assert.equal(r.score, 3);
  assert.equal(r.max, 3);
  assert.equal(r.summary, "Fine.");
});

test("parse caps a part at its marks and tolerates missing fields", () => {
  const r = marking.parse({ parts: [{ label: "1" }, { label: "2", met: [0, 1, 2] }] }, q);
  assert.deepEqual(r.parts.map((p) => p.marks), [0, 2]);
  assert.equal(r.parts[0].feedback, "");
  assert.equal(r.summary, "");
});

test("parse rejects a reply that does not fit the question", () => {
  assert.throws(() => marking.parse(null, q), /no parts list/);
  assert.throws(() => marking.parse("text", q), /no parts list/);
  assert.throws(() => marking.parse({ parts: {} }, q), /no parts list/);
  assert.throws(() => marking.parse({ parts: [{ label: "1", met: [] }] }, q), /no part 2/);
});
