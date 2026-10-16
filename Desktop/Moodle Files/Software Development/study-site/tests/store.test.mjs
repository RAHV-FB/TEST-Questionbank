// SD.makeStore: saving, merging with what another tab saved, preferences, and the storage event.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const SD = load("util.js", "progress.js", "leitner.js", "store.js");
const KEY = "swdev-midterm-v1";

// A localStorage stand-in shared by several stores, like two tabs on one device.
function fakeDisk(failing = false) {
  const data = new Map();
  return {
    data,
    getItem(key) {
      if (failing) throw new Error("blocked");
      return data.has(key) ? data.get(key) : null;
    },
    setItem(key, value) {
      if (failing) throw new Error("blocked");
      data.set(key, value);
    },
  };
}

const tab = (disk) => {
  const store = SD.makeStore({ storage: disk });
  store.init();
  return store;
};
const stored = (disk) => JSON.parse(disk.data.get(KEY));

test("answers are saved, and loaded by a fresh tab", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  a.recordAnswer("q1", true, "sure");
  a.setPlanItem("p1", true);
  a.flush();
  assert.equal(stored(disk).q.q1.ok, true);
  const b = tab(disk);
  assert.equal(b.get().q.q1.conf, "sure");
  assert.equal(b.get().plan.p1.done, true);
  assert.equal(b.storageMode(), "local");
});

test("a stale tab that only opens a lesson does not wipe another tab's running exam", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  const b = tab(disk); // opened earlier, never refreshed
  a.saveExam({ id: "sample-1", paper: "sample", status: "running", started: 5, questions: ["x"] });
  a.recordAnswer("q1", false);
  a.flush();
  b.markSection("scrum-s2"); // all b does is read a lesson
  b.setLast("learn.scrum.s2", "Scrum");
  b.flush();
  const saved = stored(disk);
  assert.deepEqual(saved.exams.map((e) => [e.id, e.status]), [["sample-1", "running"]]);
  assert.equal(saved.q.q1.ok, false);
  assert.ok(saved.sec["scrum-s2"] > 0, "and b's own progress is kept too");
  assert.equal(b.get().exams.length, 1, "b adopts what it found");
});

test("two tabs answering different questions keep both answers", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  const b = tab(disk);
  a.recordAnswer("q1", true);
  a.flush();
  b.recordAnswer("q2", false);
  b.flush();
  assert.deepEqual(Object.keys(stored(disk).q).sort(), ["q1", "q2"]);
});

test("the newer copy of one item wins, whichever tab saves last", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  const b = tab(disk);
  a.update("q", (s) => {
    s.q.x = { a: 1, c: 1, last: 100, ok: true, conf: null };
  });
  b.update("q", (s) => {
    s.q.x = { a: 1, c: 0, last: 200, ok: false, conf: null };
  });
  b.flush();
  a.flush(); // a saves later but its copy is older
  assert.equal(stored(disk).q.x.ok, false);
  assert.equal(a.get().q.x.ok, false);
});

test("a preference changed in one tab survives a save from another", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  const b = tab(disk);
  a.setPref("theme", "dark");
  a.flush();
  b.setPref("timerHidden", true);
  b.flush();
  assert.deepEqual([stored(disk).prefs.theme, stored(disk).prefs.timerHidden], ["dark", true]);
});

test("the storage event brings another tab's change in and tells the listeners", () => {
  const disk = fakeDisk();
  const a = tab(disk);
  const b = tab(disk);
  const win = new Map();
  const doc = { visibilityState: "visible", addEventListener() {} };
  b.attach({ addEventListener: (type, fn) => win.set(type, fn) }, doc);
  const seen = [];
  b.subscribe((_, kind) => seen.push(kind));
  a.recordAnswer("q9", true);
  a.flush();
  win.get("storage")({ key: KEY, newValue: disk.data.get(KEY) });
  assert.equal(b.get().q.q9.ok, true);
  assert.deepEqual(seen, ["all"]);
  win.get("storage")({ key: "other", newValue: "{}" });
  assert.deepEqual(seen, ["all"], "other keys are ignored");
});

test("two tabs do not keep rewriting each other", () => {
  const disk = fakeDisk();
  let writes = 0;
  const counting = { ...disk, getItem: disk.getItem, setItem: (k, v) => { writes += 1; disk.setItem(k, v); } };
  const a = tab(counting);
  const b = tab(counting);
  a.recordAnswer("q1", true);
  a.flush();
  b.get(); // b hears about it
  b.update("all", () => {});
  b.flush();
  const after = writes;
  b.flush();
  a.update("all", () => {});
  a.flush();
  assert.equal(writes, after, "saving unchanged state writes nothing");
});

test("blocked storage keeps the state in memory and says so", () => {
  const store = tab(fakeDisk(true));
  store.recordAnswer("q1", true);
  store.flush();
  assert.equal(store.get().q.q1.ok, true);
  assert.equal(store.storageMode(), "memory");
});

test("mergeRemote adopts a synced copy and reports whether anything changed", () => {
  const store = tab(fakeDisk());
  store.recordAnswer("q1", true);
  const seen = [];
  store.subscribe((_, kind) => seen.push(kind));
  assert.equal(store.mergeRemote({ q: { q2: { a: 1, c: 1, last: Date.now() + 1000, ok: true, conf: null } } }), true);
  assert.deepEqual(Object.keys(store.get().q).sort(), ["q1", "q2"]);
  assert.deepEqual(seen, ["all"]);
  assert.equal(store.mergeRemote({}), false);
  assert.equal(store.mergeRemote(null), false);
  assert.deepEqual(seen, ["all"], "nothing new, nobody told");
});

test("drafts and exam records round-trip, and the exam list replaces by id", () => {
  const disk = fakeDisk();
  const store = tab(disk);
  store.setDraft("open.q1.1", "text");
  store.saveExam({ id: "e1", status: "running", started: 1 });
  store.saveExam({ id: "e1", status: "done", started: 1 });
  assert.equal(store.draft("open.q1.1"), "text");
  assert.equal(store.draft("missing"), null);
  assert.deepEqual(store.get().exams.map((e) => e.status), ["done"]);
});
