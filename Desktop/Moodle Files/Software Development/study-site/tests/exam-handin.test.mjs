// SD.examPaper.handIn: handing in records the answers once, even when the paper's own tick and the
// shell's settle() both reach 0:00 in the same moment.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { load } from "./helpers/load.mjs";

const SD = load("util.js", "route.js", "progress.js", "leitner.js", "scoring.js", "data.js", "exam.js", "store.js");
const T0 = Date.UTC(2026, 9, 15, 8, 0, 0);
const MIN = 60 * 1000;

const mcq = (id) => ({
  id,
  mid: "m01",
  section_ref: "m01-s1",
  type: "mcq",
  options: [{ correct: false }, { correct: true }, { correct: false }, { correct: false }],
});
const questions = [mcq("a"), mcq("b")];
const lookup = new Map(questions.map((q) => [q.id, q]));

function memoryDisk() {
  const data = new Map();
  return {
    getItem: (key) => (data.has(key) ? data.get(key) : null),
    setItem: (key, value) => data.set(key, value),
    removeItem: (key) => data.delete(key),
  };
}

SD.store = SD.makeStore({ storage: memoryDisk() });
SD.data = { ...SD.data, question: (id) => lookup.get(id) };
SD.dom = { h: () => ({}) };
vm.runInThisContext(`"use strict";${readFileSync(new URL("../app/js/exam-paper.js", import.meta.url), "utf8")}`, {
  filename: "app/js/exam-paper.js",
});

test("handing in twice at 0:00 records each answer once", () => {
  const rec = { ...SD.exam.start({ id: "paper-a", title: "Paper A", minutes: 60 }, questions, T0), answers: { a: 1, b: 0 } };
  SD.store.saveExam(rec);
  const end = T0 + 60 * MIN;
  const first = SD.examPaper.handIn(rec, true, end);
  SD.examPaper.settle(end);
  const second = SD.examPaper.handIn(rec, true, end);
  const state = SD.store.get();
  assert.equal(first.status, "done");
  assert.equal(second.status, "done");
  assert.equal(state.q.a.a, 1, "a recorded once");
  assert.equal(state.q.b.a, 1, "b recorded once");
  assert.equal(state.exams.filter((e) => e.id === rec.id).length, 1);
});
