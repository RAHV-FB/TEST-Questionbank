// SD.indexContent: the content index every view reads, built here from the fixture.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load, fixture } from "./helpers/load.mjs";

const SD = load("util.js", "route.js", "data.js");
const raw = fixture();
const data = SD.indexContent({ meta: { exam: {} }, modules: raw.modules, papers: raw.papers, plan: [] });

test("every section carries its heading without code marks", () => {
  for (const mod of data.modules) {
    for (const section of mod.sections) assert.equal(section.plain, section.heading.replace(/`/g, ""));
  }
});

test("modules come in course order", () => {
  const orders = data.modules.map((m) => m.order);
  assert.deepEqual(orders, [...orders].sort((a, b) => a - b));
  assert.equal(data.module("scrum").id, "scrum");
  assert.equal(data.module("nope"), null);
});

test("sections know their module, position and route token", () => {
  const s = data.section("testing-tdd-s2");
  assert.equal(s.mid, "testing-tdd");
  assert.equal(s.index, 1);
  assert.equal(s.token, "s2");
  assert.equal(data.sectionRoute("testing-tdd-s2"), "learn.testing-tdd.s2");
  assert.equal(data.sectionRoute("nope"), null);
});

test("the bank holds module questions; paper questions are found by id too", () => {
  const bankIds = data.bank.map((q) => q.id);
  assert.ok(bankIds.includes("scrum-q01"));
  assert.ok(!bankIds.some((id) => id.startsWith("paper-")));
  const pq = data.question("paper-a-q01");
  assert.equal(pq.paper, "paper-a");
  assert.equal(pq.mid, pq.module_ref);
  assert.equal(data.allQuestions.length, data.bank.length + raw.papers.flatMap((p) => p.questions).length);
  assert.equal(data.paper("paper-b").kind, "worst-case");
});

test("sectionQuestions lists bank and paper questions on that section", () => {
  for (const q of data.allQuestions) {
    assert.ok(data.sectionQuestions(q.section_ref).includes(q.id), q.id);
  }
  assert.deepEqual(data.sectionQuestions("nope"), []);
});

test("flashcards are indexed with their module", () => {
  assert.equal(data.cards.length, raw.modules.reduce((n, m) => n + m.flashcards.length, 0));
  const first = data.cards[0];
  assert.equal(data.card(first.id).mid, first.id.replace(/-f\d+$/, ""));
});

test("a predicted module's title drops a trailing (predicted): the chip says it", () => {
  const mods = [
    { id: "p", order: 1, predicted: true, title: "Pipes and bash (predicted)" },
    { id: "q", order: 2, predicted: false, title: "Odd (predicted)" },
  ].map((m) => ({ ...m, sections: [], questions: [], flashcards: [] }));
  const d = SD.indexContent({ meta: {}, modules: mods });
  assert.equal(d.module("p").title, "Pipes and bash");
  assert.equal(d.module("q").title, "Odd (predicted)", "only predicted modules carry the chip");
});
