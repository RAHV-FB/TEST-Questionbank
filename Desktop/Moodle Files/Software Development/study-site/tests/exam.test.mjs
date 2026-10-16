// SD.exam: the paper catalogue, drawing a paper from the bank, the clock, answer states, marking
// and the attempt records.
import { test } from "node:test";
import assert from "node:assert/strict";
import { fixture, load } from "./helpers/load.mjs";

const SD = load("util.js", "route.js", "progress.js", "scoring.js", "data.js", "exam.js");
const { exam } = SD;
const MIN = 60 * 1000;
const T0 = Date.UTC(2026, 9, 15, 8, 0, 0);

const mcq = (id, mid, extra = {}) => ({
  id,
  mid,
  section_ref: `${mid}-s1`,
  type: "mcq",
  options: [{ correct: false }, { correct: true }, { correct: false }, { correct: false }],
  ...extra,
});
const open = (id, mid, marks = [1, 2]) => ({
  id,
  mid,
  section_ref: `${mid}-s2`,
  type: "open",
  parts: marks.map((m, i) => ({ label: String(i + 1), marks: m, rubric: ["a", "b", "c"] })),
});
const sort = (id, mid, extra = {}) => ({
  id,
  mid,
  section_ref: `${mid}-s1`,
  type: "sort",
  categories: [{ id: "x" }, { id: "y" }],
  items: [{ category: "x" }, { category: "y" }, { category: "x" }],
  ...extra,
});

// A bank of `mods` modules with `perModule` mcq and 2 open questions each, in course order.
function bank(mods = 12, perModule = 5) {
  const out = [];
  for (let m = 1; m <= mods; m += 1) {
    const mid = `m${String(m).padStart(2, "0")}`;
    for (let i = 1; i <= perModule; i += 1) out.push(mcq(`${mid}-q${i}`, mid));
    out.push(open(`${mid}-o1`, mid), open(`${mid}-o2`, mid));
  }
  return out;
}

const byId = (list) => new Map(list.map((q) => [q.id, q]));
const perModule = (ids, lookup) => {
  const counts = {};
  for (const id of ids) counts[lookup.get(id).mid] = (counts[lookup.get(id).mid] || 0) + 1;
  return counts;
};

test("catalogue: the sample paper, the mock papers, then the bank", () => {
  const data = SD.indexContent({ meta: {}, ...fixture() });
  const list = exam.catalogue(data);
  assert.deepEqual(
    list.map((p) => [p.id, p.kind, p.minutes]),
    [
      ["sample", "sample", 30],
      ["paper-a", "realistic", 60],
      ["paper-b", "worst-case", 60],
      ["bank", "bank", 60],
    ],
  );
  const sample = list[0];
  assert.deepEqual(sample.questions, ["sample-paper-q01", "sample-paper-q06", "sample-paper-q07"]);
  assert.ok(sample.questions.every((id) => data.question(id).origin === "teacher-sample"));
  assert.deepEqual(list[1].questions, ["paper-a-q01", "paper-a-q02", "paper-a-q03"]);
  assert.equal(list[3].questions, null, "the bank paper is drawn when it starts");
});

test("catalogue: no sample paper without the sample-paper module", () => {
  const raw = fixture();
  raw.modules = raw.modules.filter((m) => m.id !== "sample-paper");
  const ids = exam.catalogue(SD.indexContent({ meta: {}, ...raw })).map((p) => p.id);
  assert.deepEqual(ids, ["paper-a", "paper-b", "bank"]);
});

test("marksOf and typeCounts", () => {
  assert.equal(exam.marksOf(mcq("a", "m")), 1);
  assert.equal(exam.marksOf(open("b", "m", [1, 2, 3])), 6);
  assert.equal(exam.marksOf(sort("c", "m")), 1);
  assert.deepEqual(exam.typeCounts([mcq("a", "m"), open("b", "m"), mcq("c", "m")]), { mcq: 2, open: 1, sort: 0 });
});

test("buildBank: 12 mcq + 3 open, one mcq per module, mcq first, no repeats", () => {
  const b = bank();
  const ids = exam.buildBank(b, {}, 7);
  const lookup = byId(b);
  assert.equal(ids.length, 15);
  assert.equal(new Set(ids).size, 15, "never the same question twice");
  assert.deepEqual(
    ids.map((id) => lookup.get(id).type),
    [...Array(12).fill("mcq"), ...Array(3).fill("open")],
  );
  const mcqIds = ids.slice(0, 12);
  assert.deepEqual(Object.values(perModule(mcqIds, lookup)), Array(12).fill(1), "stratified");
  const openMods = Object.keys(perModule(ids.slice(12), lookup));
  assert.equal(openMods.length, 3, "three open questions from three modules");
  const order = b.map((q) => q.id);
  const positions = mcqIds.map((id) => order.indexOf(id));
  assert.deepEqual(positions, [...positions].sort((x, y) => x - y), "course order within a type");
});

