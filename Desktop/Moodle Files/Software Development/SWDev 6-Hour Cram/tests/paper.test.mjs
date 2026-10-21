// CR.paper: a sitting's record and clock, marking, hand-in, recording a mark.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load, MCQ, OPEN } from "./helpers/load.mjs";

const { paper } = load("util.js", "scoring.js", "paper.js");
const MIN = 60 * 1000;
const meta = { id: "paper-a", title: "Paper A", minutes: 60 };
const questions = [MCQ("m1", 1, "S3"), MCQ("m2", 2, "S4"), OPEN("o1", "S7")]; // 1 + 1 + 3 marks
const T0 = 1_000_000;

test("start: a running record that knows its total marks", () => {
  const r = paper.start(meta, questions, T0);
  assert.equal(r.id, `paper-a-${T0}`);
  assert.equal(r.status, "running");
  assert.equal(r.max, 5);
  assert.deepEqual(r.questions, ["m1", "m2", "o1"]);
});

test("the clock runs from started: deadline, timeLeft, expired", () => {
  const r = paper.start(meta, questions, T0);
  assert.equal(paper.deadline(r), T0 + 60 * MIN);
  assert.equal(paper.timeLeft(r, T0 + 20 * MIN), 40 * MIN);
  assert.equal(paper.timeLeft(r, T0 + 90 * MIN), 0);
  assert.equal(paper.expired(r, T0 + 59 * MIN), false);
  assert.equal(paper.expired(r, T0 + 60 * MIN), true);
  assert.equal(paper.expired({ ...r, status: "done" }, T0 + 90 * MIN), false);
});

test("warning: 10 in the last ten minutes, 5 in the last five", () => {
  assert.equal(paper.warning(30 * MIN), 0);
  assert.equal(paper.warning(10 * MIN), 10);
  assert.equal(paper.warning(6 * MIN), 10);
  assert.equal(paper.warning(5 * MIN), 5);
  assert.equal(paper.warning(0), 5);
});

test("answerState: blank, partial, full; written on paper counts as full", () => {
  const [m, , o] = questions;
  assert.equal(paper.answerState(m, undefined), "blank");
  assert.equal(paper.answerState(m, 0), "full");
  assert.equal(paper.answerState(o, {}), "blank");
  assert.equal(paper.answerState(o, { 1: "text", 2: "  " }), "partial");
  assert.equal(paper.answerState(o, { 1: "a", 2: "b" }), "full");
  assert.equal(paper.answerState(o, undefined, true), "full");
});

test("mark: mcq 1 or 0, blank 0, an answered open question waits for its mark", () => {
  const r = { ...paper.start(meta, questions, T0), answers: { m1: 1, m2: 0, o1: { 1: "x", 2: "y" } } };
  const m = paper.mark(questions, r);
  assert.deepEqual(m.results.map((x) => [x.qid, x.status, x.score]), [
    ["m1", "pass", 1],
    ["m2", "fail", 0],
    ["o1", "mark", 0],
  ]);
  assert.equal(m.score, 1);
  assert.equal(m.max, 5);
  assert.equal(m.toMark, 1);
  assert.equal(m.passed, 1);
  assert.equal(m.failed, 1);
});

test("mark: a recorded open mark counts, passes only at full marks, blank scores 0", () => {
  const base = paper.start(meta, questions, T0);
  const partial = paper.mark(questions, { ...base, answers: { o1: { 1: "x", 2: "y" } }, marks: { o1: 2 } });
  assert.equal(partial.results[2].score, 2);
  assert.equal(partial.results[2].status, "fail");
  const full = paper.mark(questions, { ...base, answers: { o1: { 1: "x", 2: "y" } }, marks: { o1: 3 } });
  assert.equal(full.results[2].status, "pass");
  const blank = paper.mark(questions, { ...base, answers: {}, marks: { o1: 3 } });
  assert.equal(blank.results[2].score, 0, "a mark cannot rescue a blank answer");
  const onPaper = paper.mark(questions, { ...base, onpaper: ["o1"], marks: { o1: 2 } });
  assert.equal(onPaper.results[2].score, 2);
});

