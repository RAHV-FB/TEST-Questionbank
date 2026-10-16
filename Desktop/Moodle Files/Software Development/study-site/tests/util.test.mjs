// SD.util: formatting, dates, seeded shuffling, the handwriting line estimate.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

process.env.TZ = "Europe/Madrid"; // the course's time zone; makes the DST case below exact
const { util } = load("util.js");
const MIN = 60 * 1000;
const HOUR = 60 * MIN;

test("plural and percent", () => {
  assert.equal(util.plural(1, "line"), "1 line");
  assert.equal(util.plural(0, "line"), "0 lines");
  assert.equal(util.plural(2, "box", "boxes"), "2 boxes");
  assert.equal(util.percent(1, 3), 33);
  assert.equal(util.percent(2, 3), 67);
  assert.equal(util.percent(5, 0), 0);
  assert.equal(util.MINUTE, 60_000);
});

test("hashString is FNV-1a and stable", () => {
  assert.equal(util.hashString(""), 0x811c9dc5);
  assert.equal(util.hashString("scrum-q03#2"), util.hashString("scrum-q03#2"));
  assert.notEqual(util.hashString("scrum-q03#2"), util.hashString("scrum-q03#3"));
});

test("seededRandom repeats for one seed and stays in [0, 1)", () => {
  const a = util.seededRandom(42);
  const b = util.seededRandom(42);
  const run = Array.from({ length: 50 }, () => a());
  assert.deepEqual(run, Array.from({ length: 50 }, () => b()));
  assert.ok(run.every((x) => x >= 0 && x < 1));
  assert.notDeepEqual(run.slice(0, 5), Array.from({ length: 5 }, util.seededRandom(43)));
});

test("shuffled is a stable permutation and leaves its input alone", () => {
  const list = ["a", "b", "c", "d", "e", "f"];
  const once = util.shuffled(list, 7);
  assert.deepEqual(util.shuffled(list, 7), once);
  assert.deepEqual([...once].sort(), list);
  assert.deepEqual(list, ["a", "b", "c", "d", "e", "f"]);
  const orders = new Set([1, 2, 3, 4, 5].map((seed) => util.shuffled(list, seed).join("")));
  assert.ok(orders.size > 1, "different seeds give different orders");
});

test("lineEstimate counts about 60 characters per handwritten line", () => {
  assert.equal(util.lineEstimate(""), 0);
  assert.equal(util.lineEstimate("x".repeat(60)), 1);
  assert.equal(util.lineEstimate("x".repeat(61)), 2);
  assert.equal(util.lineEstimate("short\nshort"), 2, "every paragraph starts a new line");
  assert.equal(util.lineEstimate("one\n\n  \ntwo"), 2, "blank lines take no line");
  assert.equal(util.lineEstimate("x".repeat(30), 10), 3);
});

test("parseRange reads the lines field", () => {
  assert.deepEqual(util.parseRange("5–8"), { lo: 5, hi: 8 });
  assert.deepEqual(util.parseRange(" 6 - 9 "), { lo: 6, hi: 9 });
  assert.equal(util.parseRange("5"), null);
  assert.equal(util.parseRange("five to eight"), null);
  assert.equal(util.parseRange(undefined), null);
});

test("countdown reads like the home page", () => {
  assert.equal(util.countdown(0), "0 min");
  assert.equal(util.countdown(-5), "0 min");
  assert.equal(util.countdown(1), "1 min", "rounds up so it never shows 0 too early");
  assert.equal(util.countdown(59 * MIN), "59 min");
  assert.equal(util.countdown(61 * MIN), "1 h 01 min");
  assert.equal(util.countdown(7 * 24 * HOUR + 18 * HOUR), "7 d 18 h");
  const from = new Date(2026, 9, 14, 20, 0).getTime();
  const exam = Date.parse("2026-10-22T14:00:00+02:00");
  assert.equal(util.countdown(exam - from), "7 d 18 h");
});

test("clock and duration", () => {
  assert.equal(util.clock(0), "0:00");
  assert.equal(util.clock(59_001), "1:00", "seconds round up: 0:00 means time is up");
  assert.equal(util.clock(3_599_000), "59:59");
  assert.equal(util.clock(3_600_000), "60:00", "minutes past the hour, as an exam clock");
  assert.equal(util.clock(9 * MIN + 5_000), "9:05");
  assert.equal(util.clock(-500), "0:00");
  assert.equal(util.duration(45_000), "45s");
  assert.equal(util.duration(52 * MIN + 10_000), "52m10s");
  assert.equal(util.duration(62 * MIN), "1h02m");
});