test("buildBank: stratified when there are fewer modules than questions", () => {
  const b = bank(5, 6);
  const lookup = byId(b);
  const ids = exam.buildBank(b, {}, 3);
  const counts = Object.values(perModule(ids.filter((id) => lookup.get(id).type === "mcq"), lookup));
  assert.equal(counts.reduce((x, y) => x + y, 0), 12);
  assert.ok(Math.max(...counts) - Math.min(...counts) <= 1, `counts ${counts}`);
});

test("buildBank: weak spots first, then not tried, then solid (oldest first)", () => {
  const b = bank(2, 4); // m01-q1..q4, m02-q1..q4
  const qState = {
    "m01-q1": { a: 1, c: 1, last: 50, ok: true, conf: null },
    "m01-q2": { a: 1, c: 1, last: 10, ok: true, conf: null },
    "m01-q3": { a: 1, c: 0, last: 90, ok: false, conf: null },
    "m01-q4": { a: 1, c: 1, last: 20, ok: true, conf: "guess" },
    "m02-q1": { a: 1, c: 1, last: 5, ok: true, conf: null },
  };
  // One question per module: each module's most pressing candidate.
  const two = exam.buildBank(b, qState, 1, { mcq: 2, open: 0 });
  assert.equal(two[0], "m01-q4", "the weak spot seen longest ago (a guess) comes first in m01");
  assert.notEqual(two[1], "m02-q1", "m02 offers a question not tried before a solid one");
  const four = exam.buildBank(b, qState, 1, { mcq: 4, open: 0 });
  assert.ok(four.includes("m01-q3"), "both weak spots of m01 are taken before anything else there");
  const all = exam.buildBank(b, qState, 1, { mcq: 8, open: 0 });
  assert.deepEqual(all, b.filter((q) => q.type === "mcq").map((q) => q.id), "the whole bank, course order");
});

test("buildBank: a module with weak spots gets the spare place", () => {
  const b = bank(3, 3);
  const qState = {
    "m03-q2": { a: 1, c: 0, last: 1, ok: false, conf: null },
    "m03-q3": { a: 2, c: 1, last: 2, ok: false, conf: null },
  };
  const lookup = byId(b);
  for (const seed of [1, 2, 3, 4]) {
    const ids = exam.buildBank(b, qState, seed, { mcq: 1, open: 0 });
    assert.deepEqual(ids, ["m03-q2"], `seed ${seed}`);
    const four = exam.buildBank(b, qState, seed, { mcq: 4, open: 0 });
    assert.equal(perModule(four, lookup).m03, 2);
  }
});

test("buildBank: the same seed draws the same paper; other seeds vary it", () => {
  const b = bank();
  assert.deepEqual(exam.buildBank(b, {}, 42), exam.buildBank(b, {}, 42));
  const papers = new Set([1, 2, 3, 4, 5, 6].map((s) => exam.buildBank(b, {}, s).join()));
  assert.ok(papers.size > 1);
});

test("buildBank: never two questions of one family, and a short bank gives what it has", () => {
  const b = [
    mcq("x-q1", "x"),
    mcq("x-q2", "x", { variant_of: "x-q1" }),
    mcq("x-q3", "x", { variant_of: "x-q1" }),
    mcq("y-q1", "y"),
    open("y-o1", "y"),
    sort("y-s1", "y"),
  ];
  const ids = exam.buildBank(b, {}, 9);
  assert.equal(ids.filter((id) => id.startsWith("x-")).length, 1, "one of the x-q1 family");
  assert.deepEqual(ids.slice(-1), ["y-o1"]);
  assert.ok(!ids.includes("y-s1"), "sort questions are not drawn");
  assert.equal(ids.length, 3);
  assert.deepEqual(exam.buildBank([], {}, 1), []);
});

test("start: a running record with the paper's time and marks", () => {
  const qs = [mcq("a", "m"), open("b", "m", [2, 3])];
  const rec = exam.start({ id: "paper-a", title: "Paper A", minutes: 60 }, qs, T0);
  assert.equal(rec.id, `paper-a-${T0}`);
  assert.match(rec.id, /^[A-Za-z0-9_~-]+$/, "the id is a route token");
  assert.equal(rec.status, "running");
  assert.deepEqual(rec.questions, ["a", "b"]);
  assert.equal(rec.max, 6);
  assert.deepEqual([rec.answers, rec.flags, rec.ticks, rec.marks], [{}, [], {}, {}]);
});

