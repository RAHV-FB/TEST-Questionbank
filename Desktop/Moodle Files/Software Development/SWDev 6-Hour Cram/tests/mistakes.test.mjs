// CR.mistakes: attempt records, the mistakes queue and practice sessions.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { mistakes } = load("util.js", "mistakes.js");

test("record counts attempts, right and wrong, and keeps the latest verdict", () => {
  const q = {};
  mistakes.record(q, "a", false, 10);
  assert.deepEqual(q.a, { a: 1, c: 0, w: 1, last: 10, ok: false });
  mistakes.record(q, "a", true, 20);
  assert.deepEqual(q.a, { a: 2, c: 1, w: 1, last: 20, ok: true });
});

test("a wrong answer redone right leaves the queue; right then wrong joins it", () => {
  const q = {};
  mistakes.record(q, "a", false, 10);
  mistakes.record(q, "b", true, 11);
  assert.deepEqual(mistakes.queue(q), ["a"]);
  mistakes.record(q, "a", true, 30);
  mistakes.record(q, "b", false, 31);
  assert.deepEqual(mistakes.queue(q), ["b"]);
});

test("queue: most often wrong first, then the one wrong longest ago", () => {
  const q = {};
  mistakes.record(q, "old", false, 10);
  mistakes.record(q, "new", false, 50);
  mistakes.record(q, "twice", false, 20);
  mistakes.record(q, "twice", false, 60);
  assert.deepEqual(mistakes.queue(q), ["twice", "old", "new"]);
});

test("queue leaves out questions this build does not hold", () => {
  const q = {};
  mistakes.record(q, "kept", false, 10);
  mistakes.record(q, "gone", false, 11);
  assert.deepEqual(mistakes.queue(q, new Set(["kept"])), ["kept"]);
});

test("amend corrects the latest verdict without a new attempt", () => {
  const q = {};
  mistakes.record(q, "a", false, 10);
  mistakes.amend(q, "a", true, 20);
  assert.deepEqual(q.a, { a: 1, c: 1, w: 0, last: 20, ok: true });
  mistakes.amend(q, "a", false, 30);
  assert.deepEqual(q.a, { a: 1, c: 0, w: 1, last: 30, ok: false });
  mistakes.amend(q, "a", false, 40);
  assert.equal(q.a.w, 1);
  mistakes.amend(q, "never", true, 50);
  assert.equal(q.never.a, 1);
});

test("counts: tried, right, wrong and fresh", () => {
  const q = {};
  mistakes.record(q, "a", true, 1);
  mistakes.record(q, "b", false, 2);
  assert.deepEqual(mistakes.counts(q, ["a", "b", "c"]), { total: 3, tried: 2, right: 1, wrong: 1, fresh: 1 });
});

test("groupBy keeps first-seen order", () => {
  const groups = mistakes.groupBy(["x1", "y1", "x2"], (id) => id[0]);
  assert.deepEqual(groups, [
    ["x", ["x1", "x2"]],
    ["y", ["y1"]],
  ]);
});

test("a session goes question by question and cannot skip ahead without a verdict", () => {
  let s = mistakes.newSession(["a", "b", "c"], 1);
  assert.equal(mistakes.sessionCurrent(s), "a");
  assert.equal(mistakes.sessionAnswered(s), false);
  assert.equal(mistakes.sessionNext(s, 2).i, 0);
  s = mistakes.sessionAnswer(s, true, 3);
  assert.equal(mistakes.sessionAnswered(s), true);
  assert.equal(mistakes.sessionAnswer(s, false, 4).res.a, true, "the first verdict stands");
  s = mistakes.sessionNext(s, 5);
  assert.equal(mistakes.sessionCurrent(s), "b");
  s = mistakes.sessionNext(mistakes.sessionAnswer(s, false, 6), 7);
  s = mistakes.sessionNext(mistakes.sessionAnswer(s, null, 8), 9);
  assert.equal(mistakes.sessionFinished(s), true);
  assert.equal(mistakes.sessionCurrent(s), null);
  assert.deepEqual(mistakes.sessionSummary(s), {
    total: 3,
    answered: 2,
    right: 1,
    wrong: ["b"],
    skipped: ["c"],
    finished: true,
  });
});

test("sessionRedo starts over on the wrong and skipped ones", () => {
  let s = mistakes.newSession(["a", "b", "c"], 1);
  for (const ok of [true, false, null]) s = mistakes.sessionNext(mistakes.sessionAnswer(s, ok, 2), 3);
  const again = mistakes.sessionRedo(s, 10);
  assert.deepEqual(again.ids, ["b", "c"]);
  assert.equal(again.i, 0);
  assert.deepEqual(again.res, {});
});
