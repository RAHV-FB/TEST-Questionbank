// CR.state (repair and merge) and CR.makeStore (saving to a storage object that may throw).
import { test } from "node:test";
import assert from "node:assert/strict";
import { load, fakeStorage } from "./helpers/load.mjs";

const CR = load("util.js", "mistakes.js", "state.js", "store.js");
const KEY = "swdev-cram6-v1";

test("blank state has the documented keys", () => {
  assert.deepEqual(Object.keys(CR.state.blank()).sort(), [
    "checks", "done", "drafts", "papers", "prefs", "q", "samples", "sess", "start", "v",
  ]);
});

test("normalise repairs damage and drops unknown keys", () => {
  assert.deepEqual(CR.state.normalise(null), CR.state.blank());
  assert.deepEqual(CR.state.normalise({ v: 2, q: { a: {} } }), CR.state.blank());
  const s = CR.state.normalise({
    v: 1,
    extra: true,
    start: { ts: "soon" },
    done: { x: { d: 1, last: 5 }, bad: 3 },
    q: { a: { a: 2, c: "1", w: -4, last: 9, ok: true }, b: null },
    checks: { c1: { pick: 1, ok: 1, last: 2 }, c2: { pick: "x" } },
    drafts: { k: { v: "text", last: 3 }, j: { v: 4 } },
    sess: { S1: { ids: ["a", "b"], i: 9, res: { a: true, b: "x", c: null } }, bad: { ids: [1] } },
    samples: { S3: { pick: 1, shown: 1, last: 4 }, S7: { pick: "x", shown: false }, S9: { pick: -2 }, bad: 5 },
    papers: [{ id: "p-1", paper: "paper-a", status: "running", started: 5, answers: [] }, { id: 3 }, { id: "p-2", paper: "x", status: "weird" }],
    prefs: { theme: "dark", other: 1 },
  });
  assert.equal(s.start, null);
  assert.deepEqual(s.done, { x: { d: true, last: 5 } });
  assert.deepEqual(s.q, { a: { a: 2, c: 0, w: 0, last: 9, ok: true } });
  assert.deepEqual(s.checks, { c1: { pick: 1, ok: true, last: 2 } });
  assert.deepEqual(s.drafts, { k: { v: "text", last: 3 } });
  assert.deepEqual(s.sess, { S1: { ids: ["a", "b"], i: 2, res: { a: true, c: null }, last: 0 } });
  assert.deepEqual(s.samples, {
    S3: { pick: 1, shown: true, last: 4 },
    S7: { pick: null, shown: false, last: 0 },
    S9: { pick: null, shown: false, last: 0 },
  });
  assert.equal(s.papers.length, 1);
  assert.deepEqual(s.papers[0].answers, {});
  assert.deepEqual(s.prefs, { theme: "dark" });
  assert.equal("extra" in s, false);
});

test("merge: the newer item wins, nothing is lost, preferences stay with the first copy", () => {
  const mine = CR.state.blank();
  const theirs = CR.state.blank();
  mine.q.a = { a: 1, c: 1, w: 0, last: 10, ok: true };
  theirs.q.a = { a: 2, c: 1, w: 1, last: 20, ok: false };
  mine.q.only_mine = { a: 1, c: 0, w: 1, last: 5, ok: false };
  theirs.q.only_theirs = { a: 1, c: 1, w: 0, last: 5, ok: true };
  mine.done.s1 = { d: false, last: 30 };
  theirs.done.s1 = { d: true, last: 20 };
  mine.papers.push({ id: "p1", paper: "paper-a", status: "running", last: 10 });
  theirs.papers.push({ id: "p1", paper: "paper-a", status: "done", last: 50 }, { id: "p2", paper: "paper-c", status: "done", last: 1 });
  mine.prefs.theme = "light";
  theirs.prefs.theme = "dark";
  theirs.start = { ts: 7, last: 9 };
  const m = CR.state.merge(mine, theirs);
  assert.equal(m.q.a.ok, false);
  assert.ok(m.q.only_mine && m.q.only_theirs);
  assert.equal(m.done.s1.d, false, "un-ticking later beats an earlier tick");
  assert.deepEqual(m.papers.map((p) => [p.id, p.status]).sort(), [["p1", "done"], ["p2", "done"]]);
  assert.equal(m.prefs.theme, "light");
  assert.deepEqual(m.start, { ts: 7, last: 9 });
});

test("the store saves after a change and a new store reads it back", async () => {
  const storage = fakeStorage();
  let t = 1000;
  const store = CR.makeStore({ storage, now: () => t++ });
  store.init();
  store.recordAnswer("a", false);
  store.setDone("intro-intro", true);
  store.setCheck("S3-c1", 1, true);
  store.setDraft("open.o.1", "my answer");
  store.setSession("S3", CR.mistakes.newSession(["a", "b"], 1));
  store.flush();
  const saved = JSON.parse(storage.map.get(KEY));
  assert.equal(saved.q.a.ok, false);
  assert.equal(saved.done["intro-intro"].d, true);
  const again = CR.makeStore({ storage });
  again.init();
  assert.equal(again.get().q.a.w, 1);
  assert.equal(again.draft("open.o.1"), "my answer");
  assert.deepEqual(again.session("S3").ids, ["a", "b"]);
  assert.equal(again.storageMode(), "local");
});