test("questionsOf skips questions no longer in the content", () => {
  const lookup = byId([mcq("a", "m"), mcq("c", "m")]);
  const rec = { questions: ["a", "b", "c"] };
  assert.deepEqual(exam.questionsOf(rec, (id) => lookup.get(id) || null).map((q) => q.id), ["a", "c"]);
});

test("the clock: time left survives a reload because it runs from the start time", () => {
  const rec = exam.start({ id: "paper-a", title: "Paper A", minutes: 60 }, [], T0);
  assert.equal(exam.deadline(rec), T0 + 60 * MIN);
  assert.equal(exam.timeLeft(rec, T0 + 12 * MIN + 30_000), 47 * MIN + 30_000);
  assert.equal(exam.timeLeft(rec, T0 + 61 * MIN), 0);
  assert.equal(exam.expired(rec, T0 + 60 * MIN - 1), false);
  assert.equal(exam.expired(rec, T0 + 60 * MIN), true);
  assert.equal(exam.expired({ ...rec, status: "done" }, T0 + 99 * MIN), false);
});

test("warnings at 10 and 5 minutes", () => {
  assert.equal(exam.warning(10 * MIN + 1), 0);
  assert.equal(exam.warning(10 * MIN), 10);
  assert.equal(exam.warning(5 * MIN + 1), 10);
  assert.equal(exam.warning(5 * MIN), 5);
  assert.equal(exam.warning(0), 5);
});

test("finish: handed in early, at 0:00, or noticed late", () => {
  const rec = exam.start({ id: "sample", title: "Sample", minutes: 30 }, [], T0);
  const early = exam.finish(rec, T0 + 22 * MIN);
  assert.deepEqual(
    [early.status, early.ended, early.used_ms, early.timed_out],
    ["done", T0 + 22 * MIN, 22 * MIN, false],
  );
  const out = exam.finish(rec, T0 + 30 * MIN + 400, true);
  assert.deepEqual([out.ended, out.used_ms, out.timed_out], [T0 + 30 * MIN, 30 * MIN, true]);
  const late = exam.finish(rec, T0 + 26 * 60 * MIN);
  assert.deepEqual([late.ended, late.used_ms, late.timed_out], [T0 + 30 * MIN, 30 * MIN, true]);
});

test("answerState for each question type", () => {
  const q = open("o", "m", [1, 1, 1]);
  assert.equal(exam.answerState(mcq("a", "m"), undefined), "blank");
  assert.equal(exam.answerState(mcq("a", "m"), 0), "full");
  assert.equal(exam.answerState(q, undefined), "blank");
  assert.equal(exam.answerState(q, { 1: "  \n " }), "blank");
  assert.equal(exam.answerState(q, { 1: "text", 3: "more" }), "partial");
  assert.equal(exam.answerState(q, { 1: "a", 2: "b", 3: "c" }), "full");
  assert.equal(exam.answerState(sort("s", "m"), [null, null, null]), "blank");
  assert.equal(exam.answerState(sort("s", "m"), ["x", null, "x"]), "partial");
  assert.equal(exam.answerState(sort("s", "m"), ["x", "y", "y"]), "full");
});

test("mark: mcq auto-marked, open to mark until recorded, blank open scores 0", () => {
  const qs = [
    mcq("q1", "m1"),
    mcq("q2", "m1"),
    mcq("q3", "m2"),
    open("q4", "m2", [1, 2]),
    open("q5", "m1", [2, 2]),
    open("q6", "m2", [1, 1]),
    sort("q7", "m1"),
  ];
  const rec = {
    answers: {
      q1: 1, // right
      q2: 3, // wrong
      // q3 blank
      q4: { 1: "an answer", 2: "another" },
      q5: { 1: "something" },
      // q6 blank
      q7: ["x", "y", "x"],
    },
    marks: { q5: 3 },
  };
  const m = exam.mark(qs, rec);
  assert.deepEqual(
    m.results.map((r) => [r.qid, r.status, r.score, r.max]),
    [
      ["q1", "pass", 1, 1],
      ["q2", "fail", 0, 1],
      ["q3", "fail", 0, 1],
      ["q4", "mark", 0, 3],
      ["q5", "fail", 3, 4],
      ["q6", "fail", 0, 2],
      ["q7", "pass", 1, 1],
    ],
  );
  assert.deepEqual([m.passed, m.failed, m.toMark, m.score, m.max], [2, 4, 1, 5, 13]);
  assert.deepEqual(m.modules, [
    { mid: "m1", count: 4, passed: 2, failed: 2, toMark: 0, score: 5, max: 7 },
    { mid: "m2", count: 3, passed: 0, failed: 2, toMark: 1, score: 0, max: 6 },
  ]);

  assert.deepEqual(
    m.sections.map((row) => [row.sid, row.count, row.score, row.max]),
    [
      ["m1-s1", 3, 2, 3],
      ["m2-s1", 1, 0, 1],
      ["m2-s2", 2, 0, 5],
      ["m1-s2", 1, 3, 4],
    ],
    "the same figures per section, in order of first appearance",
  );

  const marked = exam.mark(qs, { ...rec, marks: { q4: 3, q5: 9 } });
  assert.deepEqual(marked.results[3], {
    qid: "q4",
    mid: "m2",
    sid: "m2-s2",
    type: "open",
    state: "full",
    status: "pass",
    score: 3,
    max: 3,
  });
  assert.equal(marked.results[4].score, 4, "a recorded mark is capped at the question's marks");
});

