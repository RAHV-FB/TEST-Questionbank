// SD.progress: the stored state, answer records, CI-style statuses, weak spots, merging.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { progress } = load("progress.js");
const right = (last, conf = null) => ({ a: 1, c: 1, last, ok: true, conf });
const wrong = (last) => ({ a: 1, c: 0, last, ok: false, conf: null });

test("normalise keeps well-formed parts and drops the rest", () => {
  assert.deepEqual(progress.normalise(null), progress.blankState());
  assert.deepEqual(progress.normalise("text"), progress.blankState());
  assert.deepEqual(progress.normalise({ v: 2, q: { x: right(1) } }), progress.blankState());
  const s = progress.normalise({
    v: 1,
    q: { x: right(1) },
    fc: [],
    exams: [{ id: "e1" }, { title: "no id" }, null],
    prefs: { theme: "dark" },
    last: { route: "learn.scrum", label: "Scrum", ts: 5 },
    junk: 1,
  });
  assert.deepEqual(s.q, { x: right(1) });
  assert.deepEqual(s.fc, {}, "an array is not a map");
  assert.equal(s.exams.length, 1, "records without an id or that are not objects are dropped");
  assert.equal(s.exams[0].id, "e1");
  assert.deepEqual(s.prefs, { theme: "dark", timerHidden: false });
  assert.equal(s.last.route, "learn.scrum");
  assert.equal("junk" in s, false);
});

test("record counts attempts and keeps the latest verdict", () => {
  const first = progress.record(undefined, false, "sure", 10);
  assert.deepEqual(first, { a: 1, c: 0, last: 10, ok: false, conf: "sure" });
  const second = progress.record(first, true, null, 20);
  assert.deepEqual(second, { a: 2, c: 1, last: 20, ok: true, conf: null });
});

test("amend corrects the latest verdict without a new attempt", () => {
  const entry = { a: 3, c: 1, last: 10, ok: false, conf: null };
  assert.deepEqual(progress.amend(entry, true, 30), { a: 3, c: 2, last: 30, ok: true, conf: null });
  assert.deepEqual(progress.amend({ ...entry, ok: true, c: 2 }, false, 30).c, 1);
  assert.deepEqual(progress.amend({ ...entry, ok: true, c: 2 }, true, 30).c, 2);
  assert.deepEqual(progress.amend(undefined, true, 5), { a: 1, c: 1, last: 5, ok: true, conf: null });
});

test("a weak spot is a wrong answer or a right guess", () => {
  assert.equal(progress.isWeak(undefined), false);
  assert.equal(progress.isWeak(wrong(1)), true);
  assert.equal(progress.isWeak(right(1, "guess")), true);
  assert.equal(progress.isWeak(right(1, "unsure")), false);
  assert.equal(progress.isWeak(right(1)), false);
});

test("sectionStatus: pass at >= 80% with 3 answered, fail below 60% with 2", () => {
  const ids = ["a", "b", "c", "d", "e"];
  const st = (q) => progress.sectionStatus(ids, q).status;
  assert.equal(st({}), "none");
  assert.equal(st({ a: right(1), b: right(1) }), "part", "two right is not enough to pass");
  assert.equal(st({ a: right(1), b: right(1), c: right(1) }), "pass");
  assert.equal(st({ a: right(1), b: right(1), c: right(1), d: right(1), e: wrong(1) }), "pass", "80% passes");
  assert.equal(st({ a: right(1), b: right(1), c: wrong(1) }), "part", "67% is neither");
  assert.equal(st({ a: wrong(1) }), "part", "one answer cannot fail a section of five");
  assert.equal(st({ a: right(1), b: wrong(1) }), "fail", "50% with two answered fails");
  assert.equal(st({ a: right(1), b: right(1), c: wrong(1), d: wrong(1), e: wrong(1) }), "fail", "40% fails");
  assert.deepEqual(progress.sectionStatus(ids, { a: right(1), z: right(1) }), {
    status: "part",
    answered: 1,
    correct: 1,
    total: 5,
  });
});

test("sectionStatus: a section with fewer than three questions can pass and fail", () => {
  // 11 real sections hold one or two questions; they must be able to show a verdict.
  const two = (q) => progress.sectionStatus(["a", "b"], q).status;
  assert.equal(two({ a: right(1) }), "part", "one of two answered: not judged yet");
  assert.equal(two({ a: right(1), b: right(1) }), "pass");
  assert.equal(two({ a: right(1), b: wrong(1) }), "fail");
  const one = (q) => progress.sectionStatus(["a"], q).status;
  assert.equal(one({}), "none");
  assert.equal(one({ a: right(1) }), "pass");
  assert.equal(one({ a: wrong(1) }), "fail");
  assert.equal(progress.sectionStatus([], {}).status, "none", "no questions: nothing to judge");
});

