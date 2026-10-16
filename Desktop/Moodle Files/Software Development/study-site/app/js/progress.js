// Pure progress logic: the state shape, answer records, CI-style statuses, weak spots, and the
// merge used when two devices sync.
SD.progress = (() => {
  const PASS_MIN = 3;
  const PASS_RATE = 0.8;
  const FAIL_MIN = 2;
  const FAIL_RATE = 0.6;

  const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);

  // The whole persisted state. See app/API.md for each key.
  function blankState() {
    return {
      v: 1,
      q: {},
      fc: {},
      sec: {},
      exams: [],
      drafts: {},
      plan: {},
      prefs: { theme: null, timerHidden: false },
      last: null,
    };
  }

  // An exam record from storage or another device with missing parts gets safe defaults, so one
  // damaged record cannot break the page that shows it (see app/API.md for the shape).
  function repairExam(exam) {
    return {
      ...exam,
      title: typeof exam.title === "string" ? exam.title : String(exam.paper || "Paper"),
      questions: Array.isArray(exam.questions) ? exam.questions : [],
      answers: isObject(exam.answers) ? exam.answers : {},
      flags: Array.isArray(exam.flags) ? exam.flags : [],
      paper_answers: Array.isArray(exam.paper_answers) ? exam.paper_answers : [],
      recorded: Array.isArray(exam.recorded) ? exam.recorded : [],
      ticks: isObject(exam.ticks) ? exam.ticks : {},
      marks: isObject(exam.marks) ? exam.marks : {},
      started: Number.isFinite(exam.started) ? exam.started : 0,
      minutes: Number.isFinite(exam.minutes) ? exam.minutes : 60,
    };
  }

  // Accept whatever came out of storage; keep only well-formed parts.
  function normalise(raw) {
    const state = blankState();
    if (!isObject(raw) || raw.v !== 1) return state;
    for (const key of ["q", "fc", "sec", "drafts", "plan"]) {
      if (isObject(raw[key])) state[key] = raw[key];
    }
    if (Array.isArray(raw.exams)) state.exams = raw.exams.filter((e) => isObject(e) && e.id).map(repairExam);
    if (isObject(raw.prefs)) state.prefs = { ...state.prefs, ...raw.prefs };
    if (isObject(raw.last) && typeof raw.last.route === "string") state.last = raw.last;
    return state;
  }

  // One more attempt at a question. conf is "sure" | "unsure" | "guess" | null.
  function record(prev, ok, conf, now) {
    return {
      a: (prev ? prev.a : 0) + 1,
      c: (prev ? prev.c : 0) + (ok ? 1 : 0),
      last: now,
      ok: Boolean(ok),
      conf: conf || null,
    };
  }

  // Correct the verdict of the latest attempt without counting a new one (an open answer
  // re-marked after the student changed their ticks).
  function amend(entry, ok, now) {
    if (!entry) return record(null, ok, null, now);
    const c = entry.c - (entry.ok ? 1 : 0) + (ok ? 1 : 0);
    return { ...entry, c, ok: Boolean(ok), last: now };
  }

  // Wrong last time, or right but guessed.
  function isWeak(entry) {
    return Boolean(entry) && (!entry.ok || entry.conf === "guess");
  }

  // Status of a section from the last attempt at each of its questions:
  //   pass  >= 80% right with >= 3 answered (a section with fewer questions: all of them answered),
  //   fail  < 60% right with >= 2 answered (a one-question section: that question),
  //   part  answered something, not yet passing or failing,
  //   none  not tried.
  function sectionStatus(qids, qState) {
    let answered = 0;
    let correct = 0;
    for (const id of qids) {
      const entry = qState[id];
      if (!entry) continue;
      answered += 1;
      if (entry.ok) correct += 1;
    }
    const total = qids.length;
    const rate = answered > 0 ? correct / answered : 0;
    let status = "none";
    if (answered > 0) {
      status = "part";
      if (answered >= Math.min(PASS_MIN, total) && rate >= PASS_RATE) status = "pass";
      else if (answered >= Math.min(FAIL_MIN, total) && rate < FAIL_RATE) status = "fail";
    }
    return { status, answered, correct, total };
  }

  // A module fails if any section fails and passes only when every section passes; in between
  // it is "part" (some work done) or "none" (nothing tried).
  function moduleStatus(statuses) {
    const count = (name) => statuses.filter((s) => s === name).length;
    const pass = count("pass");
    const fail = count("fail");
    const part = count("part");
    const total = statuses.length;
    let status = "none";
    if (fail > 0) status = "fail";
    else if (total > 0 && pass === total) status = "pass";
    else if (pass + part > 0) status = "part";
    return { status, pass, fail, part, total };
  }

  // Weak questions, the one answered longest ago first (ties keep the given order).
  function weakSpots(qids, qState) {
    return qids
      .filter((id) => isWeak(qState[id]))
      .sort((a, b) => qState[a].last - qState[b].last);
  }

  function notTried(qids, qState) {
    return qids.filter((id) => !qState[id]);
  }

  // ---- merging two copies of the state (this device and the synced copy)

  function newer(a, b, key) {
    if (!a) return b;
    if (!b) return a;
    return (b[key] || 0) > (a[key] || 0) ? b : a;
  }

  function mergeMap(a, b, key) {
    const out = { ...(isObject(a) ? a : {}) };
    for (const [id, value] of Object.entries(isObject(b) ? b : {})) {
      out[id] = newer(out[id], value, key);
    }
    return out;
  }

  function mergeTimes(a, b) {
    const out = { ...(isObject(a) ? a : {}) };
    for (const [id, ts] of Object.entries(isObject(b) ? b : {})) {
      out[id] = Math.max(out[id] || 0, ts || 0);
    }
    return out;
  }

  function mergeExams(a, b) {
    const byId = new Map();
    for (const exam of [...(a || []), ...(b || [])]) {
      if (!isObject(exam) || !exam.id) continue;
      byId.set(exam.id, newer(byId.get(exam.id), exam, "last"));
    }
    return [...byId.values()].map(repairExam).sort((x, y) => (x.started || 0) - (y.started || 0));
  }

  // Item by item, the copy changed most recently wins. prefs stay local to the device.
  function mergeState(local, remote) {
    const r = isObject(remote) ? remote : {};
    return {
      ...local,
      q: mergeMap(local.q, r.q, "last"),
      fc: mergeMap(local.fc, r.fc, "last"),
      sec: mergeTimes(local.sec, r.sec),
      plan: mergeMap(local.plan, r.plan, "last"),
      drafts: mergeMap(local.drafts, r.drafts, "last"),
      exams: mergeExams(local.exams, Array.isArray(r.exams) ? r.exams : []),
      last: newer(local.last, isObject(r.last) ? r.last : null, "ts"),
    };
  }

  // JSON with sorted keys, so two equal states always compare equal as text.
  function stableJson(value) {
    if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
    if (isObject(value)) {
      const keys = Object.keys(value).filter((k) => value[k] !== undefined).sort();
      return `{${keys.map((k) => `${JSON.stringify(k)}:${stableJson(value[k])}`).join(",")}}`;
    }
    return JSON.stringify(value ?? null);
  }

  return {
    blankState,
    normalise,
    record,
    amend,
    isWeak,
    sectionStatus,
    moduleStatus,
    weakSpots,
    notTried,
    mergeState,
    stableJson,
  };
})();
