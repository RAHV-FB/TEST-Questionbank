// SD.makeSync against a fake db: merging in what another device wrote, writing back only what
// differs, changes made while a write is in flight, and how errors are handled.
import { test } from "node:test";
import assert from "node:assert/strict";
import { load } from "./helpers/load.mjs";

const SD = load("util.js", "progress.js", "leitner.js", "store.js", "sync.js");
const tick = (ms = 0) => new Promise((resolve) => setTimeout(resolve, ms));

function fakeDisk() {
  const data = new Map();
  return { getItem: (k) => data.get(k) ?? null, setItem: (k, v) => data.set(k, v) };
}

// A db with two documents; set() takes `latency` ms and can be told to fail.
function fakeDb(initial = {}, { latency = 0 } = {}) {
  const docs = new Map(Object.entries(initial));
  const log = [];
  const failWith = { code: null };
  const ref = (id) => ({
    get: async () => ({ exists: docs.has(id), data: () => docs.get(id) }),
    set: async (data) => {
      log.push(["set", id, JSON.parse(JSON.stringify(data))]);
      await tick(latency);
      if (failWith.code) throw Object.assign(new Error("x"), { code: failWith.code });
      docs.set(id, JSON.parse(JSON.stringify(data)));
    },
  });
  return {
    docs,
    log,
    failWith,
    capabilities: {
      db: { collection: () => ({ doc: ref }) },
      user: { id: async () => "u1" },
    },
  };
}

function setup(db) {
  const store = SD.makeStore({ storage: fakeDisk() });
  store.init();
  const timers = [];
  const sync = SD.makeSync({
    capability: async (name) => db.capabilities[name] ?? null,
    store,
    schedule: (fn, ms) => timers.push([fn, ms]) && timers.length,
  });
  const statuses = [];
  sync.onStatus((s) => statuses.push(s));
  return { store, sync, statuses, timers };
}

test("first connect merges the other device's work in and writes this device's back", async () => {
  const remote = { q: { r1: { a: 1, c: 1, last: Date.now() + 5, ok: true, conf: null } }, drafts: {}, exams: [] };
  const db = fakeDb({ progress: remote });
  const { store, sync, statuses } = setup(db);
  store.recordAnswer("mine", false);
  await sync.start();
  assert.deepEqual(Object.keys(store.get().q).sort(), ["mine", "r1"]);
  assert.deepEqual(Object.keys(db.docs.get("progress").q).sort(), ["mine", "r1"]);
  assert.equal(statuses.at(-1), "synced");
});

test("a draft typed while a write is in flight is kept and goes out next time", async () => {
  const db = fakeDb({}, { latency: 40 });
  const { store, sync, timers } = setup(db);
  store.recordAnswer("q1", true);
  const first = sync.start();
  await tick(10); // the first set() is on its way
  store.setDraft("open.q1.1", "typed while the push was in flight");
  await first;
  assert.equal(store.draft("open.q1.1"), "typed while the push was in flight", "not reverted");
  assert.ok(timers.length > 0, "the change queued another push");
  await sync.flush();
  assert.equal(db.docs.get("work").drafts["open.q1.1"].v, "typed while the push was in flight");
});

test("nothing is written when nothing differs", async () => {
  const db = fakeDb();
  const { store, sync } = setup(db);
  store.recordAnswer("q1", true);
  await sync.start();
  const writes = db.log.length;
  await sync.flush();
  assert.equal(db.log.length, writes);
});

test("a transient error retries later with a longer wait each time; a fatal one gives up", async () => {
  const db = fakeDb();
  const { store, sync, timers, statuses } = setup(db);
  store.recordAnswer("q1", true);
  db.failWith.code = "unavailable";
  await sync.start();
  assert.equal(statuses.at(-1), "off");
  assert.equal(timers.length, 1);
  const first = timers[0][1];
  db.failWith.code = "something_new"; // an unknown code counts as transient
  await timers[0][0]();
  assert.equal(timers.length, 2);
  assert.ok(timers[1][1] > first, "backs off");
  db.failWith.code = "quota_exceeded";
  await timers[1][0]();
  assert.equal(timers.length, 2, "fatal: no more retries");
});

test("a document over the size limit is not written and the status says so", async () => {
  const db = fakeDb();
  const { store, sync, statuses } = setup(db);
  store.setDraft("big", "é".repeat(130 * 1024)); // 260 KiB in bytes, 130K UTF-16 units
  await sync.start();
  assert.equal(statuses.at(-1), "large");
  assert.equal(db.docs.has("work"), false);
});

test("without the capabilities nothing happens", async () => {
  const db = { capabilities: {} };
  const { sync, statuses } = setup(db);
  await sync.start();
  assert.deepEqual(statuses, ["off"]);
});
