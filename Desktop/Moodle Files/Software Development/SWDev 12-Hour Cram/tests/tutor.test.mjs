// CR.tutor: the prompt for "Ask Claude about this".
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { tutor } = load("tutor.js");

const mcq = {
  type: "mcq",
  stem: "A test fails: assert 90.0 == 95.0. What can you conclude?",
  explanation: "A failing test is information, not a verdict.",
  options: [
    { text: "The function is wrong", correct: false },
    { text: "Check the rule first", correct: true },
    { text: "Rerun it", correct: false },
    { text: "The test is wrong", correct: false },
  ],
};

test("an mcq prompt shows the options, marks the right one and names the student's choice", () => {
  const p = tutor.request(mcq, { choice: 0 });
  assert.match(p, /a\) The function is wrong\n/);
  assert.match(p, /b\) Check the rule first {2}\[the right answer\]/);
  assert.match(p, /The student chose a\)\./);
  assert.match(p, /COURSE EXPLANATION\nA failing test is information/);
  assert.match(p, /British English/);
  assert.match(p, /no more than 120 words/);
});

test("an unanswered mcq says so", () => {
  assert.match(tutor.request(mcq, {}), /did not choose an option/);
});

test("the student's own question comes first, cut and flattened", () => {
  const p = tutor.request(mcq, { choice: 2 }, "  why not   b?\n\n" + "x".repeat(400));
  assert.match(p, /The student asks: "why not b\? x+"\. Answer that first/);
  assert.equal(p.includes("x".repeat(301)), false);
  assert.equal(tutor.request(mcq, { choice: 2 }, "   ").includes("The student asks"), false);
});

test("an open prompt carries the student's words, the model answer, the rubric and their mark", () => {
  const open = {
    type: "open",
    stem: "Read the code.",
    explanation: "Name the problem and its cost.",
    parts: [{ label: "1", prompt: "What does it do?", marks: 1, model: "It totals food.", rubric: ["Says food", "Says total"] }],
  };
  const p = tutor.request(open, { answers: { 1: "it adds things" }, score: 0, max: 1 });
  assert.match(p, /PART 1 \(1 mark\): What does it do\?/);
  assert.match(p, /Rubric: 1\. Says food 2\. Says total/);
  assert.match(p, /Student's answer: it adds things/);
  assert.match(p, /marked themselves 0 out of 1/);
  assert.match(tutor.request(open, { answers: {} }), /\(nothing written\)/);
});

test("a sort prompt compares each item's right category with the student's", () => {
  const sort = {
    type: "sort",
    stem: "Sort the errors.",
    explanation: "Three kinds.",
    categories: [{ id: "a", label: "Missing" }, { id: "b", label: "None" }],
    items: [{ text: "no-untyped-def", category: "a" }, { text: "union-attr", category: "b" }],
  };
  const p = tutor.request(sort, { answers: ["b", null] });
  assert.match(p, /- no-untyped-def \| right: Missing \| student: None/);
  assert.match(p, /- union-attr \| right: None \| student: \(not placed\)/);
});
