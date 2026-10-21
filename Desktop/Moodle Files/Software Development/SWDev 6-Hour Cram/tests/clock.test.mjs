// CR.clock: the route's schedule, progress, pace and projections.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { clock, util } = load("util.js", "clock.js");
const MIN = 60 * 1000;
const stops = [
  { id: "intro-intro", minutes: 5 },
  { id: "baseline-sample", minutes: 30 },
  { id: "type-S1", minutes: 40 },
  { id: "break-break1", minutes: 10 },
];
const start = new Date(2026, 9, 20, 7, 40).getTime();
const done = (...ids) => Object.fromEntries(ids.map((id) => [id, { d: true, last: 1 }]));

test("schedule lays the stops end to end from the start", () => {
  const rows = clock.schedule(stops, start);
  assert.deepEqual(
    rows.map((r) => [r.id, util.timeOfDay(r.start), util.timeOfDay(r.end)]),
    [
      ["intro-intro", "07:40", "07:45"],
      ["baseline-sample", "07:45", "08:15"],
      ["type-S1", "08:15", "08:55"],
      ["break-break1", "08:55", "09:05"],
    ],
  );
  assert.equal(clock.totalMinutes(stops), 85);
  assert.equal(clock.plannedEnd(stops, start), start + 85 * MIN);
});

test("progress counts stops and minutes; an unticked stop is not done", () => {
  const p = clock.progress(stops, { ...done("intro-intro", "type-S1"), "break-break1": { d: false, last: 2 } });
  assert.equal(p.count, 2);
  assert.equal(p.total, 4);
  assert.equal(p.minutes, 45);
  assert.equal(p.remaining, 40);
  assert.equal(p.percent, 53);
});

test("nextIndex is the first stop not done, -1 when all are", () => {
  assert.equal(clock.nextIndex(stops, {}), 0);
  assert.equal(clock.nextIndex(stops, done("intro-intro", "type-S1")), 1);
  assert.equal(clock.nextIndex(stops, done(...stops.map((s) => s.id))), -1);
});

test("pace: before, on, ahead, behind and finished", () => {
  const first = done("intro-intro", "baseline-sample"); // 35 minutes of work
  assert.deepEqual(clock.pace(stops, {}, start, start - 10 * MIN), { state: "before", minutes: 10 });
  assert.deepEqual(clock.pace(stops, first, start, start + 35 * MIN), { state: "on", minutes: 0 });
  assert.deepEqual(clock.pace(stops, first, start, start + 38 * MIN), { state: "on", minutes: 3 });
  assert.deepEqual(clock.pace(stops, first, start, start + 60 * MIN), { state: "behind", minutes: 25 });
  assert.deepEqual(clock.pace(stops, first, start, start + 20 * MIN), { state: "ahead", minutes: 15 });
  assert.equal(clock.pace(stops, done(...stops.map((s) => s.id)), start, start + 500 * MIN).state, "finished");
});

test("projectedEnd restarts the remaining minutes from now", () => {
  const now = start + 100 * MIN;
  assert.equal(clock.projectedEnd(stops, done("intro-intro"), now), now + 80 * MIN);
});

test("label adds +1 for a stop that falls after midnight", () => {
  const late = new Date(2026, 9, 20, 23, 0).getTime();
  assert.equal(clock.label(late + 30 * MIN, late), "23:30");
  assert.equal(clock.label(late + 90 * MIN, late), "00:30 +1");
});

test("defaultStart is now to the minute", () => {
  const now = new Date(2026, 9, 20, 7, 41, 33, 500).getTime();
  assert.equal(clock.defaultStart(now), new Date(2026, 9, 20, 7, 41, 0, 0).getTime());
});

test("the real route adds up to 5 h 55, under the six-hour limit", async () => {
  const { readFileSync } = await import("node:fs");
  const route = JSON.parse(readFileSync(new URL("../route.json", import.meta.url), "utf8")).stops;
  const total = route.reduce((sum, s) => sum + s.minutes, 0);
  assert.equal(route.length, 18);
  assert.equal(total, 355, `route is ${total} minutes`);
  assert.ok(total <= 360);
});

test("after: the next stop not done, looking forward first, then from the top", () => {
  assert.equal(clock.after(stops, {}, "intro-intro").id, "baseline-sample");
  assert.equal(clock.after(stops, done("baseline-sample"), "intro-intro").id, "type-S1");
  assert.equal(clock.after(stops, done("type-S1", "break-break1"), "baseline-sample").id, "intro-intro");
  assert.equal(clock.after(stops, done("intro-intro", "baseline-sample", "type-S1"), "type-S1").id, "break-break1");
  assert.equal(clock.after(stops, done(...stops.map((s) => s.id)), "type-S1"), null);
});