test("withTotals writes the summary fields Home reads", () => {
  const qs = [mcq("q1", "m"), open("q2", "m", [2])];
  const rec = {
    ...exam.start({ id: "bank", title: "Bank", minutes: 60 }, qs, T0),
    answers: { q1: 1, q2: { 1: "x" } },
  };
  const r = exam.withTotals(rec, qs);
  assert.deepEqual([r.passed, r.failed, r.to_mark, r.score, r.max], [1, 0, 1, 1, 3]);
  const done = exam.withTotals({ ...r, marks: { q2: 1 } }, qs);
  assert.deepEqual([done.passed, done.failed, done.to_mark, done.score], [1, 1, 0, 2]);
});

test("running, newestFirst and lastDone", () => {
  const exams = [
    { id: "a", paper: "paper-a", status: "done", started: 1 },
    { id: "b", paper: "paper-a", status: "done", started: 3 },
    { id: "c", paper: "sample", status: "running", started: 2 },
  ];
  assert.equal(exam.running(exams).id, "c");
  assert.equal(exam.running(exams.slice(0, 2)), null);
  assert.deepEqual(exam.newestFirst(exams).map((e) => e.id), ["b", "c", "a"]);
  assert.equal(exam.lastDone(exams, "paper-a").id, "b");
  assert.equal(exam.lastDone(exams, "sample"), null);
});

test("buildBank: when two modules' heads are one family, neither module loses its turn", () => {
  // 22 of the real bank's variants point at an original in another module.
  const b = [];
  for (const mid of ["m1", "m2", "m3", "m4"]) for (let i = 1; i <= 3; i += 1) b.push(mcq(`${mid}-q${i}`, mid));
  b.find((q) => q.id === "m1-q1").variant_of = "m3-q1";
  b.find((q) => q.id === "m2-q1").variant_of = "m3-q1";
  const qState = { "m1-q1": { ok: false, last: 1 }, "m2-q1": { ok: false, last: 2 } };
  const ids = exam.buildBank(b, qState, 1, { mcq: 4 });
  const counts = perModule(ids, byId(b));
  assert.equal(ids.length, 4);
  assert.deepEqual(Object.values(counts).sort(), [1, 1, 1, 1], "every module gets exactly one");
  for (let seed = 0; seed < 60; seed += 1) {
    const drawn = exam.buildBank(b, qState, seed, { mcq: 4 });
    assert.equal(new Set(drawn.map((id) => byId(b).get(id).mid)).size, 4, `seed ${seed}`);
  }
});

test("answerState: an open answer written on paper counts as answered", () => {
  const q = open("o", "m", [1, 1, 1]);
  assert.equal(exam.answerState(q, undefined, true), "full");
  assert.equal(exam.answerState(q, undefined, false), "blank");
  assert.equal(exam.answerState(mcq("a", "m"), undefined, true), "blank", "only open answers can be on paper");
});

test("mark: an open answer written on paper waits to be marked instead of failing", () => {
  const qs = [open("q1", "m", [2, 2]), open("q2", "m", [1])];
  const rec = { answers: {}, marks: {}, paper_answers: ["q1"] };
  const m = exam.mark(qs, rec);
  assert.deepEqual(m.results.map((r) => [r.qid, r.state, r.status]), [
    ["q1", "full", "mark"],
    ["q2", "blank", "fail"],
  ]);
  const marked = exam.mark(qs, { ...rec, marks: { q1: 3 } });
  assert.deepEqual([marked.results[0].status, marked.results[0].score], ["fail", 3], "below full marks");
  const full = exam.mark(qs, { ...rec, marks: { q1: 4 } });
  assert.equal(full.results[0].status, "pass");
});