test("handIn: counts every mcq and every blank open question as an attempt, once", () => {
  const r = { ...paper.start(meta, questions, T0), answers: { m1: 1 } };
  const { record, outcomes } = paper.handIn(r, questions, T0 + 40 * MIN);
  assert.deepEqual(outcomes, [
    { qid: "m1", ok: true },
    { qid: "m2", ok: false },
    { qid: "o1", ok: false },
  ]);
  assert.equal(record.status, "done");
  assert.equal(record.used_ms, 40 * MIN);
  assert.equal(record.timed_out, false);
  assert.deepEqual(record.recorded, ["m1", "m2", "o1"]);
  assert.equal(record.score, 1);
  assert.equal(paper.handIn(record, questions, T0 + 41 * MIN).outcomes.length, 0, "nothing is counted twice");
});

test("handIn leaves an answered open question for its mark", () => {
  const r = { ...paper.start(meta, questions, T0), answers: { m1: 1, m2: 2, o1: { 1: "x" } } };
  const { record, outcomes } = paper.handIn(r, questions, T0 + 10 * MIN);
  assert.deepEqual(outcomes.map((o) => o.qid), ["m1", "m2"]);
  assert.deepEqual(record.recorded, ["m1", "m2"]);
  assert.equal(record.to_mark, 1);
});

test("handIn past the deadline ends at 0:00 and says it timed out", () => {
  const r = paper.start(meta, questions, T0);
  const { record } = paper.handIn(r, questions, T0 + 75 * MIN);
  assert.equal(record.ended, T0 + 60 * MIN);
  assert.equal(record.used_ms, 60 * MIN);
  assert.equal(record.timed_out, true);
  assert.equal(paper.handIn(r, questions, T0 + 10 * MIN, true).record.timed_out, true);
});

test("recordMark: the first mark is an attempt, a later one amends it", () => {
  const r0 = { ...paper.start(meta, questions, T0), answers: { o1: { 1: "x", 2: "y" } } };
  const first = paper.recordMark(r0, questions[2], 2, { 1: [0], 2: [0, 1] }, T0 + 1);
  assert.deepEqual(first.outcome, { qid: "o1", ok: false, amend: false });
  assert.deepEqual(first.record.recorded, ["o1"]);
  assert.equal(first.record.marks.o1, 2);
  assert.deepEqual(first.record.ticks.o1, { 1: [0], 2: [0, 1] });
  const again = paper.recordMark(first.record, questions[2], 3, { 1: [0], 2: [0, 1, 2] }, T0 + 2);
  assert.deepEqual(again.outcome, { qid: "o1", ok: true, amend: true });
  assert.deepEqual(again.record.recorded, ["o1"]);
  assert.equal(paper.recordMark(r0, questions[2], 99, {}, T0).record.marks.o1, 3, "capped at the question's marks");
  assert.equal(paper.recordMark(r0, questions[2], -4, {}, T0).record.marks.o1, 0);
});

test("withTotals brings the summary fields up to date", () => {
  const r = { ...paper.start(meta, questions, T0), answers: { m1: 1, m2: 2 }, marks: {} };
  const t = paper.withTotals(r, questions);
  assert.deepEqual([t.passed, t.failed, t.to_mark, t.score, t.max], [2, 1, 0, 2, 5]);
});

test("lostByType ranks the types where marks were lost, leaving out questions still to mark", () => {
  const results = [
    { qid: "a", tid: "S3", status: "fail", score: 0, max: 1 },
    { qid: "b", tid: "S3", status: "fail", score: 0, max: 1 },
    { qid: "c", tid: "S4", status: "pass", score: 1, max: 1 },
    { qid: "d", tid: "S7", status: "fail", score: 1, max: 3 },
    { qid: "e", tid: "S6", status: "mark", score: 0, max: 3 },
  ];
  assert.deepEqual(paper.lostByType(results), [
    { tid: "S3", lost: 2, score: 0, max: 2 },
    { tid: "S7", lost: 2, score: 1, max: 3 },
  ]);
});

test("running, lastDone and newestFirst ignore discarded sittings", () => {
  const a = { ...paper.start(meta, questions, 100), status: "done" };
  const b = { ...paper.start(meta, questions, 200), status: "done" };
  const c = paper.start({ ...meta, id: "paper-c" }, questions, 300);
  const d = paper.discard(paper.start(meta, questions, 400), 450);
  const all = [a, b, c, d];
  assert.equal(paper.running(all).id, c.id);
  assert.equal(paper.lastDone(all, "paper-a").id, b.id);
  assert.equal(paper.lastDone(all, "paper-c"), null);
  assert.deepEqual(paper.newestFirst(all).map((p) => p.started), [300, 200, 100]);
  assert.equal(d.status, "discarded");
  assert.equal("answers" in d, false);
});
