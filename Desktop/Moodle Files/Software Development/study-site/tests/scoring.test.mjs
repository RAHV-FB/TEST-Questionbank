// SD.scoring: multiple choice, rubric self-marking, sorting, and pytest's summary line.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { scoring } = load("util.js", "scoring.js");

const open = {
  parts: [
    { label: "1", marks: 1, rubric: ["r0", "r1"] },
    { label: "2", marks: 2, rubric: ["r0", "r1", "r2"] },
    { label: "3", marks: 3, rubric: ["r0", "r1", "r2"] },
  ],
};

test("openScore: one mark per ticked point, capped at the part's marks", () => {
  const r = scoring.openScore(open, { 1: [0, 1], 2: [2], 3: [] });
  assert.deepEqual(r.parts, [
    { label: "1", score: 1, max: 1 },
    { label: "2", score: 1, max: 2 },
    { label: "3", score: 0, max: 3 },
  ]);
  assert.equal(r.score, 2);
  assert.equal(r.max, 6);
  assert.equal(r.full, false);
});

test("openScore ignores repeated, out-of-range and non-integer ticks", () => {
  const r = scoring.openScore(open, { 2: [1, 1, 7, -1, 0.5, "0"], 3: [0, 1, 2] });
  assert.deepEqual(r.parts.map((p) => p.score), [0, 1, 3]);
  assert.equal(scoring.openScore(open, {}).score, 0);
  const full = scoring.openScore(open, { 1: [1], 2: [0, 2], 3: [0, 1, 2] });
  assert.equal(full.full, true);
  assert.equal(full.score, 6);
});

test("sortScore marks each item", () => {
  const q = { items: [{ category: "x" }, { category: "y" }, { category: "x" }] };
  assert.deepEqual(scoring.sortScore(q, ["x", "x", null]), {
    correct: 1,
    total: 3,
    items: [true, false, false],
    full: false,
  });
  assert.equal(scoring.sortScore(q, ["x", "y", "x"]).full, true);
});

test("pytestSummary reads like pytest", () => {
  assert.deepEqual(scoring.pytestSummary({ passed: 14, failed: 3, toMark: 2, ms: 3_130_000 }), {
    segments: [
      { text: "14 passed", kind: "pass" },
      { text: "3 failed", kind: "fail" },
      { text: "2 to mark", kind: "warn" },
    ],
    tail: "in 52m10s",
  });
  assert.deepEqual(scoring.pytestSummary({ failed: 1 }), {
    segments: [{ text: "1 failed", kind: "fail" }],
    tail: "",
  });
  assert.deepEqual(scoring.pytestSummary({}).segments, [{ text: "no answers", kind: "none" }]);
});
