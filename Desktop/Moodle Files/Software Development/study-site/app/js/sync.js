// Optional cloud sync when the page runs as a claude.ai Artifact with the db and user
// capabilities. Two private documents per viewer: data/users/<id>/progress (answers, cards,
// sections, plan, last place) and data/users/<id>/work (drafts and exam records). The local copy
// stays the source of truth; any failure leaves the page on localStorage without a word.
// SD.makeSync takes the capability lookup and the store so tests can give it fakes.
SD.makeSync = ({ capability, store, schedule: later = (fn, ms) => setTimeout(fn, ms) }) => {
  const WRITE_MS = 4000;
  const MAX_WAIT_MS = 5 * 60 * 1000;
  const MAX_DOC = 240 * 1024; // a db document holds at most 256 KiB (bytes)
  const DOCS = { progress: ["q", "fc", "sec", "plan", "last"], work: ["drafts", "exams"] };
  // Errors retrying cannot cure (db.d.ts); every other code, known or not, counts as transient.
  const FATAL = new Set([
    "invalid_argument",
    "quota_exceeded",
    "revoked",
    "not_granted",
    "capability_disabled",
    "capability_removed",
    "transform_error",
  ]);
  const listeners = new Set();
  const written = { progress: "", work: "" };
  let status = "off"; // "off" | "synced" | "large" (synced, but one document is too big to write)
  let refs = null;
  let timer = null;
  let busy = false;
  let failures = 0;

  function setStatus(next) {
    status = next;
    for (const listener of listeners) listener(status);
  }

  const pick = (source, keys) => Object.fromEntries(keys.map((k) => [k, source[k] ?? null]));
  const bytes = (text) => new TextEncoder().encode(text).length;

  async function readRemote() {
    const [progress, work] = await Promise.all([refs.progress.get(), refs.work.get()]);
    return {
      ...(progress.exists ? progress.data() : {}),
      ...(work.exists ? work.data() : {}),
    };
  }

  // Read, merge into the live state, write back what differs. Reading first keeps progress made
  // on another device. Nothing local is replaced after a write starts: changes made while a
  // write is in flight stay in the store and go out with the next one.
  async function push() {
    const remote = await readRemote();
    store.mergeRemote(remote);
    let large = false;
    for (const [name, keys] of Object.entries(DOCS)) {
      const live = store.get();
      const mine = SD.progress.stableJson(pick(live, keys));
      if (mine === SD.progress.stableJson(pick(remote, keys)) || mine === written[name]) continue;
      if (bytes(mine) >= MAX_DOC) {
        large = true;
        continue;
      }
      await refs[name].set(pick(live, keys));
      written[name] = mine;
    }
    return large;
  }

  async function flush() {
    timer = null;
    if (!refs) return;
    if (busy) {
      queue(WRITE_MS);
      return;
    }
    busy = true;
    try {
      const large = await push();
      failures = 0;
      setStatus(large ? "large" : "synced");
    } catch (e) {
      setStatus("off");
      if (e && FATAL.has(e.code)) refs = null; // denied, revoked or over quota: stay on this device
      else {
        failures += 1;
        queue(Math.min(WRITE_MS * 2 ** failures, MAX_WAIT_MS));
      }
    } finally {
      busy = false;
    }
  }

  // At most one round trip every four seconds, and only after something changed.
  function queue(ms = WRITE_MS) {
    if (refs && timer === null) timer = later(flush, ms);
  }

  async function connect() {
    const [db, user] = await Promise.all([capability("db"), capability("user")]);
    if (!db || !user) return;
    const uid = await user.id();
    if (!uid) return;
    const mine = db.collection("data/users/" + uid);
    refs = { progress: mine.doc("progress"), work: mine.doc("work") };
    // Listen before the first round trip: what the student does meanwhile goes out with the next.
    store.subscribe((_, kind) => {
      if (kind !== "prefs") queue();
    });
    await flush();
  }

  function start() {
    return connect().catch(() => setStatus("off"));
  }

  function onStatus(listener) {
    listeners.add(listener);
    listener(status);
    return () => listeners.delete(listener);
  }

  return { start, onStatus, flush };
};

SD.sync = SD.makeSync({ capability: (name) => SD.claude.capability(name), store: SD.store });
