// SD.select: Practice filters, the four modes, and stable option shuffles.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const { select } = load("util.js", "progress.js", "select.js");
const q = (id, more = {}) => ({ id, mid: "m1", section_ref: "m1-s1", type: "mcq", level: "exam", ...more });
const right = (last, conf = null) => ({ a: 1, c: 1, last, ok: true, conf });
const wrong = (last) => ({ a: 1, c: 0, last, ok: false, conf: null });
const ALL = ["core", "exam", "hard", "beyond"];

test("filter by scope, type and level", () => {
  const bank = [
    q("a"),
    q("b", { mid: "m2", section_ref: "m2-s1" }),
    q("c", { type: "open" }),
    q("d", { level: "beyond", section_ref: "m1-s2" }),
  ];
  const ids = (opts) => select.filter(bank, opts).map((x) => x.id);
  assert.deepEqual(ids({ scope: { kind: "all" }, type: "any", levels: ALL }), ["a", "b", "c", "d"]);
  assert.deepEqual(ids({ scope: { kind: "module", id: "m1" }, type: "any", levels: ALL }), ["a", "c", "d"]);
  assert.deepEqual(ids({ scope: { kind: "section", id: "m1-s2" }, type: "any", levels: ALL }), ["d"]);
  assert.deepEqual(ids({ scope: { kind: "all" }, type: "open", levels: ALL }), ["c"]);
  assert.deepEqual(ids({ scope: { kind: "all" }, type: "any", levels: ["beyond"] }), ["d"]);
  assert.deepEqual(ids({ scope: { kind: "all" }, type: "any", levels: [] }), []);
});

test("next10: up to 3 weak spots, then untried in course order, then the rest", () => {
  const pool = "abcdefghijkl".split("").map((id) => q(id));
  const state = {
    a: right(5), // solid, seen at 5
    b: wrong(40),
    c: wrong(10),
    d: right(20, "guess"),
    e: wrong(30),
    f: right(1), // solid, seen first
  };
  assert.deepEqual(select.pick("next10", pool, state, 10), ["c", "d", "e", "g", "h", "i", "j", "k", "l", "b"]);
  assert.deepEqual(select.pick("next10", pool, state, Infinity).slice(-3), ["b", "f", "a"]);
});

test("weak and new modes", () => {
  const pool = ["a", "b", "c", "d"].map((id) => q(id));
  const state = { a: wrong(9), b: right(1), c: right(3, "guess") };
  assert.deepEqual(select.pick("weak", pool, state, 10), ["c", "a"]);
  assert.deepEqual(select.pick("weak", pool, state, 1), ["c"]);
  assert.deepEqual(select.pick("new", pool, state, 10), ["d"]);
  assert.throws(() => select.pick("random", pool, state, 10), RangeError);
});

test("sample mode: each original, then its variants", () => {
  const pool = [
    q("s01", { origin: "teacher-sample" }),
    q("s02", { origin: "teacher-sample" }),
    q("s10", { origin: "teacher-variant", variant_of: "s02" }),
    q("s11", { origin: "teacher-variant", variant_of: "s01" }),
    q("s12", { origin: "teacher-variant", variant_of: "s01" }),
    q("s20", { origin: "slides" }),
  ];
  assert.deepEqual(select.sampleOrder(pool), ["s01", "s11", "s12", "s02", "s10"]);
  assert.deepEqual(select.pick("sample", pool, {}, 3), ["s01", "s11", "s12"]);
  const orphan = [q("v", { origin: "teacher-variant", variant_of: "gone" })];
  assert.deepEqual(select.sampleOrder(orphan), ["v"], "a variant whose original was filtered out still shows");
});

test("optionOrder is a stable permutation per question and attempt", () => {
  const order = select.optionOrder("scrum-q03", 0);
  assert.deepEqual(select.optionOrder("scrum-q03", 0), order);
  assert.deepEqual([...order].sort(), [0, 1, 2, 3]);
  const attempts = new Set([0, 1, 2, 3, 4, 5].map((a) => select.optionOrder("scrum-q03", a).join("")));
  assert.ok(attempts.size > 1, "a new attempt reshuffles");
  assert.equal(select.optionOrder("x", 0, 3).length, 3);
});
