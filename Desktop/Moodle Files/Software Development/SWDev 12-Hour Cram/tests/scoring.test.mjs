// CR.scoring: multiple choice, rubric self-marking, sorting, the pytest-style line.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load, MCQ, OPEN } from "./helpers/load.mjs";

const { scoring } = load("util.js", "scoring.js");

test("marksOf: one for mcq and sort, the parts' marks for an open question", () => {
  assert.equal(scoring.marksOf(MCQ("a")), 1);
  assert.equal(scoring.marksOf({ type: "sort", items: [] }), 1);
  assert.equal(scoring.marksOf(OPEN("o")), 3);
});

test("mcqOk and correctIndex", () => {
  const q = MCQ("a", 2);
  assert.equal(scoring.correctIndex(q), 2);
  assert.equal(scoring.mcqOk(q, 2), true);
  assert.equal(scoring.mcqOk(q, 0), false);
  assert.equal(scoring.mcqOk(q, undefined), false);
  assert.equal(scoring.mcqOk(q, "2"), false);
});

test("openScore: one mark per ticked point, capped at the part's marks", () => {
  const q = OPEN("o");
  const r = scoring.openScore(q, { 1: [0, 1], 2: [2] });
  assert.deepEqual(r.parts, [
    { label: "1", score: 1, max: 1 },
    { label: "2", score: 1, max: 2 },
  ]);
  assert.equal(r.score, 2);
  assert.equal(r.max, 3);
  assert.equal(r.full, false);
  assert.equal(scoring.openScore(q, { 1: [0], 2: [0, 1, 2] }).full, true);
});

test("openScore ignores repeated, out-of-range and non-integer ticks", () => {
  const r = scoring.openScore(OPEN("o"), { 1: [0, 0, 0], 2: [1, 1, 7, -1, 0.5, "0"] });
  assert.deepEqual(r.parts.map((p) => p.score), [1, 1]);
});

test("openScore with no ticks scores nothing", () => {
  const r = scoring.openScore(OPEN("o"), {});
  assert.equal(r.score, 0);
  assert.equal(r.full, false);
});

test("sortScore counts the items in the right category", () => {
  const q = { items: [{ category: "a" }, { category: "b" }, { category: "a" }] };
  const r = scoring.sortScore(q, ["a", "a", null]);
  assert.deepEqual(r.items, [true, false, false]);
  assert.equal(r.correct, 1);
  assert.equal(r.full, false);
  assert.equal(scoring.sortScore(q, ["a", "b", "a"]).full, true);
});

test("summary reads like pytest's last line", () => {
  const s = scoring.summary({ passed: 14, failed: 3, toMark: 2, ms: (52 * 60 + 10) * 1000 });
  assert.deepEqual(
    s.segments.map((x) => x.text),
    ["14 passed", "3 failed", "2 to mark"],
  );
  assert.equal(s.tail, "in 52m10s");
  assert.deepEqual(scoring.summary({}).segments, [{ text: "no answers", kind: "none" }]);
  assert.equal(scoring.summary({ passed: 1 }).tail, "");
});
