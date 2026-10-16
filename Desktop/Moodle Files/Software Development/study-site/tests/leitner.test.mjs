// SD.leitner: flashcard boxes 1–5 and when each card is due.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

process.env.TZ = "Europe/Madrid";
const { leitner, util } = load("util.js", "leitner.js");
const NOW = new Date(2026, 9, 14, 21, 30).getTime();
const card = (box, due, n = 1) => ({ box, due, last: 0, n });

test("a new card counts as box 1", () => {
  assert.deepEqual(leitner.review(undefined, "good", NOW), {
    box: 2,
    due: util.addDays(NOW, 1),
    last: NOW,
    n: 1,
  });
  assert.equal(leitner.review(undefined, "again", NOW).box, 1);
  assert.equal(leitner.review(undefined, "easy", NOW).box, 3);
});

test("again sends a card back to box 1, due at once, in this session", () => {
  const r = leitner.review(card(4, 0, 3), "again", NOW);
  assert.deepEqual(r, { box: 1, due: NOW, last: NOW, n: 4 });
  assert.equal(leitner.waitDays(card(4, 0), "again"), 0);
});

test("good moves up one box, easy two, never past box 5", () => {
  assert.equal(leitner.review(card(2, 0), "good", NOW).box, 3);
  assert.equal(leitner.review(card(2, 0), "easy", NOW).box, 4);
  assert.equal(leitner.review(card(4, 0), "easy", NOW).box, 5);
  assert.equal(leitner.review(card(5, 0), "good", NOW).box, 5);
});

test("each box waits longer: 0, 1, 2, 4, 7 days, to local midnight", () => {
  assert.deepEqual(
    [1, 2, 3, 4].map((box) => leitner.waitDays(card(box, 0), "good")),
    [1, 2, 4, 7],
  );
  const due = leitner.review(card(4, 0), "good", NOW).due;
  assert.equal(due, new Date(2026, 9, 21).getTime(), "box 5: a week later, from midnight");
});

test("an unknown grade is a programming error", () => {
  assert.throws(() => leitner.review(card(1, 0), "hard", NOW), RangeError);
});

test("isDue", () => {
  assert.equal(leitner.isDue(undefined, NOW), false, "a card never seen is new, not due");
  assert.equal(leitner.isDue(card(2, NOW), NOW), true);
  assert.equal(leitner.isDue(card(2, NOW + 1), NOW), false);
});

test("queue: due cards (lowest box, then oldest due), then new cards, up to the limit", () => {
  const ids = ["a", "b", "c", "d", "e", "f"];
  const fc = {
    a: card(3, NOW - 10),
    b: card(1, NOW - 5),
    c: card(1, NOW - 50),
    d: card(2, NOW + 1000), // not due yet
  };
  assert.deepEqual(leitner.queue(ids, fc, NOW, 20), ["c", "b", "a", "e", "f"]);
  assert.deepEqual(leitner.queue(ids, fc, NOW, 2), ["c", "b"]);
  assert.deepEqual(leitner.queue([], fc, NOW, 5), []);
});

test("counts per box, due and new", () => {
  const fc = { a: card(3, NOW - 10), b: card(1, NOW - 5), d: card(2, NOW + 1000) };
  assert.deepEqual(leitner.counts(["a", "b", "c", "d"], fc, NOW), {
    due: 2,
    fresh: 1,
    boxes: [1, 1, 1, 0, 0],
    total: 4,
  });
});

test("with an exam date, no card waits past the exam eve, and none less than tomorrow", () => {
  const exam = new Date(2026, 9, 22, 14, 0).getTime(); // Thu 22 Oct, 14:00
  const eve = new Date(2026, 9, 21).getTime(); // Wed 21 Oct, midnight
  const mon = new Date(2026, 9, 19, 10, 0).getTime();
  // Monday, box 4 + good = box 5 = a week: cut to Wednesday's midnight.
  assert.equal(leitner.review(card(4, 0), "good", mon, exam).due, eve);
  assert.equal(leitner.waitDays(card(4, 0), "good", mon, exam), 2);
  // without an exam date the wait is the full week
  assert.equal(leitner.review(card(4, 0), "good", mon).due, new Date(2026, 9, 26).getTime());
  // box 2 (one day) is not cut
  assert.equal(leitner.review(card(1, 0), "good", mon, exam).due, new Date(2026, 9, 20).getTime());
  // On Wednesday the eve is today: a card still comes back tomorrow, not later.
  const wed = new Date(2026, 9, 21, 9, 0).getTime();
  assert.equal(leitner.review(card(4, 0), "easy", wed, exam).due, new Date(2026, 9, 22).getTime());
  assert.equal(leitner.waitDays(card(4, 0), "easy", wed, exam), 1);
  // "again" is still due in this session
  assert.equal(leitner.review(card(4, 0), "again", mon, exam).due, mon);
  assert.equal(leitner.waitDays(card(4, 0), "again", mon, exam), 0);
});

test("queue can leave out cards never seen", () => {
  const ids = ["a", "b", "c"];
  const fc = { a: card(1, NOW - 5) };
  assert.deepEqual(leitner.queue(ids, fc, NOW, 10), ["a", "b", "c"]);
  assert.deepEqual(leitner.queue(ids, fc, NOW, 10, false), ["a"]);
});
