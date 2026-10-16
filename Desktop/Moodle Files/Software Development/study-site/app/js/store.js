// The progress store: one state object, saved to localStorage when it can be (every access is
// guarded; the page works with storage blocked). Listeners hear (state, kind) after each change,
// where kind names the part that changed: "q", "fc", "sec", "drafts", "plan", "prefs", "last",
// "exams" or "all".
//
// Several tabs may be open on one device. Each save first reads what is stored and merges it with
// this tab's state item by item (the newer copy of each item wins, see SD.progress.mergeState),
// so a tab that was only reading never wipes the work done in another; the browser's "storage"
// event brings the other tab's changes in. SD.makeStore takes the storage object so tests can
// give it a fake.
SD.makeStore = ({ storage = null } = {}) => {
  const KEY = "swdev-midterm-v1";
  const SAVE_MS = 300;
  const listeners = new Set();
  const dirtyPrefs = new Set(); // preference keys changed here since the last save
  // localStorage, reached through functions so that merely touching it cannot throw here.
  const disk = storage || {
    getItem: (key) => window.localStorage.getItem(key),
    setItem: (key, value) => window.localStorage.setItem(key, value),
  };
  let state = SD.progress.blankState();
  let mode = "memory"; // "local" once a write to storage has succeeded
  let saveTimer = null;

  function parse(text) {
    try {
      return text ? JSON.parse(text) : null;
    } catch {
      return null;
    }
  }

  function readStored() {
    try {
      return SD.progress.normalise(parse(disk.getItem(KEY)));
    } catch {
      return null;
    }
  }

  // This tab's state merged with what another tab stored: newer items win; of the preferences,
  // those changed here win and the rest come from storage.
  function mergedWith(stored) {
    const merged = SD.progress.mergeState(state, stored);
    const mine = Object.fromEntries([...dirtyPrefs].map((k) => [k, state.prefs[k]]));
    merged.prefs = { ...state.prefs, ...stored.prefs, ...mine };
    return merged;
  }

  function save() {
    saveTimer = null;
    const stored = readStored();
    if (stored) Object.assign(state, mergedWith(stored));
    dirtyPrefs.clear();
    try {
      // Skip a write that changes nothing, so two tabs never keep rewriting each other.
      if (!stored || SD.progress.stableJson(stored) !== SD.progress.stableJson(state)) {
        disk.setItem(KEY, JSON.stringify(state));
      }
      mode = "local";
    } catch {
      mode = "memory";
    }
  }

  function flush() {
    if (saveTimer !== null) {
      clearTimeout(saveTimer);
      save();
    }
  }

  function notify(kind) {
    for (const listener of [...listeners]) listener(state, kind);
  }

  // The one way to change state: mutate it inside fn, then listeners run and a save is queued.
  function update(kind, fn) {
    fn(state);
    if (saveTimer === null) saveTimer = setTimeout(save, SAVE_MS);
    notify(kind);
  }

  function init() {
    state = readStored() || SD.progress.blankState();
    save();
  }

  // Hook the store to the page: save when the page is hidden or left, and pick up what another
  // tab saved. win and doc are window and document (or stand-ins in tests).
  function attach(win, doc) {
    win.addEventListener("pagehide", flush);
    doc.addEventListener("visibilitychange", () => {
      if (doc.visibilityState === "hidden") flush();
    });
    win.addEventListener("storage", (event) => {
      if (event.key !== KEY) return;
      const stored = SD.progress.normalise(parse(event.newValue));
      Object.assign(state, mergedWith(stored));
      notify("all");
    });
  }

  // Merge a copy from another device (sync) into this state; true when anything changed.
  function mergeRemote(remote) {
    const merged = SD.progress.mergeState(state, remote);
    if (SD.progress.stableJson(merged) === SD.progress.stableJson(state)) return false;
    update("all", (s) => Object.assign(s, merged));
    return true;
  }

  const now = () => Date.now();

  return {
    init,
    attach,
    flush,
    get: () => state,
    update,
    mergeRemote,
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    storageMode: () => mode,
    recordAnswer: (qid, ok, conf = null) =>
      update("q", (s) => {
        s.q[qid] = SD.progress.record(s.q[qid], ok, conf, now());
      }),
    amendAnswer: (qid, ok) =>
      update("q", (s) => {
        s.q[qid] = SD.progress.amend(s.q[qid], ok, now());
      }),
    // examStart (a timestamp) cuts long waits short so the card is back before the exam.
    reviewCard: (id, grade, examStart = null) =>
      update("fc", (s) => {
        s.fc[id] = SD.leitner.review(s.fc[id], grade, now(), examStart);
      }),
    markSection: (id) =>
      update("sec", (s) => {
        s.sec[id] = now();
      }),
    draft: (key) => state.drafts[key]?.v ?? null,
    setDraft: (key, value) =>
      update("drafts", (s) => {
        s.drafts[key] = { v: value, last: now() };
      }),
    setPlanItem: (id, done) =>
      update("plan", (s) => {
        s.plan[id] = { done, last: now() };
      }),
    setPref: (key, value) =>
      update("prefs", (s) => {
        s.prefs[key] = value;
        dirtyPrefs.add(key);
      }),
    setLast: (route, label) =>
      update("last", (s) => {
        s.last = { route, label, ts: now() };
      }),
    saveExam: (exam) =>
      update("exams", (s) => {
        const record = { ...exam, last: now() };
        const i = s.exams.findIndex((e) => e.id === record.id);
        if (i === -1) s.exams.push(record);
        else s.exams[i] = record;
      }),
  };
};

SD.store = SD.makeStore();