test("untouched and discard: a sitting with no answers leaves nothing behind", () => {
  const qs = [mcq("a", "m"), open("b", "m")];
  const rec = exam.start({ id: "paper-a", title: "Paper A", minutes: 60 }, qs, T0);
  assert.equal(exam.untouched(rec, qs), true);
  assert.equal(exam.untouched({ ...rec, answers: { a: 0 } }, qs), false);
  assert.equal(exam.untouched({ ...rec, answers: { b: { 1: "  " } } }, qs), true, "spaces are not an answer");
  assert.equal(exam.untouched({ ...rec, paper_answers: ["b"] }, qs), false, "written on paper is an answer");
  const gone = exam.discard({ ...rec, answers: { a: 2 } }, T0 + MIN);
  assert.deepEqual(gone, {
    id: rec.id,
    paper: "paper-a",
    title: "Paper A",
    minutes: 60,
    started: T0,
    ended: T0 + MIN,
    status: "discarded",
  });
  const exams = [gone, { id: "z", paper: "paper-a", status: "done", started: 1 }];
  assert.deepEqual(exam.newestFirst(exams).map((e) => e.id), ["z"], "discarded sittings are not listed");
  assert.equal(exam.running(exams), null);
  assert.equal(exam.lastDone([gone], "paper-a"), null);
});

test("start: the record has room for the paper answers and what hand-in recorded", () => {
  const rec = exam.start({ id: "paper-a", title: "Paper A", minutes: 60 }, [mcq("a", "m")], T0);
  assert.deepEqual([rec.paper_answers, rec.recorded], [[], []]);
});

test("lostBySection ranks sections by marks lost and leaves out what is still to mark", () => {
  const r = (sid, status, score, max) => ({ sid, status, score, max });
  const results = [
    r("s1", "fail", 0, 1),
    r("s2", "fail", 1, 4),
    r("s1", "pass", 1, 1),
    r("s3", "mark", 0, 5),
    r("s2", "fail", 0, 1),
    r("s4", "pass", 2, 2),
    r("s5", "fail", 0, 1),
  ];
  assert.deepEqual(exam.lostBySection(results), [
    { sid: "s2", lost: 4 },
    { sid: "s1", lost: 1 },
    { sid: "s5", lost: 1 },
  ]);
  assert.deepEqual(exam.lostBySection([]), []);
});

test("resit: each original is swapped for an unseen variant of its own type", () => {
  const originals = [mcq("o1", "m"), mcq("o2", "m"), open("o3", "m")];
  const variants = [
    mcq("v1a", "m", { variant_of: "o1" }),
    mcq("v1b", "m", { variant_of: "o1" }),
    sort("v2s", "m", { variant_of: "o2" }),
    { ...open("v3a", "m"), variant_of: "o3" },
    mcq("v3m", "m", { variant_of: "o3" }),
    mcq("other", "m", { variant_of: "zzz" }),
  ];
  const ids = exam.resit(originals, variants, {}, 3);
  assert.equal(ids.length, 3);
  assert.ok(["v1a", "v1b"].includes(ids[0]));
  assert.equal(ids[1], "o2", "only a sort variant exists for an mcq: the original stays");
  assert.equal(ids[2], "v3a", "an open question is swapped for an open variant, not an mcq");
  // unseen first, then the one seen longest ago
  assert.equal(exam.resit(originals, variants, { v1a: { last: 5 } }, 1)[0], "v1b");
  assert.equal(exam.resit(originals, variants, { v1a: { last: 5 }, v1b: { last: 9 } }, 1)[0], "v1a");
  assert.deepEqual(exam.resit(originals, variants, {}, 8), exam.resit(originals, variants, {}, 8), "stable for a seed");
  const seen = new Set(Array.from({ length: 30 }, (_, i) => exam.resit(originals, variants, {}, i)[0]));
  assert.equal(seen.size, 2, "other seeds choose the other variant");
});

test("firstDone is the baseline sitting; lastDone the newest", () => {
  const exams = [
    { id: "b", paper: "sample", status: "done", started: 3 },
    { id: "a", paper: "sample", status: "done", started: 1 },
    { id: "c", paper: "sample", status: "running", started: 5 },
    { id: "d", paper: "sample", status: "discarded", started: 0 },
  ];
  assert.equal(exam.firstDone(exams, "sample").id, "a");
  assert.equal(exam.lastDone(exams, "sample").id, "b");
  assert.equal(exam.firstDone(exams, "paper-a"), null);
});