test("moduleStatus: any failing section fails it; all passing passes it; work in between is part", () => {
  assert.equal(progress.moduleStatus([]).status, "none");
  assert.equal(progress.moduleStatus(["pass", "pass"]).status, "pass");
  assert.equal(progress.moduleStatus(["pass", "none"]).status, "part", "8 of 9 passing is not 'not tried'");
  assert.equal(progress.moduleStatus(["part", "none"]).status, "part");
  assert.equal(progress.moduleStatus(["none", "none"]).status, "none");
  assert.deepEqual(progress.moduleStatus(["pass", "fail", "none"]), {
    status: "fail",
    pass: 1,
    fail: 1,
    part: 0,
    total: 3,
  });
});

test("every question right in every section means the module passes", () => {
  const s = (ids) => progress.sectionStatus(ids, Object.fromEntries(ids.map((i) => [i, right(1)])));
  const sections = [s(["a", "b", "c"]), s(["d", "e"])];
  assert.equal(progress.moduleStatus(sections.map((x) => x.status)).status, "pass");
});

test("a damaged exam record is repaired, not trusted", () => {
  const s = progress.normalise({ v: 1, exams: [{ id: "e1", status: "running" }] });
  const e = s.exams[0];
  assert.deepEqual(e.questions, []);
  assert.deepEqual(e.answers, {});
  assert.deepEqual(e.flags, []);
  assert.deepEqual(e.paper_answers, []);
  assert.deepEqual(e.ticks, {});
  assert.deepEqual(e.marks, {});
  assert.equal(e.status, "running");
  const kept = progress.normalise({
    v: 1,
    exams: [{ id: "e2", questions: ["a"], answers: { a: 1 }, flags: ["a"], started: 5, minutes: 30, title: "T" }],
  }).exams[0];
  assert.deepEqual([kept.questions, kept.answers, kept.flags, kept.started, kept.minutes], [["a"], { a: 1 }, ["a"], 5, 30]);
  const merged = progress.mergeState(progress.blankState(), { exams: [{ id: "bad" }, null, 7] }).exams;
  assert.deepEqual(merged.map((x) => [x.id, x.questions]), [["bad", []]], "a synced record is repaired too");
});

test("weakSpots lists the oldest first; notTried keeps course order", () => {
  const q = { a: wrong(30), b: right(5), c: right(10, "guess"), d: wrong(20) };
  assert.deepEqual(progress.weakSpots(["a", "b", "c", "d", "e"], q), ["c", "d", "a"]);
  assert.deepEqual(progress.notTried(["a", "x", "b", "y"], q), ["x", "y"]);
});

test("mergeState: per item, the newer copy wins; prefs stay on this device", () => {
  const local = {
    ...progress.blankState(),
    q: { a: right(10), b: wrong(50) },
    fc: { f1: { box: 2, due: 1, last: 5, n: 1 } },
    sec: { s1: 100 },
    plan: { p1: { done: true, last: 9 } },
    exams: [{ id: "e1", started: 1, last: 5, score: 1 }],
    prefs: { theme: "dark", timerHidden: false },
    last: { route: "home", label: "Home", ts: 7 },
  };
  const remote = {
    q: { a: wrong(20), c: right(1) },
    fc: { f1: { box: 4, due: 2, last: 3, n: 2 } },
    sec: { s1: 50, s2: 60 },
    plan: { p1: { done: false, last: 12 } },
    exams: [{ id: "e1", started: 1, last: 9, score: 2 }, { id: "e0", started: 0, last: 1 }],
    prefs: { theme: "light" },
    last: { route: "cards", label: "Flashcards", ts: 3 },
  };
  const m = progress.mergeState(local, remote);
  assert.deepEqual(m.q, { a: wrong(20), b: wrong(50), c: right(1) });
  assert.equal(m.fc.f1.box, 2, "the local card was reviewed later");
  assert.deepEqual(m.sec, { s1: 100, s2: 60 });
  assert.equal(m.plan.p1.done, false);
  assert.deepEqual(m.exams.map((e) => [e.id, e.score]), [["e0", undefined], ["e1", 2]]);
  assert.equal(m.prefs.theme, "dark");
  assert.equal(m.last.route, "home");
  assert.deepEqual(progress.mergeState(local, null).q, local.q, "no remote copy changes nothing");
});

test("stableJson ignores key order and undefined values", () => {
  assert.equal(progress.stableJson({ b: 1, a: [2, { d: 3, c: undefined }] }), '{"a":[2,{"d":3}],"b":1}');
  assert.equal(progress.stableJson({ a: 1, b: 2 }), progress.stableJson({ b: 2, a: 1 }));
  assert.equal(progress.stableJson(undefined), "null");
});
