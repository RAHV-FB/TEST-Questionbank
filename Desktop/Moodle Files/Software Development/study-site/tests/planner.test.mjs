// SD.planner: which plan day is today, and how much of a day is done.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { load } from "./helpers/load.mjs";

const { planner } = load("route.js", "planner.js");
const days = JSON.parse(readFileSync(new URL("../content/plan.json", import.meta.url), "utf8")).days;

test("the real plan runs from Wed 14 Oct to the exam on Thu 22 Oct, in date order", () => {
  const dates = days.map((d) => d.date);
  assert.equal(dates[0], "2026-10-14");
  assert.equal(dates.at(-1), "2026-10-22");
  assert.deepEqual([...dates].sort(), dates);
  assert.equal(new Set(dates).size, dates.length);
});

test("todayIndex: the day itself, the first day before the plan, the last after it", () => {
  assert.equal(planner.todayIndex(days, "2026-10-14"), 0);
  assert.equal(planner.todayIndex(days, "2026-10-18"), 4);
  assert.equal(planner.todayIndex(days, "2026-10-01"), 0);
  assert.equal(planner.todayIndex(days, "2026-11-30"), days.length - 1);
  assert.equal(planner.todayIndex([], "2026-10-14"), -1);
});

test("todayIndex: a date between two plan days shows the next one", () => {
  const gappy = [{ date: "2026-10-14" }, { date: "2026-10-16" }];
  assert.equal(planner.todayIndex(gappy, "2026-10-15"), 1);
});

test("dayProgress counts ticked items", () => {
  const day = { items: [{ id: "a" }, { id: "b" }, { id: "c" }] };
  const state = { a: { done: true, last: 1 }, b: { done: false, last: 2 }, x: { done: true, last: 3 } };
  assert.deepEqual(planner.dayProgress(day, state), { done: 1, total: 3 });
  assert.deepEqual(planner.dayProgress(day, {}), { done: 0, total: 3 });
});

test("every plan item has a unique id and a route link", () => {
  const ids = days.flatMap((d) => d.items.map((i) => i.id));
  assert.equal(new Set(ids).size, ids.length);
  for (const item of days.flatMap((d) => d.items)) {
    assert.match(item.link, /^#[A-Za-z0-9._~-]+$/, item.id);
    assert.ok(item.label.length > 0, item.id);
  }
});

test("missed lists the unticked items of earlier days, in plan order", () => {
  const plan = [
    { id: "d1", items: [{ id: "a" }, { id: "b" }] },
    { id: "d2", items: [{ id: "c" }] },
    { id: "d3", items: [{ id: "d" }] },
  ];
  const state = { a: { done: true, last: 1 }, d: { done: false, last: 2 } };
  assert.deepEqual(planner.missed(plan, state, 2).map((m) => [m.day.id, m.item.id]), [["d1", "b"], ["d2", "c"]]);
  assert.deepEqual(planner.missed(plan, state, 0), [], "on the first day nothing is behind");
  assert.deepEqual(planner.missed(plan, state, -1), []);
  assert.deepEqual(planner.missed(plan, { a: { done: true }, b: { done: true }, c: { done: true } }, 2), []);
});

test("hint reads the progress a plan link leads to", () => {
  const lookup = {
    sections: (id) => (id === "scrum" ? { read: 3, total: 9 } : id === "fresh" ? { read: 0, total: 5 } : null),
    lastExam: (id) => (id === "paper-a" ? { score: 14, max: 27 } : null),
  };
  assert.equal(planner.hint("#learn.scrum", lookup), "3 of 9 sections read");
  assert.equal(planner.hint("#learn.fresh", lookup), "", "nothing read yet: no hint");
  assert.equal(planner.hint("#learn.nope", lookup), "");
  assert.equal(planner.hint("#learn.scrum.s2", lookup), "", "a section link has no module hint");
  assert.equal(planner.hint("#exam.paper-a", lookup), "last 14/27");
  assert.equal(planner.hint("#exam.paper-b", lookup), "");
  assert.equal(planner.hint("#practice.next10.scrum", lookup), "");
  assert.equal(planner.hint("#bad/route", lookup), "");
});
