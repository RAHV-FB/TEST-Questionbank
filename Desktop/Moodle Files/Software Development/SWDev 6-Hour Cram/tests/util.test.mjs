// CR.util: clocks, labels, the seeded shuffle, the handwriting estimate.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { util } = load("util.js");

test("clock rounds up so 0:00 means time is up", () => {
  assert.equal(util.clock(60 * 60 * 1000), "60:00");
  assert.equal(util.clock(59 * 60 * 1000 + 59 * 1000 + 1), "60:00");
  assert.equal(util.clock(9 * 60 * 1000 + 5 * 1000), "9:05");
  assert.equal(util.clock(1), "0:01");
  assert.equal(util.clock(0), "0:00");
  assert.equal(util.clock(-5000), "0:00");
});

test("duration reads like pytest's summary", () => {
  assert.equal(util.duration(45 * 1000), "45s");
  assert.equal(util.duration((52 * 60 + 10) * 1000), "52m10s");
  assert.equal(util.duration((62 * 60) * 1000), "1h02m");
});

test("minutesLabel: minutes, hours and minutes", () => {
  assert.equal(util.minutesLabel(45), "45 min");
  assert.equal(util.minutesLabel(60), "1 h");
  assert.equal(util.minutesLabel(65), "1 h 05");
  assert.equal(util.minutesLabel(710), "11 h 50");
});

test("countdown", () => {
  assert.equal(util.countdown(0), "0 min");
  assert.equal(util.countdown(12 * 60 * 1000), "12 min");
  assert.equal(util.countdown((5 * 60 + 4) * 60 * 1000), "5 h 04 min");
  assert.equal(util.countdown((30 * 60 + 10) * 60 * 1000), "1 d 6 h");
});

test("timeFromInput puts HH:MM on the day of now and refuses nonsense", () => {
  const now = new Date(2026, 9, 20, 15, 30).getTime();
  assert.equal(util.timeFromInput("07:40", now), new Date(2026, 9, 20, 7, 40).getTime());
  assert.equal(util.timeFromInput("7:05", now), new Date(2026, 9, 20, 7, 5).getTime());
  assert.equal(util.timeFromInput("24:00", now), null);
  assert.equal(util.timeFromInput("12:60", now), null);
  assert.equal(util.timeFromInput("", now), null);
  assert.equal(util.timeFromInput("noon", now), null);
});

test("timeOfDay and dayDiff use calendar days", () => {
  const a = new Date(2026, 9, 20, 7, 40).getTime();
  const b = new Date(2026, 9, 21, 0, 5).getTime();
  assert.equal(util.timeOfDay(a), "07:40");
  assert.equal(util.dayDiff(b, a), 1);
  assert.equal(util.dayDiff(a, a), 0);
});

test("the exam's own clock is read in Madrid whatever the browser's zone", () => {
  const exam = Date.parse("2026-10-22T14:00:00+02:00");
  assert.equal(util.dateTimeLabel(exam, util.EXAM_TZ), "Thu 22 Oct, 14:00");
});

test("shuffled is stable for one seed and keeps every element", () => {
  const list = [1, 2, 3, 4, 5, 6, 7, 8];
  const seed = util.hashString("t07-q01#1");
  assert.deepEqual(util.shuffled(list, seed), util.shuffled(list, seed));
  assert.deepEqual([...util.shuffled(list, seed)].sort(), list);
  assert.deepEqual(list, [1, 2, 3, 4, 5, 6, 7, 8]);
});

test("lineEstimate and parseRange", () => {
  assert.equal(util.lineEstimate(""), 0);
  assert.equal(util.lineEstimate("x".repeat(61)), 2);
  assert.equal(util.lineEstimate("one\ntwo"), 2);
  assert.deepEqual(util.parseRange("5–8"), { lo: 5, hi: 8 });
  assert.equal(util.parseRange("many"), null);
});
