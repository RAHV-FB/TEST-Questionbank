// Pure paper logic: a sitting's record, its clock and warnings, answer states, marking, hand-in and
// recording a mark. No DOM, no store. A paper is {id, title, kind, minutes, questions: [ids]}.
CR.paper = (() => {
  const { marksOf } = CR.scoring;
  const MINUTE = CR.util.MINUTE;

  // The record of one sitting, saved on every change so a reload resumes with the right time left
  // (the clock runs from `started`, not from the page).
  function start(paper, questions, now) {
    return {
      id: `${paper.id}-${now}`,
      paper: paper.id,
      title: paper.title,
      minutes: paper.minutes,
      status: "running",
      started: now,
      ended: null,
      used_ms: 0,
      timed_out: false,
      questions: questions.map((q) => q.id),
      answers: {},
      onpaper: [],
      recorded: [],
      ticks: {},
      marks: {},
      passed: 0,
      failed: 0,
      to_mark: 0,
      score: 0,
      max: questions.reduce((sum, q) => sum + marksOf(q), 0),
      last: now,
    };
  }

  // ---- the clock

  const deadline = (record) => record.started + record.minutes * MINUTE;
  const timeLeft = (record, now) => Math.max(0, deadline(record) - now);
  const expired = (record, now) => record.status === "running" && now >= deadline(record);

  // The warning for the time left: 5 in the last five minutes, 10 in the last ten, else 0.
  function warning(left) {
    if (left <= 5 * MINUTE) return 5;
    if (left <= 10 * MINUTE) return 10;
    return 0;
  }

  // ---- answers and marking

  // "blank", "partial" (an open question with an empty part) or "full".
  // onPaper: the student wrote this open answer on paper, as on the day, so it counts as answered.
  function answerState(q, answer, onPaper = false) {
    if (q.type === "mcq") return Number.isInteger(answer) ? "full" : "blank";
    if (q.type === "open" && onPaper) return "full";
    let filled = 0;
    let total = 0;
    if (q.type === "open") {
      total = q.parts.length;
      filled = q.parts.filter((p) => String(answer?.[p.label] ?? "").trim() !== "").length;
    } else {
      total = q.items.length;
      filled = Array.isArray(answer) ? answer.filter((a) => a !== null && a !== undefined).length : 0;
    }
    if (filled === 0) return "blank";
    return filled === total ? "full" : "partial";
  }

  const tallyRow = () => ({ count: 0, passed: 0, failed: 0, toMark: 0, score: 0, max: 0 });

  function add(into, r) {
    into.count += 1;
    into.passed += r.status === "pass" ? 1 : 0;
    into.failed += r.status === "fail" ? 1 : 0;
    into.toMark += r.status === "mark" ? 1 : 0;
    into.score += r.score;
    into.max += r.max;
  }

  // Each question's result and the totals. A multiple-choice question scores 1 or 0 (blank is 0).
  // An open question scores what the student recorded against its rubric (record.marks), passes
  // only at full marks, scores 0 when left blank, and is "mark" (still to mark) until then.
  function mark(questions, record) {
    const marks = record.marks || {};
    const onPaper = new Set(record.onpaper || []);
    const results = questions.map((q) => {
      const answer = record.answers[q.id];
      const state = answerState(q, answer, onPaper.has(q.id));
      const max = marksOf(q);
      let score = 0;
      let status = "fail";
      if (q.type === "mcq") {
        score = state === "full" && q.options[answer]?.correct ? 1 : 0;
      } else if (q.type === "sort") {
        score = CR.scoring.sortScore(q, Array.isArray(answer) ? answer : []).full ? 1 : 0;
      } else if (state !== "blank" && q.id in marks) {
        score = Math.max(0, Math.min(max, marks[q.id]));
      } else if (state !== "blank") {
        status = "mark";
      }
      if (status !== "mark" && score === max) status = "pass";
      return { qid: q.id, tid: q.tid, type: q.type, state, status, score, max };
    });
    const totals = tallyRow();
    for (const r of results) add(totals, r);
    return { results, ...totals };
  }

  // The record with its summary fields (what the lists read) brought up to date.
  function withTotals(record, questions) {
    const m = mark(questions, record);
    return { ...record, passed: m.passed, failed: m.failed, to_mark: m.toMark, score: m.score, max: m.max };
  }

  // Marks lost per cram type, the most first: [{tid, lost, score, max}]. Questions still to mark
  // are left out (nothing is known yet); types that lost nothing are left out too.
  function lostByType(results) {
    const rows = new Map();
    for (const r of results) {
      if (r.status === "mark") continue;
      const row = rows.get(r.tid) || { tid: r.tid, lost: 0, score: 0, max: 0 };
      row.lost += r.max - r.score;
      row.score += r.score;
      row.max += r.max;
      rows.set(r.tid, row);
    }
    return [...rows.values()].filter((r) => r.lost > 0).sort((a, b) => b.lost - a.lost || (a.tid < b.tid ? -1 : 1));
  }

  // ---- hand-in

  // Hand the paper in. At or past the deadline it counts as time running out and ends at 0:00.
  // Returns the finished record (with totals) and the verdicts to count as attempts: every
  // multiple-choice question (a blank one is wrong) and every blank open question. An answered
  // open question is counted when its mark is recorded (recordMark).
  function handIn(record, questions, now, timedOut = false) {
    const end = deadline(record);
    const out = Boolean(timedOut) || now >= end;
    const ended = out ? end : now;
    const onPaper = new Set(record.onpaper || []);
    const outcomes = [];
    for (const q of questions) {
      if (record.recorded.includes(q.id)) continue;
      const answer = record.answers[q.id];
      if (q.type === "mcq") outcomes.push({ qid: q.id, ok: CR.scoring.mcqOk(q, answer) });
      else if (answerState(q, answer, onPaper.has(q.id)) === "blank") outcomes.push({ qid: q.id, ok: false });
    }
    const recorded = [...record.recorded, ...outcomes.map((o) => o.qid)];
    const finished = withTotals(
      { ...record, status: "done", ended, used_ms: ended - record.started, timed_out: out, recorded, last: now },
      questions,
    );
    return { record: finished, outcomes };
  }

  // Record the mark of an open question (ticks -> score). The first time it counts as an attempt,
  // after that it amends it. Returns the record and the verdict to apply.
  function recordMark(record, q, score, ticks, now) {
    const value = Math.max(0, Math.min(marksOf(q), score));
    const amend = record.recorded.includes(q.id);
    return {
      record: {
        ...record,
        marks: { ...record.marks, [q.id]: value },
        ticks: { ...record.ticks, [q.id]: ticks },
        recorded: amend ? record.recorded : [...record.recorded, q.id],
        last: now,
      },
      outcome: { qid: q.id, ok: value === marksOf(q), amend },
    };
  }

  // ---- the list of sittings

  // The sitting in progress (the latest started, should there be more than one), or null.
  function running(papers) {
    const live = papers.filter((p) => p.status === "running");
    return live.length ? live.reduce((a, b) => (b.started > a.started ? b : a)) : null;
  }

  // Sittings to show, newest first (discarded ones are not shown).
  const newestFirst = (papers) => papers.filter((p) => p.status !== "discarded").sort((a, b) => b.started - a.started);

  const lastDone = (papers, paperId) =>
    newestFirst(papers).find((p) => p.paper === paperId && p.status === "done") || null;

  // What is kept of a sitting the student threw away: no answers, nothing recorded.
  function discard(record, now) {
    const { id, paper, title, minutes, started } = record;
    return { id, paper, title, minutes, started, ended: now, status: "discarded", last: now };
  }

  return {
    start,
    deadline,
    timeLeft,
    expired,
    warning,
    answerState,
    mark,
    withTotals,
    lostByType,
    handIn,
    recordMark,
    running,
    newestFirst,
    lastDone,
    discard,
  };
})();
