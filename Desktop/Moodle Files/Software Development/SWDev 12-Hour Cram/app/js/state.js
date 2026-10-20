// Pure progress state: the blank state, repairing whatever storage holds, and merging two copies
// (two tabs of one browser). Shape (v: 1):
//   start   {ts, last} | null      the time the 12-hour route starts
//   done    {[stopId]: {d, last}}   route stops ticked off
//   q       {[qid]: {a, c, w, last, ok}}   attempts at questions (see CR.mistakes)
//   checks  {[checkId]: {pick, ok, last}}  the quick checks inside the basics
//   drafts  {[key]: {v, last}}      open-answer text, saved as you type
//   sess    {[key]: {ids, i, res, last}}   a practice session in progress (see CR.mistakes)
//   papers  [record]                sittings (see CR.paper)
//   prefs   {theme}                 device-local settings
CR.state = (() => {
  const VERSION = 1;
  const isObject = (x) => x !== null && typeof x === "object" && !Array.isArray(x);
  const num = (x, fallback = 0) => (typeof x === "number" && Number.isFinite(x) ? x : fallback);
  const int = (x, fallback = 0) => (Number.isInteger(x) && x >= 0 ? x : fallback);
  const text = (x) => (typeof x === "string" ? x : "");

  function blank() {
    return { v: VERSION, start: null, done: {}, q: {}, checks: {}, drafts: {}, sess: {}, papers: [], prefs: {} };
  }

  function mapOf(source, fix) {
    const out = {};
    if (!isObject(source)) return out;
    for (const [key, value] of Object.entries(source)) {
      const fixed = isObject(value) ? fix(value) : null;
      if (fixed) out[key] = fixed;
    }
    return out;
  }

  function paperRecord(r) {
    if (typeof r.id !== "string" || typeof r.paper !== "string") return null;
    if (!["running", "done", "discarded"].includes(r.status)) return null;
    const base = {
      id: r.id,
      paper: r.paper,
      title: text(r.title),
      minutes: int(r.minutes, 60),
      status: r.status,
      started: num(r.started),
      ended: r.ended === null || r.ended === undefined ? null : num(r.ended),
      last: num(r.last, num(r.started)),
    };
    if (r.status === "discarded") return base;
    return {
      ...base,
      used_ms: num(r.used_ms),
      timed_out: Boolean(r.timed_out),
      questions: Array.isArray(r.questions) ? r.questions.filter((x) => typeof x === "string") : [],
      answers: isObject(r.answers) ? r.answers : {},
      onpaper: Array.isArray(r.onpaper) ? r.onpaper.filter((x) => typeof x === "string") : [],
      recorded: Array.isArray(r.recorded) ? r.recorded.filter((x) => typeof x === "string") : [],
      ticks: isObject(r.ticks) ? r.ticks : {},
      marks: isObject(r.marks) ? r.marks : {},
      passed: int(r.passed),
      failed: int(r.failed),
      to_mark: int(r.to_mark),
      score: int(r.score),
      max: int(r.max),
    };
  }

  // Whatever storage held (or null) -> a valid state. Unknown keys and damaged items are dropped.
  function normalise(raw) {
    const out = blank();
    if (!isObject(raw) || raw.v !== VERSION) return out;
    if (isObject(raw.start) && Number.isFinite(raw.start.ts)) out.start = { ts: raw.start.ts, last: num(raw.start.last) };
    out.done = mapOf(raw.done, (e) => ({ d: Boolean(e.d), last: num(e.last) }));
    out.q = mapOf(raw.q, (e) => ({ a: int(e.a), c: int(e.c), w: int(e.w), last: num(e.last), ok: Boolean(e.ok) }));
    out.checks = mapOf(raw.checks, (e) =>
      Number.isInteger(e.pick) ? { pick: e.pick, ok: Boolean(e.ok), last: num(e.last) } : null,
    );
    out.drafts = mapOf(raw.drafts, (e) => (typeof e.v === "string" ? { v: e.v, last: num(e.last) } : null));
    out.sess = mapOf(raw.sess, (e) => {
      if (!Array.isArray(e.ids) || !e.ids.every((x) => typeof x === "string")) return null;
      const res = {};
      for (const [id, v] of Object.entries(isObject(e.res) ? e.res : {})) {
        if (v === true || v === false || v === null) res[id] = v;
      }
      return { ids: e.ids, i: Math.min(int(e.i), e.ids.length), res, last: num(e.last) };
    });
    if (Array.isArray(raw.papers)) {
      out.papers = raw.papers.filter(isObject).map(paperRecord).filter(Boolean);
    }
    if (isObject(raw.prefs) && (raw.prefs.theme === "light" || raw.prefs.theme === "dark")) {
      out.prefs.theme = raw.prefs.theme;
    }
    return out;
  }

  // The newer of two copies of one item (by `last`); a tie keeps the first.
  const newer = (a, b) => (b && num(b.last) > num(a.last) ? b : a);

  function mergeMap(mine, theirs) {
    const out = { ...theirs };
    for (const [key, value] of Object.entries(mine)) out[key] = key in theirs ? newer(value, theirs[key]) : value;
    return out;
  }

  // Two copies of the state become one, item by item: the newer `last` of each item wins, so a tab
  // that only read never erases work done in another. Preferences are the first copy's.
  function merge(mine, theirs) {
    const papers = new Map(theirs.papers.map((p) => [p.id, p]));
    for (const p of mine.papers) papers.set(p.id, papers.has(p.id) ? newer(p, papers.get(p.id)) : p);
    let start = mine.start;
    if (theirs.start && (!start || theirs.start.last > start.last)) start = theirs.start;
    return {
      v: VERSION,
      start,
      done: mergeMap(mine.done, theirs.done),
      q: mergeMap(mine.q, theirs.q),
      checks: mergeMap(mine.checks, theirs.checks),
      drafts: mergeMap(mine.drafts, theirs.drafts),
      sess: mergeMap(mine.sess, theirs.sess),
      papers: [...papers.values()],
      prefs: { ...mine.prefs },
    };
  }

  // A stable string for comparing two states (keys sorted), to skip a write that changes nothing.
  function stableJson(value) {
    if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
    if (isObject(value)) {
      return `{${Object.keys(value)
        .sort()
        .map((k) => `${JSON.stringify(k)}:${stableJson(value[k])}`)
        .join(",")}}`;
    }
    return JSON.stringify(value);
  }

  return { VERSION, blank, normalise, merge, stableJson };
})();