test("calendar labels and keys use local time", () => {
  const exam = new Date(2026, 9, 22, 14, 0).getTime();
  assert.equal(util.dayLabel(exam), "Thu 22 Oct");
  assert.equal(util.dateTimeLabel(exam), "Thu 22 Oct, 14:00");
  assert.equal(util.dateKey(exam), "2026-10-22");
  assert.equal(util.dateKey(new Date(2026, 0, 5, 23, 59).getTime()), "2026-01-05");
});

test("addDays returns local midnight, across the end of summer time", () => {
  const sat = new Date(2026, 9, 24, 10, 30).getTime(); // clocks go back on Sun 25 Oct
  const mon = util.addDays(sat, 2);
  assert.equal(mon, new Date(2026, 9, 26, 0, 0).getTime());
  assert.equal(mon - util.addDays(sat, 0), 2 * 24 * HOUR + HOUR, "that weekend has a 25-hour day");
  assert.equal(util.addDays(sat, 0), new Date(2026, 9, 24).getTime());
});

test("calendar labels can be read on the exam's clock, whatever the browser's zone", () => {
  const exam = Date.parse("2026-10-22T14:00:00+02:00");
  assert.equal(util.EXAM_TZ, "Europe/Madrid");
  assert.equal(util.dateTimeLabel(exam, "Europe/Madrid"), "Thu 22 Oct, 14:00");
  assert.equal(util.dateTimeLabel(exam, "Europe/London"), "Thu 22 Oct, 13:00");
  assert.equal(util.dateTimeLabel(exam, "America/New_York"), "Thu 22 Oct, 08:00");
  // 23:30 on Wed 14 Oct in Madrid is already Thu 15 in Tokyo and still Wed in New York.
  const late = Date.parse("2026-10-14T23:30:00+02:00");
  assert.equal(util.dateKey(late, "Europe/Madrid"), "2026-10-14");
  assert.equal(util.dateKey(late, "Asia/Tokyo"), "2026-10-15");
  assert.equal(util.dateKey(late, "America/New_York"), "2026-10-14");
  assert.equal(util.dayLabel(Date.parse("2026-01-01T00:30:00+01:00"), "Europe/Madrid"), "Thu 1 Jan");
  assert.equal(util.dateTimeLabel(Date.parse("2026-10-15T00:05:00+02:00"), "Europe/Madrid"), "Thu 15 Oct, 00:05");
});

test("truncate cuts at a word and says so; plain drops backticks", () => {
  assert.equal(util.truncate("short text", 40), "short text");
  assert.equal(util.truncate("  spaced \n out  ", 40), "spaced out");
  const long = "Which assertion would a reviewer ask for after the refactoring step";
  const cut = util.truncate(long, 30);
  assert.equal(cut, "Which assertion would a…");
  assert.ok(cut.length <= 30);
  assert.equal(util.truncate("x".repeat(50), 20), "x".repeat(19) + "…", "no space to cut at: cut the word");
  assert.equal(util.truncate("ends with a comma, then more words here", 22), "ends with a comma…");
  assert.equal(util.plain("`__main__.py`: the other door"), "__main__.py: the other door");
});

test("pick chooses one element with the random source it is given", () => {
  assert.equal(util.pick(() => 0, ["a", "b", "c"]), "a");
  assert.equal(util.pick(() => 0.99, ["a", "b", "c"]), "c");
  const seen = new Set(Array.from({ length: 40 }, (_, i) => util.pick(util.seededRandom(i), ["a", "b", "c"])));
  assert.equal(seen.size, 3);
});

test("lead is the first sentence when it fits, else the text cut at a word", () => {
  const text = "Sit it in 60 minutes with a pen. No notes, no devices, and read every option before choosing.";
  assert.equal(util.lead(text, 100), "Sit it in 60 minutes with a pen.");
  assert.equal(util.lead(text, 20), "Sit it in 60…");
  assert.equal(util.lead("One sentence without an end", 100), "One sentence without an end");
  assert.equal(util.lead("Is it? Yes it is.", 100), "Is it?");
  assert.equal(util.lead("Version 3.5 is out. Fine.", 100), "Version 3.5 is out.", "a dot inside a number is not an end");
  assert.equal(util.lead("", 10), "");
});
