// The progress store: one state object, saved to localStorage under "swdev-cram-v1" when it can
// be. Every access is in try/catch; with storage blocked the page still works and the footer says
// progress is not being saved. Listeners hear (state, kind) after each change. Several tabs can be
// open: each save merges what is stored with this tab's state item by item (CR.state.merge) and the
// browser's "storage" event brings another tab's changes in. CR.makeStore takes a storage object
// so tests can give it a fake.
CR.makeStore = ({ storage = null, now = Date.now } = {}) => {
  const KEY = "swdev-cram-v1";
  const SAVE_MS = 300;
  const listeners = new Set();
  const dirtyPrefs = new Set();
  const disk = storage || {
    getItem: (key) => window.localStorage.getItem(key),
    setItem: (key, value) => window.localStorage.setItem(key, value),
  };
  let state = CR.state.blank();
  let mode = "memory"; // "local" once a write to storage has succeeded
  let saveTimer = null;

  function parse(raw) {
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function readStored() {
    try {
      const raw = disk.getItem(KEY);
      return raw ? CR.state.normalise(parse(raw)) : null;
    } catch {
      return null;
    }
  }

  function save() {
    saveTimer = null;
    const stored = readStored();
    if (stored) {
      // Preferences changed in this tab win; the rest come from storage.
      const merged = CR.state.merge(state, stored);
      const prefs = { ...stored.prefs };
      for (const key of dirtyPrefs) {
        if (key in state.prefs) prefs[key] = state.prefs[key];
        else delete prefs[key];
      }
      merged.prefs = prefs;
      Object.assign(state, merged);
    }
    dirtyPrefs.clear();
    try {
      if (!stored || CR.state.stableJson(stored) !== CR.state.stableJson(state)) {
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
    const stored = readStored();
    if (stored) {
      state = stored;
      mode = "local";
    } else {
      // Storage empty, blocked or damaged: probe with a write so the footer tells the truth.
      try {
        disk.setItem(KEY, JSON.stringify(state));
        mode = "local";
      } catch {
        mode = "memory";
      }
    }
    return state;
  }

  function attach(win, doc) {
    doc.addEventListener("visibilitychange", () => {
      if (doc.visibilityState === "hidden") flush();
    });
    win.addEventListener("pagehide", flush);
    win.addEventListener("storage", (event) => {
      if (event.key !== KEY) return;
      const stored = readStored();
      if (!stored) return;
      Object.assign(state, CR.state.merge(state, stored));
      notify("all");
    });
  }

  const subscribe = (fn) => {
    listeners.add(fn);
    return () => listeners.delete(fn);
  };

  return {
    init,
    attach,
    flush,
    subscribe,
    update,
    get: () => state,
    storageMode: () => mode,

    // ---- questions and sessions
    recordAnswer(qid, ok) {
      update("q", (s) => CR.mistakes.record(s.q, qid, ok, now()));
    },
    amendAnswer(qid, ok) {
      update("q", (s) => CR.mistakes.amend(s.q, qid, ok, now()));
    },
    session: (key) => state.sess[key] || null,
    setSession(key, sess) {
      update("sess", (s) => {
        s.sess[key] = { ...sess, last: now() };
      });
    },
    // A new session over `sess.ids`: the open answers typed last time are cleared, so a question
    // is answered again from memory and not from the old text.
    startSession(key, sess) {
      update("sess", (s) => {
        s.sess[key] = { ...sess, last: now() };
        for (const dk of Object.keys(s.drafts)) {
          if (sess.ids.some((id) => dk.startsWith(`open.${id}.`))) delete s.drafts[dk];
        }
      });
    },
    clearSession(key) {
      update("sess", (s) => {
        delete s.sess[key];
      });
    },

    // ---- the route
    setDone(stopId, done) {
      update("done", (s) => {
        s.done[stopId] = { d: Boolean(done), last: now() };
      });
    },
    setStart(ts) {
      update("start", (s) => {
        s.start = ts === null ? null : { ts, last: now() };
      });
    },

    // ---- quick checks and drafts
    setCheck(id, pick, ok) {
      update("checks", (s) => {
        s.checks[id] = { pick, ok: Boolean(ok), last: now() };
      });
    },
    clearCheck(id) {
      update("checks", (s) => {
        delete s.checks[id];
      });
    },
    draft: (key) => state.drafts[key]?.v ?? "",
    setDraft(key, value) {
      update("drafts", (s) => {
        s.drafts[key] = { v: value, last: now() };
      });
    },

    // ---- papers
    savePaper(record) {
      update("papers", (s) => {
        const i = s.papers.findIndex((p) => p.id === record.id);
        const next = { ...record, last: now() };
        if (i >= 0) s.papers[i] = next;
        else s.papers.push(next);
      });
    },

    // ---- start again: everything but the device settings
    reset() {
      // Written straight to storage: a merge with the stored copy would bring everything back.
      if (saveTimer !== null) clearTimeout(saveTimer);
      saveTimer = null;
      const fresh = CR.state.blank();
      fresh.prefs = state.prefs;
      Object.assign(state, fresh);
      try {
        disk.setItem(KEY, JSON.stringify(state));
        mode = "local";
      } catch {
        mode = "memory";
      }
      notify("all");
    },

    // ---- device settings
    setPref(key, value) {
      dirtyPrefs.add(key);
      update("prefs", (s) => {
        if (value === null || value === undefined) delete s.prefs[key];
        else s.prefs[key] = value;
      });
    },
  };
};