test("with storage blocked the store still works in memory", () => {
  const store = CR.makeStore({ storage: fakeStorage({ blocked: true }) });
  store.init();
  assert.equal(store.storageMode(), "memory");
  store.recordAnswer("a", true);
  store.setStart(5000);
  store.flush();
  assert.equal(store.get().q.a.ok, true);
  assert.equal(store.get().start.ts, 5000);
  assert.equal(store.storageMode(), "memory");
});

test("a damaged saved value is replaced by a blank state", () => {
  const storage = fakeStorage();
  storage.map.set(KEY, "{not json");
  const store = CR.makeStore({ storage });
  assert.deepEqual(store.init(), CR.state.blank());
});

test("subscribers hear each change and can unsubscribe", () => {
  const store = CR.makeStore({ storage: fakeStorage() });
  store.init();
  const heard = [];
  const off = store.subscribe((_, kind) => heard.push(kind));
  store.setPref("theme", "dark");
  store.recordAnswer("a", true);
  off();
  store.recordAnswer("b", true);
  assert.deepEqual(heard, ["prefs", "q"]);
});

test("a preference changed here survives the merge with a stored copy", () => {
  const storage = fakeStorage();
  const a = CR.makeStore({ storage });
  a.init();
  a.setPref("theme", "dark");
  a.flush();
  const b = CR.makeStore({ storage });
  b.init();
  b.setPref("theme", "light");
  b.flush();
  assert.equal(JSON.parse(storage.map.get(KEY)).prefs.theme, "light");
  b.setPref("theme", null);
  b.flush();
  assert.equal("theme" in JSON.parse(storage.map.get(KEY)).prefs, false);
});

test("reset writes a blank state straight to storage and keeps the preferences", () => {
  const storage = fakeStorage();
  const store = CR.makeStore({ storage });
  store.init();
  store.setPref("theme", "dark");
  store.recordAnswer("a", false);
  store.setDone("intro-intro", true);
  store.flush();
  store.reset();
  assert.deepEqual(store.get().q, {});
  assert.deepEqual(store.get().done, {});
  const saved = JSON.parse(storage.map.get(KEY));
  assert.deepEqual(saved.q, {});
  assert.equal(saved.prefs.theme, "dark");
  store.flush();
  assert.deepEqual(JSON.parse(storage.map.get(KEY)).q, {}, "nothing comes back on the next save");
});

test("startSession replaces the session and clears the open answers typed for its questions", () => {
  const store = CR.makeStore({ storage: fakeStorage() });
  store.init();
  store.setDraft("open.o1.1", "old text");
  store.setDraft("open.o1.2", "old text");
  store.setDraft("open.other.1", "keep me");
  store.startSession("S7", CR.mistakes.newSession(["o1", "m1"], 5));
  assert.deepEqual(store.session("S7").ids, ["o1", "m1"]);
  assert.equal(store.draft("open.o1.1"), "");
  assert.equal(store.draft("open.o1.2"), "");
  assert.equal(store.draft("open.other.1"), "keep me");
});

test("a sample block remembers the option tried and whether his answer is shown", () => {
  const storage = fakeStorage();
  let t = 10;
  const store = CR.makeStore({ storage, now: () => t++ });
  store.init();
  assert.deepEqual(store.sample("S3"), { pick: null, shown: false, last: 0 });
  store.setSample("S3", { pick: 2 });
  assert.deepEqual(store.sample("S3"), { pick: 2, shown: false, last: 10 });
  store.setSample("S3", { shown: true, pick: 2 });
  store.setSample("S3", { pick: 2 });
  assert.equal(store.sample("S3").shown, true, "a patch changes only the fields it names");
  store.setSample("S3", { shown: false, pick: null });
  store.setSample("S7", { shown: true, pick: null });
  store.flush();
  const again = CR.makeStore({ storage });
  again.init();
  assert.deepEqual(again.sample("S3"), { pick: null, shown: false, last: store.sample("S3").last });
  assert.equal(again.sample("S7").shown, true);
});

test("sample blocks merge item by item and are cleared by reset; their typed parts survive a new session", () => {
  const mine = CR.state.blank();
  const theirs = CR.state.blank();
  mine.samples.S3 = { pick: 1, shown: false, last: 10 };
  theirs.samples.S3 = { pick: 3, shown: true, last: 20 };
  theirs.samples.S4 = { pick: null, shown: true, last: 5 };
  const m = CR.state.merge(mine, theirs);
  assert.deepEqual(m.samples.S3, { pick: 3, shown: true, last: 20 });
  assert.equal(m.samples.S4.shown, true);

  const store = CR.makeStore({ storage: fakeStorage() });
  store.init();
  store.setSample("S7", { shown: true });
  store.setDraft("sample.S7.1", "my try");
  store.startSession("S7", CR.mistakes.newSession(["clean-code-q17"], 5));
  assert.equal(store.draft("sample.S7.1"), "my try", "only the open practice answers are cleared");
  store.reset();
  assert.deepEqual(store.get().samples, {});
  assert.equal(store.draft("sample.S7.1"), "");
});
